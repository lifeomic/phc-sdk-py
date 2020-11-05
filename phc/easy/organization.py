import pandas as pd

from phc.easy.frame import Frame
from phc.easy.item import Item


class Organization(Item):
    @staticmethod
    def table_name():
        return "organization"

    @staticmethod
    def code_fields():
        return ["type.coding", "meta.tag"]

    @staticmethod
    def transform_results(df: pd.DataFrame, **expand_args):
        return Frame.expand(
            df,
            code_columns=[*expand_args.get("code_columns", []), "type"],
            custom_columns=[
                *expand_args.get("custom_columns", []),
                Frame.codeable_like_column_expander("subject"),
            ],
        )
