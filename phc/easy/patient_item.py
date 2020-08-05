from typing import Union, List

import pandas as pd

from phc.easy.auth import Auth
from phc.easy.query import Query
from phc.easy.util import without_keys


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

    @staticmethod
    def code_keys() -> List[str]:
        "Returns the code keys (e.g. when searching for codes)"
        return []

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
        patient_ids: List[str] = [],
        query_overrides: dict = {},
        auth_args=Auth.shared(),
        ignore_cache: bool = False,
        expand_args: dict = {},
        log: bool = False,
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

        log : bool = False
            Whether to log some diagnostic statements for debugging

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
        query = {
            "type": "select",
            "columns": "*",
            "from": [{"table": cls.table_name()}],
        }

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
            patient_id=patient_id,
            patient_ids=patient_ids,
            patient_key=cls.patient_key(),
            log=log,
        )

    @classmethod
    def get_codes(cls, **kwargs):
        """Find all codes

        See possible argments for :func:`~phc.easy.query.Query.get_codes`

        Examples
        --------
        >>> import phc.easy as phc
        >>> phc.Auth.set({'account': '<your-account-name>'})
        >>> phc.Project.set_current('My Project Name')
        >>>
        >>> phc.Observation.get_codes(patient_id="<id>", max_pages=3)
        """
        code_fields = [*cls.code_keys(), *kwargs.get("code_fields", [])]

        return Query.get_codes(
            table_name=cls.table_name(),
            code_fields=code_fields,
            **without_keys(kwargs, ["code_fields"]),
        )

    @classmethod
    def get_count_by_field(cls, field: str, **kwargs):
        """Count records by a given field

        See argments for :func:`~phc.easy.query.Query.get_count_by_field`

        Attributes
        ----------
        field : str
            The field name to count the values of (e.g. "gender")

        Examples
        --------
        >>> import phc.easy as phc
        >>> phc.Auth.set({'account': '<your-account-name>'})
        >>> phc.Project.set_current('My Project Name')
        >>>
        >>> phc.Observation.get_count_by_field('category.coding.code')
        """
        return Query.get_count_by_field(
            table_name=cls.table_name(), field=field, **kwargs
        )

    @classmethod
    def get_count_by_patient(cls, **kwargs):
        """Count records by a given field

        See argments for :func:`~phc.easy.query.Query.get_count_by_field`

        Examples
        --------
        >>> import phc.easy as phc
        >>> phc.Auth.set({'account': '<your-account-name>'})
        >>> phc.Project.set_current('My Project Name')
        >>>
        >>> phc.Observation.get_count_by_patient()
        """
        patient_key = cls.patient_key()

        df = Query.get_count_by_field(
            table_name=cls.table_name(), field=cls.patient_key(), **kwargs
        )

        # Make keys consistent (some are prefixed while others are not)
        df[patient_key] = df[patient_key].str.replace("Patient/", "")

        return df.groupby(patient_key).sum()
