import pandas as pd
from phc.base_client import BaseClient
from phc.easy.auth import Auth


class GeneSet:
    def get_data_frame(auth_args: Auth = Auth.shared()):
        auth = Auth(auth_args)
        client = BaseClient(auth.session())

        response = client._api_call(
            "knowledge/gene-sets",
            http_verb="GET",
            params={"datasetId": auth.project_id},
        )

        frame = pd.DataFrame(response.data["items"])

        if "genes" in frame.columns:
            frame["genes"] = frame.genes.apply(
                lambda genes: ",".join([d["gene"] for d in genes])
            )

        frame = frame.drop(["datasetId"], errors="ignore")

        return frame
