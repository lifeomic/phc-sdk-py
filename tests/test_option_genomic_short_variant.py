import pytest
from uuid import uuid4
from pydantic.error_wrappers import ValidationError
from phc.easy.omics.options.genomic_short_variant import (
    GenomicShortVariantOptions,
)


def test_transforms_in_ckb_to_string():
    assert GenomicShortVariantOptions.transform("in_ckb", None) == ("drugAssociations", None)
    

    assert GenomicShortVariantOptions.transform("in_ckb", False) == ("drugAssociations", None)
    

    assert GenomicShortVariantOptions.transform("in_ckb", True) == ("drugAssociations", "true")
    


def test_transforms_cosmic_min_count():
    assert GenomicShortVariantOptions.transform("cosmic_min_count", 3) == ("cosmicSampleCount", "3:gte")
    

    # None values get trimmed out downstream
    assert GenomicShortVariantOptions.transform("cosmic_min_count", None) == ("cosmic_min_count", None)
    


def test_min_allele_frequency_range():
    result = GenomicShortVariantOptions(
        variant_set_ids=[str(uuid4())], min_allele_frequency="0.0002-0.1"
    ).dict()

    assert result.get("minAlleleFrequency") == "0.0002-0.1"

    # Valid range is required
    with pytest.raises(ValidationError):
        GenomicShortVariantOptions(
            variant_set_ids=[str(uuid4())], min_allele_frequency="0.0002"
        )
