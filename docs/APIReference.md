# API Reference (Canonical)

All endpoints are mounted at the root (no `/api/v1`). JWT Bearer auth is required unless specified.

## Auth
- `POST /auth/token`
  - Form: `username`, `password`
  - Response: `{ access_token, token_type }`
- `POST /auth/register`
  - JSON: `{ username, email, password, full_name? }`
  - Response: `User`
- `GET /auth/me`
  - Headers: `Authorization: Bearer <token>`
  - Response: `User`

## Users
- `GET /users/` (if implemented in router)

## Cameras
- `GET /cameras/`
  - Query: `skip?`, `limit?`
  - Response: `Camera[]`
- `GET /cameras/{camera_id}`
  - Path: `camera_id` (UUID)
  - Response: `Camera`
- `POST /cameras/`
  - JSON: `{ name, rtsp_uri, description?, location? }`
  - Response: `Camera`
- `PUT /cameras/{camera_id}`
  - JSON: partial camera fields (e.g., `{ is_active: true }`)
  - Response: `Camera`
- `DELETE /cameras/{camera_id}`
  - Response: `{ message }`
- `POST /cameras/{camera_id}/start_stream`
  - Response: `{ message, camera_id, stream_url }`
- `POST /cameras/{camera_id}/stop_stream`
  - Response: `{ message, camera_id }`
- `GET /cameras/{camera_id}/stream_status`
  - Response: `{ camera_id, stream_active, stream_url?, camera_active, last_updated? }`

## Streams (HLS)
- `GET /streams/{camera_id}/`
  - Returns `index.m3u8` (helper)
  - Headers: `Authorization: Bearer <token>`
- `GET /streams/{camera_id}/{filename}`
  - `filename`: `index.m3u8`, `playlist.m3u8`, or `.ts` segment
  - Headers: `Authorization: Bearer <token>`
- `POST /streams/upload`
  - Multipart: `file=@video.mp4`
  - Response: `{ camera_id, stream_url }`

## WebSockets
- Legacy WebSocket: `ws://localhost:8000/ws/ws?token=<JWT>`
  - Messages: `subscribe_camera`, `unsubscribe_camera`, `ping`
  - Broadcasts: detections, counts, stats (from simulator)
- Socket.IO: client connects to `http://localhost:8000` and emits `authenticate { token }`

## Notes
- Camera IDs are UUID strings.
- Some endpoints require trailing slash (e.g., `GET /streams/{camera_id}/`).
- HLS requests must include `Authorization` header.
