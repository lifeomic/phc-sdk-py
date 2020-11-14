import pandas as pd
from nose.tools import assert_equals
from unittest import mock
from unittest.mock import ANY
from phc.easy.omics.genomic_short_variant import GenomicShortVariant
from uuid import uuid4


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


@mock.patch("phc.easy.query.Query.execute_paging_api")
def test_batches_of_variant_set_ids(execute_paging_api):
    def get_variant_set_ids(index: int):
        return execute_paging_api.call_args_list[index][0][1][
            "variantSetIds"
        ].split(",")

    execute_paging_api.return_value = pd.DataFrame(
        {"id": [], "variant_set_id": []}
    )

    variant_set_ids = [str(uuid4()) for _ in range(250)]

    GenomicShortVariant.get_data_frame(variant_set_ids, all_results=True)

    assert_equals(execute_paging_api.call_count, 3)

    assert_equals(len(get_variant_set_ids(0)), 100)
    assert_equals(len(get_variant_set_ids(1)), 100)
    assert_equals(len(get_variant_set_ids(2)), 50)
