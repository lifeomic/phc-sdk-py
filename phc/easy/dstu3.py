import json
from typing import Callable

from phc.base_client import BaseClient
from phc.easy.auth import Auth
from phc.errors import ApiError


class DSTU3:
    entity: str

    def __init__(self, entity: str):
        self.entity = entity

    def get(
        self,
        record_id: str,
        auth_args: Auth = Auth.shared(),
        return_if_not_found=True,
    ):
        """Perform a GET on the DSTU3 resource"""
        auth = Auth(auth_args)
        client = BaseClient(auth.session())

        try:
            response = client._fhir_call(
                f"{self.entity}/{record_id}", http_verb="GET"
            ).data
        except ApiError as e:
            if return_if_not_found and e.response.data == "Not Found":
                return None

            raise e

        return json.loads(response)

    def update(
        self,
        record_id: str,
        update: Callable[[dict], dict],
        auth_args: Auth = Auth.shared(),
    ):
        """Perform an update on the DSTU3 resource through an update function"""
        data = self.get(
            record_id, auth_args=auth_args, return_if_not_found=False
        )

        return self.put(record_id, update(data), auth_args)

    def put(self, record_id: str, data: dict, auth_args: Auth = Auth.shared()):
        """Perform a PUT on the DSTU3 resource

        (Recommended to use `update(...)` unless a direct PUT is required.)
        """
        auth = Auth(auth_args)
        client = BaseClient(auth.session())

        response = client._fhir_call(
            f"{self.entity}/{record_id}", http_verb="PUT", json=data
        )

        if 200 <= response.status_code < 300:
            return response.data

        raise ValueError(f"Unexpected response: {response}")

    def create(self, data: dict, auth_args: Auth = Auth.shared()):
        """Perform a POST for the DSTU3 resource"""
        auth = Auth(auth_args)
        client = BaseClient(auth.session())

        response = client._fhir_call(
            f"{self.entity}", http_verb="POST", json=data
        )

        if 200 <= response.status_code < 300:
            return response.data

        raise ValueError(f"Unexpected response: {response}")

    def delete(self, record_id: str, auth_args: Auth = Auth.shared()):
        """Perform a DELETE for the DSTU3 resource

        Returns nothing.
        """
        auth = Auth(auth_args)
        client = BaseClient(auth.session())

        return client._fhir_call(
            f"{self.entity}/{record_id}", http_verb="DELETE"
        ).data
