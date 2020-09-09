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
