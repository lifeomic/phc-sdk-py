"""A Python Module for FHIR Search"""

import warnings

from phc.base_client import BaseClient
from phc import ApiResponse
from typing import List, Dict


class Fhir(BaseClient):
    """Provides bindings to the LifeOmic FHIR Service APIs"""

    def dsl(self, project: str, data: dict, scroll=""):
        """Executes a LifeOmic FHIR Service DSL request

        Parameters
        ----------
        project : str
            The target LifeOmic project identifier
        data : dict
            The DSL request object
        scroll
            The scroll request parameter

        Returns
        -------
        phc.ApiResponse
            The API response
        """
        path = f"fhir-search/projects/{project}"
        scroll = scroll if scroll is not True else "true"
        params = {"scroll": scroll if scroll is not True else "true"}
        return self._api_call(
            http_verb="POST", api_path=path, params=params, json=data
        )

    def sql(self, project: str, statement: str, scroll="") -> ApiResponse:
        """Executes a LifeOmic FHIR Service SQL request

        Parameters
        ----------
        project : str
            The target LifeOmic project identifier
        statement : str
            The SQL request statement
        scroll
            The scroll request parameter

        Returns
        -------
        phc.ApiResponse
            The API response
        """
        path = f"fhir-search/projects/{project}"
        headers = {"Content-Type": "text/plain"}
        params = {"scroll": scroll if scroll is not True else "true"}
        return self._api_call(
            http_verb="POST",
            api_path=path,
            headers=headers,
            params=params,
            data=statement,
        )

    def execute_sql(
        self, project_id: str, statement: str, scroll=""
    ) -> ApiResponse:
        """Executes an SQL query against fhir-search-service

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

        """Executes an SQL query against fhir-search-service
        Returns:
            [List] -- Dictionary with query response
        """
        warnings.warn("Use the sql method instead", DeprecationWarning)
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
        """Executes an elasticsearch query against fhir-search-service

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
        warnings.warn("Use the dsl method instead", DeprecationWarning)
        return self._api_call(
            api_path=f"fhir-search/projects/{project_id}",
            http_verb="POST",
            json=query,
            params={"scroll": scroll},
        )

    def es_sql(
        self,
        project_id: str,
        statement: str,
        params: List[Dict] = [],
        subject_id="",
    ) -> ApiResponse:
        """Executes an OpenSearch SQL against fhir-search-service

        Parameters
        ----------
        project_id : str
            The project ID
        statement : str
            The prepared OpenSearch SQL statement
        params: List[Dict]
            The parameters for the SQL statement
        subject_id : str, optional
            The subject ID

        Returns
        -------
        phc.ApiResponse
            The query response
        """
        api_path = f"fhir-search/sql/projects/{project_id}"
        if subject_id is not None and subject_id != "":
            api_path = f"{api_path}/patients/{subject_id}"

        return self._api_call(
            api_path=api_path,
            http_verb="POST",
            json={"query": statement, "parameters": params},
        )
