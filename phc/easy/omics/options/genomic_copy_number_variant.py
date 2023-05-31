from enum import Enum
from typing import List, Optional

from phc.easy.omics.options.copy_number_status import CopyNumberStatus
from phc.easy.omics.options.common import GenomicVariantInclude
from phc.easy.abstract.paging_api_item import PagingApiOptions
from pydantic import Field

MAPPINGS = {
    "variant_set_ids": "copyNumberSetIds",
    "in_ckb": "drugAssociations",
    "effect": "status",
}


class GenomicCopyNumberVariantOptions(PagingApiOptions):
    """Options to pass to `/v1/genomics/copy-numbers`"""

    variant_set_ids: List[str] = Field(..., min_items=1)
    include: List[GenomicVariantInclude] = []
    gene: List[str] = []
    interpretation: List[str] = []
    effect: List[CopyNumberStatus] = []
    in_ckb: Optional[bool] = None

    @staticmethod
    def transform(key, value):
        if isinstance(value, list):
            value = ",".join(
                [elem if isinstance(elem, str) else str(elem) for elem in value]
            )
        elif isinstance(value, bool):
            value = "true" if value else None

        return (MAPPINGS.get(key, key), value)
