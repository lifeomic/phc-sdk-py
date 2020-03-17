"""A Python Module for Accounts"""

from phc.base_client import BaseClient
from phc import ApiResponse


class Accounts(BaseClient):
    """Provides acccess to PHC accounts

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

    def get_list(self) -> ApiResponse:
        """Fetches the list of accounts for the current session

        Returns
        -------
        phc.ApiResponse
            The list accounts response
        """
        return self._api_call("accounts", http_verb="GET")
