import inspect
import pandas as pd
from typing import List, Optional
from phc.easy.frame import Frame
from pydantic import Field
from phc.easy.auth import Auth
from phc.easy.paging_api_item import PagingApiItem, PagingApiOptions

from enum import Enum


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
    "drug_associations": "drugAssociations",
}


class GenomicShortVariantInclude(str, Enum):
    ENSEMBL = "ensembl"
    VCF = "vcf"
    DRUG_ASSOCIATIONS = "drugAssociations"


class GenomicShortVariantOptions(PagingApiOptions):
    """Options to pass to `/v1/genomics/variants`

    See https://docs.us.lifeomic.com/api/#query-short-variant-data
    """

    variant_set_ids: List[str] = Field(..., min_items=1)
    include: List[GenomicShortVariantInclude] = ["vcf"]
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
    group: List[str] = []
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
    drug_associations: Optional[bool]

    @staticmethod
    def transform(key, value):
        if key not in ["drug_associations"]:
            value = ",".join(value)

        return (MAPPINGS.get(key, key), value)


class GenomicShortVariant(PagingApiItem):
    @staticmethod
    def resource_path():
        return "genomics/variants"

    @staticmethod
    def params_class():
        return GenomicShortVariantOptions

    @staticmethod
    def transform_results(data_frame: pd.DataFrame, **expand_args):
        args = {
            **expand_args,
            "custom_columns": [
                *expand_args.get("custom_columns", []),
                *[
                    Frame.codeable_like_column_expander(k)
                    for k in ["clinvar", "cosmic", "vcf"]
                ],
            ],
        }

        return Frame.expand(data_frame, **args)

    @classmethod
    def get_data_frame(
        cls,
        # Query parameters
        variant_set_ids: List[str],
        include: List[GenomicShortVariantInclude] = ["vcf"],
        gene: List[str] = [],
        rsid: List[str] = [],
        chromosome: List[str] = [],
        clinvar_allele_id: List[str] = [],
        clinvar_disease: List[str] = [],
        clinvar_review: List[str] = [],
        clinvar_significance: List[str] = [],
        cosmic_id: List[str] = [],
        cosmic_status: List[str] = [],
        cosmic_histology: List[str] = [],
        cosmic_tumor_site: List[str] = [],
        variant_class: List[str] = [],
        group: List[str] = [],
        impact: List[str] = [],
        transcript_id: List[str] = [],
        biotype: List[str] = [],
        amino_acid_change: List[str] = [],
        sequence_type: List[str] = [],
        position: List[str] = [],
        cosmic_sample_count: List[str] = [],
        min_allele_frequency: List[str] = [],
        max_allele_frequency: List[str] = [],
        pop_allele_frequency: List[str] = [],
        exac_allele_frequency: List[str] = [],
        exac_homozygous: List[str] = [],
        dbnsfp_damaging_count: List[str] = [],
        dbnsfp_damaging_predictor: List[str] = [],
        dbnsfp_damaging_vote: List[str] = [],
        dbnsfp_fathmm_rankscore: List[str] = [],
        dbnsfp_fathmm_pred: List[str] = [],
        dbnsfp_mean_rankscore: List[str] = [],
        dbnsfp_mean_rankscore_predictor: List[str] = [],
        dbnsfp_mutationtaster_rankscore: List[str] = [],
        dbnsfp_mutationtaster_pred: List[str] = [],
        dbnsfp_sift_rankscore: List[str] = [],
        dbnsfp_sift_pred: List[str] = [],
        zygosity: List[str] = [],
        genotype: List[str] = [],
        variant_allele_frequency: List[str] = [],
        quality: List[str] = [],
        read_depth: List[str] = [],
        alt_read_depth: List[str] = [],
        ref_read_depth: List[str] = [],
        variant_filter: List[str] = [],
        drug_associations: Optional[bool] = None,
        # Execution parameters,
        all_results: bool = False,
        auth_args: Auth = Auth.shared(),
        max_pages: Optional[int] = None,
        page_size: Optional[int] = None,
        log: bool = False,
        **kw_args,
    ):
        """Execute a request for genomic short variants

        ## Parameters

        Query: `GenomicShortVariantOptions`

        Execution: `phc.easy.query.Query.execute_paging_api`

        Expansion: `phc.easy.frame.Frame.expand`

        NOTE:
         - `variant_class` is translated to `class` as a parameter
         - `variant_filter` is translated to `filter` as a parameter
        """
        return super().get_data_frame(
            **kw_args, **cls._get_current_args(inspect.currentframe(), locals())
        )
