from typing import List, Optional, Union

import pandas as pd
from phc.easy.auth import Auth
from phc.easy.dstu3 import DSTU3
from phc.easy.query import Query
from phc.easy.query.fhir_dsl_query import DEFAULT_MAX_TERMS
from phc.easy.util import without_keys
from phc.util.string_case import snake_to_title_case


class ClassProperty(property):
    """Magic python to create a classmethod property to make it look like you're
    just accessing a nested resource (but will actually have access to the class
    resources and can dynamically return a result)

    Usage:

    class MyClass:
        @ClassProperty
        @classmethod
        def Method(cls):
            return OtherClass(cls.entity)

    MyClass.Method  => <# OtherClass(entity: ...) #>
    """

    def __get__(self, cls, owner):
        return self.fget.__get__(None, owner)()


class FhirServiceItem:
    """Provides an abstract class and/or static methods for retrieving items
    from a FSS table
    """

    @ClassProperty
    @classmethod
    def DSTU3(cls) -> DSTU3:
        """Return a DSTU3 instance with the entity name configured

        Usage:
            phc.Patient.DSTU3.get(...)
        """
        try:
            # Must wrap in try/except since docs try to access this on abstract classes
            # where table_name() throws a ValueError
            table_name = cls.table_name()
        except Exception:
            table_name = ""

        return DSTU3(snake_to_title_case(table_name))

    @staticmethod
    def table_name() -> str:
        "Returns the FSS table name for retrieval"
        raise ValueError("Table name should be implemented by subclass")

    @staticmethod
    def code_fields() -> List[str]:
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
    def transform_results(data_frame: pd.DataFrame, **_expand_args):
        "Transform data frame batch"
        return data_frame

    @classmethod
    def get_data_frame(
        cls,
        all_results: bool = False,
        raw: bool = False,
        page_size: Union[int, None] = None,
        max_pages: Union[int, None] = None,
        query_overrides: dict = {},
        auth_args=Auth.shared(),
        ignore_cache: bool = False,
        expand_args: dict = {},
        log: bool = False,
        id: Optional[str] = None,
        ids: List[str] = [],
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

        id : None or str = None
            Find records for a given id

        ids : List[str]
            Find records for given ids

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

        return Query.execute_fhir_dsl_with_options(
            query,
            transform,
            all_results,
            raw,
            query_overrides,
            auth_args,
            ignore_cache,
            page_size=page_size,
            max_pages=max_pages,
            log=log,
            # Terms
            term=term,
            terms=terms,
            max_terms=max_terms,
            # Codes
            code_fields=code_fields,
            code=code,
            display=display,
            system=system,
            id=id,
            ids=ids,
        )

    @classmethod
    def get_codes(
        cls,
        display_query: Optional[str] = None,
        sample_size: Optional[int] = None,
        exclude_meta_tag=True,
        **kwargs,
    ):
        """Find all codes

        See possible argments for `phc.easy.query.Query.get_codes`

        Examples
        --------
        >>> import phc.easy as phc
        >>> phc.Auth.set({'account': '<your-account-name>'})
        >>> phc.Project.set_current('My Project Name')
        >>>
        >>> phc.Observation.get_codes(patient_id="<id>", max_pages=3)
        """
        code_fields = [*cls.code_fields(), *kwargs.get("code_fields", [])]

        # Meta tag can significantly clutter things up since it's often a date
        # value instead of a real code
        if exclude_meta_tag:
            code_fields = [
                field for field in code_fields if field != "meta.tag"
            ]

        return Query.get_codes(
            display_query=display_query,
            sample_size=sample_size,
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
