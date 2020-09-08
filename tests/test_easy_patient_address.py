import pandas as pd
import math
from phc.easy.patients.address import expand_address_column


def non_na_dict(dictionary: dict):
    return {
        k: v
        for k, v in dictionary.items()
        if not isinstance(v, float) or not math.isnan(v)
    }


def test_expand_address_column():
    sample = pd.DataFrame(
        [
            {
                "address": [
                    {
                        "line": ["123 ABC Court"],
                        "city": "Zionsville",
                        "state": "IN",
                        "use": "home",
                    }
                ]
            },
            {
                "address": [
                    {
                        "use": "old",
                        "state": "SC",
                        "period": {"start": "1999", "end": "2001"},
                    },
                    {
                        "state": "NC",
                        "city": "Raleigh",
                        "period": {"start": "2001"},
                    },
                ]
            },
        ]
    )

    df = expand_address_column(sample.address)

    assert non_na_dict(df.iloc[0].to_dict()) == {
        "address_line_0": "123 ABC Court",
        "address_city": "Zionsville",
        "address_state": "IN",
        "address_use": "home",
    }

    assert non_na_dict(df.iloc[1].to_dict()) == {
        "address_city": "Raleigh",
        "address_state": "NC",
        "address_period_start": "2001",
        "other_addresses": [
            {
                "use": "old",
                "state": "SC",
                "period": {"start": "1999", "end": "2001"},
            }
        ],
    }
