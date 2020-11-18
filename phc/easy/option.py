from phc.easy.omics.options.coding_effect import CodingEffect
from phc.easy.omics.options.common import GenomicVariantInclude
from phc.easy.omics.options.genomic_copy_number_variant import (
    GenomicCopyNumberVariantOptions,
)
from phc.easy.omics.options.genomic_short_variant import (
    GenomicShortVariantOptions,
)
from phc.easy.omics.options.genomic_test import (
    GenomicTestType,
    GenomicTestStatus,
)


class Option:
    """Class that references all available API options"""

    GenomicVariantInclude = GenomicVariantInclude
    GenomicCopyNumberVariantOptions = GenomicCopyNumberVariantOptions
    GenomicShortVariantOptions = GenomicShortVariantOptions
    GenomicTestType = GenomicTestType
    GenomicTestStatus = GenomicTestStatus
    CodingEffect = CodingEffect
