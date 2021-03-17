import json

from phc.base_client import BaseClient
from phc.easy.auth import Auth
from phc.easy.ocr.options.ocr_config_types import Config as OcrConfig


class Config:
    @staticmethod
    def create(config: OcrConfig, auth_args: Auth = Auth.shared()):
        auth = Auth(auth_args)
        client = BaseClient(auth.session())

        return client._api_call(
            "ocr/config",
            json={
                "project": auth.project_id,
                "config": json.loads(config.json(exclude_none=True)),
            },
        ).data

    @staticmethod
    def get(auth_args: Auth = Auth.shared()):
        auth = Auth(auth_args)
        client = BaseClient(auth.session())

        return client._api_call(
            f"ocr/config/{auth.project_id}", http_verb="GET"
        ).data
