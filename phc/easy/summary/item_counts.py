import inspect
from typing import Optional, Union

import pandas as pd
from phc.easy.abstract.paging_api_item import PagingApiItem
from phc.easy.auth import Auth
from phc.easy.summary.options.item_counts import (
    SummaryClinicalType,
    SummaryItemCountsOptions,
    SummaryOmicsType,
)


class SummaryItemCounts(PagingApiItem):
    @staticmethod
    def resource_path():
        return "analytics/summary/{project_id}/{summary_type}/{summary}/counts"

    @classmethod
    def process_params(cls, params: dict) -> dict:
        new_params = cls.params_class()(**params).dict()

        if SummaryClinicalType.has_value(new_params["summary"]):
            return {**new_params, "summary_type": "clinical"}
        elif SummaryOmicsType.has_value(new_params["summary"]):
            return {**new_params, "summary_type": "omics"}

        # Unknown summary_type
        return None

    @staticmethod
    def transform_results(data_frame: pd.DataFrame, **expand_args):
        if len(data_frame) == 0:
            return data_frame

        if expand_args.get("params", {}).get("summary") == "demographic":
            # Sort demographics results in a nice way
            return data_frame.sort_values(
                ["demographic_name", "count"], ascending=False
            ).reset_index(drop=True)

        if (
            "code_count" in data_frame.columns
            and "patient_count" in data_frame.columns
        ):
            return data_frame.sort_values(
                ["code_count", "patient_count"], ascending=False
            )

        return data_frame

    @staticmethod
    def execute_args() -> dict:
        return dict(ignore_cache=True)

    @staticmethod
    def params_class():
        return SummaryItemCountsOptions

    @classmethod
    def get_data_frame(
        cls,
        summary: Union[SummaryOmicsType, SummaryClinicalType],
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

        df = super().get_data_frame(
            **kw_args, **cls._get_current_args(inspect.currentframe(), locals())
        )

        return df
