## Diagnosed Issues
- Internal Server Error on `POST /cameras/{camera_id}/start_stream` due to referencing a non-existent `ai_model_id` on `Camera` (app/routers/cameras.py:243). The `Camera` model does not define `ai_model_id` (app/models/models.py:25–47).
- Background consumer crash: `'NoneType' object has no attribute 'receive'` caused by bad Pulsar constant and missing safety checks when broker/consumer isn’t connected (app/services/consumer_service.py:29, 138).
- API path usage inconsistencies: list endpoint redirects from `/cameras` to `/cameras/` (trailing slash). Frontend/clients should use the canonical paths; avoid `/api/v1/*` since actual routes are mounted at `/cameras`, `/streams`, etc. (app/main.py:105–118, openapi.json).
- Stream serving is correctly wired (`/streams/{camera_id}/` and `/streams/{camera_id}/{filename}`) but start-stream fails before generating playlists (app/routers/streams.py:60–68).

## Fix Approach
- Remove or correct the AI model check in start-stream:
  - Option A (minimal): drop the `if camera.ai_model_id:` block to unblock streaming.
  - Option B (better): fetch the active `AnalyticsJob` for the camera and derive its `ai_model` if needed (app/models/models.py:84–108).
- Harden Pulsar consumer:
  - Import and use the correct constant `InitialPosition.Earliest` during subscribe.
  - Guard receive loop to skip when `self.consumer` is `None` and retry connection.
  - Log and backoff cleanly when broker is unavailable in local dev.
- Align stream URL returned by start-stream with router: return `"/streams/{camera_id}/"` so clients can fetch `index.m3u8` and segments (app/routers/cameras.py:262–279, app/routers/streams.py:60–68).
- Ensure clients use trailing-slash endpoints for collection routes (e.g., `/cameras/`) and correct base paths.

## Implementation Steps
1. Edit `app/routers/cameras.py`:
   - At `start_camera_stream` remove the `camera.ai_model_id` access (app/routers/cameras.py:243–246). Optionally, add a query for active `AnalyticsJob` if model selection is required.
   - Adjust returned `stream_url` to `"/streams/{camera_id}/"` (app/routers/cameras.py:265–279).
2. Edit `app/services/consumer_service.py`:
   - Change imports to `from pulsar import Client, ConsumerType, InitialPosition` (app/services/consumer_service.py:10).
   - Update `subscribe(..., initial_position=InitialPosition.Earliest)` (app/services/consumer_service.py:29).
   - In `consume_metadata`, before calling `self.consumer.receive(...)`, add a guard: if `self.consumer` is `None`, sleep and continue (app/services/consumer_service.py:137–141).
3. No schema changes are required; `Camera` stays without `ai_model_id` (app/models/models.py:25–47). Use `AnalyticsJob` for AI model linkage when needed (app/models/models.py:84–108).

## Validation Plan
- Restart API and confirm startup logs are clean (no Pulsar consumer AttributeError).
- `GET /cameras/` returns camera list.
- `POST /cameras/{camera_uuid}/start_stream` returns 200 with `stream_url`.
- `GET /streams/{camera_uuid}/` returns `index.m3u8`; `GET /streams/{camera_uuid}/playlist.m3u8` returns media playlist; `GET /streams/{camera_uuid}/segment_000000.ts` returns TS data.
- Frontend `VideoStreamPlayer` loads HLS using `stream_url`.

## Notes & Risks
- In local dev without Pulsar, consumer will stay idle and log retries; detection simulator continues generating events, so analytics UI remains dynamic.
- If later we need per-camera model selection at stream start, we will add an `AnalyticsJob` lookup rather than extending `Camera`.

## Outcome
- Stream start endpoint no longer 500s.
- HLS streams generate and serve correctly.
- Background consumer no longer crashes when broker is absent.
- Clients use canonical API paths, avoiding redirects and mismatches.