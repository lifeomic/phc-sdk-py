from typing import Dict
import phc.easy as phc
import pandas as pd
from toolz import pipe
from functools import partial
from pmap import pmap
import queue

NOT_SELECTED = "[Not Selected]"


def load_entities(auth: phc.Auth, fetch_counts: bool = True):
    counts = pipe(
        dir(phc),
        partial(map, partial(getattr, phc)),
        partial(
            filter,
            lambda m: (
                type(m) == type
                and issubclass(m, phc.Item)
                and m not in [phc.Item, phc.PatientItem]
            ),
        ),
        partial(
            pmap,
            lambda m: (
                m,
                m.get_count(auth_args=auth) if fetch_counts else None,
            ),
        ),
        partial(pd.DataFrame, columns=["module", "count"]),
    )

    if not fetch_counts:
        return counts

    return (
        counts.query("(count > 0)")
        .sort_values(["count", "module"], ascending=False)
        .reset_index(drop=True)
    )


class State:
    auth: phc.Auth

    account: str
    queue: queue.Queue

    _project: dict
    _projects: pd.DataFrame
    _all_entity_counts: Dict[str, pd.DataFrame]
    _fetch_counts: bool

    def __init__(self, auth: phc.auth = phc.Auth.shared(), fetch_counts=True):
        self.auth = auth
        self.account = NOT_SELECTED
        self.queue = queue.Queue()
        self._project = {}
        self._projects = pd.DataFrame()
        self._all_entity_counts = {}
        self._fetch_counts = fetch_counts

    def load_projects(self):
        self._projects = phc.Project.get_data_frame()

    def select_project(self, project_id: str):
        projects = self.projects

        assert len(projects) > 0

        self.project = projects[projects.id == project_id].iloc[0].to_dict()

    @property
    def accounts(self):
        return self._projects.account.unique()

    @property
    def project(self):
        return self._project

    @project.setter
    def project(self, project: dict):
        self._project = project

        self.auth.update(
            {"account": project["account"], "project_id": project["id"]}
        )

    @property
    def projects(self):
        return self._projects[self._projects.account == self.account]

    @property
    def entity_counts(self):
        project_id = self.project.get("id")

        if project_id is None:
            return pd.DataFrame([], columns=["module", "count"])

        if self._all_entity_counts.get(project_id) is None:
            self._all_entity_counts[project_id] = load_entities(
                self.auth, fetch_counts=self._fetch_counts
            )

        return self._all_entity_counts[project_id]
