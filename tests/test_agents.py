from types import SimpleNamespace
from unittest.mock import MagicMock, call, patch

import pytest

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


@patch.object(Agents, "get_template_invocation")
@patch.object(Agents, "invoke_template")
def test_invoke_template_for_subjects(mock_invoke_template, mock_get_template_invocation):
    session = Session(token=jwt.encode(sample, "secret"), account="test-account")
    agents = Agents(session)

    subject_ids = ["pat_1", "pat_2"]
    template_id = "tmpl_123"
    project_id = "proj_456"

    mock_invoke_template.side_effect = [
        SimpleNamespace(data={"id": "task_1"}),
        SimpleNamespace(data={"id": "task_2"}),
    ]

    mock_get_template_invocation.side_effect = [
        SimpleNamespace(data={"id": "task_1", "status": "processing", "subjectId": "pat_1"}),
        SimpleNamespace(data={"id": "task_2", "status": "pending", "subjectId": "pat_2"}),
        SimpleNamespace(data={"id": "task_1", "status": "completed", "subjectId": "pat_1"}),
        SimpleNamespace(data={"id": "task_2", "status": "failed", "subjectId": "pat_2"}),
    ]

    sleep_mock = MagicMock()

    statuses = agents.invoke_template_for_subjects(
        template_id=template_id,
        subject_ids=subject_ids,
        project_id=project_id,
        initial_wait_seconds=0,
        poll_interval_seconds=0,
        sleep_fn=sleep_mock,
    )

    assert statuses == [
        {"id": "task_1", "status": "completed", "subjectId": "pat_1"},
        {"id": "task_2", "status": "failed", "subjectId": "pat_2"},
    ]

    assert mock_invoke_template.call_count == 2
    mock_invoke_template.assert_has_calls(
        [
            call(
                template_id=template_id,
                subject_id="pat_1",
                project_id=project_id,
                instructions=None,
            ),
            call(
                template_id=template_id,
                subject_id="pat_2",
                project_id=project_id,
                instructions=None,
            ),
        ]
    )

    assert mock_get_template_invocation.call_count == 4
    assert sleep_mock.call_args_list == [call(0), call(0)]


def test_invoke_template_for_subjects_requires_subject_ids():
    session = Session(token=jwt.encode(sample, "secret"), account="test-account")
    agents = Agents(session)

    with pytest.raises(ValueError):
        agents.invoke_template_for_subjects(
            template_id="tmpl",
            subject_ids=[],
            project_id="proj",
        )
