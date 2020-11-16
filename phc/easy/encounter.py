import pandas as pd

from phc.easy.frame import Frame
from phc.easy.abstract.fhir_service_patient_item import FhirServicePatientItem


class Encounter(FhirServicePatientItem):
    @staticmethod
    def table_name():
        return "encounter"

    @staticmethod
    def patient_key():
        return "subject.reference"

    @staticmethod
    def code_fields():
        return [
            "class",
            "priority.coding",
            "participant.type.coding",
            "length",
            "hospitalization.admitSource.coding",
            "hospitalization.dischargeDisposition.coding",
            "meta.tag",
        ]

    @staticmethod
    def transform_results(df: pd.DataFrame, **expand_args):
        return Frame.expand(
            df,
            date_columns=[
                *expand_args.get("date_columns", []),
                "period.start",
                "period.end",
            ],
            code_columns=[
                *expand_args.get("code_columns", []),
                "class",
                "priority",
                "participant",
                "length",
                "hospitalization",
            ],
            custom_columns=[
                *expand_args.get("custom_columns", []),
                Frame.codeable_like_column_expander("subject"),
                Frame.codeable_like_column_expander("period"),
                Frame.codeable_like_column_expander("reason"),
                Frame.codeable_like_column_expander("location"),
                Frame.codeable_like_column_expander("serviceProvider"),
            ],
        )
