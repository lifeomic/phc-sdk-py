import pandas as pd
from phc.easy.codeable import expand_extension, concat_dicts


def expand_address_attr(key, attr_value):
    if type(attr_value) is dict:
        return expand_extension(attr_value, key)

    if type(attr_value) is list:
        return concat_dicts([expand_address_attr(f'{key}_{index}', value) for index, value in enumerate(attr_value)])

    return {key: attr_value}


def expand_address_value(value):
    if type(value) is not list:
        return {}

    # Value is always list of one item
    assert len(value) == 1
    value = value[0]

    return concat_dicts([
        expand_address_attr(f'address_{key}', item_value)
        for key, item_value in value.items()
        if key != 'text'])


def expand_address_column(address_col):
    """
    Example input:

        sample = pd.DataFrame([{
            'address': [
                {'line': ['6109 Eagles Nest Blvd'], 'city': 'Zionsville', 'state': 'IN', 'use': 'home'}
            ]
        }])

        expand_address_column(sample.address)
    """

    values = [expand_address_value(value)
              for value in address_col.values]

    return pd.DataFrame(values)
