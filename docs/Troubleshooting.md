# Troubleshooting

## Authentication
- 401 Unauthorized: check token; obtain via `POST /auth/token`. Ensure `Authorization: Bearer <token>` on all protected requests.
- Token missing in HLS: use `SecuredVideoPlayer` (headers injected via `xhrSetup`).

## Routing & Paths
- 307 Redirects: add trailing slash where required (e.g., `GET /streams/{camera_id}/`).
- 422 Unprocessable Entity on camera ID: ensure UUID string is used, not integers.

## Streams
- 404 for `index.m3u8`: stream not started or HLS files absent; call `POST /cameras/{camera_id}/start_stream` or upload a video at `POST /streams/upload`.
- HLS playback stalls: verify `HLS_OUTPUT_DIR` exists and is writable.

## WebSockets
- Legacy WS not connecting: ensure `ws://localhost:8000/ws/ws?token=<JWT>` and valid token.
- Socket.IO auth errors: emit `authenticate { token }` after connect.

## Frontend Dev
- Import alias errors (`@/lib/utils`): alias `@` → `./src` in `vite.config.ts`; use existing util `@/utils/cn`.
- Blank Dashboard: ensure Dashboard imports `useWebSocket` from `hooks/useWebSocket.tsx` (native WS implementation).

## Ports & CORS
- Port conflicts: verify nothing else is listening on 3000/8000.
- CORS errors: confirm `CORS_ORIGINS` includes your frontend origin.

## Quick Verification Commands
```bash
# Get token
curl -s -X POST -d "username=demo&password=demo123" http://localhost:8000/auth/token

# List cameras
curl -H "Authorization: Bearer <token>" http://localhost:8000/cameras/

# Start stream
curl -H "Authorization: Bearer <token>" -X POST http://localhost:8000/cameras/<uuid>/start_stream

# Fetch HLS playlist
curl -H "Authorization: Bearer <token>" http://localhost:8000/streams/<uuid>/index.m3u8

# Upload a video
curl -H "Authorization: Bearer <token>" -F "file=@video.mp4" http://localhost:8000/streams/upload
```
