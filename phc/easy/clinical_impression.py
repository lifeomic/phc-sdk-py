import pandas as pd

from phc.easy.frame import Frame
from phc.easy.abstract.fhir_service_patient_item import FhirServicePatientItem


class ClinicalImpression(FhirServicePatientItem):
    @staticmethod
    def table_name():
        return "clinical_impression"

    @staticmethod
    def code_fields():
        return [
            "meta.tag",
            "code.coding",
        ]

    @staticmethod
    def transform_results(df: pd.DataFrame, **expand_args):
        return Frame.expand(
            df,
            date_columns=[
                *expand_args.get("date_columns", []),
                "effectiveDateTime",
            ],
            custom_columns=[
                *expand_args.get("custom_columns", []),
                Frame.codeable_like_column_expander("subject"),
                Frame.codeable_like_column_expander("finding"),
            ],
        )

