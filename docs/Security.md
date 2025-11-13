# Security Guide

## Authentication
- JWT Bearer tokens for user access:
  - Obtain via `POST /auth/token` with username/password.
  - Include in requests: `Authorization: Bearer <token>`.
- API key support for machine integrations (header name from config: `API_KEY_HEADER_NAME`).

## JWT Lifecycle
- Algorithm: `HS256` (configurable).
- Expiry: `ACCESS_TOKEN_EXPIRE_MINUTES` (default 30).
- Storage: frontend uses local storage (`aries_token`) and attaches to axios requests.
- Refresh: not implemented; re-login for new token in current setup.

## HLS Authorization
- All HLS playlists and segments under `/streams/{camera_id}/...` require `Authorization: Bearer <token>`.
- Frontend injects the header in `SecuredVideoPlayer` via HLS `xhrSetup`.

## WebSockets
- Legacy WS: token in query string `ws://localhost:8000/ws/ws?token=<JWT>`.
- Socket.IO: emit `authenticate { token }` after connect.

## CORS
- Allowed origins configured in `CORS_ORIGINS`.
- Backend enables credentials and allows all methods/headers for local dev.

## Secrets Management
- Never commit real secrets; use `.env` and a secrets manager in production.
- Rotate JWT secrets regularly; avoid default keys in production.

## Additional Considerations
- CSRF: APIs are token-based; avoid mixing cookie-auth without CSRF protection.
- RBAC: basic roles exist in models; full RBAC can be introduced via route dependencies.
