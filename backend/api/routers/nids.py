from fastapi import APIRouter, HTTPException, status
from fastapi.responses import JSONResponse

from ml.models.explain import explain_binary
from ml.models.predict import predict_full_report
from schemas.nids import ExplanationResponse, PredictRequest, UnifiedPredictionResponse

router = APIRouter(prefix="/api/v1/nids", tags=["NIDS"])


@router.post("/predict/full", response_model=UnifiedPredictionResponse, status_code=status.HTTP_200_OK)
async def predict_traffic_full(request: PredictRequest):
    """
    Runs a complete security assessment on a network flow.
    Executes Binary, Multiclass, and Anomaly detection models in parallel.
    """
    try:
        # We pass request.features (the dict) directly to our new predictor
        return predict_full_report(request.features)
    except RuntimeError as e:
        raise HTTPException(status_code=503, detail=str(e))
    except Exception as e:
        # Catch-all for pipeline errors (e.g., missing features in input)
        raise HTTPException(status_code=400, detail=f"Inference failed: {str(e)}")


@router.post("/explain/binary", response_model=ExplanationResponse)
def explain_traffic_binary(request: PredictRequest):
    """
    Generates a SHAP explanation for a specific network flow.
    Shows which features pushed the model towards 'Malicious' or 'Benign'.
    """
    try:
        # Run explanation generation
        explanation = explain_binary(request.features)

        return {
            "status": "success",
            "predicted_label": "Calculated by Frontend",
            "base_value": explanation["base_value"],
            "contributions": explanation["contributions"],
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Explanation failed: {str(e)}")


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
