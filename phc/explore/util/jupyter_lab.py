import json
import os
from toolz import pipe
from functools import partial
import re

USER_SETTINGS_PATH = os.path.expanduser(
    "~/.jupyter/lab/user-settings/@jupyterlab/apputils-extension/themes.jupyterlab-settings"
)


class JupyterLab:
    @staticmethod
    def user_settings() -> dict:
        if not os.path.exists(USER_SETTINGS_PATH):
            return {}

        with open(USER_SETTINGS_PATH, "r") as f:
            return pipe(f.read(), partial(re.sub, r"\/\/.*", ""), json.loads)

    @classmethod
    def is_dark_theme(cls) -> bool:
        return cls.user_settings().get("theme") == "JupyterLab Dark"
