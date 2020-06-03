import pandas as pd


def expand_name_value(value):
    if type(value) is not list:
        return {}

    assert len(value) == 1

    return {**{f'given_name_{index}': given
               for index, given
               in enumerate(value[0]['given'])},
            'family_name': value[0]['family']}


def expand_name_column(name_col):
    return pd.DataFrame([expand_name_value(name) for name in name_col.values])
