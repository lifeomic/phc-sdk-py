import os
from typing import Any, Dict, Union

from phc import Session
from phc.adapter import Adapter
from phc.easy.util import defaultprop
from phc.services import Accounts

_shared_auth = None


class Auth:
    token: str
    project_id: str
    account: str
    adapter: Adapter

    def __init__(self, details: Union[Any, None, Dict[str, str]] = None):
        """Create an authentication object that can be shared as a single argument to
        the 'easy' SDK calls

        Attributes
        ----------
        details : Auth | dict | None

          A dictionary representation of the token, account, and/or project id.
          Can also be another authentication object. Will use environment
          variables as the default.

          account : str
              The PHC account to authenticate against
              Defaults to $PHC_ACCOUNT

          project_id : str
              (Optional) The ID of the project to pull resources from
              Defaults to $PHC_PROJECT_ID

          token : str
              (Optional) The API key to use
              Defaults to $PHC_ACCESS_TOKEN

          adapter: Adapter
              (Optional) A custom adapter to execute requests
              Defaults to normal API adapter
        """
        if _shared_auth:
            # Start with shared credentials
            self.update(_shared_auth.details())

        self.update(details)

    @staticmethod
    def custom(details: Union[None, Dict[str, str]]):
        "Returns customized auth object from the shared one"
        return Auth.shared().customized(details)

    @staticmethod
    def set(details: Union[None, Dict[str, str]]):
        "Updates and returns the shared authentication singleton"
        shared = Auth.shared()
        shared.update(details)
        return shared

    @staticmethod
    def shared():
        global _shared_auth

        if not _shared_auth:
            _shared_auth = Auth()

        return _shared_auth

    def customized(self, details: Union[None, Dict[str, str]]):
        "Returns copied, customized auth object from this object"
        custom = self.__copy()
        custom.update(details)
        return custom

    @defaultprop
    def token(self):
        return os.environ.get("PHC_ACCESS_TOKEN")

    @defaultprop
    def account(self):
        return os.environ.get("PHC_ACCOUNT")

    @defaultprop
    def project_id(self):
        env_project_id = os.environ.get("PHC_PROJECT_ID")

        if env_project_id is None:
            raise ValueError("No project_id has been selected.")

        return env_project_id

    @defaultprop
    def adapter(self):
        return Adapter()

    def session(self):
        "Create an API session for use with modules not in the 'easy' namespace"
        return Session(
            token=self.token, account=self.account, adapter=self.adapter
        )

    def accounts(self):
        "List available accounts for the authenticated user"
        return Accounts(self.session()).get_list().data.get("accounts")

    def details(self):
        return {
            "account": self.account,
            "project_id": getattr(self, "_project_id", None),
            "token": self.token,
            "adapter": self.adapter,
        }

    def __copy(self):
        return Auth(self)

    def update(self, details: Union[Any, None, Dict[str, str]] = None):
        """Set details of authentication for API calls
        (Prefer auth.customized unless mutation is required.)

        Attributes
        ----------
        details : Auth | dict | None

          A dictionary representation of the token, account, and/or project id.
          Can also be another authentication object. Will use environment
          variables as the default.

          account : str
              The PHC account to authenticate against
              Defaults to $PHC_ACCOUNT

          project_id : str
              (Optional) The ID of the project to pull resources from
              Defaults to $PHC_PROJECT_ID

          token : str
              (Optional) The API key to use
              Defaults to $PHC_ACCESS_TOKEN

          adapter: Adapter
              (Optional) A custom adapter to execute requests
              Defaults to normal API adapter
        """
        if details is None:
            return

        if type(details) == Auth:
            auth = details
            details = auth.details()

        if details.get("account"):
            self._account = details.get("account")

        if details.get("project_id"):
            self._project_id = details.get("project_id")

        if details.get("token"):
            self._token = details.get("token")

        if details.get("adapter"):
            self._adapter = details.get("adapter")
