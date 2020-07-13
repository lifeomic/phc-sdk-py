import pandas as pd

from phc.easy.frame import Frame
from phc.easy.patient_item import PatientItem


class Consent(PatientItem):
    @staticmethod
    def table_name():
        return "consent"

    @staticmethod
    def patient_key():
        return "patient.reference"

    @staticmethod
    def transform_results(df: pd.DataFrame, **expand_args):
        return Frame.expand(
            df,
            date_columns=[*expand_args.get("date_columns", []), "dateTime"],
            custom_columns=[
                *expand_args.get("custom_columns", []),
                Frame.codeable_like_column_expander("patient"),
                Frame.codeable_like_column_expander("actor"),
                Frame.codeable_like_column_expander("sourceReference"),
            ],
        )
