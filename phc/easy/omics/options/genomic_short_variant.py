from enum import Enum
from typing import List, Optional

from phc.easy.omics.options.coding_effect import CodingEffect
from phc.easy.omics.options.common import GenomicVariantInclude
from phc.easy.abstract.paging_api_item import PagingApiOptions
from pydantic import Field

MAPPINGS = {
    "variant_set_ids": "variantSetIds",
    "clinvar_allele_id": "clinvarAlleleId",
    "clinvar_disease": "clinvarDisease",
    "clinvar_review": "clinvarReview",
    "clinvar_significance": "clinvarSignificance",
    "cosmic_id": "cosmicId",
    "cosmic_status": "cosmicStatus",
    "cosmic_histology": "cosmicHistology",
    "cosmic_tumor_site": "cosmicTumorSite",
    "coding_effect": "group",
    "variant_class": "class",
    "transcript_id": "transcriptId",
    "amino_acid_change": "aminoAcidChange",
    "sequence_type": "sequenceType",
    "cosmic_sample_count": "cosmicSampleCount",
    "min_allele_frequency": "minAlleleFrequency",
    "max_allele_frequency": "maxAlleleFrequency",
    "pop_allele_frequency": "popAlleleFrequency",
    "exac_allele_frequency": "exacAlleleFrequency",
    "exac_homozygous": "exacHomozygous",
    "dbnsfp_damaging_count": "dbnsfpDamagingCount",
    "dbnsfp_damaging_predictor": "dbnsfpDamagingPredictor",
    "dbnsfp_damaging_vote": "dbnsfpDamagingVote",
    "dbnsfp_fathmm_rankscore": "dbnsfpFathmmRankscore",
    "dbnsfp_fathmm_pred": "dbnsfpFathmmPred",
    "dbnsfp_mean_rankscore": "dbnsfpMeanRankscore",
    "dbnsfp_mean_rankscore_predictor": "dbnsfpMeanRankscorePredictor",
    "dbnsfp_mutationtaster_rankscore": "dbnsfpMutationtasterRankscore",
    "dbnsfp_mutationtaster_pred": "dbnsfpMutationtasterPred",
    "dbnsfp_sift_rankscore": "dbnsfpSiftRankscore",
    "dbnsfp_sift_pred": "dbnsfpSiftPred",
    "variant_allele_frequency": "variantAlleleFrequency",
    "read_depth": "readDepth",
    "alt_read_depth": "altReadDepth",
    "ref_read_depth": "refReadDepth",
    "variant_filter": "filter",
    "in_ckb": "drugAssociations",
}


class GenomicShortVariantOptions(PagingApiOptions):
    """Options to pass to `/v1/genomics/variants`

    See https://docs.us.lifeomic.com/api/#query-short-variant-data
    """

    variant_set_ids: List[str] = Field(..., min_items=1)
    include: List[GenomicVariantInclude] = ["vcf"]
    gene: List[str] = []
    rsid: List[str] = []
    chromosome: List[str] = []
    clinvar_allele_id: List[str] = []
    clinvar_disease: List[str] = []
    clinvar_review: List[str] = []
    clinvar_significance: List[str] = []
    cosmic_id: List[str] = []
    cosmic_status: List[str] = []
    cosmic_histology: List[str] = []
    cosmic_tumor_site: List[str] = []
    variant_class: List[str] = []  # Renamed from 'class'
    coding_effect: List[CodingEffect] = []
    impact: List[str] = []
    transcript_id: List[str] = []
    biotype: List[str] = []
    amino_acid_change: List[str] = []
    sequence_type: List[str] = []
    position: List[str] = []
    cosmic_sample_count: List[str] = []
    min_allele_frequency: List[str] = []
    max_allele_frequency: List[str] = []
    pop_allele_frequency: List[str] = []
    exac_allele_frequency: List[str] = []
    exac_homozygous: List[str] = []
    dbnsfp_damaging_count: List[str] = []
    dbnsfp_damaging_predictor: List[str] = []
    dbnsfp_damaging_vote: List[str] = []
    dbnsfp_fathmm_rankscore: List[str] = []
    dbnsfp_fathmm_pred: List[str] = []
    dbnsfp_mean_rankscore: List[str] = []
    dbnsfp_mean_rankscore_predictor: List[str] = []
    dbnsfp_mutationtaster_rankscore: List[str] = []
    dbnsfp_mutationtaster_pred: List[str] = []
    dbnsfp_sift_rankscore: List[str] = []
    dbnsfp_sift_pred: List[str] = []
    zygosity: List[str] = []
    genotype: List[str] = []
    variant_allele_frequency: List[str] = []
    quality: List[str] = []
    read_depth: List[str] = []
    alt_read_depth: List[str] = []
    ref_read_depth: List[str] = []
    variant_filter: List[str] = []
    in_ckb: Optional[bool]

    @staticmethod
    def transform(key, value):
        if isinstance(value, list):
            value = ",".join(value)
        elif isinstance(value, bool):
            value = "true" if value else None

        return (MAPPINGS.get(key, key), value)
