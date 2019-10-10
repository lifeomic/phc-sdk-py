import unittest

from phc.web.subject_search_query_builder import SubjectSearchQueryBuilder


class SubjectSearchTest(unittest.TestCase):

    def test_subject_search(self):
        search = SubjectSearchQueryBuilder()
        search.patient().observations().value_codeable_concept(
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
        self.assertDictEqual(search.to_dict(), expected)
