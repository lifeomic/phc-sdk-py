import pandas as pd

from phc.easy.frame import Frame
from phc.easy.abstract.fhir_service_patient_item import FhirServicePatientItem


class ProcedureRequest(FhirServicePatientItem):
    @staticmethod
    def table_name():
        return "procedure_request"

    @staticmethod
    def code_fields():
        return ["code.coding", "meta.tag"]

    @staticmethod
    def transform_results(df: pd.DataFrame, **expand_args):
        return Frame.expand(
            df,
            date_columns=[
                *expand_args.get("date_columns", []),
                "occurrencePeriod.start",
                "occurrencePeriod.end",
                "occurrenceDateTime",
                "authoredOn",
            ],
            custom_columns=[
                *expand_args.get("custom_columns", []),
                Frame.codeable_like_column_expander("subject"),
                Frame.codeable_like_column_expander("context"),
                Frame.codeable_like_column_expander("occurrencePeriod"),
                Frame.codeable_like_column_expander("note"),
            ],
        )
