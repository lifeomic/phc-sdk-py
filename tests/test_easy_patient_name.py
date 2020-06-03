from phc.easy.patients.name import expand_name_value

def test_name():
    assert expand_name_value([{
        'text': 'ARA251 LO',
        'given': ['ARA251'],
        'family': 'LO'
    }]) == {
        'given_name_0': 'ARA251',
        'family_name': 'LO'
    }
