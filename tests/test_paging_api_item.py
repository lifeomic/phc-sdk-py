from phc.easy.abstract.paging_api_item import split_kw_args


def test_split_kw_args():
    result = split_kw_args(
        dict(
            page_size=100,
            max_pages=2,
            test_type="shortVariant",
            date_columns=[],
        )
    )

    assert result == {
        "execute": {"page_size": 100, "max_pages": 2},
        "query": {"test_type": "shortVariant"},
        "expand": {"date_columns": []},
    }
