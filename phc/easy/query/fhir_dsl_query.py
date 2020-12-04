from functools import partial
from typing import Callable, List, Optional, Union

from lenses import lens
from toolz import compose, curry, identity, pipe

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
    return {"bool": {"must": [first_query_clause, second_query_clause]}}


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


def _ids_adder(id: Union[str, None] = None, ids: List[str] = []):
    ids = [*ids, *([id] if id else [])]

    if len(ids) == 0:
        return identity

    return lambda query: and_query_clause(query, {"terms": {"id.keyword": ids}})


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


def _term_adder(term: Optional[dict]):
    if term is None:
        return identity

    return partial(and_query_clause, query_clause={"term": term})


def _code_adder(
    attribute: Union[str],
    code_fields: List[str],
    value: Optional[Union[str, List[str]]],
):
    if len(code_fields) == 0 or value is None:
        return identity

    term_or_terms = "term" if isinstance(value, str) else "terms"

    return partial(
        and_query_clause,
        query_clause={
            "bool": {
                "should": [
                    {term_or_terms: {f"{key}.{attribute}.keyword": value}}
                    for key in code_fields
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
    id: Optional[str] = None,
    ids: List[str] = [],
    patient_id: Optional[str] = None,
    patient_ids: List[str] = [],
    patient_key: str = "subject.reference",
    patient_id_prefixes: List[str] = ["Patient/"],
    page_size: Optional[int] = None,
    term: Optional[dict] = None,
    # Codes
    code_fields: List[str] = [],
    code: Optional[Union[str, List[str]]] = None,
    display: Optional[Union[str, List[str]]] = None,
    system: Optional[Union[str, List[str]]] = None,
):
    """Build query with various options

    Attributes
    ----------
    query : dict
        The base FSS query

    id : str
        Adds where clause for a single id (will be merged with
        ids if both supplied)

    ids : List[str]
        Adds where clause for multiple ids

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

    term : dict
        Add an arbitrary ES term to the query

    page_size: int
        The number of records to fetch per page

    code_fields : List[str]
        A list of paths to find FHIR codes in

    code : str | List[str]
        Adds where clause for code value(s)

    display : str | List[str]
        Adds where clause for code display value(s)

    system : str | List[str]
        Adds where clause for code system value(s)
    """

    return pipe(
        query,
        _ids_adder(id=id, ids=ids),
        _patient_ids_adder(
            patient_id=patient_id,
            patient_ids=patient_ids,
            patient_key=patient_key,
            patient_id_prefixes=patient_id_prefixes,
        ),
        _term_adder(term),
        _code_adder(attribute="code", code_fields=code_fields, value=code),
        _code_adder(
            attribute="display", code_fields=code_fields, value=display
        ),
        _code_adder(attribute="system", code_fields=code_fields, value=system),
        _limit_adder(page_size),
    )
