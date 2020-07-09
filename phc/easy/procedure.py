from typing import Union

import pandas as pd

from phc.easy.auth import Auth
from phc.easy.frame import Frame
from phc.easy.patient_item import PatientItem
from phc.easy.query import Query


class Procedure:
    @staticmethod
    def get_count(query_overrides: dict = {}, auth_args=Auth.shared()):
        return Query.find_count_of_dsl_query(
            {
                "type": "select",
                "columns": "*",
                "from": [{"table": "procedure"}],
                **query_overrides,
            },
            auth_args=auth_args,
        )

    @staticmethod
    def transform_results(data_frame: pd.DataFrame, **expand_args):
        args = {
            **expand_args,
            "date_columns": [
                *expand_args.get("date_columns", []),
                "performedPeriod.start",
                "performedPeriod.end",
            ],
            "custom_columns": [
                *expand_args.get("custom_columns", []),
                Frame.codeable_like_column_expander("subject"),
                Frame.codeable_like_column_expander("performedPeriod"),
            ],
        }

        return Frame.expand(data_frame, **args)

    @staticmethod
    def get_data_frame(
        all_results: bool = False,
        raw: bool = False,
        patient_id: Union[None, str] = None,
        query_overrides: dict = {},
        auth_args=Auth.shared(),
        ignore_cache: bool = False,
        expand_args: dict = {},
    ):
        """Retrieve procedures

        Attributes
        ----------
        all_results : bool = False
            Retrieve sample of results (10) or entire set of procedures

        raw : bool = False
            If raw, then values will not be expanded (useful for manual
            inspection if something goes wrong)

        patient_id : None or str = None
            Find procedures for a given patient_id

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
        >>> phc.Procedure.get_data_frame(patient_id='<patient-id>')
        """
        query = PatientItem.build_query("procedure", patient_id)

        def transform(df: pd.DataFrame):
            return Procedure.transform_results(df, **expand_args)

        return Query.execute_fhir_dsl_with_options(
            query,
            transform,
            all_results,
            raw,
            query_overrides,
            auth_args,
            ignore_cache,
        )
