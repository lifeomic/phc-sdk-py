from phc.util.string_case import snake_to_title_case


def test_snake_to_title_case():
    assert snake_to_title_case("document_reference") == "DocumentReference"
    assert snake_to_title_case("patient") == "Patient"
    assert snake_to_title_case("") == ""
