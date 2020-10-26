import pandas as pd

from phc.easy.frame import Frame
from phc.easy.patient_item import PatientItem


class Provenance(PatientItem):
    @staticmethod
    def table_name():
        return "provenance"

    @staticmethod
    def patient_key():
        """Patient relationship is based on who signed this provenance"""
        return "signature.whoReference.reference"

    @staticmethod
    def code_fields():
        return ["signature.type", "agent.role.coding", "meta.tag"]

    @staticmethod
    def transform_results(df: pd.DataFrame, **expand_args):
        return Frame.expand(
            df,
            date_columns=[
                *expand_args.get("date_columns", []),
                "recorded",
                "signature.when",
            ],
            code_columns=[
                *expand_args.get("code_columns", []),
                "agent",
                "signature",
            ],
        )
