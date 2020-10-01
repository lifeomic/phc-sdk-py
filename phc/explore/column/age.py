from typing import List
import pandas as pd
import numpy as np

from phc.explore.column import Column, ColumnConfig

NAME = "Age"


def get_possible_columns(preview: pd.DataFrame) -> List[str]:
    return [
        c
        for c in preview.columns
        if "birth" in c and isinstance(preview.dtypes[c], pd.DatetimeTZDtype)
    ]


def transform(df: pd.DataFrame, config: ColumnConfig):
    return pd.Series(
        np.floor(
            (
                pd.Timestamp("now", tz="UTC") - df[config.column]
            ).dt.total_seconds()
            / (3600 * 24 * 365)
        ),
        dtype=pd.Int32Dtype(),
    ).rename(NAME)


age = Column(
    name=NAME, get_possible_columns=get_possible_columns, transform=transform
)

__all__ = ["age"]
