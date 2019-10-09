import unittest

from phc.web.subject_search import SubjectSearch


class SubjectSearchTest(unittest.TestCase):

    def test_subject_search(self):
        search = SubjectSearch()
        search.patient()\
            .observations()\
            .value_codeable_concept(eq=['LA10316-0', 'LA10315-2'])

        expected = {'patient': {'observations': [{'value_codeable_concept': {'eq': ['LA10316-0', 'LA10315-2']}}]}}
        self.assertDictEqual(search.to_dict(), expected)
