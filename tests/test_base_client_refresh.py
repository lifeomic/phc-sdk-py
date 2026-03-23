"""Tests for OAuth token refresh in BaseClient."""

import os
import time
from unittest.mock import patch

import jwt
import pytest

from phc.api_response import ApiResponse
from phc.base_client import BaseClient
from phc.session import Session


def _access_jwt(
    *,
    exp_offset: int = 3600,
    client_id: str = "test-client-id",
) -> str:
    payload = {
        "client_id": client_id,
        "exp": int(time.time()) + exp_offset,
        "iss": "https://cognito-idp.us-east-1.amazonaws.com/pool",
        "token_use": "access",
    }
    return jwt.encode(payload, "secret", algorithm="HS256")


@pytest.fixture
def expired_session(monkeypatch):
    monkeypatch.setenv(
        "PHC_ACCESS_TOKEN",
        _access_jwt(exp_offset=-60),
    )
    monkeypatch.setenv("PHC_REFRESH_TOKEN", "old-refresh")
    monkeypatch.setenv("PHC_ACCOUNT", "test-account")
    return Session()


def test_refresh_updates_session_tokens_and_env(expired_session, monkeypatch):
    new_access = _access_jwt(exp_offset=7200)
    new_refresh = "rotated-refresh-token"

    mock_res = ApiResponse(
        client=None,
        http_verb="POST",
        api_url="https://api.dev.lifeomic.com/v1/oauth/token",
        req_args={},
        data={
            "access_token": new_access,
            "refresh_token": new_refresh,
        },
        headers={},
        status_code=200,
    )

    client = BaseClient(expired_session)
    with patch.object(client, "_api_call_impl", return_value=mock_res):
        client._refresh_token()

    assert expired_session.token == new_access
    assert expired_session.refresh_token == new_refresh
    assert os.environ["PHC_ACCESS_TOKEN"] == new_access
    assert os.environ["PHC_REFRESH_TOKEN"] == new_refresh


def test_refresh_keeps_refresh_when_api_omits_rotation(
    expired_session, monkeypatch
):
    new_access = _access_jwt(exp_offset=7200)

    mock_res = ApiResponse(
        client=None,
        http_verb="POST",
        api_url="https://api.dev.lifeomic.com/v1/oauth/token",
        req_args={},
        data={"access_token": new_access},
        headers={},
        status_code=200,
    )

    client = BaseClient(expired_session)
    with patch.object(client, "_api_call_impl", return_value=mock_res):
        client._refresh_token()

    assert expired_session.token == new_access
    assert expired_session.refresh_token == "old-refresh"
    assert os.environ["PHC_ACCESS_TOKEN"] == new_access
    assert os.environ["PHC_REFRESH_TOKEN"] == "old-refresh"


def test_refresh_does_not_create_env_without_phc_vars(monkeypatch):
    """Sessions not using PHC_* env should not get env vars injected."""
    for key in ("PHC_ACCESS_TOKEN", "PHC_REFRESH_TOKEN", "PHC_ACCOUNT"):
        monkeypatch.delenv(key, raising=False)
    exp = int(time.time()) - 10
    token = jwt.encode(
        {
            "client_id": "cid",
            "exp": exp,
            "iss": "https://cognito-idp.us-east-1.amazonaws.com/x",
            "token_use": "access",
        },
        "secret",
        algorithm="HS256",
    )
    session = Session(
        token=token,
        refresh_token="r1",
        account="acct",
    )
    assert "PHC_ACCESS_TOKEN" not in os.environ

    new_access = _access_jwt(exp_offset=3600)
    mock_res = ApiResponse(
        client=None,
        http_verb="POST",
        api_url="https://api.dev.lifeomic.com/v1/oauth/token",
        req_args={},
        data={"access_token": new_access},
        headers={},
        status_code=200,
    )

    client = BaseClient(session)
    with patch.object(client, "_api_call_impl", return_value=mock_res):
        client._refresh_token()

    assert "PHC_ACCESS_TOKEN" not in os.environ
    assert session.token == new_access
