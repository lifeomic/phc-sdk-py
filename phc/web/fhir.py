"""A Python Module for FHIR Search"""

from phc.web.base_client import BaseClient


class Fhir(BaseClient):
    """Provides methods to run search using SQL or Elasticsearch queries"""

    def execute_sql(self, project, statement):
        """Executes an SQL query against fhir-searh-service
        Returns:
            [List] -- Dictionary with query response
        """
        return self._api_call(
            api_path="fhir-search/projects/{}".format(project),
            http_verb="POST",
            data=statement,
            headers={"Content-Type": "text/plain"},
        ).data

    def execute_es(self, project, query):
        """Executes an elasticsearch query against fhir-searh-service
        Returns:
            [Dict] -- Dictionary with query response
        """
        return self._api_call(
            api_path="fhir-search/projects/{}".format(project),
            http_verb="POST",
            json=query,
        ).data
