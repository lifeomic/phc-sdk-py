from enum import Enum
from typing import List, Optional, Union
from pydantic import Field, constr

from phc.easy.abstract.paging_api_item import PagingApiOptions
from phc.easy.omics.options.common import GenomicVariantInclude

EXPRESSION = constr(
    regex=r"^(\d+(\.\d+)?\-\d+(\.\d+)?|[\>\<]\=\s?\d+(\.\d+)?|\d+(\.\d+)?:(lte|gte))$"
)

ORDER_BY = constr(regex=r"^expression(:desc)?$")

MAPPINGS = {
    "variant_set_ids": "rnaQuantificationSetIds",
    "outlier_std_dev": "outlierStdDev",
    "in_ckb": "drugAssociations",
    "order_by": "orderBy",
}


class GenomicExpressionOptions(PagingApiOptions):
    """Options to pass to `/v1/genomics/expressions`"""

    variant_set_ids: List[str] = Field(..., min_items=1)
    include: List[GenomicVariantInclude] = []
    gene: List[str] = []
    expression: Optional[EXPRESSION] = None
    order_by: Optional[ORDER_BY] = None
    in_ckb: Optional[bool] = None
    # TODO: Fill out allowed options for this parameter
    outlier_std_dev: Optional[str] = None

    @staticmethod
    def transform(key, value):
        if key == "expression" and value is not None:
            value = GenomicExpressionOptions.transform_expression(value)

        if isinstance(value, list):
            value = ",".join(
                [elem if isinstance(elem, str) else str(elem) for elem in value]
            )
        elif isinstance(value, bool):
            value = "true" if value else None

        return (MAPPINGS.get(key, key), value)

    @staticmethod
    def transform_expression(value: str):
        value = value.replace(" ", "")

        if ">=" in value:
            return value.replace(">=", "") + ":gte"

        if "<=" in value:
            return value.replace("<=", "") + ":lte"

        return value
