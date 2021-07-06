from enum import Enum
from typing import List, Optional, Union

from phc.easy.abstract.paging_api_item import PagingApiOptions


class SummarySearchMatchOption(str, Enum):
    FUZZY = "fuzzy"
    EXACT = "exact"


class SummaryClinicalCountsOptions(PagingApiOptions):
    match: Optional[SummarySearchMatchOption]
    code: Optional[Union[str, List[str]]]
    display: Optional[Union[str, List[str]]]
    system: Optional[Union[str, List[str]]]

    @classmethod
    def transform(cls, key, value):
        CODE_ATTRS = ["code", "display", "system"]

        if (
            key in CODE_ATTRS
            and isinstance(value, list)
            and any(filter(lambda v: "," in v, value))
        ):
            raise ValueError("Commas are not supported when searching codes")

        if key in CODE_ATTRS and isinstance(value, str):
            return (key + "s", value)

        if key in CODE_ATTRS and isinstance(value, list):
            return (key + "s", ",".join(value))

        return (key, value)
