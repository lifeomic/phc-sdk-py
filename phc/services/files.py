"""A Python Module for Files"""

from phc.base_client import BaseClient
from phc import ApiResponse
from urllib.parse import urlencode


class Files(BaseClient):
    """Provides acccess to PHC files

    Parameters
    ----------
    session : phc.Session
        The PHC session
    run_async: bool
        True to return promises, False to return results (default is False)
    timeout: int
        Operation timeout (default is 30)
    """

    def get(self, file_id):
        """Fetch a file by id

        Parameters
        ----------
        file_id : str
            The file ID.

        Returns
        -------
        phc.ApiResponse
            The get file response
        """
        return self._api_call(f"files/{file_id}", http_verb="GET")

    def update(
        self, file_id: str, project_id: str = None, name: str = None
    ) -> ApiResponse:
        """Update a files by moving it to a new project or by renaming it.

        Parameters
        ----------
        file_id : str
            The file ID to update.
        project_id : str
            The new project ID for the file.
        name : str
            The new file name

        Returns
        -------
        phc.ApiResponse
            The update file response
        """
        if not project_id and not name:
            raise ValueError(
                "Must provide a value for either 'project_id' or 'name'"
            )

        json_body = {}
        if name:
            json_body["name"] = name
        if project_id:
            json_body["datasetId"] = project_id

        return self._api_call(
            f"files/{file_id}", json=json_body, http_verb="PATCH"
        )

    def delete(self, file_id: str) -> bool:
        """Delete a file

        Parameters
        ----------
        file_id : str
            The file ID.

        Returns
        -------
        bool
            True if the delete succeeeds, otherwise False
        """
        return (
            self._api_call(f"files/{file_id}", http_verb="DELETE").status_code
            == 204
        )

    def get_list(
        self,
        project_id: str,
        folder: str = None,
        page_size: int = None,
        next_page_token: str = None,
    ) -> ApiResponse:
        """Fetch a list of files in a project

        Parameters
        ----------
        project_id: str
            The project ID
        folder: str, optional
            The folder prefix to look for files, by default None
        page_size : int, optional
            The page size, by default None
        next_page_token : str, optional
            The next page token, by default None

        Returns
        -------
        phc.ApiResponse
            The list files response
        """
        query_dict = {}
        if page_size:
            query_dict["pageSize"] = page_size
        if next_page_token:
            query_dict["nextPageToken"] = next_page_token
        if folder:
            query_dict["prefix"] = folder

        return self._api_call(
            f"projects/{project_id}/files?{urlencode(query_dict)}",
            http_verb="GET",
        )
