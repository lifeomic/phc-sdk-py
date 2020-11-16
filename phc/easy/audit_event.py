import pandas as pd

from phc.easy.frame import Frame
from phc.easy.abstract.fhir_service_patient_item import FhirServicePatientItem


class AuditEvent(FhirServicePatientItem):
    @staticmethod
    def table_name():
        return "audit_event"

    @staticmethod
    def patient_key():
        return "entity.reference.reference"

    @staticmethod
    def code_fields():
        return ["source.type", "entity.lifecycle"]

    @staticmethod
    def transform_results(df: pd.DataFrame, **expand_args):
        return Frame.expand(
            df,
            date_columns=[
                *expand_args.get("date_columns", []),
                "effectiveDateTime",
            ],
            code_columns=[
                *expand_args.get("code_columns", []),
                "type",
                "subtype",
            ],
            custom_columns=[
                *expand_args.get("custom_columns", []),
                Frame.codeable_like_column_expander("agent"),
                Frame.codeable_like_column_expander("source"),
                Frame.codeable_like_column_expander("entity"),
            ],
        )

    @staticmethod
    def get_count_by_patient():
        raise ValueError("AuditEvent records are not exclusive to a patient.")
