# Aries Edge Frontend

React frontend for the Aries Edge intelligent video analytics platform.

## Features

- **Real-time Video Streaming**: HLS-based video playback with authentication
- **Live Alerts**: WebSocket-powered real-time alert notifications
- **Interactive ROI Editor**: Konva.js-based region of interest drawing tool
- **Responsive Design**: Modern UI with Tailwind CSS
- **Authentication**: JWT-based authentication with token management

## Tech Stack

- React 18 with TypeScript
- Vite for build tooling
- Tailwind CSS for styling
- React Router for navigation
- Axios for API calls
- React Player with HLS.js for video streaming
- Konva.js for interactive canvas operations
- Zustand for state management (ready for implementation)
- Sonner for toast notifications

## Development

```bash
# Install dependencies
npm install

# Start development server
npm run dev

# Build for production
npm run build
```

## Environment Variables

Create a `.env` file in the root directory:

```env
VITE_API_URL=http://localhost:8000
```

## API Integration

The frontend integrates with the Aries API backend:

- Authentication: `/auth/*` endpoints
- Camera management: `/cameras/*` endpoints
- Analytics: `/analytics/*` endpoints
- Video streams: `/streams/*` endpoints (with auth headers)
- WebSocket: `/ws` endpoint (with token query param)

## Components

### Core Components

- `SecuredVideoPlayer`: Authenticated HLS video player
- `ROIEditor`: Interactive region of interest editor
- `AlertCard`: Real-time alert display
- `StatsCard`: Dashboard statistics cards

### Pages

- `Login`: Authentication page
- `Dashboard`: Main dashboard with live feeds and alerts
- `Cameras`: Camera management (placeholder)
- `Analytics`: Analytics configuration (placeholder)
- `Settings`: System settings (placeholder)

## Security Features

- JWT token-based authentication
- Secure video stream access with Authorization headers
- WebSocket authentication via query parameters
- Automatic token refresh and session management
- Protected routes with authentication guards