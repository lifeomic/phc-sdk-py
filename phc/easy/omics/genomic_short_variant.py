import inspect
import math
from typing import List, Optional, Union

import pandas as pd
from phc.easy.auth import Auth
from phc.easy.frame import Frame
from phc.easy.omics.options.coding_effect import CodingEffect
from phc.easy.omics.options.chromosome import Chromosome
from phc.easy.omics.options.clinvar_significance import ClinVarSignificance
from phc.easy.omics.options.clinvar_review import ClinVarReview
from phc.easy.omics.options.gene_class import GeneClass
from phc.easy.omics.options.zygosity import Zygosity
from phc.easy.omics.options.genomic_test import (
    GenomicTestStatus,
    GenomicTestType,
)
from phc.easy.omics.options.common import GenomicVariantInclude
from phc.easy.omics.options.genomic_short_variant import (
    GenomicShortVariantOptions,
)
from phc.easy.abstract.genomic_variant import GenomicVariant
from phc.easy.util import split_by
from phc.easy.util.batch import batch_get_frame


class GenomicShortVariant(GenomicVariant):
    @staticmethod
    def resource_path():
        return "genomics/variants"

    @staticmethod
    def params_class():
        return GenomicShortVariantOptions

    @staticmethod
    def transform_results(data_frame: pd.DataFrame, params={}, **expand_args):
        def expand_id(id_column: pd.Series):
            return pd.concat(
                [
                    id_column,
                    id_column.str.split(":", expand=True).rename(
                        columns={0: "variant_set_id", 2: "gene"}
                    )[["variant_set_id", "gene"]],
                ],
                axis=1,
            )

        args = {
            **expand_args,
            "custom_columns": [
                *expand_args.get("custom_columns", []),
                *[
                    Frame.codeable_like_column_expander(k)
                    for k in [
                        "clinvar",
                        "cosmic",
                        "vcf",
                        "ensemblCanon",
                        "dbnsfp",
                    ]
                ],
                ("id", expand_id),
            ],
        }

        return Frame.expand(data_frame, **args)

    @classmethod
    def get_data_frame(
        cls,
        # Query parameters
        variant_set_ids: List[str] = [],
        include: List[GenomicVariantInclude] = ["vcf"],
        gene: List[str] = [],
        rs_id: List[str] = [],
        chromosome: List[Chromosome] = [],
        clinvar_allele_id: List[str] = [],
        clinvar_disease: List[str] = [],
        clinvar_review: List[ClinVarReview] = [],
        clinvar_significance: List[ClinVarSignificance] = [],
        cosmic_id: List[str] = [],
        cosmic_status: List[str] = [],
        cosmic_histology: List[str] = [],
        cosmic_tumor_site: List[str] = [],
        variant_class: List[str] = [],
        coding_effect: List[CodingEffect] = [],
        impact: List[str] = [],
        transcript_id: List[str] = [],
        gene_class: List[GeneClass] = [],
        protein_changes: List[str] = [],
        sequence_type: List[str] = [],
        position: List[Union[str, int]] = [],
        cosmic_min_count: Optional[int] = None,
        min_allele_frequency: Optional[str] = None,
        max_allele_frequency: Optional[str] = None,
        pop_allele_frequency: Optional[str] = None,
        exac_allele_frequency: Optional[str] = None,
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
        zygosity: List[Zygosity] = [],
        genotype: List[str] = [],
        variant_allele_frequency: List[str] = [],
        quality: List[str] = [],
        read_depth: List[str] = [],
        alt_read_depth: List[str] = [],
        ref_read_depth: List[str] = [],
        variant_filter: List[str] = [],
        in_ckb: Optional[bool] = None,
        # Test parameters
        patient_id: Optional[str] = None,
        test_status: Optional[GenomicTestStatus] = GenomicTestStatus.ACTIVE,
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

        Query: `phc.easy.omics.options.genomic_short_variant.GenomicShortVariantOptions`

        Execution: `phc.easy.query.Query.execute_paging_api`

        Expansion: `phc.easy.frame.Frame.expand`

        NOTE:
         - `variant_class` is translated to `class` as a parameter
         - `variant_filter` is translated to `filter` as a parameter
        """

        args = cls._get_current_args(inspect.currentframe(), locals())

        return super().get_data_frame(
            test_type=GenomicTestType.SHORT_VARIANT, **{**kw_args, **args}
        )
