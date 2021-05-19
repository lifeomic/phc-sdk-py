import pandas as pd
from phc.easy.omics.genomic_copy_number_variant import GenomicCopyNumberVariant


def test_parse_id():
    raw_df = pd.DataFrame(
        # NOTE: Sample is taken and adapted from BRCA data set
        [
            {"id": "6b0591ce-7b3b-4b04-85bc-d17e463ca869:A235y+Jw+v="},
            {"id": "f0e381b6-a9b3-4411-af56-7f7f5ce3ce6b:XjQLzpOuLm="},
            {"id": "6b0591ce-7b3b-4b04-85bc-d17e463ca869:BsZ3G0NtUz="},
        ]
    )
    frame = GenomicCopyNumberVariant.transform_results(raw_df)

    assert list(frame.columns) == ["id", "variant_set_id"]

    assert list(frame.variant_set_id.unique()) == [
        "6b0591ce-7b3b-4b04-85bc-d17e463ca869",
        "f0e381b6-a9b3-4411-af56-7f7f5ce3ce6b",
    ]
