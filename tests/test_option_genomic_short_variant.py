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
