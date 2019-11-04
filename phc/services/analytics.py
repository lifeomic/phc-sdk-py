from phc.base_client import BaseClient
from phc.util import PatientFilterQueryBuilder, DataLakeQuery
from phc import ApiResponse


class Analytics(BaseClient):
    """Provides acccess to PHC accounts

    Parameters
    ----------
    session : phc.Session
        The PHC session
    run_async: bool
        True to return promises, False to return results (default is False)
    timeout: int
        Operation timeout (default is 30)
    """

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

        >>> dataset_id = '19e34782-91c4-4143-aaee-2ba81ed0b206'
        >>> query_string = "SELECT sample_id, gene, impact, amino_acid_change, histology FROM variant WHERE tumor_site='breast'"
        >>> output_file_name = 'query-test-notebook'
        >>> query = DataLakeQuery(dataset_id=dataset_id, query=query_string, output_file_name=output_file_name)

        >>> query_id = client.execute_data_lake_query(query)
        >>> specific_query = client.get_data_lake_query(query_id)
        >>> paginated_dataset_queries = client.list_data_lake_queries(dataset_id=dataset_id)
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
