# Aries-Edge Platform

Industrial-grade intelligent video analytics platform with hardware acceleration and real-time processing capabilities.

## Architecture

This is a monorepo containing all services and packages for the Aries-Edge Platform:

```
aries/
├── services/
│   ├── api/           # FastAPI backend (JWT, cameras, streams, websockets)
│   └── frontend/      # React + TypeScript frontend (HLS player, dashboard)
├── packages/
│   └── schemas/       # Shared data schemas (TypeScript & Python)
├── tooling/           # Build and dev tooling (vite, nx, etc.)
├── docs/              # Platform documentation
├── docker-compose.yml # Local orchestration (optional services)
└── package.json       # Monorepo root configuration
```

## Quick Start

### Prerequisites

- Docker & Docker Compose
- Node.js 18+ 
- Python 3.8+
- NVIDIA GPU with CUDA support (for video processing)

### Development Setup

1. **Clone and install dependencies:**
   ```bash
   git clone <repository-url>
   cd aries
   npm install
   ```

2. **Run API locally:**
   ```bash
   cd services/api
   uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
   ```

3. **Run Frontend locally:**
   ```bash
   cd services/frontend
   npm run dev
   ```

4. **Access services:**
   - Frontend: http://localhost:3000
   - API: http://localhost:8000
   - API Docs (OpenAPI): http://localhost:8000/docs

### Notes

- Demo credentials (dev only): username `demo`, password `demo123`.
- All API endpoints are mounted at the root (no `/api/v1`).
- HLS streaming is secured; frontend injects `Authorization: Bearer <token>` into HLS requests automatically.

## Build & Deployment

### Local Development
```bash
# Build frontend
cd services/frontend && npm run build

# Run backend tests (if configured)
cd services/api && pytest

# Optional: start with docker compose
cd ../.. && docker compose up -d
```

### Production Deployment
- Containerization via Docker Compose and Kubernetes (see docs/ for guidance).

## Services Overview

### API Service (FastAPI)
- REST API + WebSockets
- JWT authentication (user tokens) + API keys (machine access)
- SQLite (local dev), SQLModel models
- Camera CRUD + HLS stream serving
- Detection simulator for dynamic alerts

### Frontend Service (React)
- React + TypeScript + Tailwind
- HLS playback with auth headers
- Live dashboard and detection panels
- Camera management UI (CRUD, start/stop streams)

### Simulator & Streams
- Mock HLS stream generator for local testing
- Real-time detection simulator broadcasting via WebSocket

### Broker Service (Apache Pulsar)
- Event-driven architecture
- Guaranteed message delivery
- Topic-based messaging
- Scalable pub/sub system

## Key Features

- **Hardware Acceleration**: NVIDIA GPU optimization with TensorRT
- **Real-time Processing**: Sub-100ms latency for object detection
- **Scalable Architecture**: Microservices with event-driven design
- **Multi-camera Support**: Process 100+ concurrent video streams
- **AI Analytics**: YOLO-based object detection with custom training
- **WebRTC Streaming**: Low-latency video streaming
- **RESTful API**: Comprehensive API with OpenAPI documentation
- **Authentication**: JWT tokens + API key support
- **Monitoring**: Built-in metrics and health checks

## Technology Stack

- **Backend**: FastAPI, SQLModel, SQLite (dev)
- **Frontend**: React, TypeScript, Tailwind CSS, HLS
- **Realtime**: WebSockets (legacy) and Socket.IO (client)
- **Infrastructure**: Docker, Docker Compose

## Development

### Code Quality
```bash
# Lint all code
npm run lint

# Format code
npm run format

# Type checking
npm run type-check
```

### Testing
```bash
# Run all tests
npm run test

# Test specific service
cd services/api && pytest
cd services/frontend && npm test
```

### Build Tools
- **Monorepo**: npm workspaces
- **Linting**: ESLint, Black, isort
- **Testing**: Jest, Pytest
- **CI/CD**: GitHub Actions
- **Containers**: Docker, Docker Compose

## Contributing

See docs/Contributing.md for coding standards, commit conventions, and PR workflow.

## Project Structure & Docs

- Project structure and conventions: docs/ProjectStructure.md
- Backend configuration and env vars: docs/BackendConfiguration.md
- API reference (endpoints and examples): docs/APIReference.md
- Security guide (JWT, HLS auth, CORS): docs/Security.md
- Troubleshooting guide: docs/Troubleshooting.md

## License

MIT License - see LICENSE file for details.
