import pandas as pd

from phc.easy.frame import Frame
from phc.easy.abstract.fhir_service_patient_item import FhirServicePatientItem


class Person(FhirServicePatientItem):
    @staticmethod
    def table_name():
        return "person"

    @staticmethod
    def patient_key():
        return "link.target.reference"

    @staticmethod
    def code_fields():
        return ["meta.tag"]

    @staticmethod
    def transform_results(df: pd.DataFrame, **expand_args):
        return Frame.expand(
            df,
            code_columns=[*expand_args.get("code_columns", []), "link"],
            custom_columns=[
                *expand_args.get("custom_columns", []),
                Frame.codeable_like_column_expander("subject"),
            ],
        )
