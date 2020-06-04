from phc.easy.codeable import (generic_codeable_to_dict)

def test_parsing_lat_long_extension():
    expected = {
        'hl7_org_fhir_StructureDefinition_geolocation__latitude__valueDecimal':
        -71.058706,
        'hl7_org_fhir_StructureDefinition_geolocation__longitude__valueDecimal':
        42.42938
    }

    assert generic_codeable_to_dict({
        'url':
        'http://hl7.org/fhir/StructureDefinition/geolocation',
        'extension': [{
            'url': 'latitude',
            'valueDecimal': -71.058706
        }, {
            'url': 'longitude',
            'valueDecimal': 42.42938
        }]
    }) == expected


def test_parsing_simple_meta_value():
    input_dict = {
        'tag': [{
            'system': 'http://lifeomic.com/fhir/group',
            'code': 'group-code-id'
        }, {
            'system': 'http://lifeomic.com/fhir/dataset',
            'code': 'dataset-code-id'
        }, {
            'system': 'http://lifeomic.com/fhir/dataset',
            'code': 'dataset-second-code-id'
        }, {
            'system': 'http://lifeomic.com/fhir/source',
            'code': 'LifeOmic Consent'
        }, {
            'system': 'http://lifeomic.com/fhir/questionnaire-type',
            'code': 'consent-form'
        }],
        'lastUpdated':
        '2019-08-13T17:47:18.957Z'
    }

    assert generic_codeable_to_dict(input_dict) == {
        'tag_lastUpdated': '2019-08-13T17:47:18.957Z',
        'tag_lifeomic_com_fhir_group__code': 'group-code-id',
        'tag_lifeomic_com_fhir_dataset__code': 'dataset-code-id',
        'tag_lifeomic_com_fhir_dataset__code_1': 'dataset-second-code-id',
        'tag_lifeomic_com_fhir_source__code': 'LifeOmic Consent',
        'tag_lifeomic_com_fhir_questionnaire-type__code': 'consent-form'
    }


def test_parsing_system_value():
    assert generic_codeable_to_dict(
        {
            'system': 'http://lifeomic.com/fhir/consent-form-id',
            'value': 'default-project-consent-form'
        },
        prefix='extension') == {
            'extension_lifeomic_com_fhir_consent-form-id__value':
            'default-project-consent-form'
        }


def test_parsing_extension_with_race():
    input_dict = [{
        'url': 'http://hl7.org/fhir/StructureDefinition/us-core-race',
        'valueCodeableConcept': {
            'text':
            'race',
            'coding': [{
                'code': '2106-3',
                'system': 'http://hl7.org/fhir/v3/Race',
                'display': 'white'
            }]
        }
    }, {
        'url': 'http://hl7.org/fhir/StructureDefinition/us-core-ethnicity',
        'valueCodeableConcept': {
            'text':
            'ethnicity',
            'coding': [{
                'code': '2186-5',
                'system': 'http://hl7.org/fhir/v3/Ethnicity',
                'display': 'not hispanic or latino'
            }]
        }
    }]

    assert generic_codeable_to_dict(input_dict) == {
        'hl7_org_fhir_StructureDefinition_us-core-race__hl7_org_fhir_v3_Race__text':
        'race',
        'hl7_org_fhir_StructureDefinition_us-core-race__hl7_org_fhir_v3_Race__code':
        '2106-3',
        'hl7_org_fhir_StructureDefinition_us-core-race__hl7_org_fhir_v3_Race__display':
        'white',
        'hl7_org_fhir_StructureDefinition_us-core-ethnicity__hl7_org_fhir_v3_Ethnicity__text':
        'ethnicity',
        'hl7_org_fhir_StructureDefinition_us-core-ethnicity__hl7_org_fhir_v3_Ethnicity__code':
        '2186-5',
        'hl7_org_fhir_StructureDefinition_us-core-ethnicity__hl7_org_fhir_v3_Ethnicity__display':
        'not hispanic or latino',
    }


def test_parsing_anonymous_identifier():
    input_dict = [{
        'type': {
            'coding': [{
                'code': 'ANON',
                'system': 'http://hl7.org/fhir/v2/0203'
            }]
        },
        'value': 'LO-AR-A251'
    }]

    assert generic_codeable_to_dict(input_dict) == {
        'hl7_org_fhir_v2_0203__code': 'ANON',
        'hl7_org_fhir_v2_0203__value': 'LO-AR-A251'
    }


def test_parsing_basic_meta_value():
    input_dict = {'tag': [{'system': 'http://lifeomic.com/fhir/dataset',
        'code': 'dataset-code'}]}

    assert generic_codeable_to_dict(input_dict) == {
        'tag_lifeomic_com_fhir_dataset__code': 'dataset-code'
    }
