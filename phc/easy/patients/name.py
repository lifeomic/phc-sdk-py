import pandas as pd
from funcy import first
from phc.easy.util import concat_dicts, join_underscore

NAME_BLACKLIST_KEYS = ["text"]


def __expand_key_value(key, value):
    if type(value) is list:
        return {
            join_underscore([key, index]): element
            for index, element in enumerate(value)
        }

    return {key: value}


def expand_name_value(value):
    if type(value) is not list or len(value) == 0:
        return {}

    primary_name = first(
        filter(lambda v: v.get("use") == "official", value)
    ) or first(value)

    other_names = list(filter(lambda name: name != primary_name, value))

    other_attrs = {"other_names": other_names} if len(other_names) > 0 else {}

    return {
        **concat_dicts(
            [
                __expand_key_value(key, value)
                for key, value in primary_name.items()
                if key not in NAME_BLACKLIST_KEYS
            ],
            "name",
        ),
        **other_attrs,
    }


def expand_name_column(name_col):
    return pd.DataFrame([expand_name_value(name) for name in name_col.values])
