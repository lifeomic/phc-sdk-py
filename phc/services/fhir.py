"""A Python Module for FHIR Search"""

from phc.base_client import BaseClient


class Fhir(BaseClient):
    """Provides methods to run search using SQL or Elasticsearch queries

    Parameters
    ----------
    session : phc.Session
        The PHC session
    run_async: bool
        True to return promises, False to return results (default is False)
    timeout: int
        Operation timeout (default is 30)
    """

    def execute_sql(self, project_id, statement):
        """Executes an SQL query against fhir-searh-service

        Parameters
        ----------
        project_id : str
            The project ID.
        statement : str
            The SQL statement.

        Returns
        -------
        phc.ApiResponse
            The query response.
        """

        """Executes an SQL query against fhir-searh-service
        Returns:
            [List] -- Dictionary with query response
        """
        return self._api_call(
            api_path="fhir-search/projects/{}".format(project_id),
            http_verb="POST",
            data=statement,
            headers={"Content-Type": "text/plain"},
        )

    def execute_es(self, project_id, query):
        """Executes an elasticsearch query against fhir-searh-service

        Parameters
        ----------
        project_id : str
            The project ID
        query : dict
            The ES query dictionary

        Returns
        -------
        phc.ApiResponse
            The query response
        """
        return self._api_call(
            api_path="fhir-search/projects/{}".format(project_id),
            http_verb="POST",
            json=query,
        ).data