import pandas as pd
from phc.explore.imports import w

from phc.explore.view.column.custom import CustomColumnView


class SubjectIdColumnView(CustomColumnView):
    column_selector: w.Dropdown

    @staticmethod
    def name():
        return "Subject ID"

    @staticmethod
    def relevant_columns(preview: pd.DataFrame):
        return [c for c in preview.columns if "subject" in c and "value" in c]

    @classmethod
    def transform(cls, df: pd.DataFrame, attrs: dict):
        # simple selection of column
        return df[attrs["column"]].rename(cls.name())
