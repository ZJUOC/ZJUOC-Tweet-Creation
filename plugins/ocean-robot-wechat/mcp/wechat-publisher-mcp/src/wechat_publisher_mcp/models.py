from __future__ import annotations

from typing import Any, Literal

from pydantic import BaseModel, Field, field_validator


class DraftArticle(BaseModel):
    title: str = Field(min_length=1, max_length=128)
    content: str = Field(min_length=1)
    thumb_media_id: str = Field(min_length=1)
    author: str | None = Field(default=None, max_length=64)
    digest: str | None = Field(default=None, max_length=256)
    content_source_url: str | None = Field(default=None, max_length=1024)
    need_open_comment: Literal[0, 1] = 1
    only_fans_can_comment: Literal[0, 1] = 0

    @field_validator("content")
    @classmethod
    def reject_scripts(cls, value: str) -> str:
        if "<script" in value.lower():
            raise ValueError("article content must not contain script tags")
        return value


class AccountSummary(BaseModel):
    alias: str
    name: str
    account_type: Literal["subscription", "service"]


class UploadResult(BaseModel):
    account_alias: str
    kind: Literal["content_image", "cover"]
    url: str | None = None
    media_id: str | None = None


class DraftResult(BaseModel):
    account_alias: str
    media_id: str
    idempotency_key: str
    reused: bool = False


class PublishResult(BaseModel):
    account_alias: str
    publish_id: str
    idempotency_key: str
    reused: bool = False


class ApiResult(BaseModel):
    account_alias: str
    data: dict[str, Any]
