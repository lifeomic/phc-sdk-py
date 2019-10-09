import unittest

from ..web.subject_search import SubjectSearch, SubjectSearchComponents


class SubjectSearchTest(unittest.TestCase):
    def test_subject_search(self):
        search = SubjectSearchComponents()
        search.observations().value_codeable_concept(
            eq=["LA10316-0", "LA10315-2"]
        )

        expected = {
            "observations": [
                {"value_codeable_concept": {"eq": ["LA10316-0", "LA10315-2"]}}
            ]
        }
        self.assertDictEqual(search.to_dict(), expected)
