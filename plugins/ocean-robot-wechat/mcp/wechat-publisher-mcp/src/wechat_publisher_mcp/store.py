from __future__ import annotations

import asyncio
import json
import sqlite3
from pathlib import Path
from typing import Any


class IdempotencyStore:
    def __init__(self, path: str) -> None:
        self.path = Path(path).expanduser().resolve()
        self._lock = asyncio.Lock()

    async def initialize(self) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        await asyncio.to_thread(self._initialize_sync)

    def _connect(self) -> sqlite3.Connection:
        connection = sqlite3.connect(self.path, timeout=10)
        connection.execute("PRAGMA journal_mode=WAL")
        return connection

    def _initialize_sync(self) -> None:
        with self._connect() as connection:
            connection.execute(
                """
                CREATE TABLE IF NOT EXISTS idempotency_results (
                    operation TEXT NOT NULL,
                    account_alias TEXT NOT NULL,
                    idempotency_key TEXT NOT NULL,
                    response_json TEXT NOT NULL,
                    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                    PRIMARY KEY (operation, account_alias, idempotency_key)
                )
                """
            )

    async def get(
        self, operation: str, account_alias: str, idempotency_key: str
    ) -> dict[str, Any] | None:
        async with self._lock:
            return await asyncio.to_thread(
                self._get_sync, operation, account_alias, idempotency_key
            )

    def _get_sync(
        self, operation: str, account_alias: str, idempotency_key: str
    ) -> dict[str, Any] | None:
        with self._connect() as connection:
            row = connection.execute(
                """
                SELECT response_json FROM idempotency_results
                WHERE operation = ? AND account_alias = ? AND idempotency_key = ?
                """,
                (operation, account_alias, idempotency_key),
            ).fetchone()
        return json.loads(row[0]) if row else None

    async def put(
        self,
        operation: str,
        account_alias: str,
        idempotency_key: str,
        response: dict[str, Any],
    ) -> dict[str, Any]:
        async with self._lock:
            return await asyncio.to_thread(
                self._put_sync, operation, account_alias, idempotency_key, response
            )

    def _put_sync(
        self,
        operation: str,
        account_alias: str,
        idempotency_key: str,
        response: dict[str, Any],
    ) -> dict[str, Any]:
        encoded = json.dumps(response, ensure_ascii=False, separators=(",", ":"))
        with self._connect() as connection:
            connection.execute(
                """
                INSERT OR IGNORE INTO idempotency_results
                    (operation, account_alias, idempotency_key, response_json)
                VALUES (?, ?, ?, ?)
                """,
                (operation, account_alias, idempotency_key, encoded),
            )
            row = connection.execute(
                """
                SELECT response_json FROM idempotency_results
                WHERE operation = ? AND account_alias = ? AND idempotency_key = ?
                """,
                (operation, account_alias, idempotency_key),
            ).fetchone()
        if row is None:
            raise RuntimeError("failed to persist idempotency result")
        return json.loads(row[0])
