"""A Python Module for Projects"""

from phc.web.base_client import BaseClient
from urllib.parse import urlencode


class Projects(BaseClient):
    """Provides acccess to PHC projects"""

    def create(self, name, description=None):
        """Creates a project.

        Returns:
            [Dict] -- created project
        """
        json_body = {"name": name}
        if description:
            json_body["description"] = description
        return self._api_call("projects", json=json_body, http_verb="POST").data

    def get(self, project):
        """Fetch a project by id.

        Returns:
            [Dict] -- project details
        """
        return self._api_call(
            "projects/{}".format(project), http_verb="GET"
        ).data

    def update(self, project, name, description=None):
        """Fetch a project by id.

        Returns:
            [Dict] -- project details
        """
        json_body = {"name": name}
        if description:
            json_body["description"] = description
        return self._api_call(
            "projects/{}".format(project), json=json_body, http_verb="PATCH"
        ).data

    def delete(self, project):
        """Deletes a project.

        Returns:
          [Boolean] -- True upon successful deletion
        """
        return (
            self._api_call(
                "projects/{}".format(project), http_verb="DELETE"
            ).status_code
            == 204
        )

    def get_list(
        self,
        page_size: int = None,
        next_page_token: str = None,
        name: str = None,
    ):
        """Fetch the list of projects that the current session belongs to.

        Returns:
            [Dict] -- A list of projects as pages
        """
        query_dict = {}
        if page_size:
            query_dict["pageSize"] = page_size
        if next_page_token:
            query_dict["nextPageToken"] = next_page_token
        if name:
            query_dict["name"] = name
        api_response = self._api_call(
            "projects?{}".format(urlencode(query_dict)), http_verb="GET"
        )

        retVal = {"items": api_response.get("items")}
        if "next" in api_response.get("links"):
            link_next = api_response.get("links")["next"]
            retVal["next_page_token"] = link_next[
                link_next.find("=") + 1 : link_next.find("&")
            ]

        return retVal
