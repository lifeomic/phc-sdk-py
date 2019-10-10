"""A Python Module for FHIR Search"""

from phc.web.base_client import BaseClient


class FhirSearch(BaseClient):
    """Provides acccess to PHC accounts"""

    def execute(self, project, statement):
        """Fetch the list of accounts that the current session belongs to.

        Returns:
            [list] -- A list of accounts
        """
        return self.api_call("fhir-search/projects/{project}".format(project),
                             http_verb="POST", )
