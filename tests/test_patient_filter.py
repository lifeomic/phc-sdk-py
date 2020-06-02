import unittest

from phc.util.patient_filter_query_builder import (
    PatientFilterQueryBuilder,
    QueryObservationProperty,
    QueryProperty,
)


def test_patient_filter():
    filter_obj = PatientFilterQueryBuilder()
    filter_obj.patient().with_observations(
        [
            QueryObservationProperty().value_codeable_concept(
                eq=["LA10316-0", "LA10315-2"]
            )
        ]
    )

    expected = {
        "query": {
            "where": {
                "patient": {
                    "observations": {
                        "value_codeable_concept": [
                            {"operator": "eq", "value": "LA10316-0"},
                            {"operator": "eq", "value": "LA10315-2"},
                        ]
                    }
                }
            },
            "domain": "filter",
            "target": "patient",
        }
    }

    assert filter_obj.to_dict() == expected

def test_patient_filter_observation_component():
    filter_obj = PatientFilterQueryBuilder()
    filter_obj.patient().with_observations(
        [
            QueryObservationProperty().value_codeable_concept_code(
                eq=["LA10316-0", "LA10315-2"]
            ),
            QueryObservationProperty().with_components(
                [
                    QueryProperty()
                    .code(eq="allele1")
                    .system(eq="http://regenstrief.org/pgx")
                    .value_string(eq="C"),
                    QueryProperty()
                    .code(eq="allele2")
                    .system(eq="http://regenstrief.org/pgx")
                    .value_string(eq="G"),
                ]
            ),
        ]
    )

    expected = {
        "query": {
            "where": {
                "patient": {
                    "observations": {
                        "value_codeable_concept_code": [
                            {"operator": "eq", "value": "LA10316-0"},
                            {"operator": "eq", "value": "LA10315-2"},
                        ],
                        "components": [
                            {
                                "code": [
                                    {"operator": "eq", "value": "allele1"}
                                ],
                                "system": [
                                    {
                                        "operator": "eq",
                                        "value": "http://regenstrief.org/pgx",
                                    }
                                ],
                                "value_string": [
                                    {"operator": "eq", "value": "C"}
                                ],
                            },
                            {
                                "code": [
                                    {"operator": "eq", "value": "allele2"}
                                ],
                                "system": [
                                    {
                                        "operator": "eq",
                                        "value": "http://regenstrief.org/pgx",
                                    }
                                ],
                                "value_string": [
                                    {"operator": "eq", "value": "G"}
                                ],
                            },
                        ],
                    }
                }
            },
            "domain": "filter",
            "target": "patient",
        }
    }

    assert filter_obj.to_dict() == expected
