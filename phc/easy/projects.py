import pandas as pd
from functools import reduce
from funcy import memoize
from phc.easy.auth import Auth
import phc.services as services

SEARCH_COLUMNS = ['name', 'description', 'id']


def join_strings(row):
    return ' '.join([value for value in row if type(value) == str]).lower()


class Project:
    @staticmethod
    @memoize
    def get_data_frame(auth=Auth.shared()):
        def list_projects(acc, account):
            session = auth.custom(account=account['id']).session()

            return [
                *acc, *[{
                    **project, 'account': account['id']
                } for project in services.Projects(
                    session).get_list().data['items']]
            ]

        return pd.DataFrame(reduce(list_projects, auth.accounts(), []))

    @staticmethod
    def set_current(search, auth=Auth.shared()):
        projects = Project.get_data_frame(auth)
        text = projects[SEARCH_COLUMNS].agg(join_strings, axis=1)
        matches = projects[text.str.contains(search.lower())]

        if len(matches) > 1:
            print('Multiple projects found. Try a more specific search')
        elif len(matches) == 0:
            print(f'No matches found for search "{search}"')
        else:
            project = matches.iloc[0]
            auth.set_details(account=project.account, project_id=project.id)

        return matches
