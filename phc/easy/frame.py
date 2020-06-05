import pandas as pd
from typing import Callable, List, Tuple
from phc.easy.codeable import Codeable

CODE_COLUMNS = ['meta', 'identifier', 'extension', 'telecom']
DATE_COLUMNS = ['dob', 'birth_date', 'birthDate', 'deceasedDateTime']


def column_to_frame(frame: pd.DataFrame, column_name: str, expand_func):
    "Converts a column (if exists) to a data frame with multiple columns"
    if column_name in frame.columns:
        return expand_func(frame[column_name])

    return pd.DataFrame([])


class Frame():
    @staticmethod
    def expand(frame: pd.DataFrame,
               code_columns: List[str] = [],
               date_columns: List[str] = [],
               custom_columns: List[Tuple[str, Callable[[pd.Series],
                                                        pd.DataFrame]]] = []):
        all_code_columns = [*CODE_COLUMNS, *code_columns]
        all_date_columns = [*DATE_COLUMNS, *date_columns]

        codeable_col_names = [
            col_name for col_name in all_code_columns
            if col_name in frame.columns
        ]

        code_frames = [
            Codeable.expand_column(frame[col_name])
            for col_name in codeable_col_names
        ]

        custom_names = [
            key for key, _func in custom_columns if key in frame.columns
        ]

        combined = pd.concat([
            *[
                column_to_frame(frame, key, func)
                for key, func in custom_columns
            ],
            frame.drop([*codeable_col_names, *custom_names], axis=1),
            *code_frames
        ], axis=1)

        # Mutate data frame to parse date columns
        for column_key in all_date_columns:
            if column_key in combined.columns:
                combined[column_key] = pd.to_datetime(combined[column_key])

        return combined
