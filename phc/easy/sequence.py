import pandas as pd

from phc.easy.frame import Frame
from phc.easy.patient_item import PatientItem


class Sequence(PatientItem):
    @staticmethod
    def table_name():
        return "sequence"

    @staticmethod
    def patient_key() -> str:
        return "patient.reference"

    @staticmethod
    def transform_results(data_frame: pd.DataFrame, **expand_args):
        args = {
            **expand_args,
            "code_columns": [
                *expand_args.get("code_columns", []),
                "specimen",
                "repository",
            ],
            "custom_columns": [
                *expand_args.get("custom_columns", []),
                Frame.codeable_like_column_expander("patient"),
                Frame.codeable_like_column_expander("referenceSeq"),
            ],
        }

        return Frame.expand(data_frame, **args)
