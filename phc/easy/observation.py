from typing import Union
import pandas as pd
from phc.easy.query import Query
from phc.easy.frame import Frame
from phc.easy.auth import Auth


class Observation:
    @staticmethod
    def get_data_frame(
        all_results: bool = False,
        raw: bool = False,
        patient_id: Union[None, str] = None,
        query_overrides: dict = {},
        auth_args=Auth.shared(),
        expand_args: dict = {},
    ):
        """Retrieve observations

        Attributes
        ----------
        all_results : bool = False
            Retrieve sample of results (10) or entire set of observations

        raw : bool = False
            If raw, then values will not be expanded (useful for manual
            inspection if something goes wrong)

        patient_id : None or str = None
            Find observations for a given patient_id

        auth_args : Any
            The authenication to use for the account and project (defaults to shared)

        expand_args : Any
            Additional arguments passed to phc.Frame.expand

        Examples
        --------
        >>> import phc.easy as phc
        >>> phc.Auth.set({'account': '<your-account-name>'})
        >>> phc.Project.set_current('My Project Name')
        >>> phc.Observation.get_data_frame(patient_id='<patient-id>')
        """
        query = {
            "type": "select",
            "columns": "*",
            "from": [{"table": "observation"}],
        }

        if patient_id:
            query = {
                **query,
                "where": {
                    "type": "elasticsearch",
                    "query": {
                        "terms": {
                            "subject.reference.keyword": [
                                patient_id,
                                f"Patient/{patient_id}",
                            ]
                        }
                    },
                },
            }

        query = {**query, **query_overrides}

        results = Query.execute_dsl(query, all_results, auth_args)

        df = pd.DataFrame(map(lambda r: r["_source"], results))

        if raw:
            return df

        return Frame.expand(df, **expand_args)
