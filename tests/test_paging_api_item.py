from nose.tools import assert_equals

from phc.easy.abstract.paging_api_item import split_kw_args
from phc.easy.query.api_paging import get_next_page_token


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

    assert_equals(get_next_page_token(url), next_token)

    # Handles case when no next token exists
    assert_equals(get_next_page_token(""), None)
