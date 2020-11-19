import inspect
from typing import List, Optional
import pandas as pd

from phc.easy.auth import Auth
from phc.easy.frame import Frame
from phc.easy.omics.options.common import GenomicVariantInclude
from phc.easy.omics.options.copy_number_status import CopyNumberStatus
from phc.easy.omics.genomic_test import GenomicTestStatus, GenomicTestType
from phc.easy.omics.options.genomic_copy_number_variant import (
    GenomicCopyNumberVariantOptions,
)
from phc.easy.abstract.genomic_variant import GenomicVariant


class GenomicCopyNumberVariant(GenomicVariant):
    @staticmethod
    def resource_path():
        return "genomics/copy-numbers"

    @staticmethod
    def params_class():
        return GenomicCopyNumberVariantOptions

    @staticmethod
    def transform_results(data_frame: pd.DataFrame, params={}, **expand_args):
        def expand_id(id_column: pd.Series):
            return pd.concat(
                [
                    id_column,
                    id_column.str.split(":", expand=True).rename(
                        columns={0: "variant_set_id"}
                    )["variant_set_id"],
                ],
                axis=1,
            )

        args = {
            **expand_args,
            "custom_columns": [
                *expand_args.get("custom_columns", []),
                ("id", expand_id),
            ],
        }

        return Frame.expand(data_frame, **args)

    @classmethod
    def get_data_frame(
        cls,
        # Query parameters
        variant_set_ids: List[str] = [],
        include: List[GenomicVariantInclude] = [],
        gene: List[str] = [],
        interpretation: List[str] = [],
        effect: List[CopyNumberStatus] = [],
        in_ckb: Optional[bool] = None,
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
        """Execute a request for genomic copy number variants

        ## Parameters

        Query: `phc.easy.omics.options.genomic_copy_number_variant.GenomicCopyNumberVariantOptions`

        Execution: `phc.easy.query.Query.execute_paging_api`

        Expansion: `phc.easy.frame.Frame.expand`
        """

        args = cls._get_current_args(inspect.currentframe(), locals())

        return super().get_data_frame(
            test_type=GenomicTestType.COPY_NUMBER_VARIANT, **{**kw_args, **args}
        )
