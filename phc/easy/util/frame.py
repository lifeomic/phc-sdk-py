import pandas as pd
from functools import reduce
from typing import List


def combine_first(frame: pd.DataFrame, columns: List[str], column_name: str):
    if columns[0] not in frame.columns:
        return frame

    return frame.assign(
        **{
            column_name: reduce(
                lambda series, k: (
                    series.combine_first(frame[k])
                    if k in frame.columns
                    else series
                ),
                columns,
                frame[columns[0]],
            )
        }
    )


def drop(frame: pd.DataFrame, columns: List[str]):
    return frame.drop([c for c in columns if c in frame.columns], axis=1)
