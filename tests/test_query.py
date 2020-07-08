from phc.util.api_cache import APICache


def test_filename_for_fhir_dsl_with_simple_statement():
    filename = APICache.filename_for_fhir_dsl(
        {
            "type": "select",
            "columns": "*",
            "from": [{"table": "patient"}, {"table": "observation"}],
        }
    )

    assert filename == "fhir_dsl_patient_observation_c57bdb78.csv"


def test_filename_for_fhir_dsl_with_complex_statement():
    filename = APICache.filename_for_fhir_dsl(
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
        }
    )

    assert filename == "fhir_dsl_goal_1col_where_58a8bb32.csv"
