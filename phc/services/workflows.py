"""A Python Module for Workflows"""

from typing import Optional
from phc.base_client import BaseClient
from phc import ApiResponse
from urllib.parse import urlencode


class Workflows(BaseClient):
    """Provides acccess to PHC Workflows

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

    def run(
        self,
        project_id: str,
        name: str,
        tool: str,
        workflow_inputs: Optional[str] = None,
        workflow_inputs_file_id: Optional[str] = None,
        output_project_folder: Optional[str] = None,
    ) -> ApiResponse:
        """Create a tool.

        Parameters
        ----------
        project_id: str
            The project ID
        name: str
            The name to give to this run of a tool
        tool: str
            The tool id or organization/name of the tool to run
        workflow_inputs: str, optional
            The inputs required by the workflow as a json string, either this or workflow_inputs_file_id are required
        workflow_inputs_file_id: str, optional
            The inputs required by the workflow as provided in a file in PHC, either this or workflow_inputs are required
        output_project_folder: str, optional
            The destination output folder in PHC for the workflow run outputs

        Returns
        -------
        ApiResponse
            The workflow run response

        Examples
        --------
        >>> from phc.services import Workflows
        >>> workflows = Workflows(session)
        >>> workflows.run(project_id="d2876f48-724f-4987-9cf0-92c7ef99a9fa",
              name="Ashion ingest subj: 2405",
              tool="lifeomic/ashion-ingest-workflow",
              workflow_inputs="{'reference': 'GRCh37','tarFile': {'class': 'File','fileId': '28235c74-9731-4496-bb3c-41c361f106f3'}, 'source': 'incoming/ashion_C043_9999_009990_T1_K1ID2_ps20190814000000.tar.gz'}")
        """
        create_request = {
            "datasetId": project_id,
            "name": name,
            "workflowSourceFileId": tool,
        }

        if workflow_inputs:
            create_request["workflowInputs"] = workflow_inputs
        elif workflow_inputs_file_id:
            create_request["workflowInputsFileId"] = workflow_inputs_file_id
        else:
            raise ValueError(
                "Must provide a value for the workflow_inputs or workflow_inputs_file_id"
            )

        if output_project_folder:
            create_request["outputProjectFolder"] = output_project_folder

        res = self._api_call(
            "/v1/workflows/ga4gh/wes/runs",
            json=create_request,
            http_verb="POST",
        )
        return res

    def get(self, project_id: str, workflow_id: str) -> ApiResponse:
        """Get workflow metadata by id

        Parameters
        ----------
        project_id: str
            The project ID
        workflow_id : str
            The workflow ID.

        Returns
        -------
        phc.ApiResponse
            The get workflow response
        """
        return self._api_call(
            f"/v1/workflows/ga4gh/wes/runs/{project_id}:{workflow_id}",
            http_verb="GET",
        )

    def get_list(
        self,
        project_id: str,
        page_size: Optional[int] = 100,
        next_page_token: Optional[str] = None,
    ) -> ApiResponse:
        """Fetch a list of workflows run in the specified project

        Parameters
        ----------
        project_id: str
            The project ID
        page_size : int, optional
            The page size, by default 100
        next_page_token : str, optional
            The next page token, by default None

        Returns
        -------
        phc.ApiResponse
            The list workflow run response
        """
        query_dict = {"datasetId": project_id}
        if page_size:
            query_dict["pageSize"] = page_size
        if next_page_token:
            query_dict["nextPageToken"] = next_page_token

        return self._api_call(
            f"/v1/workflows/ga4gh/wes/runs?{urlencode(query_dict)}",
            http_verb="GET",
        )

    def describe(self, project_id: str, tool: str) -> ApiResponse:
        """Returns a description of the inputs the workflow engine requires for the given tool

        Parameters
        ----------
        project_id: str
            The project ID
        tool: str
            The tool id or organization/name of the tool to run

        Returns
        -------
        phc.ApiResponse
            The description of the inputs for the given tool
        """
        describe_request = {
            "datasetId": project_id,
            "workflowSourceFileId": tool,
        }

        return self._api_call(
            "/v1/workflows/ga4gh/wes/runs/parse",
            json=describe_request,
            http_verb="POST",
        )
