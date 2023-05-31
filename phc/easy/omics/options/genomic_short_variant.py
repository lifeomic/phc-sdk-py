from enum import Enum
from typing import List, Optional, Union

from phc.easy.omics.options.coding_effect import CodingEffect
from phc.easy.omics.options.chromosome import Chromosome
from phc.easy.omics.options.clinvar_significance import ClinVarSignificance
from phc.easy.omics.options.clinvar_review import ClinVarReview
from phc.easy.omics.options.gene_class import GeneClass
from phc.easy.omics.options.zygosity import Zygosity
from phc.easy.omics.options.common import GenomicVariantInclude
from phc.easy.abstract.paging_api_item import PagingApiOptions
from pydantic import Field, constr

RS_ID = r"^rs(\d+)$"
NUM_DECIMAL_RANGE = constr(regex=r"^\d+(\.\d+)?\-\d+(\.\d+)?$")
NUM_RANGE = constr(regex=r"^(\d+\-\d+|\d+)$")

MAPPINGS = {
    "variant_set_ids": "variantSetIds",
    "rs_id": "rsid",
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
    "gene_class": "biotype",
    "protein_changes": "aminoAcidChange",
    "sequence_type": "sequenceType",
    # Used cosmic_min_count instead to match PHC interface
    # "cosmic_sample_count": "cosmicSampleCount",
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
    """Options to pass to `/v1/genomics/variants`"""

    # TODO: Add remaining options from Omics Explorer in PHC
    # - Variant Quality
    # - Variant Allele Freq
    # - Combined In Silico Prediction
    # - Individual In Silico Predictors

    variant_set_ids: List[str] = Field(..., min_items=1)
    include: List[GenomicVariantInclude] = ["vcf"]
    gene: List[str] = []
    rs_id: List[constr(regex=RS_ID)] = []
    chromosome: List[Chromosome] = []
    clinvar_allele_id: List[str] = []
    clinvar_disease: List[str] = []
    clinvar_review: List[ClinVarReview] = []
    clinvar_significance: List[ClinVarSignificance] = []
    cosmic_id: List[str] = []
    cosmic_status: List[str] = []
    cosmic_histology: List[str] = []
    cosmic_tumor_site: List[str] = []
    variant_class: List[str] = []  # Renamed from 'class'
    coding_effect: List[CodingEffect] = []
    impact: List[str] = []
    transcript_id: List[str] = []
    gene_class: List[GeneClass] = []
    protein_changes: List[str] = []
    sequence_type: List[str] = []
    position: List[Union[int, NUM_RANGE]] = []
    cosmic_min_count: Optional[int] = None
    min_allele_frequency: Optional[NUM_DECIMAL_RANGE] = None
    max_allele_frequency: Optional[NUM_DECIMAL_RANGE] = None
    pop_allele_frequency: Optional[NUM_DECIMAL_RANGE] = None
    exac_allele_frequency: Optional[NUM_DECIMAL_RANGE] = None
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
    zygosity: List[Zygosity] = []
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
            value = ",".join(
                [elem if isinstance(elem, str) else str(elem) for elem in value]
            )
        elif isinstance(value, bool):
            value = "true" if value else None

        if key == "cosmic_min_count" and value is not None:
            return ("cosmicSampleCount", f"{value}:gte")

        return (MAPPINGS.get(key, key), value)
