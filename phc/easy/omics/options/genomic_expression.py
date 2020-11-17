from enum import Enum
from typing import List, Optional

from phc.easy.abstract.paging_api_item import PagingApiOptions
from phc.easy.omics.options.common import GenomicVariantInclude
from pydantic import Field

MAPPINGS = {
    "variant_set_ids": "rnaQuantificationSetIds",
    "outlier_std_dev": "outlierStdDev",
    "drug_associations": "drugAssociations",
}


class GenomicExpressionOptions(PagingApiOptions):
    """Options to pass to `/v1/genomics/expressions`

    See https://docs.us.lifeomic.com/api/#query-expression-data
    """

    variant_set_ids: List[str] = Field(..., min_items=1)
    include: List[GenomicVariantInclude] = []
    gene: List[str] = []
    outlier_std_dev: Optional[str]
    drug_associations: Optional[bool]

    @staticmethod
    def transform(key, value):
        if key not in ["drug_associations", "outlier_std_dev"]:
            value = ",".join(value)

        return (MAPPINGS.get(key, key), value)
