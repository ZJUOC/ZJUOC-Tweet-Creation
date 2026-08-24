# Repository guidance

- Manage Python and dependencies with `uv`; do not add `requirements.txt`.
- Keep the stable MCP Python SDK on the `1.x` line until `2.x` is stable.
- Never log or commit WeChat `AppSecret`, access tokens, MCP bearer tokens, or article bodies.
- Default all workflows to draft creation. Formal publishing requires both explicit user confirmation and `MCP_ALLOW_PUBLISH=true`.
- Run `uv run ruff check .`, `uv run pytest`, and the MCP smoke test before shipping changes.
- Keep WeChat API calls inside `wechat.py`; keep MCP orchestration and safety gates inside `tools.py`.
