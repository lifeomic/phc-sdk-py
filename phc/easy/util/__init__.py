import math
from functools import reduce, wraps
from typing import Callable, List, Optional, Union

import pandas as pd
from funcy import lmapcat
from toolz import groupby

try:
    from tqdm.auto import tqdm
except ImportError:
    _has_tqdm = False
    tqdm = None
else:
    _has_tqdm = True


def rename_keys(dictionary: dict, mapping: dict):
    "Rename keys in a dictionary"
    return {mapping.get(k, k): v for k, v in dictionary.items()}


def join_underscore(values):
    return "_".join(
        [
            str(value)
            for value in values
            if isinstance(value, int) or len(value) > 0
        ]
    )


def without_keys(dictionary, keys):
    return {k: v for k, v in dictionary.items() if k not in keys}


def prefix_dict_keys(dictionary, prefix: Union[str, int]):
    if isinstance(prefix, str) and len(prefix) == 0:
        return dictionary

    return {f"{prefix}_{key}": value for key, value in dictionary.items()}


def concat_dicts(dicts, prefix: Union[str, int] = ""):
    "Concatenate list of dictionaries"

    def bump_key_index(key, existing_dict, start=1):
        "Prefix with _1 until index not in existing dictionary"
        if key not in existing_dict:
            return key

        new_key = f"{key}_{start}"
        if new_key in existing_dict:
            return bump_key_index(key, existing_dict, start + 1)

        return new_key

    def reduce_two_dicts(acc, dictionary):
        return {
            **acc,
            **{bump_key_index(k, acc): v for k, v in dictionary.items()},
        }

    return prefix_dict_keys(reduce(reduce_two_dicts, dicts, {}), prefix)


def defaultprop(fn):
    """Function decorator to have a default property (but not automatically set
    it)
    """
    attr_name = "_" + fn.__name__

    @property
    @wraps(fn)
    def _defaultprop(self):
        if not hasattr(self, attr_name):
            return fn(self)

        value = getattr(self, attr_name)
        if value is None:
            return fn(self)

        return value

    return _defaultprop


def with_progress(
    init_progress: Callable[[], Optional[tqdm]],
    func: Callable[[Union[None, tqdm]], None],
):
    if _has_tqdm:
        progress = init_progress()
        result = func(progress)
        if progress is not None:
            progress.close()
        return result

    return func(None)


def add_prefixes(values: List[str], prefixes: List[str]):
    """Add prefix to each value if not already present"""
    if len(prefixes) == 0:
        return values

    return lmapcat(
        lambda prefix: [
            (value if value.startswith(prefix) else f"{prefix}{value}")
            for value in values
        ],
        prefixes,
    )


class Hashabledict(dict):
    """Dictionary that is hashable (useful for creating set of unique dictionaries)"""

    def __hash__(self):
        return hash(frozenset(self))


def get_values_at_codeable_paths(value: dict, keys: List[str]):
    """Extract values from FHIR records based on keys (useful for extracting codes)"""

    def _get_value_at_codeable_path(
        value: Union[list, dict], components: List[str], key: str
    ):
        if value is None:
            return []

        if isinstance(value, list):
            return lmapcat(
                lambda v: _get_value_at_codeable_path(v, components, key), value
            )

        if len(components) == 0:
            return [Hashabledict({"field": key, **value})]

        if not isinstance(value, dict) and not isinstance(value, pd.Series):
            return []

        return _get_value_at_codeable_path(
            value.get(components[0], None), components[1:], key
        )

    def get_value_at_codeable_path(value: dict, key: str):
        return _get_value_at_codeable_path(value, key.split("."), key)

    return lmapcat(lambda key: get_value_at_codeable_path(value, key), keys)


def extract_codes(results: list, display: str, code_fields: List[str]):
    """Extract code values from a list of dictionaries based on the code keys.
    Requires a display value to filter results preemptively (instead of
    filtering afterwards)
    """

    codes = set()

    for row in results:
        row_codes = get_values_at_codeable_paths(row, code_fields)
        for code in row_codes:
            if (
                isinstance(code, dict)
                # Poor man's way to filter only matching codes (since Elasticsearch
                # returns records which will include other codes)
                and display.lower() in code.get("display", "").lower()
            ):
                codes.add(code)

    return pd.DataFrame(list(codes))


def split_by(args: dict, left_keys: List[str]):
    """Split into two dictionaries (left is whitelist and right is remaining)"""
    result = {
        k: dict(v)
        for k, v in groupby(
            lambda pair: pair[0] in left_keys, args.items()
        ).items()
    }

    return (result.get(True, {}), result.get(False, {}))
