from phc.easy.auth import Auth, _shared_auth


def test_basic_use():
    auth = Auth(
        {
            "token": "my-token",
            "account": "my-account",
            "project_id": "my-project-id",
        }
    )

    assert auth.account == "my-account"


def test_updating_attributes():
    auth = Auth(
        {
            "token": "my-token",
            "account": "my-account",
            "project_id": "my-project-id",
        }
    )

    assert auth.customized({"account": "new-account"}).account == "new-account"


def test_updated_shared_auth():
    # Capture existing shared values
    shared = Auth.shared()
    original_account = shared.account
    original_token = shared.token

    Auth.set({"account": "research"})

    assert shared.account == "research"
    assert shared.token == original_token

    # Reset shared object
    Auth.set({"account": original_account, "token": original_token})


def test_custom_auth():
    shared = Auth.shared()
    original_account = shared.account
    original_token = shared.token

    auth = Auth.custom({"account": "research"})

    assert auth.account == "research"
    assert auth.token == original_token

    # Does not change shared auth object
    assert shared.account == original_account
    assert shared.token == original_token


def test_creating_auth_from_another_auth_object():
    auth = Auth({"account": "demo"})

    auth1 = Auth(auth)
    assert auth1.account == "demo"
