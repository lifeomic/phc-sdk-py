from phc.easy.codeable import (
    expand_url_dict,
    generic_codeable_to_dict
)


def test_expand_url_dict():
    expected = {
        'hl7_org_fhir_StructureDefinition_geolocation_latitude_valueDecimal':
        -71.058706,
        'hl7_org_fhir_StructureDefinition_geolocation_longitude_valueDecimal':
        42.42938
    }

    assert expand_url_dict({
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
    input_dict = {'tag': [{'system': 'http://lifeomic.com/fhir/group',
        'code': 'group-code-id'},
       {'system': 'http://lifeomic.com/fhir/dataset',
        'code': 'dataset-code-id'},
       {'system': 'http://lifeomic.com/fhir/dataset',
        'code': 'dataset-second-code-id'},
       {'system': 'http://lifeomic.com/fhir/source',
        'code': 'LifeOmic Consent'},
       {'system': 'http://lifeomic.com/fhir/questionnaire-type',
        'code': 'consent-form'}],
      'lastUpdated': '2019-08-13T17:47:18.957Z'}

    assert generic_codeable_to_dict(input_dict) == {
        'tag_lastUpdated': '2019-08-13T17:47:18.957Z',
        'tag_lifeomic_com_fhir_group': 'group-code-id',
        'tag_lifeomic_com_fhir_dataset': 'dataset-code-id',
        'tag_lifeomic_com_fhir_dataset_1': 'dataset-second-code-id',
        'tag_lifeomic_com_fhir_source': 'LifeOmic Consent',
        'tag_lifeomic_com_fhir_questionnaire-type': 'consent-form'
    }

def test_parsing_system_value():
    assert generic_codeable_to_dict({
        'system': 'http://lifeomic.com/fhir/consent-form-id',
        'value': 'default-project-consent-form'
    }, prefix='0') == {
        '0_lifeomic_com_fhir_consent-form-id': 'default-project-consent-form'
    }
