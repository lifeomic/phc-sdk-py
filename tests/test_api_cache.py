from io import StringIO
from phc.easy.util.api_cache import APICache, FHIR_DSL


def test_filename_for_genomics_api_call():
    filename = APICache.filename_for_query(
        {
            "path": f"genomics/projects/0dbe33af-022a-4416-aca9-d468e99648ee/tests"
        }
    )

    assert filename == "genomics_projects_tests_2f4d9e60.csv"


def test_filename_for_structural_variant_call():
    filename = APICache.filename_for_query(
        {"path": "genomics/structural-variants"}
    )

    assert filename == "genomics_structural_variants_769987ca.csv"


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


def test_reading_cache_file_with_invalid_date_does_not_raise():
    sample_file = StringIO()
    sample_file.write(
        "\n".join(
            [
                "date,name",
                "2020-01-01T00:00:00Z,A",
                "2020-01-02T00:00:00Z,B",
                "2020-01-03T00:00:00Z,C",
                "2020-01-04T00:00:00Z,D",
                "217-06-07T00:00:00Z,E",
            ]
        )
    )
    sample_file.seek(0)

    APICache.read_csv(sample_file)
