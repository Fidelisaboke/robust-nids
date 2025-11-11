import uuid
from collections import deque
from datetime import datetime, timedelta, timezone

from fastapi import APIRouter, HTTPException, status
from fastapi.responses import JSONResponse

from ml.models.explain import explain_binary
from ml.models.predict import predict_full_report
from schemas.nids import ExplanationResponse, PredictRequest, UnifiedPredictionResponse
from utils.constants import BENIGN_LABELS

router = APIRouter(prefix="/api/v1/nids", tags=["NIDS"])

# In-memory storage for recent high-threat events (last 50)
# TODO: Replace with a proper database or caching solution
RECENT_ALERTS = deque(maxlen=50)

# Aggregation State (prevents alert flooding)
# Key: (src_ip, attack_type) -> Value: {first_seen, last_seen, count, alert_id}
ACTIVE_INCIDENTS = {}
AGGREGATION_WINDOW = timedelta(seconds=60)  # Group events happening within 60s

# Ignore benign traffic labels
IGNORED_LABELS = BENIGN_LABELS


@router.post("/predict/full", response_model=UnifiedPredictionResponse, status_code=status.HTTP_200_OK)
async def predict_traffic_full(request: PredictRequest):
    try:
        # Run inference
        result = predict_full_report(request.features)

        # --- Aggregation Logic ---
        if result["threat_level"] in ["High", "Critical"]:
            # Extract key identifiers from the raw features
            src_ip = request.features.get("src_ip", "unknown")
            attack_type = result["multiclass"]["label"]
            now = datetime.now(timezone.utc)

            incident_key = (src_ip, attack_type)
            incident = ACTIVE_INCIDENTS.get(incident_key)

            if incident and (now - incident["last_seen"] < AGGREGATION_WINDOW):
                # Existing incident: just update the counter, don't push to frontend
                incident["count"] += 1
                incident["last_seen"] = now
                # Optional: You could update the existing alert in RECENT_ALERTS if you want
                # to show a live counter on the dashboard, but skipping it is easier for V1.
            else:
                # New incident (or old one timed out): Create fresh alert
                result["id"] = str(uuid.uuid4())
                RECENT_ALERTS.appendleft(result)

                ACTIVE_INCIDENTS[incident_key] = {
                    "first_seen": now,
                    "last_seen": now,
                    "count": 1,
                    "alert_id": result["id"],
                }

        return result
    except RuntimeError as e:
        raise HTTPException(status_code=503, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Inference failed: {str(e)}")


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
    return None


@router.get("/alerts", status_code=status.HTTP_200_OK)
def list_alerts():
    """Fetch recent intrusion detection alerts."""
    # TODO: query from alerts table or logs
    return JSONResponse(
        content={"alerts": [], "message": "No alerts yet (placeholder)."}, status_code=status.HTTP_200_OK
    )


@router.get("/alerts/{alert_id}", status_code=status.HTTP_200_OK)
def get_alert(alert_id: int):
    """Fetch a specific alert by its ID."""
    # TODO: query from alerts table by alert_id
    return JSONResponse(
        content={"alert": None, "message": f"No alert found with ID {alert_id} (placeholder)."},
        status_code=status.HTTP_200_OK,
    )


@router.get("/logs", status_code=status.HTTP_200_OK)
def list_logs():
    """Fetch system or training logs."""
    # TODO: integrate with logging system or database logs table
    return JSONResponse(
        content={"logs": [], "message": "No logs yet (placeholder)."}, status_code=status.HTTP_200_OK
    )
