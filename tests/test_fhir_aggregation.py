from phc.easy.query.fhir_aggregation import FhirAggregation


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
