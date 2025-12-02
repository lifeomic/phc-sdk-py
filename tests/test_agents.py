from unittest.mock import patch

from phc import Session
from phc.services import Agents
from test_session import jwt, sample


@patch("phc.base_client.BaseClient._api_call")
def test_invoke_template(mock_api_call):
    session = Session(token=jwt.encode(sample, "secret"), account="test-account")
    agents = Agents(session)

    template_id = "tmpl_123"
    subject_id = "pat_123"
    project_id = "proj_456"
    instructions = "Summarize the latest encounters."

    agents.invoke_template(
        template_id=template_id,
        subject_id=subject_id,
        project_id=project_id,
        instructions=instructions,
    )

    mock_api_call.assert_called_once()
    _, kwargs = mock_api_call.call_args

    assert kwargs["api_path"] == "/template-agent/invoke"
    assert kwargs["json"] == {
        "template_id": template_id,
        "subject_id": subject_id,
        "project_id": project_id,
        "instructions": instructions,
    }
    assert kwargs["http_verb"] == "POST"


@patch("phc.base_client.BaseClient._api_call")
def test_get_template_invocation(mock_api_call):
    session = Session(token=jwt.encode(sample, "secret"), account="test-account")
    agents = Agents(session)

    task_id = "task_abc"

    agents.get_template_invocation(task_id=task_id)

    mock_api_call.assert_called_once()
    _, kwargs = mock_api_call.call_args

    assert kwargs["api_path"] == f"/template-agent/invocations/{task_id}"
    assert kwargs["http_verb"] == "GET"
