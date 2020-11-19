import inspect
from typing import List, Optional

import pandas as pd
from phc.easy.auth import Auth
from phc.easy.frame import Frame
from phc.easy.abstract.genomic_variant import GenomicVariant
from phc.easy.omics.options.genomic_test import (
    GenomicTestStatus,
    GenomicTestType,
)
from phc.easy.omics.options.common import GenomicVariantInclude
from phc.easy.omics.options.genomic_expression import GenomicExpressionOptions
from phc.easy.abstract.paging_api_item import PagingApiItem


class GenomicExpression(GenomicVariant):
    @staticmethod
    def resource_path():
        return "genomics/expressions"

    @staticmethod
    def params_class():
        return GenomicExpressionOptions

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
        expression: Optional[str] = None,
        outlier_std_dev: str = None,
        in_ckb: Optional[bool] = None,
        order_by: Optional[str] = None,
        # Execution parameters,
        all_results: bool = False,
        auth_args: Auth = Auth.shared(),
        max_pages: Optional[int] = None,
        page_size: Optional[int] = None,
        log: bool = False,
        **kw_args,
    ):
        """Execute a request for genomic expression

        ## Parameters

        Query: `phc.easy.omics.options.genomic_expression.GenomicExpressionOptions`

        Execution: `phc.easy.query.Query.execute_paging_api`

        Expansion: `phc.easy.frame.Frame.expand`

        """

        args = cls._get_current_args(inspect.currentframe(), locals())

        return super().get_data_frame(
            test_type=GenomicTestType.EXPRESSION, **{**kw_args, **args}
        )
