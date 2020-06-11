import os
from typing import Union, Dict, Any
from phc import Session
from phc.services import Accounts
from phc.easy.util import defaultprop

_shared_auth = None


class Auth:
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
        """
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
        return os.environ.get("PHC_PROJECT_ID")

    def session(self):
        "Create an API session for use with modules not in the 'easy' namespace"
        return Session(token=self.token, account=self.account)

    def accounts(self):
        "List available accounts for the authenticated user"
        return Accounts(self.session()).get_list().data.get("accounts")

    def details(self):
        return {
            "account": self.account,
            "project_id": self.project_id,
            "token": self.token,
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
