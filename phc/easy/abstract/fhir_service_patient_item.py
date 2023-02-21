from typing import List, Optional, Union

import pandas as pd
from phc.easy.abstract.fhir_service_item import FhirServiceItem
from phc.easy.auth import Auth
from phc.easy.query import Query
from phc.easy.query.fhir_dsl_query import DEFAULT_MAX_TERMS


class FhirServicePatientItem(FhirServiceItem):
    """Provides an abstract class and/or static methods for retrieving items
    from a FSS table that relates to a patient
    """

    @staticmethod
    def patient_key() -> str:
        return "subject.reference"

    @staticmethod
    def patient_id_prefixes() -> List[str]:
        return ["Patient/"]

    @classmethod
    def get_data_frame(
        cls,
        all_results: bool = False,
        raw: bool = False,
        id: Optional[str] = None,
        ids: List[str] = [],
        patient_id: Union[None, str] = None,
        patient_ids: List[str] = [],
        device_id: Union[None, str] = None,
        device_ids: List[str] = [],
        page_size: Union[int, None] = None,
        max_pages: Union[int, None] = None,
        query_overrides: dict = {},
        auth_args=Auth.shared(),
        ignore_cache: bool = False,
        expand_args: dict = {},
        log: bool = False,
        # Terms
        term: Optional[dict] = None,
        terms: List[dict] = [],
        max_terms: int = DEFAULT_MAX_TERMS,
        # Codes
        code: Optional[Union[str, List[str]]] = None,
        display: Optional[Union[str, List[str]]] = None,
        system: Optional[Union[str, List[str]]] = None,
        code_fields: List[str] = [],
    ):
        """Retrieve records

        Attributes
        ----------
        all_results : bool = False
            Retrieve sample of results (10) or entire set of records

        raw : bool = False
            If raw, then values will not be expanded (useful for manual
            inspection if something goes wrong)

        id : None or str = None
            Find records for a given id

        ids : List[str]
            Find records for given ids

        patient_id : None or str = None
            Find records for a given patient_id

        patient_ids : List[str]
            Find records for given patient_ids

        device_id: None or str = None
            Find records for a given device_id

        device_ids: List[str]
            Find records for given device_ids

        page_size : int
            The number of records to fetch per page

        max_pages : int
            The number of pages to retrieve (useful if working with tons of records)

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

        max_terms : int
            Maximum terms per query clause before chunking into multiple requests

        term : dict
            Add an arbitrary ES term/s to the query (includes chunking)

        terms : dict
            Add multiple arbitrary ES term/s to the query (includes chunking)

        code : str | List[str]
            Adds where clause for code value(s)

        display : str | List[str]
            Adds where clause for code display value(s)

        system : str | List[str]
            Adds where clause for code system value(s)

        code_fields : List[str]
            A list of paths to find FHIR codes in (default: codes for the given entity)

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

        code_fields = [*cls.code_fields(), *code_fields]

        def transform(df: pd.DataFrame):
            return cls.transform_results(df, **expand_args)

        # TODO: As of Feb 2023, only observations with patient references are indexed.
        # So in order to query for observations associated with a device we have to set the
        # device_id to the patient_id.
        # This is a workaround and should be fixed once The Platform properly indexes devices.
        if device_id:
            patient_id = device_id

        if device_ids:
            patient_ids = device_ids

        return Query.execute_fhir_dsl_with_options(
            query,
            transform,
            all_results,
            raw,
            query_overrides,
            auth_args,
            ignore_cache,
            id=id,
            ids=ids,
            patient_id=patient_id,
            patient_ids=patient_ids,
            page_size=page_size,
            max_pages=max_pages,
            patient_key=cls.patient_key(),
            log=log,
            patient_id_prefixes=cls.patient_id_prefixes(),
            # Terms
            term=term,
            terms=terms,
            max_terms=max_terms,
            # Codes
            code_fields=code_fields,
            code=code,
            display=display,
            system=system,
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
