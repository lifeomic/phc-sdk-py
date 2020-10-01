from typing import Tuple
import phc.easy as phc
import pandas as pd

from phc.explore.column import ColumnConfig

from phc.explore.column.subject_id import subject_id
from phc.explore.column.age import age


class CustomFrame:
    COLUMNS = {phc.Patient: [subject_id, age]}

    @classmethod
    def get_columns(cls, module: type):
        return cls.COLUMNS[module]

    @classmethod
    def transform(
        cls, module: type, frame: pd.DataFrame, columns: Tuple[str, dict]
    ):
        def to_series(column_name: str, attrs: dict):
            if attrs.get("raw"):
                return (column_name, frame[column_name])

            column = next(
                filter(lambda c: c.name == column_name, cls.COLUMNS[module])
            )
            return (column_name, column.transform(frame, ColumnConfig(**attrs)))

        return pd.DataFrame(
            dict(
                [
                    to_series(column_name, attrs)
                    for column_name, attrs in columns
                ]
            )
        )
