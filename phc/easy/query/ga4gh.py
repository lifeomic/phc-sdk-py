from typing import List, Union
from phc.easy.auth import Auth
from phc.base_client import BaseClient

PAGE_SIZE = 50


def recursive_execute_ga4gh(
    auth: Auth,
    client: BaseClient,
    path: str,
    http_verb: str,
    results_key: str,
    params: dict,
    scroll: bool = False,
    next_page_token: Union[str, None] = None,
    _prev_results: List[dict] = [],
):
    page_size = params.get("pageSize", PAGE_SIZE)

    response = client._ga4gh_call(
        path, http_verb=http_verb, json={**params, "pageToken": next_page_token}
    )

    current_results = response.data[results_key]
    results = [*_prev_results, *current_results]

    is_last_batch = len(current_results) < page_size or scroll is False

    if is_last_batch:
        print(f"Retrieved {len(results)} results")
        return results

    return recursive_execute_ga4gh(
        auth=auth,
        client=client,
        path=path,
        http_verb=http_verb,
        results_key=results_key,
        params=params,
        scroll=scroll,
        next_page_token=response.data["nextPageToken"],
        _prev_results=results,
    )
