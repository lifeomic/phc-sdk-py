from typing import Dict, List, Union
from phc.base_client import BaseClient


class Agents(BaseClient):
    """
    Provides access to the PHC agents API, which allows you to call LLM-based agents.
    """

    def invoke_basic(self, body: Union[str, List[Dict]]):
        """
        Invokes a basic agent, which supports either a basic prompt string or a list of
        messages which can include images as data urls.
        """
        return self._api_call(
            "/v1/agents/basic/invoke", json={"input": body}, http_verb="POST"
        )
