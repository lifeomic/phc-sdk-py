import pandas as pd
from phc.easy.ocr.suggestion import (expand_array_column, expand_procedures,
                                     frame_for_type)

sample = expand_array_column(
    pd.DataFrame(
        [
            {
                "suggestions": [
                    {
                        "id": "728e79cd-6cd2-421f-9e38-3181200c301",
                        "condition": {
                            "conditionCode": [],
                            "onsetDate": [],
                            "abatementDate": [],
                            "bodySite": [],
                        },
                        "observation": {},
                        "procedure": {
                            "procedureCode": [
                                {
                                    "value": {
                                        "system": "",
                                        "code": "",
                                        "display": "",
                                    },
                                    "dataSource": {"source": "comprehend"},
                                    "confidence": 0.9612833261489868,
                                    "sourceText": [
                                        {
                                            "word": "CABG",
                                            "wordId": "21fc38b4-5ff7-46d4-aaf8-fa4311037cb",
                                        }
                                    ],
                                }
                            ],
                            "date": [],
                            "endDate": [],
                            "bodySite": [[]],
                        },
                        "medicationAdministration": {
                            "medicationCode": [],
                            "date": [],
                            "endDate": [],
                            "status": [],
                            "dosage": [],
                        },
                    }
                ],
                "anchorDate": "2021-02-24T12:58:32.058Z",
                "version": 4,
                "suggestionId": "00022-00007-00001",
            }
        ]
    ),
    key="suggestions",
)


def test_procedure_expansion():
    df = expand_procedures(frame_for_type(sample, "procedure"))

    pd.testing.assert_frame_equal(
        df,
        pd.DataFrame(
            [
                {
                    "anchorDate": "2021-02-24T12:58:32.058Z",
                    "version": 4,
                    "suggestionId": "00022-00007-00001",
                    "id": "728e79cd-6cd2-421f-9e38-3181200c301",
                    "code_confidence": 0.9612833261489868,
                    "code_dataSource_source": "comprehend",
                    "code_value_system": "",
                    "code_value_code": "",
                    "code_value_display": "",
                    "code_sourceText": "CABG",
                    "type": "procedure",
                }
            ]
        ),
    )
