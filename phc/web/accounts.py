"""A Python Module for Accounts"""

from phc.web.base_client import BaseClient


class Accounts(BaseClient):
    """Provides acccess to PHC accounts"""

    def get_list(self):
        """Fetch the list of accounts that the current session belongs to.

        Returns:
            [list] -- A list of accounts
        """
        return self._api_call("accounts", http_verb="GET").get("accounts")
