"""A Python Module for Tasks"""

from phc import ApiResponse
from phc.base_client import BaseClient
from typing import Optional, Dict, Union
from urllib.parse import urlencode


class Tasks(BaseClient):
    """Provides access to PHC Tasks

    Parameters
    ----------
    session: phc.Session
        The PHC session.
    run_async: bool
        True to return promises, False to return results (default is False).
    timeout: int
        Operation timeout (default is 30).
    trust_env: bool
        Get proxies information from HTTP_PROXY / HTTPS_PROXY environment variables if the parameter is True (False by default).
    """

    def get(self, task_id: str) -> ApiResponse:
        """Fetch a task by id

        Parameters
        ----------
        task_id: str
            The task ID.

        Returns
        -------
        phc.ApiResponse
            The get task response.
        """
        return self._api_call(f"tasks/{task_id}", http_verb="GET")

    def retry(self, task_id: str) -> ApiResponse:
        """Retry a task by id

        Parameters
        ----------
        task_id: str
            The task ID.

        Returns
        -------
        phc.ApiResponse
            The retry task response.
        """
        return self._api_call(f"tasks/{task_id}:clone")

    def cancel(self, task_id: str) -> ApiResponse:
        """Cancel a task by id

        Parameters
        ----------
        task_id: str
            The task ID.

        Returns
        -------
        phc.ApiResponse
            The cancel task response.
        """
        return self._api_call(f"tasks/{task_id}:cancel")

    def create(self, task: dict) -> ApiResponse:
        """Create a task

        Parameters
        ----------
        task: dict
            The task to create.

        Returns
        -------
        phc.ApiResponse
            The create task response.
        """
        return self._api_call("tasks", json=task)

    def list(
        self,
        project_id: str,
        prefix: Optional[str] = None,
        state: Optional[str] = None,
        minimal: Optional[bool] = None,
        page_size: Optional[int] = None,
        next_page_token: Optional[str] = None,
    ):
        """Fetch a list of tasks in a project

        Parameters
        ----------
        project_id: str
            The project ID for the tasks.
        prefix: str, optional
            The prefix to filter tasks by, by default None.
        state: str, optional
            The state to filter tasks by, by default None.
        bool: bool, optional
            Set to True to just get task state, by default None.
        page_size: int, optional
            The page size, by default None.
        next_page_token: str, optional
            The next page token, by default None.

        Returns
        -------
        phc.ApiResponse
            The list tasks response.
        """
        query_dict: Dict[str, Union[str, int]] = {}
        query_dict["datasetId"] = project_id
        if page_size:
            query_dict["pageSize"] = page_size
        if next_page_token:
            query_dict["nextPageToken"] = next_page_token
        if prefix:
            query_dict["name"] = prefix
        if state:
            query_dict["state"] = state
        if minimal:
            query_dict["view"] = "MINIMAL"

        return self._api_call(f"tasks?{urlencode(query_dict)}", http_verb="GET")
