import pandas as pd

from phc.easy.auth import Auth
from phc.easy.frame import Frame
from phc.easy.patients.address import expand_address_column
from phc.easy.patients.name import expand_name_column
from phc.easy.query import Query


class Patient:
    @staticmethod
    def get_count(query_overrides: dict = {}, auth_args=Auth.shared()):
        return Query.find_count_of_dsl_query(
            {
                "type": "select",
                "columns": "*",
                "from": [{"table": "patient"}],
                **query_overrides,
            },
            auth_args=auth_args,
        )

    @staticmethod
    def transform_results(data_frame: pd.DataFrame, **expand_args):
        args = {
            **expand_args,
            "custom_columns": [
                *expand_args.get("custom_columns", []),
                ("address", expand_address_column),
                ("name", expand_name_column),
            ],
        }

        return Frame.expand(data_frame, **args)

    @staticmethod
    def get_data_frame(
        limit: int = 100,
        all_results: bool = False,
        raw: bool = False,
        query_overrides: dict = {},
        auth_args: Auth = Auth.shared(),
        ignore_cache: bool = False,
        expand_args: dict = {},
    ):
        """Retrieve patients as a data frame with unwrapped FHIR columns

        Attributes
        ----------
        limit : int
            The number of patients to retrieve

        all_results : bool = False
            Override limit to retrieve all patients

        raw : bool = False
            If raw, then values will not be expanded (useful for manual
            inspection if something goes wrong). Note that this option will
            override all_results if True.

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
        >>> phc.Patient.get_data_frame()

        """
        query = {
            "type": "select",
            "columns": "*",
            "from": [{"table": "patient"}],
            "limit": [
                {"type": "number", "value": 0},
                {"type": "number", "value": limit},
            ],
            **query_overrides,
        }

        def transform(df: pd.DataFrame):
            return Patient.transform_results(df, **expand_args)

        return Query.execute_fhir_dsl_with_options(
            query,
            transform,
            all_results,
            raw,
            query_overrides,
            auth_args,
            ignore_cache,
        )
