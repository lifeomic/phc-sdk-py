from enum import Enum


class ClinVarReview(str, Enum):
    PRACTICE_GUIDELINE = "practice guideline"
    REVIEWED_BY_EXPERT_PANEL = "reviewed by expert panel"
    CRITERIA_PROVIDED_MULTIPLE_SUBMITTERS_NO_CONFLICTS = (
        "criteria provided, multiple submitters, no conflicts"
    )
    CRITERIA_PROVIDED_SINGLE_SUBMITTER = "criteria provided, single submitter"
    CRITERIA_PROVIDED_CONFLICTING_INTERPRETATIONS = (
        "criteria provided, conflicting interpretations"
    )
    NO_ASSERTION_CRITERIA_PROVIDED = "no assertion criteria provided"
    NO_ASSERTION_PROVIDED = "no assertion provided"
    NO_INTERPRETATION_FOR_THE_SINGLE_VARIANT = (
        "no interpretation for the single variant"
    )
