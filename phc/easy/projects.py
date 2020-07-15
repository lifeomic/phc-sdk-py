from functools import reduce

import pandas as pd

import phc.services as services
from funcy import memoize
from phc.easy.auth import Auth

SEARCH_COLUMNS = ["name", "description", "id"]


def join_strings(row):
    return " ".join([value for value in row if type(value) == str]).lower()


class Project:
    @staticmethod
    @memoize
    def get_data_frame(auth_args=Auth.shared()):
        """Retrieve a list of projects from the authenticated account

        Attributes
        ----------
        auth_args : Any
            The authenication to use for the account and project (defaults to shared)
        """
        auth = Auth(auth_args)

        def list_projects(acc, account):
            session = auth.customized({"account": account["id"]}).session()

            return [
                *acc,
                *[
                    {**project, "account": account["id"]}
                    for project in services.Projects(session)
                    .get_list()
                    .data["items"]
                ],
            ]

        return pd.DataFrame(reduce(list_projects, auth.accounts(), []))

    @staticmethod
    def find(search: str, auth_args: Auth = Auth.shared()):
        """Search for a project using given criteria and return results as a data frame

        Attributes
        ----------
        search : str
            Part of a project's id, name, or description to search for

        auth_args : Any
            The authenication to use for the account and project (defaults to shared)
        """
        auth = Auth(auth_args)
        projects = Project.get_data_frame(auth)
        text = projects[SEARCH_COLUMNS].agg(join_strings, axis=1)
        return projects[text.str.contains(search.lower())]

    @staticmethod
    def set_current(search: str, auth: Auth = Auth.shared()):
        """Search for a project using given criteria, set it to the authentication
        object, and return the matching projects as a data frame

        Attributes
        ----------
        search : str
            Part of a project's id, name, or description to search for

        auth : Auth
            The authenication to update for the account and project (defaults to shared)
        """
        matches = Project.find(search, auth)

        if len(matches) > 1:
            print("Multiple projects found. Try a more specific search")
        elif len(matches) == 0:
            print(f'No matches found for search "{search}"')
        else:
            project = matches.iloc[0]
            # Uses private method since this is a special case
            auth.update({"account": project.account, "project_id": project.id})

        return matches
