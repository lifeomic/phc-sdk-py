import pandas as pd

from funcy import first
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

    primary_address = first(
        filter(lambda v: v.get("use") != "old", value)
    ) or first(value)

    other_addresses = list(
        filter(lambda address: address != primary_address, value)
    )

    other_attrs = (
        {"other_addresses": other_addresses} if len(other_addresses) > 0 else {}
    )

    return {
        **concat_dicts(
            [
                expand_address_attr(f"address_{key}", item_value)
                for key, item_value in primary_address.items()
                if key != "text"
            ]
        ),
        **other_attrs,
    }


def expand_address_column(address_col):
    return pd.DataFrame(map(expand_address_value, address_col.values))
