from enum import Enum


class GenomicVariantInclude(str, Enum):
    ENSEMBL = "ensembl"
    VCF = "vcf"
    DRUG_ASSOCIATIONS = "drugAssociations"
