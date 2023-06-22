from typing import Optional
from phc.base_client import BaseClient
from phc.util import PatientFilterQueryBuilder
from phc import ApiResponse


class Analytics(BaseClient):
    """Provides acccess to PHC Analytics

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
        self,
        statement: str,
        project_id: Optional[str] = None,
        cohort_id: Optional[str] = None,
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
