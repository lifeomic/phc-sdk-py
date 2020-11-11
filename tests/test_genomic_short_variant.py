import pandas as pd
from phc.easy.omics.genomic_short_variant import GenomicShortVariant


def test_parse_id():
    raw_df = pd.DataFrame(
        # NOTE: Sample is taken and adapted from BRCA data set
        [
            {"id": "f0e381b6-a9b3-4411-af56-7f7f5ce3ce6b:XjQLzpOuLm=:GOLGA3"},
            {"id": "f0e381b6-a9b3-4411-af56-7f7f5ce3ce6b:naTuKl96CL=:ESCO1"},
            {"id": "6b0591ce-7b3b-4b04-85bc-d17e463ca869:A235y+Jw+v=:MAP3K13"},
            {"id": "f0e381b6-a9b3-4411-af56-7f7f5ce3ce6b:dOML6l4/uk=:MAP3K7"},
            {"id": "f0e381b6-a9b3-4411-af56-7f7f5ce3ce6b:tCkWMHDLL7=:CACNA1B"},
            {"id": "6b0591ce-7b3b-4b04-85bc-d17e463ca869:3szKb4RVAR=:PCDHB7"},
            {"id": "6b0591ce-7b3b-4b04-85bc-d17e463ca869:BsZ3G0NtUz=:FASN"},
        ]
    )

    frame = GenomicShortVariant.transform_results(raw_df)

    assert frame.columns.values.tolist() == ["id", "variant_set_id", "gene"]

    assert frame.variant_set_id.unique().tolist() == [
        "f0e381b6-a9b3-4411-af56-7f7f5ce3ce6b",
        "6b0591ce-7b3b-4b04-85bc-d17e463ca869",
    ]

    assert "FASN" in frame.gene.values.tolist()
