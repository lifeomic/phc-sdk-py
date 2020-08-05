import pandas as pd

from phc.easy.frame import Frame
from phc.easy.patient_item import PatientItem


class Specimen(PatientItem):
    @staticmethod
    def table_name():
        return "specimen"

    @staticmethod
    def code_keys():
        return ["type.coding", "meta.tag", "collection.bodySite.coding"]

    @staticmethod
    def transform_results(df: pd.DataFrame, **expand_args):
        return Frame.expand(
            df,
            code_columns=[*expand_args.get("code_columns", []), "collection"],
            custom_columns=[
                *expand_args.get("custom_columns", []),
                Frame.codeable_like_column_expander("subject"),
            ],
        )
