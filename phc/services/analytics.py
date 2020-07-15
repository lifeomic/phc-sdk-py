import os
import time
import asyncio
from phc.services import files
from phc.base_client import BaseClient
from phc.util import PatientFilterQueryBuilder, DataLakeQuery
from phc import ApiResponse

try:
    import pandas as _pd
except ImportError:
    _has_pandas = False
else:
    _has_pandas = True


class Analytics(BaseClient):
    """Provides acccess to PHC Analytics and Data Lake

    Parameters
    ----------
    session : phc.Session
        The PHC session
    run_async: bool
        True to return promises, False to return results (default is False)
    timeout: int
        Operation timeout (default is 30)
    trust_env: bool
        Get proxies information from HTTP_PROXY / HTTPS_PROXY environment variables if the parameter is True (False by default)
    """

    def execute_sql(
        self, statement: str, project_id: str = None, cohort_id: str = None
    ) -> ApiResponse:
        """Executes a SQL query against Analytics

        Parameters
        ----------
        project_id : str
            The project ID
        cohort_id : str
            The cohort ID
        statement : str
            The SQL statement

        Returns
        -------
        ApiResponse
            The API Response

        Raises
        ------
        ValueError
            If no project or cohort ID is provided

        Examples
        --------
        >>> from phc.services import Analytics
        >>> client = Analytics(session)
        >>> res = client.execute_sql(cohort_id='5a07dedb-fa2a-4cb0-b662-95b23a050221', statement='SELECT patients from patient')
        >>> print(f"Found {len(res.get('data').get('patients'))} patients")
        """
        if not project_id and not cohort_id:
            raise ValueError(
                "Must provide a value for the project or cohort ID"
            )

        payload = {"string_query": statement}

        if project_id:
            payload["dataset_id"] = project_id
        if cohort_id:
            payload["cohort_id"] = cohort_id

        return self._api_call("analytics/dsl", http_verb="POST", json=payload)

    def get_patients(
        self, project_id: str, query_builder: PatientFilterQueryBuilder
    ) -> ApiResponse:
        """Executes a query that returns patients

        Parameters
        ----------
        project_id : str
            The project ID
        query_builder : util.PatientFilterQueryBuilder
            The query builder

        Returns
        -------
        list
            The list of patients

        Examples
        --------
        >>> from phc.services import Analytics
        >>> from phc.util import PatientFilterQueryBuilder
        >>> client = Analytics(session)
        >>> search = PatientFilterQueryBuilder()
        >>> search.patient() \
                .observations() \
                .code(eq='11142-7') \
                .system(eq='http://loinc.org') \
                .value_quantity(lt=40)
        >>> res = client.get_patients(project='5a07dedb-fa2a-4cb0-b662-95b23a050221', query_builder=search)
        >>> print(f"Found {len(res)} patients")
        """
        payload = query_builder.to_dict()
        payload["dataset_id"] = project_id
        return (
            self._api_call("analytics/dsl", http_verb="POST", json=payload)
            .get("data")
            .get("patients")
        )

    def execute_data_lake_query(self, query: DataLakeQuery) -> ApiResponse:
        """Executes a data lake query

        Parameters
        ----------
        query : util.DataLakeQuery
            The query builder

        Returns
        -------
        phc.ApiResponse
            The data lake query

        Examples
        --------
        >>> from phc import Session
        >>> from phc.services import Analytics
        >>> from phc.util import DataLakeQuery

        >>> session = Session()
        >>> client = Analytics(session)

        >>> project_id = '19e34782-91c4-4143-aaee-2ba81ed0b206'
        >>> query_string = "SELECT sample_id, gene, impact, amino_acid_change, histology FROM variant WHERE tumor_site='breast'"
        >>> output_file_name = 'query-test-notebook'
        >>> query = DataLakeQuery(project_id=project_id, query=query_string, output_file_name=output_file_name)

        >>> query_id = client.execute_data_lake_query(query)
        >>> specific_query = client.get_data_lake_query(query_id)
        >>> paginated_dataset_queries = client.list_data_lake_queries(project_id)
        >>> print(query_id)
        """
        payload = query.to_request_dict()
        return self._api_call(
            "analytics/query", http_verb="POST", json=payload
        ).get("queryId")

    def list_data_lake_queries(
        self, project_id: str, page_size: int = 25, next_page_token: str = None
    ) -> ApiResponse:
        """Fetches a list of data lake queries

        Parameters
        ----------
        project_id : str
            The project ID
        page_size : int, optional
            The page size, by default 25
        next_page_token : str, optional
            The next page token, by default None

        Returns
        -------
        phc.ApiResponse
            The data lake list query response
        """
        path = "analytics/query?datasetId=%s&pageSize=%d" % (
            project_id,
            page_size,
        )
        if next_page_token:
            path = "%s&nextPageToken=%s" % (path, next_page_token)
        return self._api_call(path, http_verb="GET")

    def get_data_lake_query(self, query_id: str) -> ApiResponse:
        """Fetches a data lake query

        Parameters
        ----------
        query_id : string
            The query ID

        Returns
        -------
        phc.ApiResponse
            The data lake query get response
        """
        return self._api_call("analytics/query/%s" % query_id, http_verb="GET")

    def list_data_lake_schemas(self, project_id: str) -> ApiResponse:
        """Fetches the data lake table schemas

        Parameters
        ----------
        project_id : string
            The dataset to fetch the table schemas of

        Returns
        -------
        phc.ApiResponse
            The schema for each data lake table
        """
        path = "analytics/data-lake/schema?datasetId=%s" % (project_id)
        return self._api_call(path, http_verb="GET")

    def get_data_lake_schema(self, project_id: str, table: str) -> ApiResponse:
        """Fetches the schema for a specific data lake table

        Parameters
        ----------
        project_id : string
            The dataset to fetch the table schema of

        table : string
            Name of the table

        Returns
        -------
        phc.ApiResponse
            Schema of the specified table
        """
        path = "analytics/data-lake/schema/%s?datasetId=%s" % (
            table,
            project_id,
        )
        return self._api_call(path, http_verb="GET")

    def execute_data_lake_query_to_dataframe(
        self, query: DataLakeQuery, dest_dir: str = os.getcwd()
    ):
        """Executes a data lake query, downloads the result file and converts to a Pandas dataframe.

        To use this method, the 'pandas' module is required.
        Otherwise, an exception will be thrown.

        Parameters
        ----------
        query : util.DataLakeQuery
            The query builder

        dest_dir : string
            Directory the result file will be downloaded to.
            Defaults to the current working directory.

        Returns
        -------
        asyncio.Future || pandas.DataFrame
            A Future if run_async is True, the data lake query result contained in a Pandas dataframe otherwise.

        Examples
        --------
        >>> from phc import Session
        >>> from phc.services import Analytics
        >>> from phc.util import DataLakeQuery

        >>> session = Session()
        >>> client = Analytics(session)

        >>> project_id = '19e34782-91c4-4143-aaee-2ba81ed0b206'
        >>> query_string = "SELECT sample_id, gene, impact, amino_acid_change, histology FROM variant WHERE tumor_site='breast'"
        >>> output_file_name = 'query-dataframe-test'
        >>> query = DataLakeQuery(project_id=project_id, query=query_string, output_file_name=output_file_name)

        >>> dataframe = client.execute_data_lake_query_to_dataframe(query)
        >>> dataframe.head()
        """
        if not _has_pandas:
            raise ImportError("pandas is required")

        future = asyncio.ensure_future(
            self.__execute_data_lake_query_to_dataframe_impl(query, dest_dir),
            loop=self._event_loop,
        )
        return (
            future
            if self.run_async
            else self._event_loop.run_until_complete(future)
        )

    def load_data_lake_result_to_dataframe(
        self, query_id: str, dest_dir: str = os.getcwd()
    ):
        """Downloads the result file of a query and converts to a Pandas dataframe.

        To use this method, the 'pandas' module is required.
        Otherwise, an exception will be thrown.

        Parameters
        ----------
        query_id : string
            Id of the query to load results from

        dest_dir : string
            Directory the result file will be downloaded to.
            Defaults to the current working directory.

        Returns
        -------
        asyncio.Future || pandas.DataFrame
            A Future if run_async is True, the data lake query result contained in a Pandas dataframe otherwise.
        """
        if not _has_pandas:
            raise ImportError("pandas is required")

        future = asyncio.ensure_future(
            self.__load_data_lake_result_to_dataframe_impl(query_id, dest_dir),
            loop=self._event_loop,
        )
        return (
            future
            if self.run_async
            else self._event_loop.run_until_complete(future)
        )

    async def __execute_data_lake_query_to_dataframe_impl(
        self, query: DataLakeQuery, dest_dir: str
    ):
        """Internal method for execting a data lake query, downloads the result file and converts to a Pandas dataframe.

        This method exists to support either async or synchronous execution.

        Parameters
        ----------
        query : util.DataLakeQuery
            The query builder

        dest_dir : string
            Directory the result file will be downloaded to

        Returns
        -------
        pandas.DataFrame
            The data lake query result contained in a Pandas dataframe.
        """
        analytics_client = (
            Analytics(self.session, run_async=False, timeout=self.timeout, trust_env=self.trust_env)
            if self.run_async
            else self
        )
        query_id = analytics_client.execute_data_lake_query(query)

        if not self.__poll_predicate(
            self.__data_lake_query_predicate, 3600, analytics_client, query_id
        ):
            raise RuntimeError(
                f"Timed out waiting for query {query_id} to complete"
            )

        return await self.__load_data_lake_result_to_dataframe_impl(
            query_id, dest_dir
        )

    async def __load_data_lake_result_to_dataframe_impl(
        self, query_id: str, dest_dir: str
    ):
        """Internal method for loading an existing data lake query result to a Pandas dataframe.

        This method exists to support either async or synchronous execution.

        Parameters
        ----------
        query_id : string
            Id of the query to load results from

        dest_dir : string
            Directory the result file will be downloaded to

        Returns
        -------
        pandas.DataFrame
            The data lake query result contained in a Pandas dataframe.
        """
        analytics_client = (
            Analytics(self.session, run_async=False, timeout=self.timeout, trust_env=self.trust_env)
            if self.run_async
            else self
        )
        analytics_client.get_data_lake_query(
            query_id
        )  # verify the query exists, an exception will be thrown if it does not

        files_client = files.Files(
            self.session, run_async=False, timeout=self.timeout, trust_env=self.trust_env
        )
        if not self.__poll_predicate(files_client.exists, 30, query_id):
            raise RuntimeError(
                f"Timed out waiting for result file {query_id} to become available"
            )

        download_path = files_client.download(query_id)
        return _pd.read_csv(download_path)

    def __data_lake_query_predicate(self, analytics_client, query_id):
        """Checks if a query has completed successfully.

        If the query was cancelled or failed an exception will be thrown.

        Parameters
        ----------
        analytics_client : phc.services.Analytics
            Instance of the Analytics client

        query_id : string
            Id of the query to check for completion

        Returns
        -------
        bool
            True if the query is in the 'succeeded' state, False if 'running'.
        """
        response = analytics_client.get_data_lake_query(query_id)
        state = response.get("state")

        if state == "failed" or state == "cancelled":
            raise RuntimeError(f"Query {query_id} is {state}")
        return state == "succeeded"

    def __poll_predicate(self, predicate, timeout_sec, *args, **kwargs):
        """Executes a function until it returns a truthy value or the timeout is reached.

        This method will wait 2 seconds between predicate function executions.

        Parameters
        ----------
        predicate : function
            Function to invoke until it returns a truthy value

        timeout_sec : int
            The number of seconds to wait until timing out

        args : list
            The positional args to invoke the predicate function with

        kwargs : dict
            The keyword args to invoke the predicate function with
        Returns
        -------
        bool
            True if the function evaluated to True, False otherwise.
        """
        timeout_time = time.time() + timeout_sec
        while timeout_time > time.time():
            if predicate(*args, **kwargs):
                return True
            time.sleep(2)
        return False
