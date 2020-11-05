import pandas as pd
import math
from phc.easy.codeable import generic_codeable_to_dict, Codeable


def test_parsing_lat_long_extension():
    expected = {
        "url__hl7.org/fhir/StructureDefinition/geolocation__extension_url__latitude__valueDecimal": -71.058706,
        "url__hl7.org/fhir/StructureDefinition/geolocation__extension_url__longitude__valueDecimal": 42.42938,
    }

    assert (
        generic_codeable_to_dict(
            {
                "url": "http://hl7.org/fhir/StructureDefinition/geolocation",
                "extension": [
                    {"url": "latitude", "valueDecimal": -71.058706},
                    {"url": "longitude", "valueDecimal": 42.42938},
                ],
            }
        )
        == expected
    )


def test_parsing_simple_meta_value():
    input_dict = {
        "tag": [
            {
                "system": "http://lifeomic.com/fhir/group",
                "code": "group-code-id",
            },
            {
                "system": "http://lifeomic.com/fhir/dataset",
                "code": "dataset-code-id",
            },
            {
                "system": "http://lifeomic.com/fhir/dataset",
                "code": "dataset-second-code-id",
            },
            {
                "system": "http://lifeomic.com/fhir/source",
                "code": "LifeOmic Consent",
            },
            {
                "system": "http://lifeomic.com/fhir/questionnaire-type",
                "code": "consent-form",
            },
        ],
        "lastUpdated": "2019-08-13T17:47:18.957Z",
    }

    assert generic_codeable_to_dict(input_dict) == {
        "tag_lastUpdated": "2019-08-13T17:47:18.957Z",
        "tag_system__lifeomic.com/fhir/group__code": "group-code-id",
        "tag_system__lifeomic.com/fhir/dataset__code": "dataset-code-id",
        "tag_system__lifeomic.com/fhir/dataset__code_1": "dataset-second-code-id",
        "tag_system__lifeomic.com/fhir/source__code": "LifeOmic Consent",
        "tag_system__lifeomic.com/fhir/questionnaire-type__code": "consent-form",
    }


def test_parsing_system_value():
    assert generic_codeable_to_dict(
        {
            "system": "http://lifeomic.com/fhir/consent-form-id",
            "value": "default-project-consent-form",
        },
        prefix="extension",
    ) == {
        "extension_system__lifeomic.com/fhir/consent-form-id__value": "default-project-consent-form"
    }


def test_parsing_extension_with_race():
    input_dict = [
        {
            "url": "http://hl7.org/fhir/StructureDefinition/us-core-race",
            "valueCodeableConcept": {
                "text": "race",
                "coding": [
                    {
                        "code": "2106-3",
                        "system": "http://hl7.org/fhir/v3/Race",
                        "display": "white",
                    }
                ],
            },
        },
        {
            "url": "http://hl7.org/fhir/StructureDefinition/us-core-ethnicity",
            "valueCodeableConcept": {
                "text": "ethnicity",
                "coding": [
                    {
                        "code": "2186-5",
                        "system": "http://hl7.org/fhir/v3/Ethnicity",
                        "display": "not hispanic or latino",
                    }
                ],
            },
        },
    ]

    assert generic_codeable_to_dict(input_dict) == {
        "url__hl7.org/fhir/StructureDefinition/us-core-race__valueCodeableConcept_text": "race",
        "url__hl7.org/fhir/StructureDefinition/us-core-race__valueCodeableConcept_coding_system__hl7.org/fhir/v3/Race__code": "2106-3",
        "url__hl7.org/fhir/StructureDefinition/us-core-race__valueCodeableConcept_coding_system__hl7.org/fhir/v3/Race__display": "white",
        "url__hl7.org/fhir/StructureDefinition/us-core-ethnicity__valueCodeableConcept_text": "ethnicity",
        "url__hl7.org/fhir/StructureDefinition/us-core-ethnicity__valueCodeableConcept_coding_system__hl7.org/fhir/v3/Ethnicity__code": "2186-5",
        "url__hl7.org/fhir/StructureDefinition/us-core-ethnicity__valueCodeableConcept_coding_system__hl7.org/fhir/v3/Ethnicity__display": "not hispanic or latino",
    }


def test_parsing_extension_without_coding():
    input_dict = [
        {
            "url": "http://hl7.org/fhir/StructureDefinition/us-core-race",
            "valueCodeableConcept": {
                "text": "American Indian or Alaska Native"
            },
        }
    ]

    assert generic_codeable_to_dict(input_dict) == {
        "url__hl7.org/fhir/StructureDefinition/us-core-race__valueCodeableConcept_text": "American Indian or Alaska Native"
    }


def test_parsing_anonymous_identifier():
    input_dict = [
        {
            "type": {
                "coding": [
                    {"code": "ANON", "system": "http://hl7.org/fhir/v2/0203"}
                ]
            },
            "value": "LO-AR-A251",
        }
    ]

    # NOTE: There's not much we can do to show the underlying structure since
    # type is really being applied to the value. So, when in conflict, we'll opt
    # to make more readable columns.
    assert generic_codeable_to_dict(input_dict) == {
        "type_coding_system__hl7.org/fhir/v2/0203__code": "ANON",
        "type_coding_system__hl7.org/fhir/v2/0203__value": "LO-AR-A251",
    }


def test_parsing_basic_meta_value():
    input_dict = {
        "tag": [
            {
                "system": "http://lifeomic.com/fhir/dataset",
                "code": "dataset-code",
            }
        ]
    }

    assert generic_codeable_to_dict(input_dict) == {
        "tag_system__lifeomic.com/fhir/dataset__code": "dataset-code"
    }


def test_not_creating_extraneous_columns():
    frame = pd.DataFrame([{"a": "value"}, {"b": math.nan}])

    assert len(Codeable.expand_column(frame.b).columns) == 0
