from typing import List, Optional

from pydantic import BaseModel


class PredictRequest(BaseModel):
    features: List[float]


class PredictResponse(BaseModel):
    prediction: str
    confidence: Optional[float]


class TrainRequest(BaseModel):
    epochs: Optional[int] = 10
    adversarial_method: Optional[str] = "FGSM"
