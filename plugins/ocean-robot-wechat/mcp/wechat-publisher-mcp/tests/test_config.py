from __future__ import annotations

import json

import pytest

from wechat_publisher_mcp.config import Settings, load_accounts


def base_settings(**overrides: object) -> Settings:
    values: dict[str, object] = {
        "mcp_bearer_token": "test-token-0123456789abcdef",
        "wechat_app_id": "wx-test",
        "wechat_app_secret": "secret",
    }
    values.update(overrides)
    return Settings(_env_file=None, **values)


def test_load_single_account() -> None:
    accounts = load_accounts(
        base_settings(
            wechat_account_alias="primary",
            wechat_account_name="Primary",
            wechat_account_type="service",
        )
    )

    assert list(accounts) == ["primary"]
    assert accounts["primary"].name == "Primary"
    assert accounts["primary"].account_type == "service"
    assert accounts["primary"].app_secret.get_secret_value() == "secret"


def test_load_multiple_accounts_from_json() -> None:
    raw = {
        "subscription": {
            "name": "Subscription",
            "account_type": "subscription",
            "app_id": "wx-one",
            "app_secret": "one-secret",
        },
        "service": {
            "name": "Service",
            "account_type": "service",
            "app_id": "wx-two",
            "app_secret": "two-secret",
        },
    }
    accounts = load_accounts(base_settings(wechat_accounts_json=json.dumps(raw)))

    assert set(accounts) == {"subscription", "service"}
    assert accounts["service"].app_id == "wx-two"


def test_reject_invalid_account_alias() -> None:
    raw = {
        "Not Valid": {
            "name": "Bad",
            "app_id": "wx-bad",
            "app_secret": "bad-secret",
        }
    }

    with pytest.raises(ValueError, match="account alias"):
        load_accounts(base_settings(wechat_accounts_json=json.dumps(raw)))
