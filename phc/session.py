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

        Parameters
        ----------
        token : str, optional
            The PHC access token or API key, by default os.environ.get("PHC_ACCESS_TOKEN")
        account : str, optional
            The PHC account ID, by default os.environ.get("PHC_ACCOUNT")
        """
        self.token = token
        self.account = account
