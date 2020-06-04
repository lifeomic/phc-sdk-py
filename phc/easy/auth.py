import os
from phc import Session
from phc.services import Accounts

_shared_auth = None

NOT_SET_ACCOUNT_VALUE = '<SET Auth.shared.account>'


class Auth:
    def __init__(self,
                 account: str,
                 project_id: str,
                 token: str = os.environ.get('PHC_ACCESS_TOKEN')):
        self.account = account
        self.project_id = project_id
        self.token = token

    @staticmethod
    def shared():
        global _shared_auth
        if not _shared_auth:
            _shared_auth = Auth(NOT_SET_ACCOUNT_VALUE,
                                '<SET Auth.shared.project>')

        return _shared_auth

    def set_details(self, account=None, project_id=None, token=None):
        if account:
            self.account = account

        if project_id:
            self.project_id = project_id

        if token:
            self.token = token

        return self

    @staticmethod
    def custom(account=None, project_id=None):
        shared = Auth.shared()

        return Auth(account=account or shared.account,
                    project_id=project_id or shared.project_id,
                    token=shared.token)

    def session(self):
        if self.account == NOT_SET_ACCOUNT_VALUE:
            print('An initial account value is required to use the API')

        return Session(token=self.token, account=self.account)

    def accounts(self):
        return Accounts(self.session()).get_list().data.get('accounts')
