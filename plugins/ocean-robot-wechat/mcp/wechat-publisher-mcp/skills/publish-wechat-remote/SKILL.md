---
name: publish-wechat-remote
description: Prepare, upload, save, inspect, and formally publish WeChat Official Account articles through the authenticated wechat_publisher remote MCP server. Use when the user asks to post Markdown, HTML, plain text, covers, or inline images to a subscription or service account; manage WeChat drafts; test account API access; or check a publication result.
---

# Publish WeChat Remote

Use the remote MCP server as the only WeChat API execution surface. Keep account secrets out of prompts and tool arguments.

## Safety rules

- Default ambiguous requests such as “发公众号” or “发布文章” to creating a draft.
- Call `wechat_publish_draft` only after the user explicitly requests formal publication and the target account plus draft `media_id` are known.
- Set `confirmed=true` only for that explicit request. Never infer confirmation from an earlier draft request.
- Never ask for or pass `AppSecret`, `access_token`, `.env` contents, or MCP bearer tokens through tools.
- Reuse the same idempotency key when retrying an uncertain result. Never invent a new key just to bypass a prior call.

## Workflow

1. Call `wechat_list_accounts` and resolve the target alias. Ask only when multiple accounts remain plausible.
2. For first use or credential diagnosis, call `wechat_check_account`. Stop on an IP-white-list or interface-permission error.
3. Resolve the article title, author, summary, body, cover, source URL, comment policy, and target account.
4. Convert Markdown or plain text to clean WeChat-compatible HTML. Remove scripts, forms, iframes, event handlers, and unsupported interactive markup.
5. For every non-WeChat inline image:
   - Read the local file and base64-encode its bytes.
   - Call `wechat_upload_content_image` with the true MIME type and plain filename.
   - Replace the corresponding HTML `src` with the returned HTTPS URL.
6. Upload the cover through `wechat_upload_cover` and retain its `media_id`.
7. Derive a stable key such as `draft:<account>:<content-sha256-prefix>`. Call `wechat_create_draft` with one to eight articles.
8. Report the account alias and draft `media_id`. Do not formally publish unless the safety rules are satisfied.
9. For an explicitly approved formal publication:
   - Derive `publish:<account>:<media-id>` as the stable key.
   - Call `wechat_publish_draft` once with `confirmed=true`.
   - Query `wechat_get_publish_status` using the returned `publish_id`; report submission separately from final success.

## Draft inspection

- Use `wechat_list_drafts` with `no_content=true` for discovery.
- Use `wechat_get_draft` only for the selected `media_id` when full content is needed.
- Do not send article HTML back to the user unless they request it; summaries are usually sufficient.

## Failure handling

- Treat API error `40164` as an incorrect server IP white list.
- Treat API error `48001` as missing account/interface permission.
- On token expiry, let the server refresh automatically; retry with the same idempotency key.
- On an unknown transport result after a write, query drafts or publication status before retrying.
- If formal publishing is disabled, leave the article in drafts and state that `MCP_ALLOW_PUBLISH=true` is required on the server.

Read [references/setup.md](references/setup.md) when MCP tools are missing, authentication fails, an account must be added, or deployment configuration is required.
