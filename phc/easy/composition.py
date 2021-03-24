import pandas as pd
from phc.easy.abstract.fhir_service_patient_item import FhirServicePatientItem
from phc.easy.frame import Frame


class Composition(FhirServicePatientItem):
    @staticmethod
    def table_name():
        return "composition"

    @staticmethod
    def code_fields():
        return ["meta.tag"]

    @staticmethod
    def transform_results(df: pd.DataFrame, **expand_args):
        return Frame.expand(
            df,
            date_columns=[*expand_args.get("date_columns", []), "date"],
            code_columns=[
                *expand_args.get("code_columns", []),
                "type",
                "author",
            ],
            custom_columns=[
                *expand_args.get("custom_columns", []),
                Frame.codeable_like_column_expander("subject"),
                Frame.codeable_like_column_expander("text"),
                Frame.codeable_like_column_expander("relatesTo"),
            ],
        )
