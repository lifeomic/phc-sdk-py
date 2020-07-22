import pandas as pd
from phc.easy.codeable import generic_codeable_to_dict
from phc.easy.util import concat_dicts


def expand_address_attr(key, attr_value):
    if type(attr_value) is dict:
        return generic_codeable_to_dict(attr_value, key)

    if type(attr_value) is list:
        return concat_dicts(
            [
                expand_address_attr(f"{key}_{index}", value)
                for index, value in enumerate(attr_value)
            ]
        )

    return {key: attr_value}


def expand_address_value(value):
    if type(value) is not list:
        return {}

    # Value is always list of one item
    assert len(value) == 1
    value = value[0]

    return concat_dicts(
        [
            expand_address_attr(f"address_{key}", item_value)
            for key, item_value in value.items()
            if key != "text"
        ]
    )


def expand_address_column(address_col):
    return pd.DataFrame(map(expand_address_value, address_col.values))
