import json
import pandas as pd
from urllib.parse import urljoin
from phc.base_client import BaseClient
from typing import List, Union, Optional
from phc.easy.auth import Auth
from phc.easy.util import tqdm

MAX_RESULT_SIZE = 999


def clean_params(params: dict):
    return {
        k: v
        for k, v in params.items()
        if ((v is not None) and (not isinstance(v, str) or len(v) > 0))
    }


def recursive_paging_api_call(
    path: str,
    params: dict = {},
    http_verb: str = "GET",
    scroll: bool = False,
    progress: Optional[tqdm] = None,
    auth_args: Optional[Auth] = Auth.shared(),
    max_pages: Optional[int] = None,
    page_size: Optional[int] = None,
    log: bool = False,
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

    params = clean_params(params)

    actual_path = path.replace(":project_id", auth.project_id)

    # Compute count and add to progress
    if _count is None and len(_prev_results) == 0:
        count_response = client._api_call(
            actual_path,
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

    if log:
        print(
            json.dumps(
                {
                    "url": urljoin(client.session.api_url, actual_path),
                    "method": http_verb,
                    "params": params,
                },
                indent=4,
            )
        )

    response = client._api_call(actual_path, http_verb=http_verb, params=params)

    current_results = response.data.get("items", [])
    results = [*_prev_results, *current_results]

    if progress is not None:
        progress.update(len(current_results))

    is_last_batch = (
        (scroll is False)
        or ((max_pages is not None) and (_current_page >= max_pages))
        # Using the next link is the only completely reliable way to tell if a
        # next page exists
        or (response.data.get("links", {}).get("next") is None)
    )

    if is_last_batch:
        if progress is not None:
            progress.close()

        print(
            f"Retrieved {len(results)}{f'/{_count}' if _count else ''} results"
        )
        return pd.DataFrame(results)

    return recursive_paging_api_call(
        path,
        params=params,
        http_verb=http_verb,
        progress=progress,
        auth_args=auth_args,
        max_pages=max_pages,
        page_size=page_size,
        log=log,
        scroll=scroll,
        _current_page=_current_page + 1,
        _prev_results=results,
        _next_page_token=response.data.get("nextPageToken"),
        _count=_count,
    )
