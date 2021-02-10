import math
import os

import numpy as np
import pandas as pd

from phc.util.csv_writer import CSVWriter


def setup():
    if os.path.exists("/tmp/sample.csv"):
        os.remove("/tmp/sample.csv")


def test_writing_batches():
    setup()
    writer = CSVWriter("/tmp/sample.csv")

    first_batch = pd.DataFrame(
        [
            {"first_name": "Laura", "last_name": "Lane"},
            {"first_name": "Susie", "last_name": "Smith"},
        ]
    )

    second_batch = pd.DataFrame(
        [
            {"first_name": "Jenny", "last_name": "Jones"},
            {"last_name": "Motte", "date_of_birth": "03/07/1986"},
        ]
    )

    writer.write(first_batch)
    writer.write(second_batch)

    frame = pd.read_csv("/tmp/sample.csv")

    assert frame.columns.tolist() == [
        "first_name",
        "last_name",
        "date_of_birth",
    ]

    # Cannot compare NaN - must use math.isnan()
    is_nan = np.vectorize(lambda x: isinstance(x, float) and math.isnan(x))

    assert np.logical_or(
        frame.values
        == [
            ["Laura", "Lane", math.nan],
            ["Susie", "Smith", math.nan],
            ["Jenny", "Jones", math.nan],
            [math.nan, "Motte", "03/07/1986"],
        ],
        is_nan(frame.values),
    ).all()


def test_bad_column_names():
    setup()
    writer = CSVWriter("/tmp/sample.csv")

    first_batch = pd.DataFrame(
        [
            {"first\n_name": "Laura", "last_name": "Lane"},
            {"first\n_name": "Susie", "last_name": "Smith"},
        ]
    )

    second_batch = pd.DataFrame(
        [
            {"first_name": "Jenny", "last\t_name": "Jones"},
            {"last\t_name": "Motte", "date_of_birth": "03/07/1986"},
        ]
    )

    writer.write(first_batch)
    writer.write(second_batch)

    frame = pd.read_csv("/tmp/sample.csv")

    assert frame.columns.tolist() == [
        "first_name",
        "last_name",
        "date_of_birth",
    ]

    # Cannot compare NaN - must use math.isnan()
    is_nan = np.vectorize(lambda x: isinstance(x, float) and math.isnan(x))

    assert np.logical_or(
        frame.values
        == [
            ["Laura", "Lane", math.nan],
            ["Susie", "Smith", math.nan],
            ["Jenny", "Jones", math.nan],
            [math.nan, "Motte", "03/07/1986"],
        ],
        is_nan(frame.values),
    ).all()
