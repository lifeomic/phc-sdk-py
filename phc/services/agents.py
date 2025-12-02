import time
from typing import Callable, Dict, List, Union
from phc.base_client import BaseClient


_IN_PROGRESS_STATUSES = {"scheduled", "pending", "processing"}


def _is_task_complete(status: Union[str, None]) -> bool:
    if not status:
        return False
    return status.lower() not in _IN_PROGRESS_STATUSES


class Agents(BaseClient):
    """
    Provides access to the PHC agents API, which allows you to call LLM-based agents.
    """

    def invoke_basic(self, body: Union[str, List[Dict]]):
        """
        Invokes a basic agent, which supports either a basic prompt string or a list of
        messages which can include images as data urls. Requires the `invokeAgent` ABAC
        permission with `agent: "api-basic-agent"` in the policy, or the `accessAdmin`
        permission.
        """
        return self._api_call(
            "/v1/agents-v2/basic/invoke", json={"input": body}, http_verb="POST"
        )

    def invoke_template(
        self,
        template_id: str,
        subject_id: str,
        project_id: str,
        instructions: Union[str, None] = None,
    ):
        """
        Invokes an agent template by ID with a subject context.

        Parameters
        ----------
        template_id : str
            Identifier of the agent template to invoke.
        subject_id : str
            Subject identifier that the template will use for context.
        project_id : str
            Project that scopes the template execution.
        instructions : str, optional
            Additional execution instructions scoped to this call.

        Returns
        -------
        phc.ApiResponse
            Response containing a `task_id` referencing the queued invocation.
        """
        if not template_id:
            raise ValueError("template_id is required")
        if not subject_id:
            raise ValueError("subject_id is required")
        if not project_id:
            raise ValueError("project_id is required")

        payload = {
            "template_id": template_id,
            "subject_id": subject_id,
            "project_id": project_id,
        }
        if instructions is not None:
            payload["instructions"] = instructions

        return self._api_call(
            api_path="/template-agent/invoke",
            json=payload,
            http_verb="POST",
        )

    def get_template_invocation(self, task_id: str):
        """
        Fetches the status/result for a template invocation task.

        Parameters
        ----------
        task_id : str
            Identifier returned by `invoke_template`.

        Returns
        -------
        phc.ApiResponse
            Response containing the latest task status/payload.
        """
        if not task_id:
            raise ValueError("task_id is required")

        return self._api_call(
            api_path=f"/template-agent/invocations/{task_id}",
            http_verb="GET",
        )

    def invoke_template_for_subjects(
        self,
        template_id: str,
        subject_ids: List[str],
        project_id: str,
        instructions: Union[str, None] = None,
        *,
        initial_wait_seconds: int = 60,
        poll_interval_seconds: int = 10,
        sleep_fn: Callable[[float], None] = time.sleep,
    ):
        """
        Invokes a template for multiple subjects and waits for each task to finish.

        Parameters
        ----------
        template_id : str
            Identifier of the agent template to invoke.
        subject_ids : List[str]
            Multiple subject identifiers to run the template against.
        project_id : str
            Project that scopes the template execution.
        instructions : str, optional
            Additional execution instructions scoped to this call.
        initial_wait_seconds : int, optional
            Seconds to wait before polling the task statuses (default 60).
        poll_interval_seconds : int, optional
            Seconds to wait between polls once polling begins (default 10).
        sleep_fn : Callable[[float], None], optional
            Sleep implementation to use. Primarily exposed for testing (default time.sleep).

        Returns
        -------
        List[dict]
            A list of task payloads ordered by the provided subject ids.
        """
        if not subject_ids:
            raise ValueError("subject_ids is required")

        ordered_subject_ids = list(subject_ids)
        invocations = []

        for subject_id in ordered_subject_ids:
            response = self.invoke_template(
                template_id=template_id,
                subject_id=subject_id,
                project_id=project_id,
                instructions=instructions,
            )
            payload = getattr(response, "data", None)
            if not isinstance(payload, dict):
                raise ValueError("Template invocation did not return JSON data.")
            task_id = payload.get("id")
            if not task_id:
                raise ValueError("Template invocation response must include 'id'.")
            invocations.append({"subject_id": subject_id, "task_id": task_id})

        if not invocations:
            return []

        sleep_fn(initial_wait_seconds)
        pending_indexes = set(range(len(invocations)))
        completed: Dict[int, dict] = {}

        while pending_indexes:
            for index in list(pending_indexes):
                task_id = invocations[index]["task_id"]
                invocation = self.get_template_invocation(task_id=task_id)
                task_payload = getattr(invocation, "data", None)
                if not isinstance(task_payload, dict):
                    raise ValueError("Task status response must be JSON data.")

                status = task_payload.get("status")
                if _is_task_complete(status):
                    completed[index] = task_payload
                    pending_indexes.remove(index)

            if pending_indexes:
                sleep_fn(poll_interval_seconds)

        return [completed[index] for index in range(len(invocations))]

    def get_token(self):
        """
        Generates a temporary token for agent-based API authentication.

        This method creates a temporary authentication token for use with AI/ML agents
        like LangChain or other API integrations. The token includes AWS credentials
        that can be used to authenticate API calls.

        Permissions
        -----------
        Requires the ABAC policy rule `generateToken`.

        Returns
        -------
        phc.ApiResponse
            An API response object containing:
            - AccessKeyId: AWS access key for authentication
            - SecretAccessKey: AWS secret key for authentication
            - SessionToken: AWS session token for authentication
            - Expiration: Token expiration timestamp

        Example
        --------
        >>> from langchain_aws import ChatBedrock
        >>> from phc.services import Agents
        >>> agent = Agents(session)
        >>> token_resp = agent.get_token()
        >>> chat = ChatBedrock(
        >>>     aws_access_key_id=token_resp.data["AccessKeyId"],
        >>>     aws_secret_access_key=token_resp.data["SecretAccessKey"],
        >>>     aws_session_token=token_resp.data["SessionToken"],
        >>>     model_id="anthropic.claude-3-5-sonnet-20240620-v1:0",
        >>>     model_kwargs={
        >>>         "temperature": 0,
        >>>         "max_tokens": 500,
        >>>     }
        >>> )
        >>> ai_message = await llm.ainvoke([
                (
                    "system",
                    "You are a medical assistant, format below csv data into markdown".
                ),
                (
                    "human", "c,s,v,data"
                )
            ])
        """
        return self._api_call("/v1/agents-v2/token", http_verb="GET")
