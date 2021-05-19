import inspect
from typing import Optional

import pandas as pd
from phc.easy.abstract.paging_api_item import PagingApiItem
from phc.easy.auth import Auth
from phc.easy.summary.counts import NoOptions, SummaryCounts


class SummaryClinicalCounts(PagingApiItem):
    @staticmethod
    def resource_path():
        return "analytics/summary/{project_id}/clinical"

    @staticmethod
    def response_to_items(data):
        # Common functionality with SummaryCounts since pd.json_normalize
        # squashes nested keys until nested arrays encountered
        return SummaryCounts.response_to_items(data)

    @staticmethod
    def transform_results(
        data_frame: pd.DataFrame, include_demographics: bool, **expand_args
    ):
        return SummaryCounts.transform_results(
            data_frame, include_demographics, **expand_args
        )

    @staticmethod
    def execute_args() -> dict:
        return SummaryCounts.execute_args()

    @staticmethod
    def params_class():
        return NoOptions

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
        """Execute a request for summary counts across clinical data

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
