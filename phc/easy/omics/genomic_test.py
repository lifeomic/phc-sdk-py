import inspect
from enum import Enum
from typing import Optional

import pandas as pd
from phc.easy.auth import Auth
from phc.easy.frame import Frame
from phc.easy.omics.options.genomic_test import (
    GenomicTestStatus,
    GenomicTestType,
)
from phc.easy.abstract.paging_api_item import PagingApiItem, PagingApiOptions


class GenomicTestOptions(PagingApiOptions):
    """Options to pass to `/v1/genomics/projects/{project_id}/tests`"""

    patient_id: Optional[str]
    status: Optional[GenomicTestStatus]
    test_type: Optional[GenomicTestType]

    @staticmethod
    def transform(key, value):
        new_key = {"patient_id": "patientId", "test_type": "type"}.get(key, key)

        return (new_key, value)


class GenomicTest(PagingApiItem):
    @staticmethod
    def resource_path():
        return "genomics/projects/{project_id}/tests"

    @staticmethod
    def params_class():
        return GenomicTestOptions

    @staticmethod
    def transform_results(
        data_frame: pd.DataFrame, params: dict, **expand_args
    ):
        args = {
            **expand_args,
            "code_columns": [
                *expand_args.get("code_columns", []),
                "bodySite",
                "patient",
            ],
            "custom_columns": [
                *expand_args.get("custom_columns", []),
                Frame.codeable_like_column_expander("sourceFile"),
            ],
        }
        df = Frame.expand(data_frame, **args)

        if "sets" in df.columns:
            df = (
                pd.concat(
                    data_frame.apply(
                        lambda x: pd.DataFrame(
                            [{"index": x.name, **s} for s in x.sets]
                        ),
                        axis=1,
                    ).values
                )
                .join(df.drop(["sets"], axis=1), on="index", rsuffix=".test")
                .drop(["index"], axis=1)
                .reset_index(drop=True)
            )

        test_type = params.get("type", None)

        if test_type and len(df) > 0:
            # TODO: Remove when API fixed

            # NOTE: The API does not filter the returned sets because it is a
            # nested structure. Since it's not a boatload of information, we opt
            # to filter client-side for now.
            return df[df.setType == test_type].reset_index(drop=True)

        return df

    @classmethod
    def get_data_frame(
        cls,
        patient_id: Optional[str] = None,
        status: Optional[GenomicTestStatus] = GenomicTestStatus.ACTIVE,
        test_type: Optional[GenomicTestType] = None,
        all_results: bool = False,
        auth_args: Auth = Auth.shared(),
        max_pages: Optional[int] = None,
        page_size: Optional[int] = None,
        log: bool = False,
        ignore_cache: bool = False,
        **kw_args,
    ):
        """Execute a request for genomic tests

        ## Parameters

        Query: `phc.easy.omics.options.genomic_test.GenomicTestOptions`

        Execution: `phc.easy.query.Query.execute_paging_api`

        Expansion: `phc.easy.frame.Frame.expand`

        NOTE: `test_type` is translated to `type` as a parameter
        """
        df = super().get_data_frame(
            **kw_args, **cls._get_current_args(inspect.currentframe(), locals())
        )

        return df
