import pandas as pd
from phc.easy.ocr.suggestion import expand_json_and_merge, expand_observations


def as_frame(data: dict):
    return expand_json_and_merge(
        pd.DataFrame([{"observation": data}]), key="observation"
    )


def test_observation_date_with_bad_data_expands_to_empty_columns():
    df = expand_observations(as_frame({"date": [], "other": 1}))
    assert len(df) == 1
    assert list(df.columns) == ["observation_other", "type"]


def test_observation_date():
    frame = as_frame(
        {
            "observationCode": [],
            "date": [
                {
                    "value": "2021-02-21T12:00:00.000Z",
                    "dataSource": {"source": "comprehend"},
                    "confidence": 0.9999053478240967,
                    "sourceText": [
                        {
                            "word": "last",
                            "wordId": "9d8ff443-17ea-4ce0-a6ff-5938d178e019",
                        },
                        {
                            "word": "few",
                            "wordId": "856ec0ad-f0a0-4ade-b594-021d0db837f7",
                        },
                        {
                            "word": "days",
                            "wordId": "74977259-20a2-4c48-9fec-fe678082752a",
                        },
                    ],
                    "isPHI": True,
                }
            ],
            "value": [],
        }
    )

    df = expand_observations(frame)
    assert len(df) == 1
    assert list(df.columns) == [
        "date_value",
        "date_confidence",
        "date_isPHI",
        "date_dataSource_source",
        "date_sourceText",
        "type",
    ]


def test_observation_date_multiple_values():
    frame = as_frame(
        {
            "observationCode": [],
            "date": [
                {
                    "value": "2021-02-23T12:00:00.000Z",
                    "dataSource": {"source": "comprehend"},
                    "confidence": 0.9997616410255432,
                    "sourceText": [
                        {
                            "word": "last",
                            "wordId": "0469a8e1-d8d3-4dc2-8d6c-d11bd2b1b558",
                        },
                        {
                            "word": "night",
                            "wordId": "38cfaf48-0a52-4934-9652-24838fd88998",
                        },
                    ],
                    "isPHI": True,
                },
                {
                    "value": "2021-02-24T12:00:00.000Z",
                    "dataSource": {"source": "comprehend"},
                    "confidence": 0.9995536208152771,
                    "sourceText": [
                        {
                            "word": "Tonight",
                            "wordId": "03ad5a9d-1d7c-4a03-8a70-e0f92d9fa5ad",
                        }
                    ],
                    "isPHI": True,
                },
            ],
            "value": [],
        }
    )

    df = expand_observations(frame)
    assert len(df) == 2
    assert list(df.columns) == [
        "date_value",
        "date_confidence",
        "date_isPHI",
        "date_dataSource_source",
        "date_sourceText",
        "type",
    ]
