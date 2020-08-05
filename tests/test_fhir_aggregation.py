from phc.easy.query.fhir_aggregation import FhirAggregation

SAMPLE_COMPOSITE_RESULT = {
    "meta.tag": {
        "after_key": {"value": "meta.tag.example-after-key"},
        "buckets": [
            {"key": {"value": "meta.tag.first-key"}, "doc_count": 3},
            {"key": {"value": "meta.tag.second-key"}, "doc_count": 1},
        ],
    },
    "code.coding": {
        "after_key": {"value": "code.coding.example-after-key"},
        "buckets": [{"key": {"value": "meta.tag.first-key"}, "doc_count": 3}],
    },
    "component.code.coding": {
        "buckets": [
            {"key": {"value": "meta.tag.first-key"}, "doc_count": 3},
            {"key": {"value": "meta.tag.second-key"}, "doc_count": 1},
        ]
    },
    "valueCodeableConcept.coding": {
        "after_key": {"value": "valueCodeableConcept.coding.example-after-key"},
        "buckets": [],
    },
}


def test_is_aggregation_query():
    query = {
        "type": "select",
        "columns": [
            # Expression columns are ignored when aggregations are present
            {"expr": {"type": "column_ref", "column": "id.keyword"}},
            {
                "type": "elasticsearch",
                "aggregations": {
                    "results": {"terms": {"field": "subject.reference.keyword"}}
                },
            },
        ],
        "from": [{"table": "observation"}],
    }

    assert FhirAggregation.is_aggregation_query(query)


def test_is_not_aggregation_query_with_specific_column_selected():
    query = {
        "type": "select",
        "columns": [{"expr": {"type": "column_ref", "column": "id.keyword"}}],
        "from": [{"table": "observation"}],
    }

    assert not FhirAggregation.is_aggregation_query(query)


def test_is_not_aggregation_query_with_all_columns():
    query = {
        "type": "select",
        "columns": "*",
        "from": [{"table": "observation"}],
    }

    assert not FhirAggregation.is_aggregation_query(query)


def test_find_composite_after_keys():
    assert FhirAggregation.find_composite_after_keys(
        SAMPLE_COMPOSITE_RESULT, batch_size=2
    ) == {"meta.tag": {"value": "meta.tag.example-after-key"}}


def test_count_composite_results():
    assert FhirAggregation.count_composite_results(SAMPLE_COMPOSITE_RESULT) == 5


def test_reduce_composite_results_from_start():
    sample = {
        "meta.tag": {
            "after_key": {"value": "meta.tag.example-after-key"},
            "buckets": [
                {"key": {"value": "meta.tag.first-example"}, "doc_count": 10},
                {"key": {"value": "meta.tag.second-example"}, "doc_count": 3},
            ],
        }
    }

    assert FhirAggregation.reduce_composite_results({}, sample) == {
        "meta.tag": {
            "buckets": [
                {"key": {"value": "meta.tag.first-example"}, "doc_count": 10},
                {"key": {"value": "meta.tag.second-example"}, "doc_count": 3},
            ]
        }
    }


def test_reduce_composite_results():
    previous = {
        "meta.tag": {
            "after_key": {"value": "meta.tag.example-after-key"},
            "buckets": [
                {"key": {"value": "meta.tag.first-example"}, "doc_count": 10},
                {"key": {"value": "meta.tag.second-example"}, "doc_count": 3},
            ],
        },
        "code.coding": {
            "after_key": {"value": "code.coding.example-after-key"},
            "buckets": [
                {"key": {"value": "code.coding.first-example"}, "doc_count": 7},
                {
                    "key": {"value": "code.coding.second-example"},
                    "doc_count": 21,
                },
            ],
        },
    }

    current = {
        "meta.tag": {
            "after_key": {"value": "meta.tag.example-next-after-key"},
            "buckets": [
                {"key": {"value": "meta.tag.third-example"}, "doc_count": 2},
                {"key": {"value": "meta.tag.fourth-example"}, "doc_count": 1},
            ],
        }
    }

    assert FhirAggregation.reduce_composite_results(previous, current) == {
        "meta.tag": {
            "buckets": [
                {"key": {"value": "meta.tag.first-example"}, "doc_count": 10},
                {"key": {"value": "meta.tag.second-example"}, "doc_count": 3},
                {"key": {"value": "meta.tag.third-example"}, "doc_count": 2},
                {"key": {"value": "meta.tag.fourth-example"}, "doc_count": 1},
            ]
        },
        "code.coding": {
            "buckets": [
                {"key": {"value": "code.coding.first-example"}, "doc_count": 7},
                {
                    "key": {"value": "code.coding.second-example"},
                    "doc_count": 21,
                },
            ]
        },
    }
