# Nx Build Tool Configuration

This directory contains Nx configuration for the Aries-Edge Platform monorepo.

## Getting Started

1. **Install Nx CLI:**
   ```bash
   npm install -g nx
   ```

2. **Run commands:**
   ```bash
   # Build all projects
   nx run-many --target=build --all

   # Build specific service
   nx build api
   nx build frontend
   nx build processor

   # Run tests
   nx run-many --target=test --all

   # Lint code
   nx run-many --target=lint --all

   # Serve development servers
   nx serve api
   nx serve frontend
   ```

## Project Graph

View the dependency graph between projects:

```bash
nx graph
```

## Affected Projects

Run commands only on affected projects:

```bash
# See what projects are affected by changes
nx affected:graph

# Build affected projects
nx affected:build

# Test affected projects
nx affected:test

# Lint affected projects
nx affected:lint
```

## Caching

Nx provides intelligent caching for builds, tests, and other tasks:

```bash
# Clear cache
nx reset

# Run with verbose logging
nx build api --verbose
```

## Workspace Structure

```
aries-edge-platform/
├── packages/
│   └── schemas/           # Shared schemas package
├── services/
│   ├── api/              # FastAPI backend service
│   ├── frontend/         # React frontend application
│   └── processor/        # DeepStream video processing service
├── tooling/
│   └── nx/               # Nx configuration and plugins
└── nx.json               # Main Nx configuration
```

## Custom Executors

Custom Nx executors can be added to `tooling/nx/executors/` for specialized build tasks.

## Plugins

Nx plugins for specific technologies:
- `@nx/react` - React applications
- `@nx/node` - Node.js applications  
- `@nx/python` - Python applications
- `@nx/docker` - Docker builds