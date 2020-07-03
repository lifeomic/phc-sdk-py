from typing import Union
import pandas as pd
from phc.easy.auth import Auth
from phc.easy.query import Query


class PatientItem:
    @staticmethod
    def retrieve_raw_data_frame(
        table_name: str,
        all_results: bool = False,
        patient_id: Union[None, str] = None,
        query_overrides: dict = {},
        auth_args=Auth.shared(),
    ):
        """Retrieve results for a given table that relates to a patient

        Attributes
        ----------
        table_name : str
            The name of the elasticsearch FHIR table

        all_results : bool = False
            Retrieve sample of results (10) or entire set of the table records

        patient_id : None or str = None
            Find table records for a given patient_id

        query_overrides : dict = {}
            Override any part of the elasticsearch FHIR query

        auth_args : Any
            The authenication to use for the account and project (defaults to shared)

        expand_args : Any
            Additional arguments passed to phc.Frame.expand

        Examples
        --------
        >>> import phc.easy as phc
        >>> phc.Auth.set({'account': '<your-account-name>'})
        >>> phc.Project.set_current('My Project Name')
        >>> phc.PatientItem.retrieve_raw_data_frame("observation", patient_id='<patient-id>')
        """

        query = {
            "type": "select",
            "columns": "*",
            "from": [{"table": table_name}],
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

        return pd.DataFrame(map(lambda r: r["_source"], results))
