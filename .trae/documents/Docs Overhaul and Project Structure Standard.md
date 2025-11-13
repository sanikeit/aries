## Scope & Objectives
- Update existing docs to industrial-standard quality and add a clear project structure guide.
- Minimize new files—edit existing docs first; introduce a small `docs/` set only where necessary.

## Targeted Doc Changes
### 1) Root README.md (update)
- Quick Start: backend + frontend local run; demo credentials, auth header usage, HLS secured playback.
- Project Structure: high-level monorepo layout with responsibilities and naming conventions.
- Services Overview: `api`, `frontend`, `schemas`, `tooling` with one-line summaries.
- Links to subdocs: API Reference, Backend Configuration, Security, Testing, Contributing, Troubleshooting.

### 2) docs/ProjectStructure.md (new)
- Standard directory tree (monorepo): `services/api`, `services/frontend`, `packages/schemas`, `tooling`, `docs`.
- Naming conventions: files, types, env vars, router path prefixes (root: `/auth`, `/users`, `/cameras`, `/analytics`, `/streams`, `/ws`), trailing-slash policy, camera IDs as UUID.
- Code organization: routers, models, services, components, hooks; boundaries between domains.
- Secrets handling: never commit secrets; .env usage; config management.

### 3) docs/BackendConfiguration.md (new)
- Env var matrix: `DATABASE_URL`, `HLS_OUTPUT_DIR`, JWT settings, CORS origins, Pulsar/optional services.
- Example `.env` and how to load configuration; security notes.

### 4) docs/APIReference.md (new, consolidated)
- Canonical endpoints aligned with current backend mounts (no `/api/v1`).
- For each router: method, path, auth requirements, parameters, request/response examples, error codes.
- Notes: trailing slash behavior, UUID formats, HLS playlist/segment endpoints and required `Authorization`.

### 5) docs/Security.md (new)
- JWT lifecycle (creation, expiry), storage, refresh strategy (current state), RBAC/roles (current and planned), CORS.
- HLS authorization: how the frontend injects `Authorization` into HLS requests.
- CSRF considerations and best practices; secret management.

### 6) docs/Testing.md (new)
- Testing strategy: unit/integration/e2e; coverage targets; commands for backend/frontend.
- Linting rules and pre-commit hooks; CI expectations.

### 7) docs/Contributing.md (update/new)
- Coding standards for Python/TS; formatter/linter.
- Conventional commits; PR workflow; branch strategy; code review checklist.

### 8) docs/ReleaseVersioning.md (new)
- SemVer policy; release notes format; CHANGELOG guidance.

### 9) docs/Troubleshooting.md (new)
- Common issues: 401 auth, trailing slash 307, UUID 422, HLS 404/401, port conflicts, alias resolution.
- Quick remedies and verification commands.

### 10) docs/DatabaseMigrations.md (new)
- SQLModel schema basics; migration approach; seed demo data; evolving schemas safely.

### 11) docs/Simulator.md (new)
- Detection simulator behavior, configuration (rates), limitations; how alerts/stats are produced.

### 12) Align Existing Architecture Docs
- Reconcile `.trae/documents/aries-edge-technical-architecture.md` endpoint tables and diagrams with actual mounts and auth flows; link it from README.

## Validation
- Cross-check each endpoint in API reference against `app.main`, routers and OpenAPI.
- Verify env var doc against `app/core/config.py`.
- Ensure HLS and auth examples work via curl.

## Deliverables
- Updated `README.md` and a minimal `docs/` directory with the files above.
- Consistent links across docs and clear navigation.

## Timeline
- One pass implementation; then review and adjust based on feedback.

## Risks & Mitigation
- Drift over time → add a short maintainer checklist and reference OpenAPI as source of truth for API docs.

Confirm to proceed and I will implement these documentation updates and the project structure guide.