import pandas as pd
from phc.explore.imports import w
import numpy as np

from phc.explore.view.column.custom import CustomColumnView


class AgeColumnView(CustomColumnView):
    column_selector: w.Dropdown

    @staticmethod
    def name():
        return "Age"

    @staticmethod
    def relevant_columns(preview: pd.DataFrame):
        return [
            c
            for c in preview.columns
            if "birth" in c
            and isinstance(preview.dtypes[c], pd.DatetimeTZDtype)
        ]

    @classmethod
    def transform(cls, df: pd.DataFrame, config: dict):
        return pd.Series(
            np.floor(
                (
                    pd.Timestamp("now", tz="UTC") - df[config["column"]]
                ).dt.total_seconds()
                / (3600 * 24 * 365)
            ),
            dtype=pd.Int32Dtype(),
        ).rename(cls.name())
