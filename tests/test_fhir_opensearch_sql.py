from phc import Session
import os
from phc.services import Fhir
from unittest.mock import patch
from test_session import jwt, sample


@patch("phc.base_client.BaseClient._api_call")
def test_es_sql(mock_api_call):
    session = Session(token=jwt.encode(sample, "secret"), account="bar")
    fhir = Fhir(session)
    project_id = "bar"
    query = "SELECT id, subject FROM diagnostic_report WHERE identifier.system = ? LIMIT 10"
    params = [
        {
            "type": "string",
            "value": "lrn:lo:dev:fountainlife:ehr:fountainlife:d22c690b-fb45-4ff2-8cb3-eed9f665cb30/DiagnosticReport",
        }
    ]

    res = fhir.es_sql(
        project_id=project_id,
        statement=query,
        params=params,
    )

    mock_api_call.assert_called_once()
    args, kwargs = mock_api_call.call_args

    assert kwargs["api_path"] == f"fhir-search/sql/projects/{project_id}"
    assert kwargs["json"]["query"] == query
    assert kwargs["json"]["parameters"] == params
