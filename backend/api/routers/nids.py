from fastapi import APIRouter, status
from fastapi.responses import JSONResponse

from ml.models.predict import predict_sample_binary, predict_sample_multi
from schemas.nids import PredictBinaryResponse, PredictMultiResponse, PredictRequest, TrainRequest

router = APIRouter(prefix="/api/v1/nids", tags=["NIDS"])


@router.post("/predict/binary", response_model=PredictBinaryResponse, status_code=status.HTTP_200_OK)
def predict_traffic_binary(request: PredictRequest):
    """Run inference for binary classification of network traffic.

    Args:
        request (PredictRequest): The network traffic prediction request data.

    Returns:
        PredictResponse: Response containing binary prediction results
    """
    return predict_sample_binary(request.features)

@router.post("/predict/multiclass", response_model=PredictMultiResponse, status_code=status.HTTP_200_OK)
def predict_traffic_multi(request: PredictRequest):
    """Run inference for multiclass classification of network traffic.

    Args:
        request (PredictRequest): The network traffic prediction request data.

    Returns:
        PredictResponse: Response containing multiclass prediction results
    """
    return predict_sample_multi(request.features)


@router.post("/train", status_code=status.HTTP_202_ACCEPTED)
def adversarial_train(request: TrainRequest):
    """Placeholder for adversarial training endpoint."""
    # TODO: call ml.models.train or ml.features.adversarial
    return JSONResponse(
        content={"message": "Adversarial training not implemented yet."}, status_code=status.HTTP_202_ACCEPTED
    )


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
