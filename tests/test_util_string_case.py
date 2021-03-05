from nose.tools import assert_equals
from phc.util.string_case import snake_to_title_case


def test_snake_to_title_case():
    assert_equals(
        snake_to_title_case("document_reference"), "DocumentReference"
    )
    assert_equals(snake_to_title_case("patient"), "Patient")
