from fastapi import APIRouter, HTTPException, status

from ml.models.predict import predict_full_report
from schemas.nids import PredictRequest, UnifiedPredictionResponse

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
