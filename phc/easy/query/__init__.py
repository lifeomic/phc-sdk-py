import json
import math
from typing import Any, Callable, List, Optional, Tuple, Union

import pandas as pd
from phc.base_client import BaseClient
from phc.easy.auth import Auth
from phc.easy.query.api_paging import clean_params, recursive_paging_api_call
from phc.easy.query.fhir_aggregation import FhirAggregation
from phc.easy.query.fhir_dsl import (
    DEFAULT_SCROLL_SIZE,
    MAX_RESULT_SIZE,
    execute_single_fhir_dsl,
    recursive_execute_fhir_dsl,
    tqdm,
    with_progress,
)
from phc.easy.query.fhir_dsl_query import build_queries
from phc.easy.query.ga4gh import recursive_execute_ga4gh
from phc.easy.query.url import merge_pattern
from phc.easy.util import _has_tqdm, extract_codes
from phc.easy.util.api_cache import FHIR_DSL, APICache
from phc.services import Fhir
from toolz import identity


class Query:
    @staticmethod
    def find_count_of_dsl_query(query: dict, auth_args: Auth = Auth.shared()):
        """Find count of a given dsl query

        See https://devcenter.docs.lifeomic.com/development/fhir-service/dsl

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
        if FhirAggregation.is_aggregation_query(query):
            raise ValueError("Count is not support for aggregation queries.")

        auth = Auth(auth_args)
        fhir = Fhir(auth.session())

        response = fhir.execute_es(
            auth.project_id, build_queries(query, page_size=1)[0], scroll="true"
        )

        return response.data["hits"]["total"]["value"]

    @staticmethod
    def execute_fhir_dsl(
        query: dict,
        all_results: bool = False,
        auth_args: Auth = Auth.shared(),
        callback: Union[Callable[[Any, bool], None], None] = None,
        max_pages: Union[int, None] = None,
        log: bool = False,
        **query_kwargs,
    ):
        """Execute a FHIR query with the DSL

        See https://devcenter.docs.lifeomic.com/development/fhir-service/dsl

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

        max_pages : int
            The number of pages to retrieve (useful if working with tons of records)

        log : bool = False
            Whether to log the elasticsearch query sent to the server

        query_kwargs : dict
            Arguments to pass to build_queries such as patient_id, patient_ids,
            and patient_key. (See phc.easy.query.fhir_dsl_query.build_queries)

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
        queries = build_queries(query, **query_kwargs)

        if log:
            print(json.dumps(queries, indent=4))

        if len(queries) > 1 and FhirAggregation.is_aggregation_query(
            queries[0]
        ):
            raise ValueError(
                "Cannot combine multiple aggregation query results"
            )

        if FhirAggregation.is_aggregation_query(queries[0]):
            response = execute_single_fhir_dsl(queries[0], auth_args=auth_args)
            return FhirAggregation.from_response(response)

        if len(queries) > 1 and _has_tqdm:
            queries = tqdm(queries)

        result_set = []

        for query in queries:
            if all_results:
                results = with_progress(
                    lambda: tqdm(total=MAX_RESULT_SIZE),
                    lambda progress: recursive_execute_fhir_dsl(
                        {
                            "limit": [
                                {"type": "number", "value": 0},
                                # Make window size smaller than maximum to reduce
                                # pressure on API
                                {
                                    "type": "number",
                                    "value": DEFAULT_SCROLL_SIZE,
                                },
                            ],
                            **query,
                        },
                        scroll=all_results,
                        progress=progress,
                        callback=callback,
                        auth_args=auth_args,
                        max_pages=max_pages,
                    ),
                )
            else:
                results = recursive_execute_fhir_dsl(
                    query,
                    scroll=all_results,
                    callback=callback,
                    auth_args=auth_args,
                    max_pages=max_pages,
                )

            if len(result_set) == 0:
                result_set = results
            else:
                result_set.append(*results)

        return result_set

    @staticmethod
    def execute_paging_api(
        path: str,
        params: dict = {},
        http_verb: str = "GET",
        transform: Callable[[pd.DataFrame], pd.DataFrame] = identity,
        all_results: bool = False,
        auth_args: Auth = Auth.shared(),
        max_pages: Optional[int] = None,
        page_size: Optional[int] = None,
        log: bool = False,
        raw: bool = False,
        ignore_cache: bool = False,
        show_progress: bool = True,
        progress: Optional[tqdm] = None,
        item_key: str = "items",
        try_count: bool = True,
        response_to_items: Optional[Callable[[Union[list, dict]], list]] = None,
    ):
        """Execute a API query that pages through results

        Attributes
        ----------
        path : str
            The API path to hit
            (Special tokens: `{project_id}`)

        params : dict
            The parameters to include with request

        http_verb : str
            The HTTP method to use

        all_results : bool = False
            Retrieve sample of results (25) or entire set of records

        auth_args : Auth, dict
            Additional arguments for authentication

        max_pages : int
            The number of pages to retrieve (useful if working with tons of records)

        page_size : int
            The number of records to fetch per page

        log : bool = False
            Whether to log some diagnostic statements for debugging

        progress : Optional[tqdm] = None
            Override the given progress indicator

        item_key : str
            The key to find the results underneath (usually "items" but not always)

        try_count : bool
            Whether to try and send a "count" param to update the progress bar

        response_to_items : Callable
            Custom function to transform response data to list of items
            (Overrides item_key when present)

        Examples
        --------
        >>> import phc.easy as phc
        >>> phc.Auth.set({ 'account': '<your-account-name>' })
        >>> phc.Project.set_current('My Project Name')
        >>> phc.Query.execute_paging_api(
                "genomics/projects/{project_id}/tests",
                params={
                    "patientId": "<patient-uuid>"
                }
            )

        """

        auth = Auth(auth_args)

        params = clean_params(params)

        # Do not pull project_id if not in URL (which throws error if project not selected)
        if "project_id" in path:
            path = path.replace("{project_id}", auth.project_id)

        path, params = merge_pattern(path, params)

        query = {"path": path, "method": http_verb, "params": params}

        if all_results and page_size is None:
            # Default to 100 if not provided but getting all results
            page_size = 100

        if log:
            print(json.dumps(query, indent=4))

        use_cache = (
            (not ignore_cache)
            and (not raw)
            and all_results
            and (max_pages is None)
        )

        if use_cache and APICache.does_cache_for_query_exist(query):
            return APICache.load_cache_for_query(query)

        callback = (
            APICache.build_cache_callback(query, transform, nested_key=None)
            if use_cache
            else None
        )

        results = with_progress(
            lambda: (progress if progress is not None else tqdm())
            if show_progress
            else None,
            lambda progress: recursive_paging_api_call(
                path,
                params=params,
                http_verb=http_verb,
                callback=callback,
                scroll=all_results or (max_pages is not None),
                max_pages=max_pages,
                page_size=page_size,
                log=log,
                auth_args=auth_args,
                progress=progress,
                item_key=item_key,
                response_to_items=response_to_items,
                try_count=try_count,
            ),
        )

        df = pd.DataFrame(results)

        if raw:
            return df

        return transform(df)

    @staticmethod
    def execute_fhir_dsl_with_options(
        query: dict,
        transform: Callable[[pd.DataFrame], pd.DataFrame],
        all_results: bool,
        raw: bool,
        query_overrides: dict,
        auth_args: Auth,
        ignore_cache: bool,
        max_pages: Union[int, None],
        log: bool = False,
        **query_kwargs,
    ):
        queries = build_queries({**query, **query_overrides}, **query_kwargs)

        if log:
            print(json.dumps(queries, indent=4))

        is_first_agg_query = FhirAggregation.is_aggregation_query(queries[0])

        if len(queries) > 1 and is_first_agg_query:
            raise ValueError("Cannot combine multiple aggregate results")

        use_cache = (
            (not ignore_cache)
            and (not raw)
            and (all_results or is_first_agg_query)
            and (max_pages is None)
        )

        if len(queries) > 1 and _has_tqdm:
            queries = tqdm(queries)

        frame = pd.DataFrame()

        for one_query in queries:
            if use_cache and APICache.does_cache_for_query_exist(
                one_query, namespace=FHIR_DSL
            ):
                results = APICache.load_cache_for_query(
                    one_query, namespace=FHIR_DSL
                )
            else:
                results = Query.execute_fhir_dsl(
                    one_query,
                    all_results,
                    auth_args,
                    callback=(
                        APICache.build_cache_callback(
                            one_query, transform, namespace=FHIR_DSL
                        )
                        if use_cache
                        else None
                    ),
                    max_pages=max_pages,
                )

            if isinstance(results, FhirAggregation):
                # Cache isn't written in batches so we need to explicitly do it here
                if use_cache:
                    APICache.write_agg(one_query, results)

                # We don't support multiple agg queries so fine to return first one
                return results

            batch_frame = (
                pd.DataFrame(map(lambda r: r["_source"], results))
                if not isinstance(results, pd.DataFrame)
                else results
            )

            frame = (
                batch_frame
                if len(frame) == 0
                else pd.concat([frame, batch_frame]).reset_index(drop=True)
            )

        if raw:
            return frame

        return transform(frame)

    @staticmethod
    def get_codes(
        table_name: str,
        code_fields: List[str],
        display_query: Optional[str] = None,
        sample_size: Optional[int] = None,
        **kwargs,
    ):
        """Find FHIR codes with a display for a given table

        Attributes
        ----------
        table_name : str
            The FHIR Search Service table to retrieve from

        code_fields : List[str]
            The fields of this table that contain a system, code, and display

        display_query : Optional[str]
            Part of the code's display to match (will try to extract full code
            if passed)

        sample_size : Optional[int]
            Override the search size for finding codes (may miss codes on later
            records)

        kwargs : dict
            Arguments to pass to `phc.easy.query.Query.execute_composite_aggregations`

        Examples
        --------
        >>> import phc.easy as phc
        >>> phc.Auth.set({ 'account': '<your-account-name>' })
        >>> phc.Project.set_current('My Project Name')
        >>> phc.Query.get_codes(
            table_name="observation",
            code_fields=["meta.tag", "code.coding"],
            patient_id="<my-patient-id>"
        )
        """
        if len(code_fields) == 0:
            raise ValueError("No code columns specified.")

        def agg_composite_to_frame(prefix: str, data: dict):
            frame = pd.json_normalize(data["buckets"])
            frame.columns = frame.columns.str.lstrip("key.")
            frame["field"] = prefix
            return frame

        if display_query is not None:
            kwargs = {
                **kwargs,
                "query_overrides": {
                    "where": {
                        "type": "elasticsearch",
                        "query": {
                            "multi_match": {
                                "query": display_query,
                                "fields": [
                                    f"{key}.display" for key in code_fields
                                ],
                            }
                        },
                    }
                },
            }

        results = Query.execute_composite_aggregations(
            table_name=table_name,
            key_sources_pairs=[
                (
                    field,
                    [
                        {
                            "display": {
                                "terms": {"field": f"{field}.display.keyword"}
                            }
                        }
                    ],
                )
                for field in code_fields
            ],
            **kwargs,
        )

        agg_result = (
            pd.concat(
                [
                    agg_composite_to_frame(key, value)
                    for key, value in results.items()
                ]
            )
            .pipe(
                lambda df: df
                if len(df) == 0 or display_query is None
                # Poor man's way to filter only matching codes (since Elasticsearch
                # returns records which will include other codes)
                else df[
                    df["display"]
                    .str.lower()
                    .str.contains(display_query.lower())
                ]
            )
            .pipe(
                lambda df: pd.DataFrame()
                if len(df) == 0
                else df.sort_values("doc_count", ascending=False).reset_index(
                    drop=True
                )
            )
        )

        if display_query is None or len(agg_result) == 0:
            return agg_result

        min_count = sample_size or agg_result.doc_count.sum()
        filtered_code_fields = agg_result.field.unique()

        # Shortcut: If one result, we just need to get the other associated
        # attributes of the code
        if len(agg_result) == 1:
            min_count = 1

        code_results = Query.execute_fhir_dsl(
            {
                "type": "select",
                "from": [{"table": table_name}],
                "columns": [
                    {
                        "expr": {
                            "type": "column_ref",
                            "column": key.split(".")[0],
                        }
                    }
                    for key in filtered_code_fields
                ],
                "where": {
                    "type": "elasticsearch",
                    "query": {
                        "multi_match": {
                            "query": display_query,
                            "fields": [
                                f"{key}.display" for key in filtered_code_fields
                            ],
                        }
                    },
                },
            },
            page_size=int(min_count % 9000),
            max_pages=int(math.ceil(min_count / 9000)),
            log=kwargs.get("log", False),
        )

        codes = extract_codes(
            map(lambda d: d["_source"], code_results),
            display_query,
            code_fields,
        )

        if len(codes) == 0:
            return codes

        if len(codes) == codes.display.nunique():
            # If display values are unique, then the counts from Elasticsearch
            # are correct. We can therefore join them.
            codes = (
                codes.join(
                    agg_result[["display", "doc_count"]].set_index("display"),
                    on="display",
                    how="outer",
                )
                .sort_values("doc_count", ascending=False)
                .reset_index(drop=True)
            )

            if len(codes[codes.field.isnull()]) > 0:
                print(
                    "Records with missing system/code values were not retrieved."
                )

            return codes

        return codes

    @staticmethod
    def execute_composite_aggregations(
        table_name: str,
        key_sources_pairs: List[Tuple[str, List[dict]]],
        batch_size: int = 100,
        query_overrides: dict = {},
        log: bool = False,
        auth_args: Auth = Auth.shared(),
        max_pages: Union[int, None] = None,
        **query_kwargs,
    ):
        """Count records by multiple fields

        Attributes
        ----------
        table_name : str
            The FHIR Search Service table to retrieve from

        key_sources_pairs : str
            Pairs of keys and sources to pull composite results from

            Example Input:
                [
                    ("meta.tag", [{"terms": {"field": "meta.tag.system.keyword"}}])
                ]

        batch_size : int
            The size of each page from elasticsearch to use

        query_overrides : dict
            Parts of the FSS query to override
            (Note that passing certain values can cause the method to error out)

            Example aggregation query executed (can use log=True to inspect):
                {
                    "type": "select",
                    "columns": [{
                        "type": "elasticsearch",
                        "aggregations": {
                            "results": {
                                "composite": {
                                    "sources": [{
                                        "meta.tag": {
                                            "terms": {
                                                "field": "meta.tag.system.keyword"
                                            }
                                        }
                                    }],
                                    "size": 100,
                                }
                            }
                        },
                    }],
                    "from": [{"table": "observation"}],
                }


        auth_args : Auth, dict
            Additional arguments for authentication

        log : bool = False
            Whether to log the elasticsearch query sent to the server

        max_pages : int
            The number of pages to retrieve (useful if working with tons of records)

        query_kwargs : dict
            Arguments to pass to build_queries such as patient_id, patient_ids,
            and patient_key. See :func:`~phc.easy.query.fhir_dsl_query.build_queries`.

        Examples
        --------
        >>> import phc.easy as phc
        >>> phc.Auth.set({ 'account': '<your-account-name>' })
        >>> phc.Project.set_current('My Project Name')
        >>> phc.Query.execute_composite_aggregations(
            table_name="observation",
            key_sources_pairs=[
                ("meta.tag", [
                    {"code": {"terms": {"field": "meta.tag.code.keyword"}}},
                ]),
                ("code.coding", [
                    {"display": {"terms": {"field": "code.coding.display.keyword"}}}
                ]),
            ]
        )
        """
        if len(key_sources_pairs) == 0:
            raise ValueError("No aggregate composite terms specified.")

        return with_progress(
            tqdm,
            lambda progress: Query._recursive_execute_composite_aggregations(
                table_name=table_name,
                key_sources_pairs=key_sources_pairs,
                batch_size=batch_size,
                progress=progress,
                log=log,
                auth_args=auth_args,
                query_overrides=query_overrides,
                max_pages=max_pages,
                **query_kwargs,
            ),
        )

    @staticmethod
    def get_count_by_field(
        table_name: str,
        field: str,
        batch_size: int = 1000,
        query_overrides: dict = {},
        log: bool = False,
        auth_args: Auth = Auth.shared(),
        **query_kwargs,
    ):
        """Count records by a given field

        Attributes
        ----------
        table_name : str
            The FHIR Search Service table to retrieve from

        field : str
            The field name to count the values of (e.g. "subject.reference")

        batch_size : int
            The size of each page from elasticsearch to use

        query_overrides : dict
            Parts of the FSS query to override
            (Note that passing certain values can cause the method to error out)

            The aggregation query is similar to this:
                {
                    "type": "select",
                    "columns": [{
                        "type": "elasticsearch",
                        "aggregations": {
                            "results": {
                                "composite": {
                                    "sources": [{
                                        "value": {
                                            "terms": {
                                                "field": "gender.keyword"
                                            }
                                        }
                                    }],
                                    "size": 100,
                                }
                            }
                        },
                    }],
                    "from": [{"table": "patient"}],
                }


        auth_args : Auth, dict
            Additional arguments for authentication

        log : bool = False
            Whether to log the elasticsearch query sent to the server

        query_kwargs : dict
            Arguments to pass to build_queries such as patient_id, patient_ids,
            and patient_key. (See phc.easy.query.fhir_dsl_query.build_queries)

        Examples
        --------
        >>> import phc.easy as phc
        >>> phc.Auth.set({ 'account': '<your-account-name>' })
        >>> phc.Project.set_current('My Project Name')
        >>> phc.Query.get_count_by_field(
            table_name="patient",
            field="gender"
        )
        """
        data = Query.execute_composite_aggregations(
            table_name=table_name,
            key_sources_pairs=[
                (
                    "results",
                    [{"value": {"terms": {"field": f"{field}.keyword"}}}],
                )
            ],
            batch_size=batch_size,
            log=log,
            auth_args=auth_args,
            query_overrides=query_overrides,
            **query_kwargs,
        )

        return pd.DataFrame(
            [
                {field: r["key"]["value"], "doc_count": r["doc_count"]}
                for r in data["results"]["buckets"]
            ]
        )

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

    @staticmethod
    def _recursive_execute_composite_aggregations(
        table_name: str,
        key_sources_pairs: List[Tuple[str, List[dict]]],
        batch_size: int = 100,
        progress: Union[tqdm, None] = None,
        query_overrides: dict = {},
        log: bool = False,
        auth_args: Auth = Auth.shared(),
        max_pages: Union[int, None] = None,
        _current_page: int = 1,
        _prev_results: dict = {},
        _after_keys: dict = {},
        **query_kwargs,
    ):
        aggregation = Query.execute_fhir_dsl(
            {
                "type": "select",
                "columns": [
                    {
                        "type": "elasticsearch",
                        "aggregations": {
                            key: {
                                "composite": {
                                    "sources": sources,
                                    "size": batch_size,
                                    **(
                                        {"after": _after_keys[key]}
                                        if key in _after_keys
                                        else {}
                                    ),
                                }
                            }
                            for key, sources in key_sources_pairs
                            if (len(_after_keys) == 0) or (key in _after_keys)
                        },
                    }
                ],
                "from": [{"table": table_name}],
                **query_overrides,
            },
            auth_args=auth_args,
            log=log,
            **query_kwargs,
        )

        current_results = aggregation.data
        results = FhirAggregation.reduce_composite_results(
            _prev_results, current_results
        )

        if (progress is not None) and (_current_page == 1) and max_pages:
            progress.reset(max_pages)

        if progress is not None:
            # Update by count or pages (if max_pages specified)
            progress.update(
                1
                if max_pages
                else FhirAggregation.count_composite_results(current_results)
            )

        after_keys = FhirAggregation.find_composite_after_keys(
            current_results, batch_size
        )

        if len(after_keys) == 0 or (
            (max_pages is not None) and (_current_page >= max_pages)
        ):
            print(
                f"Retrieved {FhirAggregation.count_composite_results(results)} results"
            )
            return results

        return Query._recursive_execute_composite_aggregations(
            table_name=table_name,
            key_sources_pairs=key_sources_pairs,
            batch_size=batch_size,
            progress=progress,
            query_overrides=query_overrides,
            log=log,
            auth_args=auth_args,
            max_pages=max_pages,
            _current_page=_current_page + 1,
            _prev_results=results,
            _after_keys=after_keys,
            **query_kwargs,
        )
