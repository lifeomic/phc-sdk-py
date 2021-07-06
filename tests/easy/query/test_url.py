from phc.easy.query.url import merge_pattern


def test_merge_pattern():
    assert merge_pattern("/api/{test}/value", {"test": "sub", "a": 1}) == (
        "/api/sub/value",
        {"a": 1},
    )

