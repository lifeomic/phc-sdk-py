import inspect
import math
from typing import List, Optional

import pandas as pd
from phc.easy.auth import Auth
from phc.easy.omics.options.genomic_test import (
    GenomicTestStatus,
    GenomicTestType,
)
from phc.easy.omics.genomic_test import GenomicTest
from phc.easy.abstract.paging_api_item import PagingApiItem
from phc.easy.util import tqdm, split_by, rename_keys
from phc.easy.util.batch import batch_get_frame

MAX_VARIANT_SET_IDS = 100


class GenomicVariant(PagingApiItem):
    @staticmethod
    def _get_genomic_tests(
        variant_set_ids: List[str],
        max_pages: Optional[int],
        all_results: bool,
        auth_args: Auth,
        log: bool,
        **test_args,
    ):
        test_args = rename_keys(test_args, {"test_status": "status"})
        test_df = pd.DataFrame()
        args = {}

        if (
            len(variant_set_ids) == 0
            and max_pages is None
            and all_results is False
        ):
            print("Using sample of 25 tests")
            args = {
                **test_args,
                "page_size": 25,
                "max_pages": 1,
                "log": log,
                "auth_args": auth_args,
            }
            test_df = GenomicTest.get_data_frame(**args)
        elif len(variant_set_ids) == 0:
            args = {
                **test_args,
                "page_size": 100,
                "all_results": True,
                "log": log,
                "auth_args": auth_args,
            }
            test_df = GenomicTest.get_data_frame(**args)
        else:
            test_df["id"] = variant_set_ids

        return test_df

    @classmethod
    def get_data_frame(
        cls,
        test_type: GenomicTestType,
        # Query parameters
        variant_set_ids: List[str] = [],
        # Test parameters
        patient_id: Optional[str] = None,
        test_status: Optional[GenomicTestStatus] = GenomicTestStatus.ACTIVE,
        # Execution parameters,
        all_results: bool = False,
        auth_args: Auth = Auth.shared(),
        max_pages: Optional[int] = None,
        page_size: Optional[int] = None,
        log: bool = False,
        **kw_args,
    ):
        """Execute a request for genomic variants

        ## Parameters

        Execution: `phc.easy.query.Query.execute_paging_api`

        Expansion: `phc.easy.frame.Frame.expand`
        """
        test_params = ["patient_id", "status"]

        test_args, args = split_by(
            cls._get_current_args(inspect.currentframe(), locals()),
            left_keys=test_params,
        )

        test_df = cls._get_genomic_tests(
            variant_set_ids=variant_set_ids,
            all_results=all_results,
            test_type=test_type,
            page_size=page_size,
            max_pages=max_pages,
            log=log,
            auth_args=auth_args,
            **test_args,
        )
        args["variant_set_ids"] = variant_set_ids = list(test_df.id)

        if len(variant_set_ids) > MAX_VARIANT_SET_IDS and (
            max_pages or (not all_results and page_size)
        ):
            print(
                "[WARNING]: All result limit parameters are approximate when performing genomic data retrieval."
            )

        get_data_frame = super().get_data_frame

        def perform_batch(ids: List[str], total_thus_far: int):
            # Determine whether to skip this batch
            if (
                # Implement approximation of max_pages
                not all_results
                and max_pages
                and (total_thus_far >= max_pages * (page_size or 100))
            ) or (
                # Use 25 or page_size for a sample (when no max_pages)
                not all_results
                and not max_pages
                and total_thus_far >= (page_size or 25)
            ):
                return pd.DataFrame()

            has_multiple_batches = len(ids) != len(variant_set_ids)

            return get_data_frame(
                **kw_args,
                **{
                    **args,
                    "variant_set_ids": list(ids),
                    "all_results": all_results
                    # Scroll through full batches and then honor the max_pages param
                    or (has_multiple_batches and max_pages),
                },
            )

        variants = batch_get_frame(
            variant_set_ids, MAX_VARIANT_SET_IDS, perform_batch
        )

        if len(variants) == 0:
            variants["variant_set_id"] = math.nan

        return variants.join(
            test_df.set_index("id"), on="variant_set_id", rsuffix=".set"
        )
