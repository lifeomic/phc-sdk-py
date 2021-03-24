import pandas as pd
from phc.easy.ocr.suggestion import (expand_array_column,
                                     expand_medication_administrations,
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
                        "medicationAdministration": {
                            "medicationCode": [
                                {
                                    "value": {
                                        "system": "http://www.nlm.nih.gov/research/umls/rxnorm",
                                        "code": "3640",
                                        "display": "doxycycline",
                                    },
                                    "dataSource": {"source": "comprehend"},
                                    "confidence": 0.996650755405426,
                                    "sourceText": {
                                        "text": "doxycycline",
                                        "location": {
                                            "startIndex": 11,
                                            "endIndex": 22,
                                        },
                                    },
                                }
                            ],
                            "date": [],
                            "endDate": [],
                            "status": [
                                {
                                    "value": "unknown",
                                    "dataSource": {"source": "comprehend"},
                                    "confidence": 0.9,
                                },
                                {
                                    "value": "completed",
                                    "dataSource": {"source": "comprehend"},
                                    "confidence": 0.9,
                                },
                                {
                                    "value": "in-progress",
                                    "dataSource": {"source": "comprehend"},
                                    "confidence": 0.9,
                                },
                            ],
                            "dosage": [
                                {
                                    "value": {
                                        "id": "0",
                                        "strength": None,
                                        "dosage": None,
                                        "duration": None,
                                        "form": None,
                                        "frequencey": None,
                                        "rate": None,
                                        "route": "po",
                                    },
                                    "dataSource": {"source": "comprehend"},
                                    "confidence": 0.996650755405426,
                                    "sourceText": {
                                        "text": "po",
                                        "location": {
                                            "startIndex": 23,
                                            "endIndex": 25,
                                        },
                                    },
                                }
                            ],
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


def test_medication_administration_expansion():
    df = expand_medication_administrations(
        frame_for_type(sample, "medicationAdministration")
    )

    pd.testing.assert_frame_equal(
        df,
        pd.DataFrame(
            [
                {
                    "anchorDate": "2021-02-24T12:58:32.058Z",
                    "version": 4,
                    "suggestionId": "00022-00007-00001",
                    "id": "728e79cd-6cd2-421f-9e38-3181200c301",
                    "status_value": "unknown",
                    "status_confidence": 0.9,
                    "status_dataSource_source": "comprehend",
                    "dosage_confidence": 0.996650755405426,
                    "dosage_dataSource_source": "comprehend",
                    "dosage_value_id": "0",
                    "dosage_value_strength": None,
                    "dosage_value_dosage": None,
                    "dosage_value_duration": None,
                    "dosage_value_form": None,
                    "dosage_value_frequencey": None,
                    "dosage_value_rate": None,
                    "dosage_value_route": "po",
                    "code_confidence": 0.996650755405426,
                    "code_dataSource_source": "comprehend",
                    "code_value_system": "http://www.nlm.nih.gov/research/umls/rxnorm",
                    "code_value_code": "3640",
                    "code_value_display": "doxycycline",
                    "dosage_sourceText": "po",
                    "code_sourceText": "doxycycline",
                    "type": "medicationAdministration",
                },
                {
                    "anchorDate": "2021-02-24T12:58:32.058Z",
                    "version": 4,
                    "suggestionId": "00022-00007-00001",
                    "id": "728e79cd-6cd2-421f-9e38-3181200c301",
                    "status_value": "completed",
                    "status_confidence": 0.9,
                    "status_dataSource_source": "comprehend",
                    "dosage_confidence": 0.996650755405426,
                    "dosage_dataSource_source": "comprehend",
                    "dosage_value_id": "0",
                    "dosage_value_strength": None,
                    "dosage_value_dosage": None,
                    "dosage_value_duration": None,
                    "dosage_value_form": None,
                    "dosage_value_frequencey": None,
                    "dosage_value_rate": None,
                    "dosage_value_route": "po",
                    "code_confidence": 0.996650755405426,
                    "code_dataSource_source": "comprehend",
                    "code_value_system": "http://www.nlm.nih.gov/research/umls/rxnorm",
                    "code_value_code": "3640",
                    "code_value_display": "doxycycline",
                    "dosage_sourceText": "po",
                    "code_sourceText": "doxycycline",
                    "type": "medicationAdministration",
                },
                {
                    "anchorDate": "2021-02-24T12:58:32.058Z",
                    "version": 4,
                    "suggestionId": "00022-00007-00001",
                    "id": "728e79cd-6cd2-421f-9e38-3181200c301",
                    "status_value": "in-progress",
                    "status_confidence": 0.9,
                    "status_dataSource_source": "comprehend",
                    "dosage_confidence": 0.996650755405426,
                    "dosage_dataSource_source": "comprehend",
                    "dosage_value_id": "0",
                    "dosage_value_strength": None,
                    "dosage_value_dosage": None,
                    "dosage_value_duration": None,
                    "dosage_value_form": None,
                    "dosage_value_frequencey": None,
                    "dosage_value_rate": None,
                    "dosage_value_route": "po",
                    "code_confidence": 0.996650755405426,
                    "code_dataSource_source": "comprehend",
                    "code_value_system": "http://www.nlm.nih.gov/research/umls/rxnorm",
                    "code_value_code": "3640",
                    "code_value_display": "doxycycline",
                    "dosage_sourceText": "po",
                    "code_sourceText": "doxycycline",
                    "type": "medicationAdministration",
                },
            ]
        ),
    )
