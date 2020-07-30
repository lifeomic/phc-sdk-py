from typing import List, Union
from lenses import lens

FHIR_WHERE = lens.Get("where", {})
FHIR_SIMPLE_QUERY = FHIR_WHERE.Get("query", {})
FHIR_BOOL_QUERY = FHIR_SIMPLE_QUERY.Get("bool", {})


def add_should_clause(query: dict, should_clause: dict):
    "Append a term/terms clause to an existing FSS query"
    if FHIR_WHERE.get()(query) == {}:
        return FHIR_SIMPLE_QUERY.set(should_clause)(query)

    query_keys = FHIR_SIMPLE_QUERY.get()(query).keys()
    if len(query_keys) == 1 and ("term" in query_keys or "terms" in query_keys):

        def combined_with_term(query_clause):
            return {
                "bool": {
                    "should": [query_clause, should_clause],
                    "minimum_should_match": 2,
                }
            }

        return FHIR_SIMPLE_QUERY.modify(combined_with_term)(query)

    bool_keys = FHIR_BOOL_QUERY.get()(query).keys()
    if "should" in bool_keys:

        def combined_with_bool(query_with_bool_clause):
            return {
                "bool": {
                    "should": [query_with_bool_clause, should_clause],
                    "minimum_should_match": 2,
                }
            }

        return FHIR_SIMPLE_QUERY.modify(combined_with_bool)(query)

    raise ValueError("Could not add clause to query", should_clause, query)


def build_query(
    query: dict,
    patient_id: Union[str, None] = None,
    patient_ids: List[str] = [],
    patient_key: str = "subject.reference",
):
    "Build query with patient_ids"
    patient_ids = [*patient_ids, *([patient_id] if patient_id else [])]

    return add_should_clause(
        query,
        {
            "terms": {
                f"{patient_key}.keyword": [
                    *[f"Patient/{patient_id}" for patient_id in patient_ids],
                    *patient_ids,
                ]
            }
        },
    )
