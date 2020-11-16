import pandas as pd

from phc.easy.frame import Frame
from phc.easy.abstract.fhir_service_patient_item import FhirServicePatientItem


class Consent(FhirServicePatientItem):
    @staticmethod
    def table_name():
        return "consent"

    @staticmethod
    def patient_key():
        return "patient.reference"

    @staticmethod
    def code_fields():
        return ["meta.tag"]

    @staticmethod
    def transform_results(df: pd.DataFrame, **expand_args):
        return Frame.expand(
            df,
            date_columns=[*expand_args.get("date_columns", []), "dateTime"],
            custom_columns=[
                *expand_args.get("custom_columns", []),
                Frame.codeable_like_column_expander("sourceReference"),
                Frame.codeable_like_column_expander("actor"),
                Frame.codeable_like_column_expander("patient"),
            ],
        )
