from typing import Any, Callable, List, Union

import pandas as pd

from phc.easy.auth import Auth
from phc.services import Fhir
from phc.easy.util import with_progress, tqdm

MAX_RESULT_SIZE = 10000


def query_allows_scrolling(query):
    limit = iter(query.get("limit", []))

    lower = next(limit, {}).get("value")
    upper = next(limit, {}).get("value")

    return isinstance(lower, int) and isinstance(upper, int)


def execute_single_fhir_dsl(
    query: dict, scroll_id: str = "", auth_args: Auth = Auth.shared()
):
    auth = Auth(auth_args)
    fhir = Fhir(auth.session())

    return fhir.execute_es(auth.project_id, query, scroll_id)


def recursive_execute_fhir_dsl(
    query: dict,
    scroll: bool = False,
    progress: Union[None, tqdm] = None,
    auth_args: Auth = Auth.shared(),
    callback: Union[Callable[[Any, bool], None], None] = None,
    max_pages: Union[int, None] = None,
    _current_page: int = 1,
    _scroll_id: str = "true",
    _prev_hits: List = [],
):
    response = execute_single_fhir_dsl(
        query,
        _scroll_id if query_allows_scrolling(query) and scroll else "",
        auth_args,
    )

    is_first_iteration = _scroll_id == "true"
    current_results = response.data.get("hits").get("hits")
    _scroll_id = response.data.get("_scroll_id", "")
    actual_count = response.data["hits"]["total"]["value"]
    current_result_count = len(current_results)

    if is_first_iteration and progress:
        progress.reset(actual_count)

    if progress:
        progress.update(current_result_count)

    is_last_batch = (
        (current_result_count == 0)
        or (scroll is False)
        or ((max_pages is not None) and (_current_page >= max_pages))
    )
    results = [] if callback else [*_prev_hits, *current_results]

    if callback and not is_last_batch:
        callback(current_results, False)
    elif callback and is_last_batch:
        return callback(current_results, True)
    elif is_last_batch:
        suffix = "+" if actual_count == MAX_RESULT_SIZE else ""
        print(f"Retrieved {len(results)}/{actual_count}{suffix} results")

        return results

    return recursive_execute_fhir_dsl(
        query,
        scroll=True,
        progress=progress,
        auth_args=auth_args,
        callback=callback,
        max_pages=max_pages,
        _current_page=_current_page + 1,
        _scroll_id=_scroll_id,
        _prev_hits=results,
    )
