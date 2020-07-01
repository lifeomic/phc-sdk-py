from phc import Session
from phc.services import Accounts, Projects, Fhir
from phc.easy.auth import Auth
from typing import List

MAX_RESULT_SIZE = 10000


def query_allows_scrolling(query):
    limit = iter(query.get("limit", []))

    lower = next(limit, {}).get("value")
    upper = next(limit, {}).get("value")

    return type(lower) == int and type(upper) == int


def recursive_execute_dsl(
    query: dict,
    scroll: bool = False,
    auth_args: Auth = Auth.shared(),
    _scroll_id: str = "true",
    _prev_hits: List = [],
):
    auth = Auth(auth_args)
    fhir = Fhir(auth.session())

    response = fhir.execute_es(
        auth.project_id,
        query,
        _scroll_id if query_allows_scrolling(query) and scroll else "",
    )

    current_results = response.data.get("hits").get("hits")
    results = [*_prev_hits, *current_results]
    _scroll_id = response.data.get("_scroll_id", "")

    if len(current_results) == 0 or scroll is False:
        return results

    return recursive_execute_dsl(
        query,
        scroll=True,
        auth_args=auth,
        _scroll_id=_scroll_id,
        _prev_hits=results,
    )


class Query:
    @staticmethod
    def execute_dsl(
        query: dict, all_results: bool = False, auth_args: Auth = Auth.shared(),
    ):
        """Execute a FHIR query with the DSL

        See https://docs.us.lifeomic.com/development/fhir-service/dsl/

        Attributes
        ----------
        query : dict
            The FHIR query to run (is a superset of elasticsearch)

        all_results : bool
            Return all results by scrolling through mutliple pages of data
            (Limit is ignored if provided)

        auth_args : Auth, dict
            Additional arguments for authentication

        Examples
        --------
        >>> import phc.easy as phc
        >>> phc.Auth.set({ 'account': '<your-account-name>' })
        >>> phc.Project.set_current('My Project Name')
        >>> phc.Query.execute_dsl({
          "type": "select",
          "columns": "*",
          "from": [
              {"table": "patient"}
          ],
        }, all_results=True)
        """
        if all_results:
            return recursive_execute_dsl(
                {
                    **query,
                    "limit": [
                        {"type": "number", "value": 0},
                        # Make window size smaller than maximum to reduce
                        # pressure on API
                        {"type": "number", "value": int(MAX_RESULT_SIZE / 5)},
                    ],
                },
                all_results,
                auth_args,
            )

        # Scroll if limit is above MAX_RESULT_SIZE
        limit = iter(query.get("limit", []))

        lower = next(limit, {}).get("value")
        upper = next(limit, {}).get("value")

        scroll = True if upper - lower > MAX_RESULT_SIZE else all_results

        return recursive_execute_dsl(query, scroll, auth_args)
