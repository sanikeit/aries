# Monorepo Build Tools

This directory contains build tool configurations for the Aries-Edge Platform monorepo.

## Available Tools

### Nx (Recommended)
- **Location**: `tooling/nx/`
- **Purpose**: Modern build system with intelligent caching
- **Features**: 
  - Dependency graph analysis
  - Affected project detection
  - Parallel task execution
  - Incremental builds

### Make (Alternative)
- **Location**: `tooling/make/`
- **Purpose**: Traditional build automation
- **Features**:
  - Simple task definitions
  - Cross-platform compatibility
  - No additional dependencies

### Bazel (Enterprise)
- **Location**: `tooling/bazel/`
- **Purpose**: Google's build system for large-scale projects
- **Features**:
  - Hermetic builds
  - Advanced caching
  - Remote execution
  - Language agnostic

## Quick Start

### Using Nx (Recommended)
```bash
# Install Nx CLI
npm install -g nx

# Build all projects
nx run-many --target=build --all

# Build specific service
nx build api

# Run tests
nx run-many --target=test --all

# Serve development servers
nx serve frontend
nx serve api
```

### Using Make
```bash
# Build all services
make build-all

# Build specific service
make build-api

# Run tests
make test-all

# Start development environment
make dev
```

### Using Bazel
```bash
# Build all targets
bazel build //...

# Build specific service
bazel build //services/api

# Run tests
bazel test //...

# Start development servers
bazel run //services/frontend:dev
```

## Choosing the Right Tool

| Tool | Best For | Learning Curve | Performance | Features |
|------|----------|----------------|-------------|----------|
| Nx | Modern development | Low | High | Excellent |
| Make | Simple projects | Very Low | Medium | Basic |
| Bazel | Large enterprises | High | Excellent | Advanced |

## Configuration Files

- `nx.json` - Nx configuration
- `Makefile` - Make configuration  
- `BUILD.bazel` - Bazel configuration
- `project.json` - Per-project Nx configuration