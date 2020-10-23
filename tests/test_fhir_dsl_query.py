import math

from nose.tools import raises

from phc.easy.query.fhir_dsl_query import build_query, get_limit, update_limit


def test_update_limit_with_base_query():
    example = {}
    assert update_limit(example, lambda x: x / 1000) == {
        "limit": [
            {"type": "number", "value": 0},
            {"type": "number", "value": 9},
        ]
    }


def test_update_limit_with_existing_limit():
    example = {
        "limit": [
            {"type": "number", "value": 0},
            {"type": "number", "value": 100},
        ]
    }

    assert update_limit(example, math.sqrt) == {
        "limit": [
            {"type": "number", "value": 0},
            {"type": "number", "value": 10},
        ]
    }


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


def test_add_patient_id_and_limit_with_query_term():
    result = build_query(
        {
            "where": {
                "type": "elasticsearch",
                "query": {"term": {"test.field.keyword": "blah"}},
            }
        },
        patient_ids=["a", "b"],
        page_size=100,
    )

    assert result == {
        "where": {
            "type": "elasticsearch",
            "query": {
                "bool": {
                    "must": [
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
                    ]
                }
            },
        },
        "limit": [
            {"type": "number", "value": 0},
            {"type": "number", "value": 100},
        ],
    }


def test_replace_limit():
    result = build_query(
        {
            "limit": [
                {"type": "number", "value": 0},
                {"type": "number", "value": 100},
            ]
        },
        page_size=1000,
    )

    assert result == {
        "limit": [
            {"type": "number", "value": 0},
            {"type": "number", "value": 1000},
        ]
    }


def test_add_patient_id_with_bool_must_query():
    result = build_query(
        {
            "where": {
                "type": "elasticsearch",
                "query": {
                    "bool": {"must": [{"term": {"gender.keyword": "male"}}]}
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
                    "must": [
                        {"term": {"gender.keyword": "male"}},
                        {"terms": {"id.keyword": ["Patient/a", "a"]}},
                    ]
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
                    "must": [
                        {
                            "bool": {
                                "should": [{"term": {"gender.keyword": "male"}}]
                            }
                        },
                        {"terms": {"id.keyword": ["Patient/a", "a"]}},
                    ]
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


def test_get_limit():
    assert get_limit({}) == None

    assert (
        get_limit(
            {
                "limit": [
                    {"type": "number", "value": 0},
                    {"type": "number", "value": 100},
                ]
            }
        )
        == 100
    )


def test_add_term():
    result = build_query(
        {
            "where": {
                "type": "elasticsearch",
                "query": {"terms": {"a.keyword": [1, 2, 3]}},
            }
        },
        term={"code.coding.code.keyword": "blah"},
    )

    assert result == {
        "where": {
            "type": "elasticsearch",
            "query": {
                "bool": {
                    "must": [
                        {"terms": {"a.keyword": [1, 2, 3]}},
                        {"term": {"code.coding.code.keyword": "blah"}},
                    ]
                }
            },
        }
    }
