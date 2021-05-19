import pandas as pd
from nose.tools import assert_equals
from phc.easy.util.frame import combine_first


def test_combine_first():
    frame = pd.DataFrame(
        [
            {"count": pd.NA, "count1": 10, "count2": 100},
            {"count": pd.NA, "count1": pd.NA, "count2": 200},
            {"count": 3, "count1": pd.NA, "count2": pd.NA},
        ]
    )

    assert_equals(
        combine_first(frame, ["count", "count1", "count2"], "count")["count"],
        pd.Series(),
    )
