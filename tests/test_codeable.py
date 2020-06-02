from phc.easy.codeable import expand_url_dict


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
