from phc.easy.util.api_cache import APICache, FHIR_DSL


def test_filename_for_genomics_api_call():
    filename = APICache.filename_for_query(
        {"path": "genomics/projects/dfkjkjsa-dkj2kd1-kjdkj-1dkj2/tests"}
    )

    assert filename == "genomics_projects_tests_04b0739f.csv"


def test_filename_for_query_with_simple_statement():
    filename = APICache.filename_for_query(
        {
            "type": "select",
            "columns": "*",
            "from": [{"table": "patient"}, {"table": "observation"}],
        },
        namespace=FHIR_DSL,
    )

    assert filename == "fhir_dsl_patient_observation_c57bdb78.csv"


def test_filename_for_query_with_complex_statement():
    filename = APICache.filename_for_query(
        {
            "type": "select",
            "columns": [
                {"expr": {"type": "column_ref", "column": "id.keyword"}}
            ],
            "from": [{"table": "goal"}],
            "where": {
                "type": "elasticsearch",
                "query": {
                    "bool": {
                        "should": [
                            {
                                "term": {
                                    "target.measure.coding.system.keyword": "http://my-system/fhir/measure1"
                                }
                            },
                            {
                                "term": {
                                    "target.measure.coding.code.keyword": "12345-6"
                                }
                            },
                        ],
                        "minimum_should_match": 2,
                    }
                },
            },
        },
        namespace=FHIR_DSL,
    )

    assert filename == "fhir_dsl_goal_1col_where_08c25b4c.csv"


def test_filename_for_query_with_aggregation():
    filename = APICache.filename_for_query(
        {
            "type": "select",
            "columns": [
                {
                    "type": "elasticsearch",
                    "aggregations": {
                        "results": {
                            "cardinality": {"field": "person.ref.keyword"}
                        }
                    },
                }
            ],
            "from": [{"table": "goal"}],
            "where": {
                "type": "elasticsearch",
                "query": {
                    "bool": {
                        "should": [
                            {
                                "term": {
                                    "target.measure.coding.system.keyword": "http://my-system/fhir/measure1"
                                }
                            },
                            {
                                "term": {
                                    "target.measure.coding.code.keyword": "12345-6"
                                }
                            },
                        ],
                        "minimum_should_match": 2,
                    }
                },
            },
        },
        namespace=FHIR_DSL,
    )

    assert filename == "fhir_dsl_goal_agg_where_58a8bb32.json"
