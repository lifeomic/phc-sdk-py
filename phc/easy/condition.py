import pandas as pd

from phc.easy.frame import Frame
from phc.easy.abstract.fhir_service_patient_item import FhirServicePatientItem


class Condition(FhirServicePatientItem):
    @staticmethod
    def table_name():
        return "condition"

    @staticmethod
    def code_fields():
        return [
            "meta.tag",
            "code.coding",
            "bodySite.coding",
            "stage.summary.coding",
        ]

    @staticmethod
    def transform_results(df: pd.DataFrame, **expand_args):
        return Frame.expand(
            df,
            date_columns=[
                *expand_args.get("date_columns", []),
                "onsetDateTime",
                "assertedDate",
                "onsetPeriod.start",
                "onsetPeriod.end",
            ],
            code_columns=[
                *expand_args.get("code_columns", []),
                "bodySite",
                "stage",
            ],
            custom_columns=[
                *expand_args.get("custom_columns", []),
                Frame.codeable_like_column_expander("subject"),
                Frame.codeable_like_column_expander("onsetPeriod"),
                Frame.codeable_like_column_expander("context"),
            ],
        )
