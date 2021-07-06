import inspect
from typing import Optional

import pandas as pd
from funcy import first, iffy, lmapcat, rpartial
from phc.easy.abstract.paging_api_item import PagingApiItem, PagingApiOptions
from phc.easy.auth import Auth
from phc.easy.util.frame import combine_first, drop
from toolz import pipe


class NoOptions(PagingApiOptions):
    pass


class SummaryCounts(PagingApiItem):
    @staticmethod
    def resource_path():
        return "analytics/summary/{project_id}"

    @staticmethod
    def response_to_items(data):
        squashed = first(pd.json_normalize(data).to_dict("records")) or {}
        return lmapcat(
            lambda k: [{"summary": k, **v} for v in squashed[k]]
            if isinstance(squashed[k], list)
            else [],
            squashed.keys(),
        )

    @staticmethod
    def execute_args() -> dict:
        return dict(ignore_cache=True)

    @staticmethod
    def params_class():
        return NoOptions

    @staticmethod
    def transform_results(
        data_frame: pd.DataFrame, include_demographics: bool, **expand_args
    ):
        return pipe(
            data_frame,
            rpartial(
                combine_first, ["code", "index", "demographic_value"], "code"
            ),
            rpartial(
                combine_first,
                [
                    "code_count",
                    "count",
                    "sequence_type_count",
                    "test_type_count",
                    "variant_count",
                ],
                "count",
            ),
            rpartial(combine_first, ["display", "sequence_type"], "display"),
            iffy(
                lambda df: "summary" in df.columns,
                lambda df: df.assign(
                    summary=df.summary.str.replace(".counts", "", regex=False)
                ),
            ),
            rpartial(
                drop,
                [
                    "index",
                    "sequence_type_count",
                    "sequence_type",
                    "code_count",
                    "demographic_value",
                    "test_type_count",
                    "variant_count",
                ],
            ),
            iffy(
                lambda df: "summary" in df.columns and "count" in df.columns,
                lambda df: df.sort_values(
                    ["summary", "count"], ascending=False
                ),
            ),
            iffy(
                lambda df: include_demographics is False
                and "summary" in df.columns,
                lambda df: df[~df.summary.str.contains("demographic")],
            ),
        ).reset_index(drop=True)

    @classmethod
    def get_data_frame(
        cls,
        include_demographics: bool = False,
        all_results: bool = True,
        auth_args: Auth = Auth.shared(),
        max_pages: Optional[int] = None,
        page_size: Optional[int] = None,
        log: bool = False,
        **kw_args,
    ):
        """Execute a request for summary counts across clinical and omics data

        NOTE: By default, demographic data is excluded since it is not
        technically counts of entities. If demographics-only data is desired,
        use this:

        >>> from phc.easy.summary.item_counts import SummaryItemCounts
        >>> SummaryItemCounts.get_data_frame(summary="demographics")

        ## Parameters

        Execution: `phc.easy.query.Query.execute_paging_api`
        """

        # NOTE: include_demographics gets passed through to transform_results
        # since explicitly declared there.

        df = super().get_data_frame(
            **kw_args, **cls._get_current_args(inspect.currentframe(), locals())
        )

        return df
