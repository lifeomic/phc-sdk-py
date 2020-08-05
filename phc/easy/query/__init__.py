from typing import Any, Callable, List, Union, NamedTuple, Tuple
import pandas as pd

from phc.services import Fhir
from phc.base_client import BaseClient
from phc.easy.auth import Auth
from phc.easy.query.ga4gh import recursive_execute_ga4gh
from phc.easy.query.fhir_dsl_query import build_query
from phc.easy.query.fhir_dsl import (
    MAX_RESULT_SIZE,
    recursive_execute_fhir_dsl,
    execute_single_fhir_dsl,
    tqdm,
    with_progress,
)
from phc.util.api_cache import APICache
from phc.easy.query.fhir_aggregation import FhirAggregation


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
        if FhirAggregation.is_aggregation_query(query):
            raise ValueError("Count is not support for aggregation queries.")

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
        log: bool = False,
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

        log : bool = False
            Whether to log the elasticsearch query sent to the server

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

        if log:
            print(query)

        if FhirAggregation.is_aggregation_query(query):
            response = execute_single_fhir_dsl(query, auth_args=auth_args)
            return FhirAggregation.from_response(response)

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
        log: bool = False,
        **query_kwargs,
    ):
        query = build_query({**query, **query_overrides}, **query_kwargs)

        if log:
            print(query)

        use_cache = (
            (not ignore_cache)
            and (not raw)
            and (all_results or FhirAggregation.is_aggregation_query(query))
        )

        if use_cache and APICache.does_cache_for_fhir_dsl_exist(query):
            return APICache.load_cache_for_fhir_dsl(query)

        callback = (
            APICache.build_cache_fhir_dsl_callback(query, transform)
            if use_cache
            else None
        )

        results = Query.execute_fhir_dsl(
            query, all_results, auth_args, callback=callback
        )

        if isinstance(results, FhirAggregation):
            # Cache isn't written in batches so we need to explicitly do it here
            if use_cache:
                APICache.write_agg(query, results)

            return results

        if isinstance(results, pd.DataFrame):
            return results

        df = pd.DataFrame(map(lambda r: r["_source"], results))

        if raw:
            return df

        return transform(df)

    @staticmethod
    def get_codes(table_name: str, code_fields: List[str], **kwargs):
        """Find FHIR codes for a given table

        Attributes
        ----------
        table_name : str
            The FHIR Search Service table to retrieve from

        code_fields : List[str]
            The fields of this table that contain a system, code, and display

        kwargs : dict
            Arguments to pass to :func:`~phc.easy.query.Query.execute_composite_aggregations`

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

        results = Query.execute_composite_aggregations(
            table_name=table_name,
            key_sources_pairs=[
                (
                    field,
                    [
                        {
                            "system": {
                                "terms": {"field": f"{field}.system.keyword"}
                            }
                        },
                        {"code": {"terms": {"field": f"{field}.code.keyword"}}},
                        {
                            "display": {
                                "terms": {
                                    "field": f"{field}.display.keyword",
                                    "missing_bucket": True,
                                }
                            }
                        },
                    ],
                )
                for field in code_fields
            ],
            **kwargs,
        )

        return pd.concat(
            [
                agg_composite_to_frame(key, value)
                for key, value in results.items()
            ]
        )

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
            Arguments to pass to build_query such as patient_id, patient_ids,
            and patient_key. See :func:`~phc.easy.query.fhir_dsl_query.build_query`.

        Examples
        --------
        >>> import phc.easy as phc
        >>> phc.Auth.set({ 'account': '<your-account-name>' })
        >>> phc.Project.set_current('My Project Name')
        >>> phc.Query.execute_composite_aggregations(
            table_name="observation",
            key_sources_pairs=[
                ("meta.tag", [
                    {"system": {"terms": {"field": "meta.tag.system.keyword"}}},
                    {"code": {"terms": {"field": "meta.tag.code.keyword"}}},
                    {"display": {"terms": {"field": "meta.tag.display.keyword"}}},
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
            Arguments to pass to build_query such as patient_id, patient_ids,
            and patient_key. (See phc.easy.query.fhir_dsl_query.build_query)

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
