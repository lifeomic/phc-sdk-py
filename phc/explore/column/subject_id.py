from typing import List
import pandas as pd

from phc.explore.column import Column, ColumnConfig

NAME = "Subject ID"


def get_possible_columns(preview: pd.DataFrame) -> List[str]:
    return [c for c in preview.columns if "subject" in c and "value" in c]


def transform(df: pd.DataFrame, config: ColumnConfig):
    return df[config.column].rename(NAME)


subject_id = Column(
    name=NAME, get_possible_columns=get_possible_columns, transform=transform
)

__all__ = ["subject_id"]
