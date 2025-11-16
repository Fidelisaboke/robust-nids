from typing import Dict

from pydantic import BaseModel


# This schema models the "fgsm" or "pgd" objects
# e.g., "fgsm": { "acc": 0.045, "asr": 0.954 }
class AttackMetrics(BaseModel):
    """Holds the accuracy and attack success rate for a specific attack type."""
    acc: float
    asr: float

# This schema models the "0.05" or "0.1" objects within baseline_results
# e.g., "0.05": { "fgsm": {...}, "pgd": {...} }
class BaselineEpsilonResult(BaseModel):
    """Holds the FGSM and PGD metrics for a specific epsilon in the baseline test."""
    fgsm: AttackMetrics
    pgd: AttackMetrics

# This schema models the "0.05" or "0.1" objects within robust_results
# e.g., "0.05": { "fgsm": {...}, "pgd": {...}, "mixed_acc": 0.999 }
class RobustEpsilonResult(BaseModel):
    """Holds the FGSM, PGD, and mixed_acc metrics for a specific epsilon in the robust test."""
    fgsm: AttackMetrics
    pgd: AttackMetrics
    mixed_acc: float

# This schema models the "baseline_results" object
class BaselineResultSet(BaseModel):
    """Contains the clean accuracy and all epsilon results for the baseline model."""
    clean_acc: float
    epsilons: Dict[str, BaselineEpsilonResult]

# This schema models the "robust_results" object
class RobustResultSet(BaseModel):
    """Contains all epsilon results for the robust (adversarially-trained) model."""
    epsilons: Dict[str, RobustEpsilonResult]

# This is the main, top-level schema for parsing the entire file (except "config")
class AdversarialReportFileSchema(BaseModel):
    """
    Pydantic schema for validating the structure of 'adversarial_experiment.json'.
    This is used by the backend to load and parse the experiment results.
    """
    baseline_clean_acc: float
    baseline_results: BaselineResultSet
    robust_clean_acc: float
    robust_results: RobustResultSet
