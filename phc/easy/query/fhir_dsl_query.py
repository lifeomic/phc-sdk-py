from toolz import pipe, identity, curry
from typing import List, Union
from lenses import lens

FHIR_WHERE = lens.Get("where", {})
FHIR_WHERE_TYPE = FHIR_WHERE.Get("type", "")
FHIR_SIMPLE_QUERY = FHIR_WHERE.Get("query", {})
FHIR_BOOL_QUERY = FHIR_SIMPLE_QUERY.Get("bool", {})


@curry
def and_query_clause_terms(second_query_clause, first_query_clause):
    return {
        "bool": {
            "should": [first_query_clause, second_query_clause],
            "minimum_should_match": 2,
        }
    }


def and_query_clause(query: dict, query_clause: dict):
    "Append a term/terms clause to an existing FSS query"
    if FHIR_WHERE.get()(query) == {}:
        return pipe(
            query,
            FHIR_SIMPLE_QUERY.set(query_clause),
            FHIR_WHERE_TYPE.set("elasticsearch"),
        )

    if FHIR_WHERE_TYPE.get()(query) != "elasticsearch":
        raise ValueError(
            "Could not add clause to query that is not elasticsearch",
            query_clause,
            query,
        )

    query_keys = list(FHIR_SIMPLE_QUERY.get()(query).keys())
    bool_keys = FHIR_BOOL_QUERY.get()(query).keys()
    if (len(query_keys) == 1 and (query_keys[0] in ["term", "terms"])) or (
        "should" in bool_keys
    ):
        return FHIR_SIMPLE_QUERY.modify(and_query_clause_terms(query_clause))(
            query
        )

    raise ValueError("Could not add clause to query", query_clause, query)


def _patient_ids_adder(
    patient_id: Union[str, None] = None,
    patient_ids: List[str] = [],
    patient_key: str = "subject.reference",
):
    patient_ids = [*patient_ids, *([patient_id] if patient_id else [])]

    if len(patient_ids) == 0:
        return identity

    return lambda query: and_query_clause(
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


def build_query(
    query: dict,
    patient_id: Union[str, None] = None,
    patient_ids: List[str] = [],
    patient_key: str = "subject.reference",
):
    "Build query with patient_ids"

    return pipe(
        query,
        _patient_ids_adder(
            patient_id=patient_id,
            patient_ids=patient_ids,
            patient_key=patient_key,
        ),
    )
