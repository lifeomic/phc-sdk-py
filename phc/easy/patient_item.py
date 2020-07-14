from typing import Union

import pandas as pd

from phc.easy.auth import Auth
from phc.easy.query import Query


class PatientItem:
    """Provides an abstract class and/or static methods for retrieving items
    from a FSS table that relates to a patient
    """

    @staticmethod
    def table_name() -> str:
        "Returns the FSS table name for retrieval"
        raise ValueError("Table name should be implemented by subclass")

    @staticmethod
    def patient_key() -> str:
        return "subject.reference"

    @classmethod
    def get_count(cls, query_overrides: dict = {}, auth_args=Auth.shared()):
        "Get the count for a given FSS query"
        return Query.find_count_of_dsl_query(
            {
                "type": "select",
                "columns": "*",
                "from": [{"table": cls.table_name()}],
                **query_overrides,
            },
            auth_args=auth_args,
        )

    @staticmethod
    def transform_results(data_frame: pd.DataFrame, **expand_args):
        "Transform data frame batch"
        return data_frame

    @classmethod
    def get_data_frame(
        cls,
        all_results: bool = False,
        raw: bool = False,
        patient_id: Union[None, str] = None,
        query_overrides: dict = {},
        auth_args=Auth.shared(),
        ignore_cache: bool = False,
        expand_args: dict = {},
    ):
        """Retrieve records

        Attributes
        ----------
        all_results : bool = False
            Retrieve sample of results (10) or entire set of records

        raw : bool = False
            If raw, then values will not be expanded (useful for manual
            inspection if something goes wrong)

        patient_id : None or str = None
            Find records for a given patient_id

        query_overrides : dict = {}
            Override any part of the elasticsearch FHIR query

        auth_args : Any
            The authenication to use for the account and project (defaults to shared)

        ignore_cache : bool = False
            Bypass the caching system that auto-saves results to a CSV file.
            Caching only occurs when all results are being retrieved.

        expand_args : Any
            Additional arguments passed to phc.Frame.expand

        Examples
        --------
        >>> import phc.easy as phc
        >>> phc.Auth.set({'account': '<your-account-name>'})
        >>> phc.Project.set_current('My Project Name')
        >>>
        >>> phc.Observation.get_data_frame(patient_id='<patient-id>')
        >>>
        >>> phc.Goal.get_data_frame(patient_id='<patient-id>')
        """
        query = PatientItem.build_query(
            cls.table_name(), patient_id, cls.patient_key()
        )

        def transform(df: pd.DataFrame):
            return cls.transform_results(df, **expand_args)

        return Query.execute_fhir_dsl_with_options(
            query,
            transform,
            all_results,
            raw,
            query_overrides,
            auth_args,
            ignore_cache,
        )

    @staticmethod
    def build_query(
        table_name: str,
        patient_id: Union[None, str] = None,
        patient_key: str = "subject.reference",
    ) -> dict:
        """Build query for a given table that relates to a patient

        Attributes
        ----------
        table_name : str
            The name of the elasticsearch FHIR table

        patient_id : None or str = None
            Find table records for a given patient_id
        """

        query = {
            "type": "select",
            "columns": "*",
            "from": [{"table": table_name}],
        }

        if patient_id:
            return {
                **query,
                "where": {
                    "type": "elasticsearch",
                    "query": {
                        "terms": {
                            f"{patient_key}.keyword": [
                                patient_id,
                                f"Patient/{patient_id}",
                            ]
                        }
                    },
                },
            }

        return query
