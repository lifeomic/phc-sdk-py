import inspect
from typing import List, Optional

import pandas as pd
from phc.easy.auth import Auth
from phc.easy.frame import Frame
from phc.easy.abstract.genomic_variant import GenomicVariant
from phc.easy.omics.options.genomic_test import GenomicTestType
from phc.easy.omics.options.genomic_structural_variant import (
    GenomicStructuralVariantOptions,
)
from phc.easy.omics.options.structural_type import StructuralType
from phc.easy.omics.options.in_frame import InFrame
from phc.easy.omics.options.common import GenomicVariantInclude


class GenomicStructuralVariant(GenomicVariant):
    @staticmethod
    def resource_path():
        return "genomics/structural-variants"

    @staticmethod
    def params_class():
        return GenomicStructuralVariantOptions

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
        gene: List[str] = [],
        effect: List[StructuralType] = [],
        interpretation: List[str] = [],
        in_frame: List[InFrame] = [],
        in_ckb: Optional[bool] = None,
        include: List[GenomicVariantInclude] = [],
        # Execution parameters,
        all_results: bool = False,
        auth_args: Auth = Auth.shared(),
        max_pages: Optional[int] = None,
        page_size: Optional[int] = None,
        log: bool = False,
        **kw_args,
    ):
        """Execute a request for genomic structural variants

        ## Parameters

        Query: `phc.easy.omics.options.genomic_structural_variant.GenomicStructuralVariantOptions`

        Execution: `phc.easy.query.Query.execute_paging_api`

        Expansion: `phc.easy.frame.Frame.expand`

        """

        args = cls._get_current_args(inspect.currentframe(), locals())

        return super().get_data_frame(
            test_type=GenomicTestType.STRUCTURAL_VARIANT, **{**kw_args, **args}
        )
