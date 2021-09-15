from functools import partial, reduce
from typing import Callable, List, Optional, Union

from funcy import chunks
from lenses import lens
from phc.easy.query.util import flat_map_pipe
from phc.easy.util import add_prefixes
from toolz import compose, curry, identity, pipe

DEFAULT_MAX_TERMS = 30_000

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


def _ids_adder(
    id: Union[str, None] = None,
    ids: List[str] = [],
    max_terms: int = DEFAULT_MAX_TERMS,
):
    ids = [*ids, *([id] if id else [])]

    if len(ids) == 0:
        return identity

    return terms_adder({"id.keyword": ids}, max_terms=max_terms)


def foreign_ids_adder(
    foreign_id: Optional[str],
    foreign_ids: List[str],
    foreign_key: str,
    foreign_id_prefixes: List[str],
    max_terms: int = DEFAULT_MAX_TERMS,
):
    foreign_ids = [*foreign_ids, *([foreign_id] if foreign_id else [])]

    if len(foreign_ids) == 0:
        return identity

    return terms_adder(
        {
            f"{foreign_key}.keyword": [
                *add_prefixes(foreign_ids, foreign_id_prefixes),
                *foreign_ids,
            ]
        },
        max_terms=max_terms,
    )


def _term_or_terms_adder(
    term: Optional[dict], terms: List[dict], max_terms: int = DEFAULT_MAX_TERMS
):
    if term is None and len(terms) == 0:
        return identity

    terms = [term, *terms] if term is not None else terms

    def _adder(query):
        return flat_map_pipe(
            query,
            *[
                (
                    terms_adder(t, max_terms=max_terms)
                    if isinstance(list(t.values())[0], list)
                    else term_adder(t)
                )
                for t in terms
            ],
        )

    return _adder


def term_adder(term: Optional[dict]):
    if term is None:
        return identity

    if len(term.keys()) > 1:
        raise ValueError(
            f"Multiple keys unexpected for term dictionary for fhir-search-service. {term}"
        )

    return partial(and_query_clause, query_clause={"term": term})


def terms_adder(terms: Optional[dict], max_terms: int = DEFAULT_MAX_TERMS):
    if terms is None:
        return identity

    if len(terms.keys()) > 1:
        raise ValueError(
            f"Multiple keys unexpected for terms dictionary for fhir-search-service. {terms}"
        )

    key = list(terms.keys())[0]
    # NOTE: Must convert chunks from generator so that function can be run multiple times
    value_batches = list(chunks(max_terms, list(terms.values())[0]))

    def _adder(query):
        return [
            and_query_clause(query, {"terms": {key: value_batch}})
            for value_batch in value_batches
        ]

    return _adder


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


def build_queries(
    query: dict,
    id: Optional[str] = None,
    ids: List[str] = [],
    patient_id: Optional[str] = None,
    patient_ids: List[str] = [],
    patient_key: str = "subject.reference",
    patient_id_prefixes: List[str] = ["Patient/"],
    page_size: Optional[int] = None,
    term: Optional[dict] = None,
    terms: List[dict] = [],
    max_terms: int = DEFAULT_MAX_TERMS,
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
        Add an arbitrary ES term/s to the query (includes chunking)

    terms : dict
        Add multiple arbitrary ES term/s to the query (includes chunking)

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
    return flat_map_pipe(
        query,
        _ids_adder(id=id, ids=ids, max_terms=max_terms),
        foreign_ids_adder(
            foreign_id=patient_id,
            foreign_ids=patient_ids,
            foreign_key=patient_key,
            foreign_id_prefixes=patient_id_prefixes,
            max_terms=max_terms,
        ),
        _term_or_terms_adder(term=term, terms=terms, max_terms=max_terms),
        _code_adder(attribute="code", code_fields=code_fields, value=code),
        _code_adder(
            attribute="display", code_fields=code_fields, value=display
        ),
        _code_adder(attribute="system", code_fields=code_fields, value=system),
        _limit_adder(page_size),
    )
