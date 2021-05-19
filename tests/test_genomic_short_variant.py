import pandas as pd
from unittest import mock
from unittest.mock import ANY
from phc.easy.auth import Auth
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


@mock.patch("phc.easy.omics.genomic_test.GenomicTest.get_data_frame")
@mock.patch("phc.easy.query.Query.execute_paging_api")
def test_batches_of_variant_set_ids(execute_paging_api, test_get_data_frame):
    def get_variant_set_ids(index: int):
        return execute_paging_api.call_args_list[index][0][1][
            "variantSetIds"
        ].split(",")

    execute_paging_api.return_value = pd.DataFrame()
    test_get_data_frame.return_value = pd.DataFrame()

    variant_set_ids = [str(uuid4()) for _ in range(250)]

    GenomicShortVariant.get_data_frame(variant_set_ids, all_results=True)

    assert execute_paging_api.call_count == 3

    assert len(get_variant_set_ids(0)) == 100
    assert len(get_variant_set_ids(1)) == 100
    assert len(get_variant_set_ids(2)) == 50

    # GenomicTest should not be retrieved
    assert test_get_data_frame.call_count == 0


@mock.patch("phc.easy.query.Query.execute_paging_api")
def test_passing_options_through_to_paging_api(execute_paging_api):
    execute_paging_api.return_value = pd.DataFrame()

    auth = Auth()

    GenomicShortVariant.get_data_frame(
        [str(uuid4())], raw=True, log=True, auth_args=auth
    )

    kwargs = execute_paging_api.call_args[1]

    assert kwargs.get("auth_args") == auth
    assert kwargs.get("log") == True
    assert kwargs.get("raw") == True
