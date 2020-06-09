import os
from phc import Session
from phc.services import Accounts

_shared_auth = None

NOT_SET_ACCOUNT_VALUE = "<SET Auth.shared.account>"


class Auth:
    def __init__(
        self,
        account: str,
        project_id: str,
        token: str = os.environ.get("PHC_ACCESS_TOKEN"),
    ):
        """Create an authentication object that can be shared as a single argument to
        the 'easy' SDK calls

        Attributes
        ----------
        account : str
            The PHC account to authenticate against

        project_id : str
            The ID of the project to pull resources from

        token : str
            (Optional) The API key to use; defaults to the $PHC_ACCESS_TOKEN var

        """
        self.account = account
        self.project_id = project_id
        self.token = token

    @staticmethod
    def shared():
        "Returns the shared authentication singleton"
        global _shared_auth
        if not _shared_auth:
            _shared_auth = Auth(
                NOT_SET_ACCOUNT_VALUE, "<SET Auth.shared.project>"
            )

        return _shared_auth

    def set_details(
        self, account: str = None, project_id: str = None, token: str = None
    ):
        """Set details of authentication for API calls

        Attributes
        ----------
        account : str
            (Optional) The PHC account to authenticate against

        project_id : str
            (Optional) The ID of the project to pull resources from

        token : str
            (Optional) The API key to use
        """
        if account:
            self.account = account

        if project_id:
            self.project_id = project_id

        if token:
            self.token = token

        return self

    @staticmethod
    def custom(account=None, project_id=None):
        """Create a new authentication object from the shared one

        Attributes
        ----------
        account : str
            (Optional) The PHC account to authenticate against

        project_id : str
            (Optional) The ID of the project to pull resources from
        """
        shared = Auth.shared()

        return Auth(
            account=account or shared.account,
            project_id=project_id or shared.project_id,
            token=shared.token,
        )

    def session(self):
        "Create an API session for use with modules not in the 'easy' namespace"
        if self.account == NOT_SET_ACCOUNT_VALUE:
            print("An initial account value is required to use the API")

        return Session(token=self.token, account=self.account)

    def accounts(self):
        "List available accounts for the authenticated user"
        return Accounts(self.session()).get_list().data.get("accounts")
