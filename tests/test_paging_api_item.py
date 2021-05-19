from phc.easy.abstract.paging_api_item import split_kw_args
from phc.easy.query.api_paging import parse_next_page_token_from_url


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


def test_parse_next_token_from_response_links():
    next_token = "<my-next-token>"
    url = f"/v1/projects?nextPageToken={next_token}&pageSize=100"

    assert parse_next_page_token_from_url(url) == next_token

    # Handles case when no next token exists
    assert parse_next_page_token_from_url("") == None
