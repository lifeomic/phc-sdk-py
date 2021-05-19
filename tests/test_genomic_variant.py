from uuid import uuid4
from unittest import mock
from phc.easy.auth import Auth
from phc.easy.abstract.genomic_variant import GenomicVariant


@mock.patch("phc.easy.omics.genomic_test.GenomicTest.get_data_frame")
def test_getting_genomic_tests(get_data_frame):
    GenomicVariant._get_genomic_tests(
        [], max_pages=None, all_results=False, auth_args=Auth(), log=False
    )

    get_data_frame.assert_called_once()


@mock.patch("phc.easy.omics.genomic_test.GenomicTest.get_data_frame")
def test_skipping_genomic_tests_if_variant_set_ids(get_data_frame):
    variant_set_ids = [str(uuid4())]

    test_df = GenomicVariant._get_genomic_tests(
        variant_set_ids,
        max_pages=None,
        all_results=False,
        auth_args=Auth(),
        log=False,
    )

    assert get_data_frame.call_count == 0

    assert len(test_df.columns) == 1
    assert list(test_df.id) == variant_set_ids
