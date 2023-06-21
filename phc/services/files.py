"""A Python Module for Files"""

import os
import math
from typing import Optional
import backoff
from phc.base_client import BaseClient
from phc import ApiResponse
from urllib.parse import urlencode
from urllib.request import urlretrieve
from phc.errors import ApiError, ClientError


class FileArchiveError(ClientError):
    """Error raised when operations are attempted on an archived file."""


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
    trust_env: bool
        Get proxies information from HTTP_PROXY / HTTPS_PROXY environment variables if the parameter is True (False by default)
    """

    _MULTIPART_MIN_SIZE = 5 * 1024 * 1024
    _MAX_PARTS = 10000

    def upload(
        self,
        project_id: str,
        source: str,
        file_name: Optional[str] = None,
        overwrite: Optional[bool] = False,
    ) -> ApiResponse:
        """Upload a file.

        Parameters
        ----------
        project_id : str
            The project ID
        source : str
            The path of the file to upload
        file_name : str, optional
            The name of the file, If None will default to the actual base file name.
        overwrite : bool, optional
            True to overwrite an existing file of the same name, by default False

        Returns
        -------
        ApiResponse
            The upload file response

        Examples
        --------
        >>> from phc.services import Files
        >>> files = files(session)
        >>> files.upload(project_id="db3e09e9-1ecd-4976-aa5e-70ac7ada0cc3", source="./myfile.txt", overwrite=True)
        """
        file_size = os.path.getsize(source)
        if file_size > self._MULTIPART_MIN_SIZE:
            res = self._api_call(
                "uploads",
                json={
                    "name": file_name
                    if file_name is not None
                    else os.path.basename(source),
                    "datasetId": project_id,
                    "overwrite": overwrite,
                },
            )
            upload_id = res.get("uploadId")
            part_size = max(
                math.ceil(file_size / self._MAX_PARTS), self._MULTIPART_MIN_SIZE
            )
            total_parts = math.ceil(file_size / part_size)
            part = 1
            while part <= total_parts:
                start = (part - 1) * part_size
                end = file_size if part == total_parts else start + part_size
                f = open(source, "rb")
                f.seek(start)
                data = f.read(end - start)
                f.close()
                part_res = self._api_call(
                    f"uploads/{upload_id}/parts/{part}", http_verb="GET"
                )
                self._api_call_impl(
                    http_verb="PUT",
                    url=part_res.get("uploadUrl"),
                    api_path=None,
                    upload_file=data,
                    headers={
                        "Content-Length": str(end - start),
                        "Authorization": None,
                        "LifeOmic-Account": None,
                        "Content-Type": None,
                    },
                )
                print(f"Upload {part}")
                part += 1
            self._api_call(f"uploads/{upload_id}", http_verb="DELETE")
            return res
        else:
            res = self._api_call(
                "files",
                json={
                    "name": file_name
                    if file_name is not None
                    else os.path.basename(source),
                    "datasetId": project_id,
                    "overwrite": overwrite,
                },
            )
            self._api_call_impl(
                http_verb="PUT",
                url=res.get("uploadUrl"),
                api_path=None,
                upload_file=source,
                headers={
                    "Content-Length": str(file_size),
                    "Authorization": None,
                    "LifeOmic-Account": None,
                    "Content-Type": None,
                },
            )
            return res

    @backoff.on_exception(
        backoff.expo, OSError, max_tries=6, jitter=backoff.full_jitter
    )
    def download(self, file_id: str, dest_dir: str = os.getcwd()) -> None:
        """Download a file

        Parameters
        ----------
        file_id : str
            The file ID
        dest_dir : str, optional
            The local directory to save the file.  Defaults to the current working directory

        Examples
        --------
        >>> from phc.services import Files
        >>> files = files(session)
        >>> files.download(file_id="db3e09e9-1ecd-4976-aa5e-70ac7ada0cc3", dest_dir="./mydata")
        """
        try:
            res = self._api_call(
                f"files/{file_id}?include=downloadUrl", http_verb="GET"
            )
        except ApiError as e:
            if e.response.status_code == 422:
                raise FileArchiveError(
                    "This file is currently archived and is not available for download. Contact LifeOmic support to learn more."
                ) from None

        file_path = os.path.join(dest_dir, res.get("name"))
        target_dir = os.path.dirname(file_path)
        if not os.path.exists(target_dir):
            os.makedirs(target_dir)

        urlretrieve(res.get("downloadUrl"), file_path)
        return file_path

    def get(self, file_id: str) -> ApiResponse:
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
        self,
        file_id: str,
        project_id: Optional[str] = None,
        name: Optional[str] = None,
    ) -> ApiResponse:
        """Update a files by moving it to a new project or by renaming it.

        Parameters
        ----------
        file_id : str
            The file ID to update.
        project_id : str, optional
            The new project ID for the file.
        name : str, optional
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

        try:
            return self._api_call(
                f"files/{file_id}", json=json_body, http_verb="PATCH"
            )
        except ApiError as e:
            if e.response.status_code == 422:
                raise FileArchiveError(
                    "This file is currently archived and cannot be moved. Contact LifeOmic support to learn more."
                ) from None

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
        folder: Optional[str] = None,
        page_size: Optional[int] = None,
        next_page_token: Optional[str] = None,
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

    def exists(self, file_id: str) -> ApiResponse:
        """Check if a file exists by id

        Parameters
        ----------
        file_id : str
            The file ID.

        Returns
        -------
        bool
            True if the file exists, false otherwise
        """
        try:
            self._api_call(f"files/{file_id}", http_verb="GET")
            return True
        except ApiError as e:
            if e.response.status_code == 404:
                return False
            raise e
