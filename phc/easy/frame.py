from toolz import curry
from typing import Callable, List, Tuple

import re
import pandas as pd

from phc.easy.codeable import Codeable

TZ_REGEX = re.compile(r"[-+]\d{2}:?\d{2}Z?$")

CODE_COLUMNS = [
    "meta",
    "identifier",
    "extension",
    "telecom",
    "valueCodeableConcept",
    "code",
    "valueQuantity",
    "category",
    "target",
]
DATE_COLUMNS = [
    "dob",
    "birth_date",
    "birthDate",
    "deceasedDateTime",
    "effectiveDateTime",
    "meta.tag_lastUpdated",
]


def column_to_frame(frame: pd.DataFrame, column_name: str, expand_func):
    "Converts a column (if exists) to a data frame with multiple columns"
    if column_name in frame.columns:
        return expand_func(frame[column_name])

    return pd.DataFrame([])


class Frame:
    @staticmethod
    @curry
    def _find_index_of_similar(columns: List[str], column_name: str):
        "Find sort order by original frame column names"
        MAX_INDEX = len(columns)

        return next(
            filter(
                lambda pair: pair[1] in column_name,
                # Start from reverse end since later columns might be longer
                reversed(list(enumerate(columns))),
            ),
            (MAX_INDEX, None),
        )[0]

    @staticmethod
    def codeable_like_column_expander(column_name: str):
        """Codeable expansion with prefix for passing to Frame.expand#custom_columns"""

        def _expander(column):
            return Codeable.expand_column(column).add_prefix(f"{column_name}.")

        return (column_name, _expander)

    @staticmethod
    def expand(
        frame: pd.DataFrame,
        code_columns: List[str] = [],
        date_columns: List[str] = [],
        custom_columns: List[
            Tuple[str, Callable[[pd.Series], pd.DataFrame]]
        ] = [],
    ):
        """Expand a data frame with FHIR codes, nested JSON structures, etc into a full,
        tabular data frame that can much more easily be wrangled

        Attributes
        ----------
        frame : pd.DataFrame
            The data frame to expand

        code_columns : List[str]
            The list of column names that contain code-like data (e.g. FHIR dictionaries)

        date_columns : List[str]
            The list of column names that contain dates (may not able to parse but might)

        custom_columns : List[Tuple[str, Callable[[pd.Series], pd.DataFrame]]]
            A list of tuples with the column name and a function that expands a
            column to a data frame. This will get merged index-wise into the
            combined frame

        """
        all_code_columns = [*CODE_COLUMNS, *code_columns]
        all_date_columns = [*DATE_COLUMNS, *date_columns]

        codeable_column_names = [
            key for key in all_code_columns if key in frame.columns
        ]

        custom_names = [
            key for key, _func in custom_columns if key in frame.columns
        ]

        code_frames = [
            (Codeable.expand_column(frame[col_name]).add_prefix(f"{col_name}."))
            for col_name in codeable_column_names
        ]

        columns = [
            frame.drop([*codeable_column_names, *custom_names], axis=1),
            *[
                (column_to_frame(frame, key, func))
                for key, func in custom_columns
            ],
            *code_frames,
        ]

        combined = pd.concat(columns, axis=1)

        date_column_names = list(
            filter(lambda k: k in combined.columns, all_date_columns)
        )

        # Mutate data frame to parse date columns
        for column_key in date_column_names:
            local_key = f"{column_key}.local"
            tz_key = f"{column_key}.tz"

            try:
                utc = pd.to_datetime(combined[column_key], utc=True)

                # Cleverness: Use regex to remove TZ and parse as utc=True to
                # produce local datetime. The column name will have ".local" as
                # suffix so it'll be clear what's happening.
                localized = pd.to_datetime(
                    combined[column_key].str.replace(TZ_REGEX, ""), utc=True
                )
            except pd.errors.OutOfBoundsDatetime as ex:
                print(
                    "[WARNING]: OutOfBoundsDatetime encountered. Casting to NaT.",
                    ex,
                )
                utc = pd.to_datetime(
                    combined[column_key], utc=True, errors="coerce"
                )
                localized = pd.to_datetime(
                    combined[column_key].str.replace(TZ_REGEX, ""),
                    utc=True,
                    errors="coerce",
                )

            combined[tz_key] = (localized - utc).dt.total_seconds() / 3600
            combined[local_key] = localized

        # Drop duplicate columns (nicety for same transform applied to cache)
        # Sort columns by original order (where possible)
        return combined.loc[:, ~combined.columns.duplicated()].reindex(
            sorted(
                [
                    c
                    for c in combined.columns.unique()
                    if c not in date_column_names
                ],
                key=Frame._find_index_of_similar(frame.columns),
            ),
            axis="columns",
        )
