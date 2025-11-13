## Current State
- No real AI inference model is implemented. `AIModel` exists only as a DB entity (services/api/app/models/models.py:65–83).
- Detection events come from `DetectionSimulator` and HLS playlists from `MockStreamProcessor`.
- Cameras page fetches data from backend; the list you see matches seeded demo cameras, not hardcoded UI. If it feels static, it’s because demo data is seeded and doesn’t change until you add/edit.

## Goals
1. Ensure dashboard and cameras use live backend data consistently.
2. Add video upload to create a temporary stream and use the simulator for detections.
3. Provide a path to test an actual model later without large refactors.

## Implementation Steps
### 1) Dynamic Cameras & Dashboard
- Align frontend API client to backend root endpoints and UUIDs (already aligned in api.ts during prior fixes).
- Dashboard: ensure WebSocket hook uses the native implementation that provides `alerts` and `getLatestAlert` (useWebSocket.tsx). Confirm the import and remove any leftover Socket.IO-only usage.
- Verify the cameras page uses API results only; remove any fallback demo blocks if present.

### 2) Video Upload to Create Stream
- Add `POST /streams/upload` to backend:
  - Accept `UploadFile` (video), save under `settings.HLS_OUTPUT_DIR/<uuid>/source.mp4`.
  - Start mock HLS generation for new `<uuid>` via `mock_stream_processor.start_stream(<uuid>, <file_path>)`.
  - Return `{ camera_id: <uuid>, stream_url: "/streams/<uuid>/" }`.
- Optional: create a transient `Camera` DB row with minimal fields so it appears in Cameras UI.
- Frontend UI:
  - On Cameras page, add an “Upload Video” button; show a file picker.
  - After upload, display the new stream tile using `SecuredVideoPlayer` pointing to returned `stream_url`.

### 3) Use Simulator to Test ‘Model’
- On upload or on any existing camera, auto-create an `AnalyticsJob` tied to that `camera_id` with reasonable rates so `DetectionSimulator` emits alerts and stats.
- Dashboard and RealTimeDetection already subscribe and display those events.

### 4) Future: Real Model Plug-in (Optional, not in this change)
- Introduce a pluggable inference service (e.g., `services/api/app/services/inference.py`) with a simple interface `load_model()`, `infer(frame)`.
- Allow `AnalyticsJob` to select model type; route frames from `StreamProcessor` to inference when available. Keep `MockStreamProcessor` + `DetectionSimulator` as fallback.

## Deliverables
- Backend upload endpoint returning a playable HLS stream URL.
- Frontend upload control on Cameras page to test with a local video file.
- Detections and alerts generated dynamically for uploaded streams using the simulator.

## Validation
- Upload a sample MP4; verify stream plays at `/streams/<uuid>/index.m3u8` with auth.
- Confirm alerts and stats appear on Dashboard and RealTimeDetection.
- Verify Cameras list shows the uploaded stream (if persisted) and supports start/stop.

## Notes
- All changes reuse existing routers and services; minimal new code, no external ML deps.
- We keep auth headers on HLS and APIs so everything works under demo login.

Please confirm this plan. Once approved, I’ll implement the backend upload endpoint, UI upload flow, and tie them into the simulator so the dashboard becomes fully dynamic with your uploaded video.