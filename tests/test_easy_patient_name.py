from phc.easy.patients.name import expand_name_value


def test_name():
    assert expand_name_value(
        [{"text": "ARA251 LO", "given": ["ARA251"], "family": "LO"}]
    ) == {"name_given_0": "ARA251", "name_family": "LO"}


def test_name_with_multiple_values():
    # NOTE: Official names are preferred first and then remaining names are put
    # in separate column
    assert expand_name_value(
        [
            {
                "text": "Christian Di Lorenzo",
                "given": ["Christian"],
                "family": "Di Lorenzo",
            },
            {
                "use": "official",
                "given": ["Robert", "Christian"],
                "family": "Di Lorenzo",
            },
        ]
    ) == {
        "name_given_0": "Robert",
        "name_given_1": "Christian",
        "name_family": "Di Lorenzo",
        "name_use": "official",
        "other_names": [
            {
                "text": "Christian Di Lorenzo",
                "given": ["Christian"],
                "family": "Di Lorenzo",
            },
        ],
    }
