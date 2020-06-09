import os

import pandas as pd
from phc.easy.auth import Auth
from phc.easy.frame import Frame
from phc.easy.patients.address import expand_address_column
from phc.easy.patients.name import expand_name_column
from phc.services import Fhir


class Patient:
    @staticmethod
    def get_data_frame(limit: int, raw: bool = False, auth=Auth.shared()):
        """Retrieve all patients (up to limit) as a data frame with unwrapped FHIR columns



        Attributes
        ----------


        """
        fhir = Fhir(auth.session())
        response = fhir.execute_sql(
            auth.project_id, f"SELECT * FROM patient LIMIT {limit}"
        )

        actual_count = response.data["hits"]["total"]["value"]
        if actual_count > limit:
            print(f"Retrieved {limit}/{actual_count} patients")

        df = pd.DataFrame(
            [hit["_source"] for hit in response.data.get("hits").get("hits")]
        )

        if raw:
            return df

        return Frame.expand(
            df,
            custom_columns=[
                ("address", expand_address_column),
                ("name", expand_name_column),
            ],
        )
