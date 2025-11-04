from typing import List, Optional

from pydantic import BaseModel


class PredictRequest(BaseModel):
    features: List[float]


class PredictBinaryResponse(BaseModel):
    binary: str
    binary_proba: Optional[List[float]] = None

class PredictMultiResponse(BaseModel):
    multilabel: str
    multilabel_proba: Optional[List[float]] = None


class TrainRequest(BaseModel):
    epochs: Optional[int] = 10
    adversarial_method: Optional[str] = "FGSM"
