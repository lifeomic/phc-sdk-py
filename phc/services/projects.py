"""A Python Module for Projects"""

from typing import Optional
from phc.base_client import BaseClient
from phc import ApiResponse
from urllib.parse import urlencode


class Projects(BaseClient):
    """Provides acccess to PHC projects

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

    def create(self, name: str, description: str = None) -> ApiResponse:
        """Creates a project

        Parameters
        ----------
        name : str
            The project name.
        description : str, optional
            The project description, by default None

        Returns
        -------
        phc.ApiResponse
            The create project response
        """
        json_body = {"name": name}
        if description:
            json_body["description"] = description
        return self._api_call("projects", json=json_body, http_verb="POST")

    def get(self, project_id: str) -> ApiResponse:
        """Fetch a project by id

        Parameters
        ----------
        project_id : str
            The project ID.

        Returns
        -------
        phc.ApiResponse
            The get project response
        """
        return self._api_call(f"projects/{project_id}", http_verb="GET")

    def update(
        self, project_id: str, name: str, description: Optional[str] = None
    ) -> ApiResponse:
        """Update a project

        Parameters
        ----------
         project_id : str
            The project ID.
        name : str
            The project name.
        description : str, optional
            The project description, by default None

        Returns
        -------
        phc.ApiResponse
            The update project response
        """
        json_body = {"name": name}
        if description:
            json_body["description"] = description
        return self._api_call(
            f"projects/{project_id}", json=json_body, http_verb="PATCH"
        ).data

    def delete(self, project_id: str) -> bool:
        """Delete a project

        Parameters
        ----------
        project_id : str
            The project ID.

        Returns
        -------
        bool
            True if the delete succeeeds, otherwise False
        """
        return (
            self._api_call(
                f"projects/{project_id}", http_verb="DELETE"
            ).status_code
            == 204
        )

    def get_list(
        self,
        page_size: Optional[int] = None,
        next_page_token: Optional[str] = None,
        name: Optional[str] = None,
    ) -> ApiResponse:
        """Fetch a list of projects in an account

        Parameters
        ----------
        page_size : int, optional
            The page size, by default None
        next_page_token : str, optional
            The next page token, by default None
        name : str, optional
            A project name filter, by default None

        Returns
        -------
        phc.ApiResponse
            The list projects response
        """
        query_dict = {}
        if page_size:
            query_dict["pageSize"] = page_size
        if next_page_token:
            query_dict["nextPageToken"] = next_page_token
        if name:
            query_dict["name"] = name
        return self._api_call(
            f"projects?{urlencode(query_dict)}", http_verb="GET"
        )
