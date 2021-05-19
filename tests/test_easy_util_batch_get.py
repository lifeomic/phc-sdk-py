from typing import List
import pandas as pd
from phc.easy.util.batch import batch_get_frame


def transform(ids: List[str], total: int):
    frame = pd.DataFrame({"id": ids})
    frame["batch_size"] = len(ids)
    frame["prev_total"] = total
    return frame


def test_batch_get_frame():
    assert batch_get_frame(["a", "b", "c"], 2, transform).to_dict(
        "records"
    ) == [
        {"id": "a", "batch_size": 2, "prev_total": 0},
        {"id": "b", "batch_size": 2, "prev_total": 0},
        {"id": "c", "batch_size": 1, "prev_total": 2},
    ]


def test_empty_batch():
    assert batch_get_frame([], 2, transform).to_dict("records") == []
