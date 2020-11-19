from enum import Enum


class ClinVarSignificance(str, Enum):
    LIKELY_PATHOGENIC = "Pathogenic:like"
    UNCERTAIN_SIGNIFICANCE = "Uncertain significance:like"
    LIKELY_BENIGN = "Benign:like"
    CONFLICTING_INTERPRETATIONS = (
        "Conflicting interpretations of pathogenicity:like"
    )
    ASSOCIATION = "association:like"
    RISK_FACTOR = "risk factor:like"
    DRUG_RESPONSE = "drug response:like"
    NOT_PROVIDED = "not provided:like"
