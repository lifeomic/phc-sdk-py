"""A Python Module for managing PHC sessions."""

import os
import jwt
import time


class Session:
    """Represents a PHC API session"""

    def __init__(
        self,
        token: str = os.environ.get("PHC_ACCESS_TOKEN"),
        refresh_token: str = os.environ.get("PHC_REFRESH_TOKEN"),
        account: str = os.environ.get("PHC_ACCOUNT"),
    ):
        """Initailizes a Session with token and account credentials.

        Parameters
        ----------
        token : str, required
            The PHC access token or API key, by default os.environ.get("PHC_ACCESS_TOKEN")
        refrsh_token : str, optional
            The PHC refresh token, by default os.environ.get("PHC_REFRESH_TOKEN")
        account : str, required
            The PHC account ID, by default os.environ.get("PHC_ACCOUNT")
        """
        if not token or not account:
            raise ValueError("Must provide a value for both token and account")

        self.token = token
        self.refresh_token = refresh_token
        self.account = account
        env = (
            "dev"
            if "cognito-idp.us-east-1.amazonaws.com"
            in self._get_decoded_token().get("iss")
            or "api.dev.lifeomic.com" in self._get_decoded_token().get("iss")
            else "us"
        )
        self.api_url = f"https://api.{env}.lifeomic.com/v1/"
        self.fhir_url = f"https://fhir.{env}.lifeomic.com/{account}/dstu3/"
        self.ga4gh_url = f"https://ga4gh.{env}.lifeomic.com/{account}/v1/"

    def _get_decoded_token(self):
        if self.token:
            return jwt.decode(self.token, verify=False)
        return {}

    def is_expired(self) -> bool:
        """Determines if the current access token is expired

        Returns
        -------
        bool
            True if there is no token or the token is expired, otherwise False
        """
        return self._get_decoded_token().get("exp", 0) < time.time()
