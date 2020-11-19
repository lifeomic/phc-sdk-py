from typing import List, Optional
from pydantic import Field
from phc.easy.abstract.paging_api_item import PagingApiOptions
from phc.easy.omics.options.common import GenomicVariantInclude
from phc.easy.omics.options.structural_type import StructuralType
from phc.easy.omics.options.in_frame import InFrame

MAPPINGS = {
    "variant_set_ids": "structuralVariantSetIds",
    "effect": "type",
    "in_frame": "inFrame",
    "in_ckb": "drugAssociations",
}


class GenomicStructuralVariantOptions(PagingApiOptions):
    variant_set_ids: List[str] = Field(..., min_items=1)
    gene: List[str] = []
    effect: List[StructuralType] = []
    interpretation: List[str] = []
    in_frame: List[InFrame] = []
    in_ckb: Optional[bool] = None
    include: List[GenomicVariantInclude] = []

    @staticmethod
    def transform(key, value):
        if isinstance(value, list):
            value = ",".join(
                [elem if isinstance(elem, str) else str(elem) for elem in value]
            )
        elif isinstance(value, bool):
            value = "true" if value else None

        return (MAPPINGS.get(key, key), value)
