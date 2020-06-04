from phc import Session
from phc.services import Accounts, Projects, Fhir
from phc.easy.auth import Auth
from typing import List


def __query_allows_scrolling(query):
    return next(iter(query.get('limit', [])), {}).get('value', 0) == 0


def execute_dsl(query,
                scroll: bool = False,
                scroll_id: str = 'true',
                prev_hits: List = [],
                auth=Auth.shared()):
    fhir = Fhir(auth.session())

    response = fhir.execute_es(
        auth.project_id, query,
        scroll_id if __query_allows_scrolling(query) and scroll else '')

    current_results = response.data.get('hits').get('hits')
    results = [*prev_hits, *current_results]
    scroll_id = response.data.get('_scroll_id', '')

    if len(current_results) == 0 or scroll is False:
        return results

    return execute_dsl(query,
                       scroll=True,
                       scroll_id=scroll_id,
                       prev_hits=results,
                       auth=auth)
