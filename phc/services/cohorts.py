"""A Python Module for Cohorts"""

from typing import Optional
from phc.base_client import BaseClient
from phc import ApiResponse
from urllib.parse import urlencode


class Cohorts(BaseClient):
    """Provides acccess to PHC cohorts

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

    def create(
        self,
        project_id: str,
        name: str,
        queries: list,
        description: Optional[str] = None,
    ) -> ApiResponse:
        """Creates a cohort

        Parameters
        ----------
        project_id: str
            The project that owns the cohort
        name : str
            The cohort name.
        queries: list
            The list of queries that define the cohort
        description : str, optional
            The cohort description, by default None

        Returns
        -------
        phc.ApiResponse
            The create cohort response
        """
        json_body = {
            "name": name,
            "ownerProject": project_id,
            "queries": queries,
        }
        if description:
            json_body["description"] = description
        return self._api_call("cohorts", json=json_body, http_verb="POST")

    def get(self, cohort_id: str) -> ApiResponse:
        """Fetch a cohort by id

        Parameters
        ----------
        cohort_id : str
            The cohort ID.

        Returns
        -------
        phc.ApiResponse
            The get cohort response
        """
        return self._api_call(f"cohorts/{cohort_id}", http_verb="GET")

    def delete(self, cohort_id: str) -> bool:
        """Delete a cohort

        Parameters
        ----------
        cohort_id : str
            The cohort ID.

        Returns
        -------
        bool
            True if the delete succeeeds, otherwise False
        """
        return (
            self._api_call(
                f"cohorts/{cohort_id}", http_verb="DELETE"
            ).status_code
            == 204
        )

    def get_list(
        self,
        project_id: str,
        page_size: Optional[int] = None,
        next_page_token: Optional[str] = None,
        name: Optional[str] = None,
    ) -> ApiResponse:
        """Fetch a list of cohorts in a project

        Parameters
        ----------
        project_id: str
            The project ID to search within
        page_size : int, optional
            The page size, by default None
        next_page_token : str, optional
            The next page token, by default None
        name : str, optional
            A cohort name filter, by default None

        Returns
        -------
        phc.ApiResponse
            The list cohorts response
        """
        query_dict = {"projectId": project_id}
        if page_size:
            query_dict["pageSize"] = page_size
        if next_page_token:
            query_dict["nextPageToken"] = next_page_token
        if name:
            query_dict["name"] = name
        return self._api_call(
            f"cohorts?{urlencode(query_dict)}", http_verb="GET"
        )
