import pandas as pd
from phc.easy.frame import Frame
from phc.base_client import BaseClient
from phc.easy.auth import Auth


class Gene:
    def get_data_frame(search: str = "", auth_args: Auth = Auth.shared()):
        auth = Auth(auth_args)
        client = BaseClient(auth.session())

        response = client._api_call(
            "knowledge/genes",
            http_verb="GET",
            params={"datasetId": auth.project_id, "gene": search},
        )

        frame = pd.DataFrame(response.data["items"])

        if "alias" in frame.columns:
            frame["alias"] = frame.alias.apply(
                lambda aliases: ",".join(aliases)
                if isinstance(aliases, list)
                else None
            )

        # We choose to not expand topCancerDrivers and cancerDrivers since it
        # can easily have 50 values in each. If we really need those, the user
        # will have to extract those.
        return frame
