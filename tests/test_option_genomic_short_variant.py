from uuid import uuid4
from nose.tools import assert_equals, assert_raises
from pydantic.error_wrappers import ValidationError
from phc.easy.omics.options.genomic_short_variant import (
    GenomicShortVariantOptions,
)


def test_transforms_in_ckb_to_string():
    assert_equals(
        GenomicShortVariantOptions.transform("in_ckb", None),
        ("drugAssociations", None),
    )

    assert_equals(
        GenomicShortVariantOptions.transform("in_ckb", False),
        ("drugAssociations", None),
    )

    assert_equals(
        GenomicShortVariantOptions.transform("in_ckb", True),
        ("drugAssociations", "true"),
    )


def test_transforms_cosmic_min_count():
    assert_equals(
        GenomicShortVariantOptions.transform("cosmic_min_count", 3),
        ("cosmicSampleCount", "3:gte"),
    )

    # None values get trimmed out downstream
    assert_equals(
        GenomicShortVariantOptions.transform("cosmic_min_count", None),
        ("cosmic_min_count", None),
    )


def test_min_allele_frequency_range():
    result = GenomicShortVariantOptions(
        variant_set_ids=[str(uuid4())], min_allele_frequency="0.0002-0.1"
    ).dict()

    assert_equals(result.get("minAlleleFrequency"), "0.0002-0.1")

    # Valid range is required
    assert_raises(
        ValidationError,
        lambda: GenomicShortVariantOptions(
            variant_set_ids=[str(uuid4())], min_allele_frequency="0.0002"
        ),
    )
