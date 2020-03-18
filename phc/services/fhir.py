"""A Python Module for FHIR Search"""

from phc.base_client import BaseClient
from phc import ApiResponse


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
    trust_env: bool
        Get proxies information from HTTP_PROXY / HTTPS_PROXY environment variables if the parameter is True (False by default)
    """

    def execute_sql(
        self, project_id: str, statement: str, scroll=""
    ) -> ApiResponse:
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

        Examples
        --------
        >>> import pandas as pd
        >>> from phc.services import Fhir
        >>> fhir = Fhir(session)
        >>> res = fhir.execute_sql(project_id='19e34782-91c4-4143-aaee-2ba81ed0b206',
                       statement='SELECT * from patient LIMIT 0,5000')

        >>> resources = list(map(lambda r: r.get("_source"), res.get("hits").get("hits")))
        >>> df = pd.DataFrame(resources)
        """

        """Executes an SQL query against fhir-searh-service
        Returns:
            [List] -- Dictionary with query response
        """
        return self._api_call(
            api_path=f"fhir-search/projects/{project_id}",
            http_verb="POST",
            data=statement,
            headers={"Content-Type": "text/plain"},
            params={"scroll": scroll},
        )

    def execute_es(
        self, project_id: str, query: dict, scroll=""
    ) -> ApiResponse:
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
            api_path=f"fhir-search/projects/{project_id}",
            http_verb="POST",
            json=query,
            params={"scroll": scroll},
        )
