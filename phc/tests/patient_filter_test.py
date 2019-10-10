import unittest

from phc.web.patient_filter_query_builder import PatientFilterQueryBuilder


class PatientFilterQueryBuilderTest(unittest.TestCase):

    def test_patient_filter_query_builder(self):
        filter = PatientFilterQueryBuilder()
        filter.patient().observations().value_codeable_concept(
            eq=['LA10316-0', 'LA10315-2'])

        expected = {
            'query': {
                'where': {
                    'patient': {
                        'observations': {
                            'value_codeable_concept': [
                                {
                                    'operator': 'eq',
                                    'value': ['LA10316-0', 'LA10315-2']
                                }
                            ]
                        }
                    }
                },
                'domain': 'filter',
                'target': 'patient'
            }
        }
        self.assertDictEqual(filter.to_dict(), expected)
