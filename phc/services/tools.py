"""A Python Module for Files"""

import os
import math
import backoff
from phc.base_client import BaseClient
from phc import ApiResponse
from urllib.parse import urlencode
from urllib.request import urlretrieve
from phc.errors import ApiError


class Tools(BaseClient):
    """Provides acccess to PHC tools registry

    Parameters
    ----------
    session: phc.Session
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
        name: str,
        description: str,
        access: str,
        version: str,
        tool_class: str,
        source: str,
        labels: str = None,
    ) -> ApiResponse:
        """Create a tool.

        Parameters
        ----------
        name: str
            The name to give to the tool
        description: str
            A description of the tool
        access: str
            The access level given to the tool [PRIVATE, ACCOUNT, PHC, PUBLIC]
        version: str
            The initial version of the tool
        tool_class: str
            The class of the tool [Workflow, Notebook]
        source: str
            The path of the tool to upload
        labels: str, optional
            A comma delimted list of labels to apply to the tool, i.e. 'bam,samtools'

        Returns
        -------
        ApiResponse
            The create tool response

        Examples
        --------
        >>> from phc.services import Tools
        >>> tools = Tools(session)
        >>> tools.create(name="Read Depth Notebook", description="Generates a chart of positional read depth from a bam file",
              access="PHC", version="1.0.0", tool_class="Notebook", source="./mynotebook.ipynb", labels="bam,samtools")
        """
        create_request = {
            "version": version,
            "access": access,
            "name": name,
            "toolClassId": "1" if tool_class == "Workflow" else "10",
            "descriptorType": "CWL" if tool_class == "Workflow" else "NOTEBOOK",
            "description": description,
        }
        if labels:
            create_request["labels"] = labels.split(",")

        res = self._api_call(
            "/v1/trs/v2/tools", json=create_request, http_verb="POST"
        )

        upload_request = {
            "fileName": source.split("/").pop(),
            "toolId": res["id"],
            "version": res["meta_version"],
        }

        upload_response = self._api_call(
            "/v1/trs/files", json=upload_request, http_verb="POST"
        )
        file_size = os.path.getsize(source)
        self._api_call_impl(
            http_verb="PUT",
            url=upload_response["uploadUrl"],
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
    def download(
        self, tool_id: str, version: str = None, dest_dir: str = os.getcwd()
    ) -> None:
        """Download a tool

        Parameters
        ----------
        tool_id : str
            The tool ID
        version : str, optional
            The version.
        dest_dir : str, optional
            The local directory to save the tool.  Defaults to the current working directory

        Examples
        --------
        >>> from phc.services import Tools
        >>> tools = Tools(session)
        >>> tools.download(tool_id="db3e09e9-1ecd-4976-aa5e-70ac7ada0cc3", dest_dir="./mydata")
        """
        id = f"{tool_id}:{version}" if version else tool_id
        res = self._api_call(f"/v1/trs/files/{id}/download", http_verb="GET")

        file_path = os.path.join(dest_dir, res.get("fileName"))
        target_dir = os.path.dirname(file_path)
        if not os.path.exists(target_dir):
            os.makedirs(target_dir)

        urlretrieve(res.get("downloadUrl"), file_path)
        return file_path

    def get(self, tool_id: str, version: str = None) -> ApiResponse:
        """Fetch a tool by id

        Parameters
        ----------
        tool_id : str
            The tool ID.
        version : str, optional
            The version.

        Returns
        -------
        phc.ApiResponse
            The get tool response
        """
        id = f"{tool_id}:{version}" if version else tool_id
        return self._api_call(f"/v1/trs/v2/tools/{id}", http_verb="GET")

    def add_version(
        self, tool_id: str, version: str, source: str, is_default: bool = False
    ) -> ApiResponse:
        """Adds a new version to a tool.

        Parameters
        ----------
        tool_id : str
            The tool ID to add the version to.
        version : str
            The new version for the tool.
        source: str
            The path of the version to upload.
        is_default: bool = False
            Updates default setting for the tool.

        Returns
        -------
        phc.ApiResponse
            The updated tool response
        """
        version_request = {
            "version": version,
            "isDefault": is_default,
        }

        res = self._api_call(
            f"/v1/trs/v2/tools/{tool_id}/versions",
            json=version_request,
            http_verb="POST",
        )
        upload_request = {
            "fileName": source.split("/").pop(),
            "toolId": res["id"],
            "version": res["meta_version"],
        }

        upload_response = self._api_call(
            "/v1/trs/files", json=upload_request, http_verb="POST"
        )
        file_size = os.path.getsize(source)
        self._api_call_impl(
            http_verb="PUT",
            url=upload_response["uploadUrl"],
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

    def delete(self, tool_id: str, version: str = None) -> bool:
        """Deletes a tool

        Parameters
        ----------
        tool_id : str
            The tool ID.
        version : str, optional
            The version.

        Returns
        -------
        bool
            True if the delete succeeeds, otherwise False
        """
        id = f"{tool_id}:{version}" if version else tool_id
        return (
            self._api_call(
                f"/v1/trs/v2/tools/{id}", http_verb="DELETE"
            ).status_code
            == 200
        )

    def get_list(
        self,
        tool_class: str = None,
        organization: str = None,
        tool_name: str = None,
        author: str = None,
        labels: str = None,
    ) -> ApiResponse:
        """Fetch a list of tools from the registry

        Parameters
        ----------
        tool_class: str, optional
            The class of the tool, by default None
        organization: str, optional
            The organization that owns the tool, by default None
        tool_name: str, optional
            The name of the tool, by default None
        author: str, optional
            The creator of the tool, by default None
        label: str, optional
            A comma delimted list of labels describing the tool, by default None

        Returns
        -------
        phc.ApiResponse
            The list files response
        """
        query_dict = {}
        if tool_class:
            query_dict["toolClass"] = tool_class
        if organization:
            query_dict["organization"] = organization
        if tool_name:
            query_dict["toolname"] = tool_name
        if author:
            query_dict["author"] = author
        if labels:
            query_dict["label"] = labels

        return self._api_call(
            f"/v1/trs/v2/tools?{urlencode(query_dict)}",
            http_verb="GET",
        )
