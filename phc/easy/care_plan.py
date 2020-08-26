import pandas as pd

from phc.easy.frame import Frame
from phc.easy.patient_item import PatientItem


class CarePlan(PatientItem):
    @staticmethod
    def table_name():
        return "care_plan"

    @staticmethod
    def code_keys():
        return ["meta.tag", "category.coding"]

    @staticmethod
    def transform_results(df: pd.DataFrame, **expand_args):
        return Frame.expand(
            df,
            custom_columns=[
                *expand_args.get("custom_columns", []),
                Frame.codeable_like_column_expander("subject"),
                Frame.codeable_like_column_expander("context"),
                Frame.codeable_like_column_expander("activity"),
            ],
        )
