from enum import Enum


class StructuralType(str, Enum):
    FUSION = "fusion"
    NEAR_FUSION = "near_fusion"
    RNA_FUSION = "rna_fusion"
    RNA_FUSION_TRANSCRIPT = "rna_fusion_transcript"
    REARRANGEMENT = "rearrangement"
    TRUNCATION = "truncation"
    TRANSLOCATION = "translocation"
    INVERSION = "inversion"
    INTERRUPTION = "interruption"
    DELETION = "deletion"
    DUPLICATION = "duplication"
