from phc.easy.omics.options.coding_effect import CodingEffect
from phc.easy.omics.options.chromosome import Chromosome
from phc.easy.omics.options.clinvar_significance import ClinVarSignificance
from phc.easy.omics.options.clinvar_review import ClinVarReview
from phc.easy.omics.options.gene_class import GeneClass
from phc.easy.omics.options.zygosity import Zygosity
from phc.easy.omics.options.common import GenomicVariantInclude
from phc.easy.omics.options.copy_number_status import CopyNumberStatus
from phc.easy.omics.options.in_frame import InFrame
from phc.easy.omics.options.structural_type import StructuralType
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
    Chromosome = Chromosome
    ClinVarSignificance = ClinVarSignificance
    ClinVarReview = ClinVarReview
    GeneClass = GeneClass
    Zygosity = Zygosity
    CopyNumberStatus = CopyNumberStatus
    InFrame = InFrame
    StructuralType = StructuralType
