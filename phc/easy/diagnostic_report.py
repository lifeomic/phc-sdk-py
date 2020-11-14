import pandas as pd

from phc.easy.frame import Frame
from phc.easy.abstract.fhir_service_patient_item import FhirServicePatientItem


class DiagnosticReport(FhirServicePatientItem):
    @staticmethod
    def table_name():
        return "diagnostic_report"

    @staticmethod
    def patient_id_prefixes():
        return ["Patient/", "urn:uuid:"]

    @staticmethod
    def patient_key():
        return "subject.reference"

    @staticmethod
    def code_fields():
        return ["meta.tag"]

    @staticmethod
    def transform_results(df: pd.DataFrame, **expand_args):
        return Frame.expand(
            df,
            custom_columns=[
                *expand_args.get("custom_columns", []),
                Frame.codeable_like_column_expander("subject"),
                Frame.codeable_like_column_expander("presentedForm"),
                Frame.codeable_like_column_expander("result"),
            ],
        )
