from typing import Dict, List, Union
from phc.base_client import BaseClient


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
            "/v1/agents/basic/invoke", json={"input": body}, http_verb="POST"
        )

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
        return self._api_call("/v1/agents/token", http_verb="GET")
