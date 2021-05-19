import inspect
from typing import Optional
import pandas as pd
from funcy import first, lmapcat
from phc.easy.auth import Auth
from phc.easy.abstract.paging_api_item import PagingApiItem
from phc.easy.summary.counts import NoOptions, SummaryCounts


class SummaryOmicsCounts(PagingApiItem):
    @staticmethod
    def resource_path():
        return "analytics/summary/{project_id}/omics"

    @staticmethod
    def response_to_items(data):
        # Common functionality with SummaryCounts since pd.json_normalize squashes nested keys until nested arrays encountered
        return SummaryCounts.response_to_items(data)

    @staticmethod
    def transform_results(data_frame: pd.DataFrame, **expand_args):
        return SummaryCounts.transform_results(
            data_frame,
            # Omics doesn't include demographics
            include_demographics=False,
            **expand_args,
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
        all_results: bool = True,
        auth_args: Auth = Auth.shared(),
        max_pages: Optional[int] = None,
        page_size: Optional[int] = None,
        log: bool = False,
        **kw_args,
    ):
        """Execute a request for summary counts across omics data

        ## Parameters

        Execution: `phc.easy.query.Query.execute_paging_api`
        """

        df = super().get_data_frame(
            **kw_args, **cls._get_current_args(inspect.currentframe(), locals())
        )

        return df
