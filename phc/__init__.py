"""
.. include:: ../README.md
"""
from phc.web.session import Session
from phc.web.accounts import Accounts
from phc.web.projects import Projects
from phc.web.fhir import Fhir
from phc.web.analytics import Analytics
from phc.web.patient_filter_query_builder import PatientFilterQueryBuilder
from phc.web.data_lake_query import DataLakeQuery
from phc.errors import ClientError, RequestError, ApiError

__all__ = [
    "Session",
    "Accounts",
    "Projects",
    "Fhir",
    "Analytics",
    "PatientFilterQueryBuilder",
    "DataLakeQuery",
    "ClientError",
    "RequestError",
    "ApiError",
]

__pdoc__ = {"web": False, "errors": False, "version": False}
