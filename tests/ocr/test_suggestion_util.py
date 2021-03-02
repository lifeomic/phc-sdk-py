import pandas as pd
from phc.easy.ocr.suggestion import expand_nested_array_column


def test_expand_nested_array_column():
    actual = expand_nested_array_column(
        pd.DataFrame(
            [
                {
                    "col1": [
                        [{"value": 1}, {"value": 2}],
                        [{"value": 3}, {"value": 4}],
                    ]
                },
                {"col1": [[{"value": 5}, {"value": 6}]]},
            ]
        ),
        "col1",
        "col1_",
    )

    pd.testing.assert_frame_equal(
        actual,
        pd.DataFrame(
            [
                {"col1__item": 0, "col1_value": 1},
                {"col1__item": 0, "col1_value": 2},
                {"col1__item": 1, "col1_value": 3},
                {"col1__item": 1, "col1_value": 4},
                {"col1__item": 0, "col1_value": 5},
                {"col1__item": 0, "col1_value": 6},
            ]
        ),
    )
