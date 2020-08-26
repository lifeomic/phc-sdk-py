from nose.tools import raises
from phc.easy.query.fhir_dsl_query import build_query


def test_no_modification():
    example = {
        "where": {
            "type": "elasticsearch",
            "query": {"term": {"gender.keyword": "male"}},
        }
    }

    assert build_query(example) == example


@raises(ValueError)
def test_throws_with_non_elasticsearch_where():
    build_query({"where": {"query": "blah-blah-blah"}}, patient_id="a")


def test_add_patient_ids_with_no_where_clause():
    assert build_query({}, patient_ids=["a"]) == {
        "where": {
            "type": "elasticsearch",
            "query": {
                "terms": {"subject.reference.keyword": ["Patient/a", "a"]}
            },
        }
    }


def test_add_patient_id_with_query_term():
    result = build_query(
        {
            "where": {
                "type": "elasticsearch",
                "query": {"term": {"test.field.keyword": "blah"}},
            }
        },
        patient_ids=["a", "b"],
    )

    assert result == {
        "where": {
            "type": "elasticsearch",
            "query": {
                "bool": {
                    "should": [
                        {"term": {"test.field.keyword": "blah"}},
                        {
                            "terms": {
                                "subject.reference.keyword": [
                                    "Patient/a",
                                    "Patient/b",
                                    "a",
                                    "b",
                                ]
                            }
                        },
                    ],
                    "minimum_should_match": 2,
                }
            },
        }
    }


def test_add_patient_id_with_bool_should_query():
    result = build_query(
        {
            "where": {
                "type": "elasticsearch",
                "query": {
                    "bool": {"should": [{"term": {"gender.keyword": "male"}}]}
                },
            }
        },
        patient_ids=["a"],
        patient_key="id",
    )

    assert result == {
        "where": {
            "type": "elasticsearch",
            "query": {
                "bool": {
                    "should": [
                        {
                            "bool": {
                                "should": [
                                    {"term": {"gender.keyword": "male"}}
                                ],
                            }
                        },
                        {"terms": {"id.keyword": ["Patient/a", "a"]}},
                    ],
                    "minimum_should_match": 2,
                }
            },
        }
    }


def test_add_single_patient_id_to_query():
    result = build_query({}, patient_id="a")

    assert result == {
        "where": {
            "type": "elasticsearch",
            "query": {
                "terms": {"subject.reference.keyword": ["Patient/a", "a"]}
            },
        }
    }


def test_add_single_patient_id_with_prefix():
    result = build_query(
        {}, patient_id="a", patient_id_prefixes=["Patient/", "urn:uuid:"]
    )

    assert result == {
        "where": {
            "type": "elasticsearch",
            "query": {
                "terms": {
                    "subject.reference.keyword": [
                        "Patient/a",
                        "urn:uuid:a",
                        "a",
                    ]
                }
            },
        }
    }
