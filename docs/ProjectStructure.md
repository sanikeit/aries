# Project Structure and Conventions

## Monorepo Layout
```
aries/
├── services/
│   ├── api/           # FastAPI backend (JWT, cameras, streams, websockets)
│   └── frontend/      # React + TypeScript frontend (HLS player, dashboard)
├── packages/
│   └── schemas/       # Shared data schemas (TypeScript & Python)
├── tooling/           # Build and dev tooling (vite, nx, etc.)
├── docs/              # Platform documentation
├── docker-compose.yml # Local orchestration
└── package.json       # Monorepo root config
```

## Backend Organization (services/api)
- `app/main.py` application setup and router mounting
- `app/models/` SQLModel entities (User, Camera, Stream, AIModel, AnalyticsJob, ROI, AlertEvent)
- `app/routers/` API endpoints (`/auth`, `/users`, `/cameras`, `/analytics`, `/streams`, `/ws`)
- `app/services/` stream generator, detection simulator, websocket manager, consumers
- `app/core/` configuration (`config.py`), security (JWT helpers), dependencies
- `app/db/` session and engine helpers

## Frontend Organization (services/frontend)
- `src/pages/` route-level pages (Dashboard, Cameras, LiveStreams)
- `src/components/` reusable components (player, cards, ui)
- `src/hooks/` data and realtime hooks (WebSocket)
- `src/services/` API client (`api.ts`)
- `vite.config.ts` dev server and aliases; Tailwind/TW config in project root

## Naming & Paths
- Router prefixes: root-mounted — `/auth`, `/users`, `/cameras`, `/analytics`, `/streams`, `/ws`
- Trailing slash policy: use trailing `/` where defined (e.g., `/streams/{camera_id}/` playlist helper)
- IDs: camera IDs are UUID strings
- HLS layout: `HLS_OUTPUT_DIR/<camera_id>/index.m3u8`, `playlist.m3u8`, `.ts` segments

## Security & Secrets
- Do not commit secrets; use `.env` loaded by `app/core/config.py`
- JWT user auth for APIs; API keys for machine integrations
- Frontend attaches `Authorization` header for HLS via player configuration

## Code Style
- Python: type hints, SQLModel, FastAPI dependency injection
- TypeScript: strict typing, functional components, hooks, Tailwind classes via `cn`
- Avoid comments in code unless necessary; prefer self-explanatory names

## Future Extensions
- Inference service can be added under `app/services/inference.py` with a simple `load_model()`/`infer(frame)` interface
- Keep boundaries clear: routers orchestrate, services do work, models store data
