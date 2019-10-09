"""A Python Module for managing PHC sessions."""

import os


class Session:
    """Represents a PHC API session"""

    def __init__(
        self,
        token: str = os.environ.get("PHC_ACCESS_TOKEN"),
        account: str = os.environ.get("PHC_ACCOUNT"),
    ):
        """Initailizes a Session with token and account credentials.

        Keyword Arguments:
            token {str} -- The access token (default: {PHC_ACCESS_TOKEN env var})
            account {str} -- The account (default: {PHC_ACCOUNT env var})
        """
        self.token = token
        self.account = account
