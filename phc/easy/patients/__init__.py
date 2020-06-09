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
        limit : int
            The number of patients to retrieve

        raw : bool = False
            If raw, then values will not be expanded (useful for manual
            inspection if something goes wrong)

        auth : Auth
            The authenication to use for the account and project (defaults to shared)

        Examples
        --------
        >>> import phc.easy as phc
        >>> phc.Auth.shared().set_details(account='<your-account-name>')
        >>> phc.Project.set_current('My Project Name')
        >>> phc.Patient.get_data_frame(limit=100)
        """
        fhir = Fhir(auth.session())

        # TODO: Add scrolling of patient resources
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
