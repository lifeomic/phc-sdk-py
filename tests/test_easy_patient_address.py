import pandas as pd
from phc.easy.patients.address import expand_address_column

def test_expand_address_column():
    sample = pd.DataFrame([{
        'address': [
            {'line': ['123 ABC Court'], 'city': 'Zionsville', 'state': 'IN', 'use': 'home'}
        ]
    }])

    df = expand_address_column(sample.address)

    assert df.iloc[0].to_dict() == {
        'address_line_0': '123 ABC Court',
        'address_city': 'Zionsville',
        'address_state': 'IN',
        'address_use': 'home'
    }
