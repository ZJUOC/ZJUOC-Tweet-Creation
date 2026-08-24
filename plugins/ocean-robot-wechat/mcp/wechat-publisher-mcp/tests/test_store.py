from __future__ import annotations

import pytest

from wechat_publisher_mcp.store import IdempotencyStore


@pytest.mark.asyncio
async def test_idempotency_store_preserves_first_result(tmp_path: object) -> None:
    path = tmp_path / "state.db"  # type: ignore[operator]
    store = IdempotencyStore(str(path))
    await store.initialize()

    first = await store.put("draft", "primary", "same-key", {"media_id": "first"})
    second = await store.put("draft", "primary", "same-key", {"media_id": "second"})
    loaded = await store.get("draft", "primary", "same-key")

    assert first == {"media_id": "first"}
    assert second == {"media_id": "first"}
    assert loaded == {"media_id": "first"}
