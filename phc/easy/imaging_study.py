import pandas as pd

from phc.easy.frame import Frame
from phc.easy.patient_item import PatientItem


class ImagingStudy(PatientItem):
    @staticmethod
    def table_name():
        return "imaging_study"

    @staticmethod
    def patient_key():
        return "patient.reference"

    @staticmethod
    def code_keys():
        return ["procedureCode.coding" "meta.tag"]

    @staticmethod
    def transform_results(df: pd.DataFrame, **expand_args):
        return Frame.expand(
            df,
            code_columns=[
                *expand_args.get("code_columns", []),
                "procedureCode",
            ],
            custom_columns=[
                *expand_args.get("custom_columns", []),
                Frame.codeable_like_column_expander("patient"),
                Frame.codeable_like_column_expander("context"),
            ],
        )
