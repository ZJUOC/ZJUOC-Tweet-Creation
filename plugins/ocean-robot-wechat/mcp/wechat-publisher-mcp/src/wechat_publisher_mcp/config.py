from __future__ import annotations

import json
import re
from typing import Literal

from pydantic import BaseModel, Field, SecretStr, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

ACCOUNT_ALIAS_RE = re.compile(r"^[a-z0-9][a-z0-9_-]{0,31}$")


class AccountCredential(BaseModel):
    alias: str
    name: str
    account_type: Literal["subscription", "service"] = "subscription"
    app_id: str
    app_secret: SecretStr

    @field_validator("alias")
    @classmethod
    def validate_alias(cls, value: str) -> str:
        if not ACCOUNT_ALIAS_RE.fullmatch(value):
            raise ValueError("account alias must match [a-z0-9][a-z0-9_-]{0,31}")
        return value


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    mcp_bearer_token: SecretStr = Field(min_length=24)
    mcp_public_base_url: str = "http://127.0.0.1:8000"
    mcp_host: str = "127.0.0.1"
    mcp_port: int = Field(default=8000, ge=1, le=65535)
    mcp_allow_publish: bool = False
    mcp_state_path: str = "./data/state.db"
    max_upload_bytes: int = Field(default=2 * 1024 * 1024, ge=1024)
    log_level: str = "INFO"

    wechat_api_base_url: str = "https://api.weixin.qq.com"
    wechat_accounts_json: str | None = None
    wechat_account_alias: str = "primary"
    wechat_account_name: str = "Primary account"
    wechat_account_type: Literal["subscription", "service"] = "subscription"
    wechat_app_id: str | None = None
    wechat_app_secret: SecretStr | None = None

    @field_validator("mcp_public_base_url", "wechat_api_base_url")
    @classmethod
    def strip_trailing_slash(cls, value: str) -> str:
        return value.rstrip("/")


def load_accounts(settings: Settings) -> dict[str, AccountCredential]:
    if settings.wechat_accounts_json:
        try:
            raw = json.loads(settings.wechat_accounts_json)
        except json.JSONDecodeError as exc:
            raise ValueError("WECHAT_ACCOUNTS_JSON is not valid JSON") from exc

        if isinstance(raw, list):
            items = raw
        elif isinstance(raw, dict):
            items = []
            for alias, value in raw.items():
                if not isinstance(value, dict):
                    raise ValueError("each WECHAT_ACCOUNTS_JSON entry must be an object")
                items.append({"alias": alias, **value})
        else:
            raise ValueError("WECHAT_ACCOUNTS_JSON must be an object or array")

        accounts = [AccountCredential.model_validate(item) for item in items]
    else:
        if not settings.wechat_app_id or not settings.wechat_app_secret:
            raise ValueError(
                "configure WECHAT_APP_ID and WECHAT_APP_SECRET, or WECHAT_ACCOUNTS_JSON"
            )
        accounts = [
            AccountCredential(
                alias=settings.wechat_account_alias,
                name=settings.wechat_account_name,
                account_type=settings.wechat_account_type,
                app_id=settings.wechat_app_id,
                app_secret=settings.wechat_app_secret,
            )
        ]

    by_alias = {account.alias: account for account in accounts}
    if len(by_alias) != len(accounts):
        raise ValueError("WeChat account aliases must be unique")
    if not by_alias:
        raise ValueError("at least one WeChat account is required")
    return by_alias
