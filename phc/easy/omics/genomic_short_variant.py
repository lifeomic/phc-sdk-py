import inspect
import math
from typing import List, Optional

import pandas as pd
from phc.easy.auth import Auth
from phc.easy.frame import Frame
from phc.easy.omics.genomic_test import (
    GenomicTest,
    GenomicTestStatus,
    GenomicTestType,
)
from phc.easy.omics.options.genomic_short_variant import (
    GenomicShortVariantInclude,
    GenomicShortVariantOptions,
)
from phc.easy.abstract.paging_api_item import PagingApiItem
from phc.easy.util import tqdm, split_by
from phc.easy.util.batch import batch_get_frame

MAX_VARIANT_SET_IDS = 100


class GenomicShortVariant(PagingApiItem):
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
                    for k in ["clinvar", "cosmic", "vcf", "ensemblCanon"]
                ],
                ("id", expand_id),
            ],
        }

        return Frame.expand(data_frame, **args)

    @staticmethod
    def _get_genomic_tests(
        variant_set_ids: List[str],
        max_pages: Optional[int],
        all_results: bool,
        auth_args: Auth,
        log: bool,
        **test_args,
    ):
        test_df = pd.DataFrame()
        args = {}

        if (
            len(variant_set_ids) == 0
            and max_pages is None
            and all_results is False
        ):
            print("Using sample of 25 tests")
            args = {
                **test_args,
                "page_size": 25,
                "max_pages": 1,
                "log": log,
                "auth_args": auth_args,
            }
        elif len(variant_set_ids) == 0:
            args = {
                **test_args,
                "page_size": 100,
                "all_results": True,
                "log": log,
                "auth_args": auth_args,
            }
        test_df = GenomicTest.get_data_frame(**args)

        if len(test_df) == 0:
            # Force id to exist as a column
            test_df["id"] = variant_set_ids

        return test_df

    @classmethod
    def get_data_frame(
        cls,
        # Query parameters
        variant_set_ids: List[str] = [],
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
        # Test parameters
        patient_id: Optional[str] = None,
        status: Optional[GenomicTestStatus] = GenomicTestStatus.ACTIVE,
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
        TEST_PARAMS = ["patient_id", "status"]

        test_args, args = split_by(
            cls._get_current_args(inspect.currentframe(), locals()),
            left_keys=TEST_PARAMS,
        )

        test_df = cls._get_genomic_tests(
            variant_set_ids=variant_set_ids,
            all_results=all_results,
            test_type=GenomicTestType.SHORT_VARIANT,
            page_size=page_size,
            max_pages=max_pages,
            log=log,
            auth_args=auth_args,
            **test_args,
        )
        variant_set_ids = list(test_df.id)

        args = cls._get_current_args(inspect.currentframe(), locals())

        if len(variant_set_ids) > MAX_VARIANT_SET_IDS and (
            max_pages or (not all_results and page_size)
        ):
            print(
                "[WARNING]: All result limit paramters are approximate when performing genomic data retrieval."
            )

        get_data_frame = super().get_data_frame

        def perform_batch(ids: List[str], total_thus_far: int):
            # Determine whether to skip this batch
            if (
                # Implement approximation of max_pages
                not all_results
                and max_pages
                and (total_thus_far >= max_pages * (page_size or 100))
            ) or (
                # Use 25 or page_size for a sample (when no max_pages)
                not all_results
                and not max_pages
                and total_thus_far >= (page_size or 25)
            ):
                return pd.DataFrame()

            has_multiple_batches = len(ids) != len(variant_set_ids)

            return get_data_frame(
                **kw_args,
                **{
                    **args,
                    "variant_set_ids": list(ids),
                    "all_results": all_results
                    # Scroll through full batches and then honor the max_pages param
                    or (has_multiple_batches and max_pages),
                },
            )

        variants = batch_get_frame(
            variant_set_ids, MAX_VARIANT_SET_IDS, perform_batch
        )

        if len(variants) == 0:
            variants["variant_set_id"] = math.nan

        return variants.join(test_df.set_index("id"), on="variant_set_id")
