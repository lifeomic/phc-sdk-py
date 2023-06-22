import inspect
from typing import List, Optional, Union

from phc.easy.abstract.paging_api_item import PagingApiItem
from phc.easy.auth import Auth
from phc.easy.summary.counts import SummaryCounts
from phc.easy.summary.options.clinical_counts import (
    SummaryClinicalCountsOptions,
    SummarySearchMatchOption,
)


class SummaryClinicalCounts(PagingApiItem):
    @staticmethod
    def resource_path():
        return "analytics/summary/{project_id}/clinical/codified/counts"

    @staticmethod
    def execute_args() -> dict:
        return SummaryCounts.execute_args()

    @staticmethod
    def params_class():
        return SummaryClinicalCountsOptions

    @classmethod
    def get_data_frame(
        cls,
        all_results: bool = True,
        auth_args: Auth = Auth.shared(),
        max_pages: Optional[int] = None,
        page_size: Optional[int] = None,
        log: bool = False,
        match: Optional[SummarySearchMatchOption] = None,
        code: Optional[Union[str, List[str]]] = None,
        display: Optional[Union[str, List[str]]] = None,
        system: Optional[Union[str, List[str]]] = None,
        **kw_args,
    ):
        """Execute a request for summary counts across clinical data

        >>> from phc.easy.summary.clinical_counts import SummaryClinicalCountsOptions
        >>> SummaryClinicalCountsOptions.get_data_frame(match="fuzzy", display="sleep")

        ## Parameters

        Execution: `phc.easy.query.Query.execute_paging_api`
        """

        df = super().get_data_frame(
            **kw_args, **cls._get_current_args(inspect.currentframe(), locals())
        )

        return df
