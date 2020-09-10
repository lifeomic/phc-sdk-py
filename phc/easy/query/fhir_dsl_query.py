from toolz import pipe, identity, curry, compose
from typing import List, Union, Callable
from lenses import lens

from phc.easy.util import add_prefixes

MAX_RESULT_SIZE = 10000
DEFAULT_SCROLL_SIZE = int(MAX_RESULT_SIZE * 0.9)

FHIR_WHERE = lens.Get("where", {})
FHIR_WHERE_TYPE = FHIR_WHERE.Get("type", "")
FHIR_SIMPLE_QUERY = FHIR_WHERE.Get("query", {})
FHIR_BOOL_QUERY = FHIR_SIMPLE_QUERY.Get("bool", {})
FHIR_BOOL_MUST_QUERY = FHIR_BOOL_QUERY.Get("must", [])
FHIR_LIMIT = lens.Get(
    "limit",
    [
        {"type": "number", "value": 0},
        {"type": "number", "value": DEFAULT_SCROLL_SIZE},
    ],
)[1]["value"]


def get_limit(query: dict):
    return lens.Get("limit", [{}, {}])[1].Get("value", None).get()(query)


def update_limit(query: dict, update: Callable[[int], int]):
    return FHIR_LIMIT.modify(compose(int, update))(query)


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

    if len(bool_keys) == 1 and "must" in bool_keys:
        return FHIR_BOOL_MUST_QUERY.modify(lambda must: [*must, query_clause])(
            query
        )

    raise ValueError("Could not add clause to query", query_clause, query)


def _patient_ids_adder(
    patient_id: Union[str, None] = None,
    patient_ids: List[str] = [],
    patient_key: str = "subject.reference",
    patient_id_prefixes: List[str] = ["Patient/"],
):
    patient_ids = [*patient_ids, *([patient_id] if patient_id else [])]

    if len(patient_ids) == 0:
        return identity

    return lambda query: and_query_clause(
        query,
        {
            "terms": {
                f"{patient_key}.keyword": [
                    *add_prefixes(patient_ids, patient_id_prefixes),
                    *patient_ids,
                ]
            }
        },
    )


def _limit_adder(page_size: Union[int, None]):
    if page_size is None:
        return identity

    return FHIR_LIMIT.set(page_size)


def build_query(
    query: dict,
    patient_id: Union[str, None] = None,
    patient_ids: List[str] = [],
    patient_key: str = "subject.reference",
    patient_id_prefixes: List[str] = ["Patient/"],
    page_size: Union[int, None] = None,
):
    """Build query with various options

    Attributes
    ----------
    query : dict
        The base FSS query

    patient_id : str
        Adds where clause for a single patient (will be merged with
        patient_ids if both supplied)

    patient_ids : List[str]
        Adds where clause for multiple patients

    patient_key : str
        The column that associates this table's records to a patient

    patient_id_prefixes : str
        Adds a prefix to patient_id values (e.g.
        "Patient/0a20d90f-c73c-4149-953d-7614ce7867f" as well as
        "0a20d90f-c73c-4149-953d-7614ce7867f")

    page_size: int
        The number of records to fetch per page
    """

    return pipe(
        query,
        _patient_ids_adder(
            patient_id=patient_id,
            patient_ids=patient_ids,
            patient_key=patient_key,
            patient_id_prefixes=patient_id_prefixes,
        ),
        _limit_adder(page_size),
    )
