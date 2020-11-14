import pandas as pd

from phc.easy.frame import Frame
from phc.easy.abstract.fhir_service_patient_item import FhirServicePatientItem


class Immunization(FhirServicePatientItem):
    @staticmethod
    def table_name():
        return "immunization"

    @staticmethod
    def patient_id_prefixes():
        return ["Patient/", "urn:uuid:"]

    @staticmethod
    def patient_key():
        return "patient.reference"

    @staticmethod
    def code_fields():
        return ["vaccineCode.coding", "meta.tag"]

    @staticmethod
    def transform_results(df: pd.DataFrame, **expand_args):
        return Frame.expand(
            df,
            date_columns=[*expand_args.get("date_columns", []), "date"],
            code_columns=[*expand_args.get("code_columns", []), "vaccineCode"],
            custom_columns=[
                *expand_args.get("custom_columns", []),
                Frame.codeable_like_column_expander("patient"),
                Frame.codeable_like_column_expander("encounter"),
            ],
        )
