from typing import List, Union, Callable
from phc import Session
from phc.services import Accounts, Projects, Fhir
from phc.easy.auth import Auth

MAX_RESULT_SIZE = 10000

try:
    from tqdm.autonotebook import tqdm
except ImportError:
    _has_tqdm = False
else:
    _has_tqdm = True


def with_progress(
    init_progress: Callable[[], tqdm], func: Callable[[Union[None, tqdm]], None]
):
    if _has_tqdm:
        progress = init_progress()
        result = func(progress)
        progress.close()
        return result

    return func(None)


def query_allows_scrolling(query):
    limit = iter(query.get("limit", []))

    lower = next(limit, {}).get("value")
    upper = next(limit, {}).get("value")

    return type(lower) == int and type(upper) == int


def recursive_execute_dsl(
    query: dict,
    scroll: bool = False,
    progress: Union[None, tqdm] = None,
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

    actual_count = response.data["hits"]["total"]["value"]
    current_result_count = len(current_results)

    if len(_prev_hits) == 0 and progress and scroll:
        progress.reset(actual_count)

    if progress:
        progress.update(current_result_count)

    if current_result_count == 0 or scroll is False:
        print(
            f"Retrieved {len(results)}/{actual_count}{'+' if actual_count == MAX_RESULT_SIZE else ''} results"
        )
        return results

    return recursive_execute_dsl(
        query,
        scroll=True,
        progress=progress,
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
            return with_progress(
                lambda: tqdm(total=MAX_RESULT_SIZE),
                lambda progress: recursive_execute_dsl(
                    {
                        "limit": [
                            {"type": "number", "value": 0},
                            # Make window size smaller than maximum to reduce
                            # pressure on API
                            {
                                "type": "number",
                                "value": int(MAX_RESULT_SIZE / 2),
                            },
                        ],
                        **query,
                    },
                    scroll=all_results,
                    progress=progress,
                    auth_args=auth_args,
                ),
            )

        return recursive_execute_dsl(
            query, scroll=all_results, auth_args=auth_args,
        )
