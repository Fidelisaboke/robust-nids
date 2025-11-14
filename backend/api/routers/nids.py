import logging
from collections import deque
from datetime import datetime, timedelta, timezone

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, Query, status
from fastapi_pagination import Page
from fastapi_pagination.ext.sqlalchemy import paginate

from api.dependencies import get_current_active_user, require_permissions
from database.models import User
from ml.models.explain import explain_binary
from ml.models.predict import predict_full_report
from schemas.nids import (
    AlertCreate,
    AlertOut,
    AlertsSummaryResponse,
    AssignAlertRequest,
    ExplanationResponse,
    PredictRequest,
    ResolveAlertRequest,
    UnifiedPredictionResponse,
)
from services.alert_service import AlertService, get_alert_service
from services.email_service import EmailService, get_email_service
from services.exceptions.alert import AlertNotFoundError
from services.exceptions.user import UserNotFoundError
from utils.constants import BENIGN_LABELS
from utils.enums import AlertSeverity, AlertStatus, SystemPermissions

router = APIRouter(prefix="/api/v1/nids", tags=["NIDS"])

# In-memory storage for recent high-threat events (last 50)
RECENT_ALERTS = deque(maxlen=50)

# Aggregation State (prevents alert flooding)
# Key: (src_ip, attack_type) -> Value: {first_seen, last_seen, count, alert_id}
ACTIVE_INCIDENTS = {}
AGGREGATION_WINDOW = timedelta(seconds=60)  # Group events happening within 60s

# Ignore benign traffic labels
IGNORED_LABELS = BENIGN_LABELS

app_logger = logging.getLogger("uvicorn.error")


async def _create_alert_from_report(
    report: dict,
    request: PredictRequest,
    alert_service: AlertService,
    email_service: EmailService,
    background_tasks: BackgroundTasks,
) -> AlertOut | None:
    """Helper to convert a prediction report into a database alert."""

    # 1. Create the AlertCreate schema
    alert_data = AlertCreate(
        title=f"{report['multiclass']['label']} detected from {report['src_ip']}",
        severity=AlertSeverity(report["threat_level"].lower()),
        category=report["multiclass"]["label"],
        src_ip=report["src_ip"],
        dst_ip=report["dst_ip"],
        dst_port=int(request.features.get("dst_port", 0)),
        flow_timestamp=datetime.fromisoformat(report["timestamp"]),
        model_output=report,  # Store the full JSON report
    )

    # 2. Save to DB (and send email)
    # This runs in the current session, managed by the dependency.
    try:
        new_alert = alert_service.create_alert(alert_data)
        # Send email if alert is Critical
        if new_alert.severity == AlertSeverity.CRITICAL:
            await email_service.send_critical_alert_notification(background_tasks, new_alert)
        return AlertOut.model_validate(new_alert, from_attributes=True)
    except Exception as e:
        app_logger.error(f"Failed to create alert in database: {e}")
        return None


@router.post(
    "/predict/full",
    response_model=UnifiedPredictionResponse,
    status_code=status.HTTP_200_OK,
)
async def predict_traffic_full(
    request: PredictRequest,
    background_tasks: BackgroundTasks,
    alert_service: AlertService = Depends(get_alert_service),
    email_service: EmailService = Depends(get_email_service),
):
    """
    Runs a complete security assessment on a network flow.
    High/Critical threats are aggregated and saved to the database.
    """
    try:
        # 1. Run inference
        result = predict_full_report(request.features)
        result["id"] = None  # Default: no alert created yet

        # 2. Aggregation & Alert Creation Logic
        if result["threat_level"] in ["High", "Critical"]:
            src_ip = result.get("src_ip", "unknown")
            attack_type = result["multiclass"]["label"]
            now = datetime.now(timezone.utc)

            incident_key = (src_ip, attack_type)
            incident = ACTIVE_INCIDENTS.get(incident_key)

            # New incident or outside aggregation window
            if not incident or (now - incident["last_seen"] > AGGREGATION_WINDOW):
                # 3. Create persistent alert in DB
                alert_obj = await _create_alert_from_report(
                    result, request, alert_service, email_service, background_tasks
                )

                if alert_obj:
                    result["id"] = alert_obj.id
                    # Add to recent alerts for live view
                    RECENT_ALERTS.appendleft(result)

                    # Update aggregation cache
                    ACTIVE_INCIDENTS[incident_key] = {
                        "first_seen": now,
                        "last_seen": now,
                        "count": 1,
                        "alert_id": result["id"],
                    }
            else:
                # This is an existing incident. Just update cache.
                incident["count"] += 1
                incident["last_seen"] = now
                result["id"] = incident["alert_id"]  # Return the ID of the original alert

        return result
    except RuntimeError as e:
        raise HTTPException(status_code=status.HTTP_503, detail=str(e))
    except Exception as e:
        app_logger.error(f"Inference failed: {e}", exc_info=True)
        raise HTTPException(status_code=400, detail=f"Inference failed: {str(e)}")


@router.get("/live-events", response_model=list[UnifiedPredictionResponse], status_code=status.HTTP_200_OK)
def get_live_events():
    """
    Fetch the 50 most recent High/Critical threats.
    Used by the frontend dashboard for real-time polling.
    """
    return list(RECENT_ALERTS)


@router.delete("/live-events", status_code=status.HTTP_204_NO_CONTENT)
def clear_live_events():
    """Clears all currently displayed live alerts."""
    RECENT_ALERTS.clear()
    ACTIVE_INCIDENTS.clear()
    return None


@router.get(
    "/alerts",
    response_model=Page[AlertOut],
    dependencies=[Depends(require_permissions(SystemPermissions.VIEW_ALERTS))],
    status_code=status.HTTP_200_OK,
)
def list_alerts(
    start_date: datetime | None = Query(None, description="Filter by start date (ISO8601)"),
    end_date: datetime | None = Query(None, description="Filter by end date (ISO8601)"),
    severity: AlertSeverity | None = Query(None),
    status: AlertStatus | None = Query(None),
    sort_by: str = Query("flow_timestamp"),
    sort_direction: str = Query("desc"),
    alert_service: AlertService = Depends(get_alert_service),
):
    """
    Get a paginated list of all persisted alerts with filtering.
    """
    alert_query = alert_service.list_alerts(
        start_date=start_date,
        end_date=end_date,
        severity=severity,
        status=status,
        sort_by=sort_by,
        sort_direction=sort_direction,
    )
    return paginate(alert_service.alert_repo.session, alert_query)


@router.get(
    "/alerts/summary",
    response_model=AlertsSummaryResponse,
    dependencies=[Depends(require_permissions(SystemPermissions.VIEW_ALERTS))],
    status_code=status.HTTP_200_OK,
)
def get_alerts_summary(
    start_date: datetime | None = Query(None, description="Start date (ISO8601)"),
    end_date: datetime | None = Query(None, description="End date (ISO8601)"),
    group_by_time: str = Query("day", enum=["day", "hour"]),
    alert_service: AlertService = Depends(get_alert_service),
):
    """
    Get aggregated statistics for alerts.
    """
    if not end_date:
        end_date = datetime.now(timezone.utc)
    if not start_date:
        start_date = end_date - timedelta(days=7)  # Default to last 7 days

    return alert_service.get_alert_summary(
        start_date=start_date, end_date=end_date, group_by_time=group_by_time
    )


@router.get(
    "/alerts/{alert_id}",
    response_model=AlertOut,
    dependencies=[Depends(require_permissions(SystemPermissions.VIEW_ALERTS))],
    status_code=status.HTTP_200_OK,
)
def get_alert(alert_id: int, alert_service: AlertService = Depends(get_alert_service)):
    """Fetch a specific alert by its ID."""
    return alert_service.get_alert(alert_id)


@router.delete(
    "/alerts/{alert_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    dependencies=[Depends(require_permissions(SystemPermissions.DELETE_ALERTS))],
)
async def delete_alert(alert_id: int, alert_service: AlertService = Depends(get_alert_service)):
    """Delete an alert by its ID."""
    return alert_service.delete_alert(alert_id)


@router.patch(
    "/alerts/{alert_id}/assign",
    response_model=AlertOut,
    status_code=status.HTTP_200_OK,
    dependencies=[Depends(require_permissions(SystemPermissions.UPDATE_ALERT_STATUS))],
)
def assign_alert(
    alert_id: int,
    request: AssignAlertRequest,
    alert_service: AlertService = Depends(get_alert_service),
    current_user: User = Depends(get_current_active_user),
):
    """
    Assign an alert to a user for investigation.

    - Admins can assign to any user
    - Analysts can assign to themselves
    - The user_id in the request determines who gets assigned
    """
    try:
        # Check if user is trying to assign to themselves or is an admin
        is_self_assignment = request.user_id == current_user.id
        is_admin = any(role.name == "admin" for role in current_user.roles)

        # Analysts can only self-assign unless they're also admins
        if not is_admin and not is_self_assignment:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You can only assign alerts to yourself. Contact an admin to assign to others.",
            )

        alert = alert_service.assign_alert(alert_id, request.user_id)
        return alert
    except AlertNotFoundError:
        raise HTTPException(status_code=404, detail="Alert not found")
    except UserNotFoundError:
        raise HTTPException(status_code=404, detail="User not found")
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.patch(
    "/alerts/{alert_id}/acknowledge",
    response_model=AlertOut,
    dependencies=[Depends(require_permissions(SystemPermissions.UPDATE_ALERT_STATUS))],
    status_code=status.HTTP_200_OK,
)
def acknowledge_alert(
    alert_id: int,
    alert_service: AlertService = Depends(get_alert_service),
    current_user: User = Depends(get_current_active_user),
):
    """Acknowledge an alert, marking it as 'ACKNOWLEDGED'."""
    try:
        alert = alert_service.acknowledge_alert(alert_id, current_user)
        return alert
    except AlertNotFoundError:
        raise HTTPException(status_code=404, detail="Alert not found")


@router.patch(
    "/alerts/{alert_id}/resolve",
    response_model=AlertOut,
    dependencies=[Depends(require_permissions(SystemPermissions.UPDATE_ALERT_STATUS))],
    status_code=status.HTTP_200_OK,
)
def resolve_alert(
    alert_id: int,
    request: ResolveAlertRequest,
    alert_service: AlertService = Depends(get_alert_service),
    current_user: User = Depends(get_current_active_user),
):
    """Resolve an alert, marking it 'RESOLVED' and adding analyst notes."""
    try:
        alert = alert_service.resolve_alert(alert_id, current_user, request.notes)
        return alert
    except AlertNotFoundError:
        raise HTTPException(status_code=404, detail="Alert not found")


@router.post("/explain/binary", response_model=ExplanationResponse)
def explain_traffic_binary(request: PredictRequest):
    """
    Generates a SHAP explanation for a specific network flow.
    Shows which features pushed the model towards 'Malicious' or 'Benign'.
    """
    try:
        explanation = explain_binary(request.features)
        return {
            "status": "success",
            "predicted_label": "Calculated by Frontend",
            "base_value": explanation["base_value"],
            "contributions": explanation["contributions"],
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Explanation failed: {str(e)}")
