import jwt
from uuid import uuid4

from phc.session import Session

sample = {
    "account": "test",
    "username": "test_john.doe113@example.com",
    "version": "1",
    "token_use": "access",
    "rnd": "blah==",
    "iat": 1611587012,
    "exp": 1623452314,
    "iss": "https://api.dev.lifeomic.com/v1/api-keys",
    "jti": str(uuid4()),
}


def test_session_env_dev_parsing():
    token = jwt.encode(sample, "secret")
    session = Session(token, account=sample["account"])
    assert session.api_url == "https://api.dev.lifeomic.com/v1/"


def test_session_env_prod_parsing():
    token = jwt.encode(
        {**sample, "iss": "https://api.us.lifeomic.com/v1/api-keys"}, "secret"
    )

    session = Session(token, account=sample["account"])
    assert session.api_url == "https://api.us.lifeomic.com/v1/"
