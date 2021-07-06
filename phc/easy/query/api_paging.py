import json
from typing import Any, Callable, List, Optional, Union
from urllib.parse import parse_qs, quote, urlparse

from funcy import nth
from phc.base_client import BaseClient
from phc.easy.auth import Auth
from phc.easy.util import tqdm

MAX_RESULT_SIZE = 999


def clean_params(params: dict):
    return {
        k: v
        for k, v in params.items()
        if ((v is not None) and (not isinstance(v, str) or len(v) > 0))
    }


def get_next_page_token(data: dict):
    if "links" in data:
        # If links is present, the only 100% accurate way to get the next token is by
        # parsing the next URL
        return parse_next_page_token_from_url(
            data.get("links", {}).get("next", "")
        )

    next_page_token = data.get("nextPageToken")
    if next_page_token and isinstance(next_page_token, dict):
        # URL encode next page token since it's sometimes a dictionary
        return json.dumps(next_page_token)

    if next_page_token and isinstance(next_page_token, str):
        return next_page_token

    return None


def parse_next_page_token_from_url(next_url: str):
    "Parse next url and retrieve nextPageToken (or None)"
    return nth(0, parse_qs(urlparse(next_url).query).get("nextPageToken", []))


def recursive_paging_api_call(
    path: str,
    params: dict = {},
    http_verb: str = "GET",
    scroll: bool = False,
    progress: Optional[tqdm] = None,
    auth_args: Optional[Auth] = Auth.shared(),
    callback: Union[Callable[[Any, bool], None], None] = None,
    max_pages: Optional[int] = None,
    page_size: Optional[int] = None,
    item_key: str = "items",
    response_to_items: Optional[Callable[[Union[list, dict]], list]] = None,
    log: bool = False,
    try_count: bool = True,
    _current_page: int = 1,
    _prev_results: List[dict] = [],
    _next_page_token: Optional[str] = None,
    _count: Optional[Union[float, int]] = None,
):
    auth = Auth(auth_args)
    client = BaseClient(auth.session())

    if _next_page_token:
        params = {**params, "nextPageToken": _next_page_token}

    if page_size:
        params = {**params, "pageSize": page_size}

    # NOTE: Parallelism is kept with execute_fhir_dsl to unify the API calls
    if scroll is False:
        max_pages = 1

    # Compute count and add to progress
    if try_count and _count is None and len(_prev_results) == 0:
        count_response = client._api_call(
            path,
            http_verb=http_verb,
            # Use minimum pageSize in case this endpoint doesn't support count
            params={**params, "include": "count", "pageSize": 1},
        )

        _count = count_response.get("count")
        # Count appears to only go up to 999
        if _count == 999:
            print(f"Results are {_count}+.")
            _count = None

        if _count and (progress is not None):
            progress.reset(_count)

    response = client._api_call(path, http_verb=http_verb, params=params)

    if response_to_items is None:

        def response_to_items(data):
            return data.get(item_key, [])

    current_results = response_to_items(response.data)

    if progress is not None:
        progress.update(len(current_results))

    next_page_token = get_next_page_token(response.data)

    is_last_batch = (
        (scroll is False)
        or ((max_pages is not None) and (_current_page >= max_pages))
        # Using the next link is the only completely reliable way to tell if a
        # next page exists
        or (next_page_token is None)
    )
    results = [] if callback else [*_prev_results, *current_results]

    # Sometimes the count doesn't match the results. We make it sync up if the
    # count doesn't match but we got all results.
    # TODO: Remove this when API fixed
    if (
        (progress is not None)
        and scroll
        and is_last_batch
        and (progress.total != progress.n)
    ):
        count = progress.n
        progress.reset(count)
        progress.update(count)

    if callback and not is_last_batch:
        callback(current_results, False)
    elif callback and is_last_batch:
        return callback(current_results, True)
    elif is_last_batch:
        if progress is not None:
            progress.close()

        # Because count is often wrong, we'll skip the logging here
        # TODO: Uncomment this when API fixed
        # print(
        #     f"Retrieved {len(results)}{f'/{_count}' if _count else ''} results"
        # )
        return results

    return recursive_paging_api_call(
        path,
        params=params,
        http_verb=http_verb,
        progress=progress,
        auth_args=auth_args,
        callback=callback,
        max_pages=max_pages,
        page_size=page_size,
        log=log,
        scroll=scroll,
        try_count=try_count,
        item_key=item_key,
        response_to_items=response_to_items,
        _current_page=_current_page + 1,
        _prev_results=results,
        _next_page_token=next_page_token,
        _count=_count,
    )
