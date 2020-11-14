import pandas as pd

from phc.easy.frame import Frame
from phc.easy.abstract.fhir_service_patient_item import FhirServicePatientItem


class Media(FhirServicePatientItem):
    @staticmethod
    def table_name():
        return "media"

    @staticmethod
    def code_fields():
        return ["bodySite.coding", "meta.tag"]

    @staticmethod
    def transform_results(df: pd.DataFrame, **expand_args):
        return Frame.expand(
            df,
            date_columns=[
                *expand_args.get("date_columns", []),
                "occurrenceDateTime",
            ],
            code_columns=[*expand_args.get("code_columns", []), "bodySite"],
            custom_columns=[
                *expand_args.get("custom_columns", []),
                Frame.codeable_like_column_expander("subject"),
                (
                    "content",
                    lambda r: pd.json_normalize(r).add_prefix("content."),
                ),
            ],
        )
