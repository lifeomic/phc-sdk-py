from enum import Enum
from typing import Union

from phc.easy.summary.options.clinical_counts import (
    SummaryClinicalCountsOptions,
)


class SummaryClinicalType(str, Enum):
    OBSERVATION = "observation"
    CONDITION = "condition"
    MEDICATION = "medication"
    PROCEDURE = "procedure"
    MEDIA = "media"
    DEMOGRAPHIC = "demographic"

    # NOTE: Patient is not included because it's just a count
    # PATIENT = "patient"

    @classmethod
    def has_value(cls, value):
        return any(value == item.value for item in cls)


class SummaryOmicsType(str, Enum):
    TEST = "test"
    SEQUENCE = "sequence"
    GENE_VARIANT = "gene-variant"
    COPY_NUMBER_STATUS = "copynumber-status"
    CLINVAR_SIG = "clinvar-significance"
    ONCOPRINT = "oncoprint"

    @classmethod
    def has_value(cls, value):
        return any(value == item.value for item in cls)


class SummaryItemCountsOptions(SummaryClinicalCountsOptions):
    summary: Union[SummaryClinicalType, SummaryOmicsType]
