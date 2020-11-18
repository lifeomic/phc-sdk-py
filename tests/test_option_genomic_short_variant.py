from nose.tools import assert_equals
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
