import math
from datetime import datetime

import pandas as pd

from phc.easy.frame import Frame


def test_frame_expand_date_out_of_range():
    original = pd.DataFrame(
        [
            {"effectiveDateTime": "2020-09-15 12:31:00-0500", "id": "obs1"},
            {"effectiveDateTime": "0217-05-04 12:31:00-0500", "id": "obs2"},
        ]
    )

    expanded = Frame.expand(original)

    assert expanded.at[0, "effectiveDateTime.tz"] == -5.0
    assert expanded.at[0, "effectiveDateTime.local"] == pd.Timestamp(
        "2020-09-15 12:31:00", tz="utc"
    )

    assert math.isnan(expanded.at[1, "effectiveDateTime.tz"])
    assert pd.isna(expanded.at[1, "effectiveDateTime.local"])


def test_local_and_timezone_split():
    original = pd.DataFrame(
        [
            {"effectiveDateTime": "2020-08-08 11:00:00+0300", "id": "obs1"},
            {"effectiveDateTime": "2020-08-09 10:00:00-0400", "id": "obs2"},
        ]
    )

    expanded = Frame.expand(original)

    assert expanded.at[0, "effectiveDateTime.tz"] == 3.0
    assert expanded.at[0, "effectiveDateTime.local"] == pd.Timestamp(
        "2020-08-08 11:00:00", tz="utc"
    )

    assert expanded.at[1, "effectiveDateTime.tz"] == -4.0
    assert expanded.at[1, "effectiveDateTime.local"] == pd.Timestamp(
        "2020-08-09 10:00:00", tz="utc"
    )
