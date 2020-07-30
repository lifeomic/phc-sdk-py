from typing import Any, Callable, List, Union

import pandas as pd

from phc.services import Fhir
from phc.base_client import BaseClient
from phc.easy.auth import Auth
from phc.easy.query.ga4gh import recursive_execute_ga4gh
from phc.easy.query.fhir_dsl_query import build_query
from phc.easy.query.fhir_dsl import (
    MAX_RESULT_SIZE,
    recursive_execute_fhir_dsl,
    tqdm,
    with_progress,
)
from phc.util.api_cache import APICache


class Query:
    @staticmethod
    def find_count_of_dsl_query(query: dict, auth_args: Auth = Auth.shared()):
        """Find count of a given dsl query

        See https://docs.us.lifeomic.com/development/fhir-service/dsl/

        Attributes
        ----------
        query : dict
            The FHIR query to run a count against

        auth_args : Auth, dict
            Additional arguments for authentication

        Examples
        --------
        >>> import phc.easy as phc
        >>> phc.Auth.set({ 'account': '<your-account-name>' })
        >>> phc.Project.set_current('My Project Name')
        >>> phc.Query.find_count_of_dsl_query({
          "type": "select",
          "columns": "*",
          "from": [{"table": "patient"}],
        })
        """
        auth = Auth(auth_args)
        fhir = Fhir(auth.session())

        response = fhir.execute_es(
            auth.project_id,
            {
                **query,
                "limit": [
                    {"type": "number", "value": 0},
                    {"type": "number", "value": 1},
                ],
            },
            scroll="true",
        )

        return response.data["hits"]["total"]["value"]

    @staticmethod
    def execute_fhir_dsl(
        query: dict,
        all_results: bool = False,
        auth_args: Auth = Auth.shared(),
        callback: Union[Callable[[Any, bool], None], None] = None,
        **query_kwargs,
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

        callback : Callable[[Any, bool], None] (optional)
            A progress function that is invoked for each batch. When the second
            argument passed is true, then the result of the callback function is
            used as the return value. This is useful if writing results out to a
            file and then returning the completed result from that file.

            Example:

                def handle_batch(batch, is_finished):
                    print(len(batch))
                    if is_finished:
                        return "batch finished

        query_kwargs : dict
            Arguments to pass to build_query such as patient_id, patient_ids,
            and patient_key. (See phc.easy.query.fhir_dsl_query.build_query)

        Examples
        --------
        >>> import phc.easy as phc
        >>> phc.Auth.set({ 'account': '<your-account-name>' })
        >>> phc.Project.set_current('My Project Name')
        >>> phc.Query.execute_fhir_dsl({
          "type": "select",
          "columns": "*",
          "from": [
              {"table": "patient"}
          ],
        }, all_results=True)

        """
        query = build_query(query, **query_kwargs)

        if all_results:
            return with_progress(
                lambda: tqdm(total=MAX_RESULT_SIZE),
                lambda progress: recursive_execute_fhir_dsl(
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
                    callback=callback,
                    auth_args=auth_args,
                ),
            )

        return recursive_execute_fhir_dsl(
            query, scroll=all_results, callback=callback, auth_args=auth_args,
        )

    @staticmethod
    def execute_fhir_dsl_with_options(
        query: dict,
        transform: Callable[[pd.DataFrame], pd.DataFrame],
        all_results: bool,
        raw: bool,
        query_overrides: dict,
        auth_args: Auth,
        ignore_cache: bool,
        **query_kwargs,
    ):
        query = build_query({**query, **query_overrides}, **query_kwargs)

        use_cache = (not ignore_cache) and (not raw) and all_results

        if use_cache and APICache.does_cache_for_fhir_dsl_exist(query):
            return APICache.load_cache_for_fhir_dsl(query)

        if use_cache:
            return Query.execute_fhir_dsl(
                query,
                all_results,
                auth_args,
                callback=APICache.build_cache_fhir_dsl_callback(
                    query, transform
                ),
            )

        results = Query.execute_fhir_dsl(query, all_results, auth_args)

        df = pd.DataFrame(map(lambda r: r["_source"], results))

        if raw:
            return df

        return transform(df)

    @staticmethod
    def execute_ga4gh(
        query: dict, all_results: bool = False, auth_args: dict = Auth.shared()
    ) -> pd.DataFrame:
        auth = Auth(auth_args)
        client = BaseClient(auth.session())
        path = query["path"]
        http_verb = query.get("http_verb", "POST")
        results_key = query["results_key"]
        params = {
            **{"datasetIds": [auth.project_id]},
            **{
                k: v for k, v in query.items() if k not in ["path", "http_verb"]
            },
        }

        return recursive_execute_ga4gh(
            auth=auth,
            client=client,
            path=path,
            http_verb=http_verb,
            results_key=results_key,
            params=params,
            scroll=all_results,
        )
