from typing import Any, Callable, List, Union
from lenses import lens

import math
import pandas as pd

from phc.easy.auth import Auth
from phc.services import Fhir
from phc.easy.util import with_progress, tqdm
from phc.easy.query.fhir_dsl_query import (
    MAX_RESULT_SIZE,
    DEFAULT_SCROLL_SIZE,
    get_limit,
    update_limit,
    build_queries,
)

MAX_RETRY_BACKOFF = 3


def query_allows_scrolling(query):
    limit = iter(query.get("limit", []))

    lower = next(limit, {}).get("value")
    upper = next(limit, {}).get("value")

    return isinstance(lower, int) and isinstance(upper, int)


def execute_single_fhir_dsl(
    query: dict,
    scroll_id: str = "",
    retry_backoff: bool = False,
    auth_args: Auth = Auth.shared(),
    _retry_time: int = 1,
):
    auth = Auth(auth_args)
    fhir = Fhir(auth.session())

    try:
        return fhir.dsl(auth.project_id, query, scroll_id)
    except Exception as err:
        if (
            (_retry_time >= MAX_RETRY_BACKOFF)
            or (retry_backoff is False)
            or ("Internal server error" not in str(err))
        ):
            raise err

        if _retry_time == 1:
            # Base first retry attempt on record count
            # NOTE: Uses the first query to grab count (not the end of the world
            # if the count isn't accurate)
            record_count = fhir.dsl(
                auth.project_id,
                build_queries(query, page_size=1)[0],
                scroll="true",
            ).data["hits"]["total"]["value"]

            def backoff_limit(limit: int):
                return min(
                    (get_limit(query) or DEFAULT_SCROLL_SIZE) / 2,
                    math.pow(record_count, 0.85),
                )

        else:

            def backoff_limit(limit: int):
                return math.pow(limit, 0.85)

        new_query = update_limit(query, backoff_limit)

        print(
            f"Received server error. Retrying with page_size={get_limit(new_query)}"
        )

        return execute_single_fhir_dsl(
            new_query,
            scroll_id=scroll_id,
            retry_backoff=True,
            auth_args=auth_args,
            _retry_time=_retry_time + 1,
        )


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
    will_scroll = query_allows_scrolling(query) and scroll

    response = execute_single_fhir_dsl(
        query,
        scroll_id=_scroll_id if will_scroll else "",
        retry_backoff=will_scroll,
        auth_args=auth_args,
    )

    is_first_iteration = _scroll_id == "true"
    current_results = response.data.get("hits").get("hits")
    _scroll_id = response.data.get("_scroll_id", "")
    actual_count = response.data["hits"]["total"]["value"]
    current_result_count = len(current_results)

    if is_first_iteration and progress:
        progress.reset(actual_count)

    if progress is not None:
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
