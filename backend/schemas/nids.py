from datetime import datetime
from typing import Dict, Union

from pydantic import BaseModel, Field

from schemas.users import UserOut
from utils.enums import AlertSeverity, AlertStatus


class PredictRequest(BaseModel):
    """Accepts a dictionary of features (key=column name, value=value)."""

    features: Dict[str, Union[float, int, str]] = Field(
        ..., example={"Flow Duration": 156, "Total Fwd Packets": 2, "Protocol": 6}
    )


class BinaryResult(BaseModel):
    label: str
    confidence: float
    is_malicious: bool


class MulticlassResult(BaseModel):
    label: str
    confidence: float
    probabilities: Dict[str, float]


class AnomalyResult(BaseModel):
    is_anomaly: bool
    anomaly_score: float
    threshold: float


class UnifiedPredictionResponse(BaseModel):
    id: int | None = None  # The Alert ID (new or existing)
    src_ip: str | None = None
    dst_ip: str | None = None
    status: str = "success"
    timestamp: str
    binary: BinaryResult
    multiclass: MulticlassResult
    anomaly: AnomalyResult
    threat_level: str


class FeatureContribution(BaseModel):
    feature: str
    value: Union[float, int, str]  # The actual value in the flow
    shap_value: float  # The push this feature gave towards "Malicious"


class ExplanationResponse(BaseModel):
    status: str = "success"
    predicted_label: str
    # Base value is the average model output before seeing this specific sample
    base_value: float
    # Top N features that pushed the prediction one way or the other
    contributions: list[FeatureContribution]


# --- Base Schema for Alerts ---
# This is the shared fields between create, update, and output
class AlertBase(BaseModel):
    title: str
    severity: AlertSeverity
    category: str | None = None
    src_ip: str | None = None
    dst_ip: str | None = None
    dst_port: int | None = None
    flow_timestamp: datetime


# --- Schema for Creating Alerts ---
# This is used when the NIDS creates a new alert
class AlertCreate(AlertBase):
    title: str
    severity: AlertSeverity
    category: str | None = None
    src_ip: str | None = None
    dst_ip: str | None = None
    dst_port: int | None = None
    flow_timestamp: datetime
    description: str | None = None
    model_output: dict | None = None
    flow_data: dict | None = None
    status: AlertStatus = AlertStatus.ACTIVE


# --- Schema for Updating Alerts ---
# This is used by an analyst to change the status, assign, or add notes
class AlertUpdate(BaseModel):
    status: AlertStatus | None = None
    assigned_to_id: int | None = None
    description: str | None = None  # For adding analyst notes


# --- Schema for API Output ---
# This is the full alert object sent to the frontend
class AlertOut(AlertBase):
    id: int
    title: str
    severity: AlertSeverity
    category: str | None = None
    src_ip: str | None = None
    dst_ip: str | None = None
    dst_port: int | None = None
    flow_timestamp: datetime
    status: AlertStatus
    description: str | None = None
    model_output: dict | None = None
    flow_data: dict | None = None
    assigned_to_id: int | None = None
    assigned_user: UserOut | None = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class AssignAlertRequest(BaseModel):
    user_id: int = Field(..., description="The ID of the user to assign the alert to.")


class ResolveAlertRequest(BaseModel):
    notes: str = Field(..., min_length=10, description="Analyst notes on how the alert was resolved.")


class AlertTimeSeriesPoint(BaseModel):
    """A single data point for a time-series chart."""

    timestamp: datetime
    count: int


class AlertsSummaryResponse(BaseModel):
    """Aggregated statistics for the alerts dashboard."""

    total_alerts: int
    by_status: Dict[AlertStatus, int]
    by_severity: Dict[AlertSeverity, int]
    by_category: list[Dict[str, Union[str, int]]]  # e.g., [{"category": "Bruteforce", "count": 10}]
    time_series: list[AlertTimeSeriesPoint]  # For a "alerts over time" chart


class RobustnessDemoResult(BaseModel):
    model_name: str  # e.g., "Baseline (Vulnerable)"
    input_type: str  # e.g., "Adversarial"
    predicted_label: str  # "Malicious" or "Benign"
    confidence: float


class RobustnessDemoResponse(BaseModel):
    status: str = "success"
    results: list[RobustnessDemoResult]
    adversarial_sample_preview: str  # A preview of the perturbed vector


class AdversarialMetric(BaseModel):
    """Holds the accuracy metrics for baseline and robust models."""

    model: str
    accuracy: float


class AdversarialExperimentResults(BaseModel):
    """Holds the results of the adversarial robustness experiment."""

    baseline_model_accuracy_normal: float
    baseline_model_accuracy_adversarial: float
    robust_model_accuracy_normal: float
    robust_model_accuracy_adversarial: float
    metrics: list[AdversarialMetric]
