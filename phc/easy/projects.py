import inspect
from typing import Optional

import pandas as pd
from funcy import memoize
from phc.easy.abstract.paging_api_item import PagingApiItem, PagingApiOptions
from phc.easy.auth import Auth
from phc.easy.util import without_keys
from phc.errors import ApiError
from pmap import pmap

SEARCH_COLUMNS = ["name", "description", "id"]


def join_strings(row):
    return " ".join([value for value in row if type(value) == str]).lower()


class ProjectListOptions(PagingApiOptions):
    name: Optional[str]


class Project(PagingApiItem):
    @staticmethod
    def resource_path():
        return "projects"

    @staticmethod
    def params_class():
        return ProjectListOptions

    @classmethod
    @memoize
    def get_data_frame(
        cls,
        name: Optional[str] = None,
        auth_args: Auth = Auth.shared(),
        max_pages: Optional[int] = None,
        page_size: Optional[int] = None,
        log: bool = False,
        show_progress: bool = False,
        account: Optional[str] = None,
    ):
        """Execute a request for projects

        ## Parameters

        Query: `phc.easy.projects.ProjectListOptions`

        Execution: `phc.easy.query.Query.execute_paging_api`
        """

        if page_size is None:
            # Projects do not have much data so use a higher page size
            page_size = 100

        get_data_frame = super().get_data_frame

        auth = Auth(auth_args)

        get_data_frame_args = without_keys(
            cls._get_current_args(inspect.currentframe(), locals()),
            ["auth_args", "account", "show_progress"],
        )

        def get_projects_for_account(account: dict):
            try:
                df = get_data_frame(
                    ignore_cache=True,
                    all_results=max_pages is None,
                    auth_args=auth.customized({"account": account["id"]}),
                    show_progress=show_progress,
                    **get_data_frame_args,
                )
                df["account"] = account["id"]

                return df

            except ApiError as e:
                message = e.response.get("error", "Unknown API error")
                print(f"Skipping \"{account['id']}\" due to \"{message}\"")

                return pd.DataFrame()

        if account:
            return get_projects_for_account({"id": account})

        return pd.concat(
            list(pmap(get_projects_for_account, auth.accounts()))
        ).reset_index(drop=True)

    @staticmethod
    def find(
        search: str,
        account: Optional[str] = None,
        auth_args: Auth = Auth.shared(),
    ):
        """Search for a project using given criteria and return results as a data frame

        Attributes
        ----------
        search : str
            Part of a project's id, name, or description to search for

        auth_args : Any
            The authenication to use for the account and project (defaults to shared)
        """
        projects = Project.get_data_frame(auth_args=auth_args, account=account)
        text = projects[SEARCH_COLUMNS].agg(join_strings, axis=1)
        return projects[text.str.contains(search.lower())]

    @staticmethod
    def set_current(
        search: str, account: Optional[str] = None, auth: Auth = Auth.shared()
    ):
        """Search for a project using given criteria, set it to the authentication
        object, and return the matching projects as a data frame

        Attributes
        ----------
        search : str
            Part of a project's id, name, or description to search for

        auth : Auth
            The authenication to update for the account and project (defaults to shared)
        """
        matches = Project.find(search, account=account, auth_args=auth)

        if len(matches) > 1:
            print("Multiple projects found. Try a more specific search")
        elif len(matches) == 0:
            print(f'No matches found for search "{search}"')
        else:
            project = matches.iloc[0]
            # Uses private method since this is a special case
            auth.update({"account": project.account, "project_id": project.id})

        return matches
