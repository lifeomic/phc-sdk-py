from enum import Enum
from typing import List, Optional

from phc.easy.omics.options.common import GenomicVariantInclude
from phc.easy.abstract.paging_api_item import PagingApiOptions
from pydantic import Field

MAPPINGS = {
    "variant_set_ids": "copyNumberSetIds",
    "drug_associations": "drugAssociations",
}


class GenomicCopyNumberVariantOptions(PagingApiOptions):
    """Options to pass to `/v1/genomics/copy-numbers`

    See https://docs.us.lifeomic.com/api/#query-copy-number-data
    """

    variant_set_ids: List[str] = Field(..., min_items=1)
    include: List[GenomicVariantInclude] = []
    gene: List[str] = []
    interpretation: List[str] = []
    status: List[str] = []
    drug_associations: Optional[bool]

    @staticmethod
    def transform(key, value):
        if key not in ["drug_associations"]:
            value = ",".join(value)

        return (MAPPINGS.get(key, key), value)
