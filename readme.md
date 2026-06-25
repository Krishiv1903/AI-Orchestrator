# AI_Platform

Comprehensive documentation for the AI_Platform project: architecture, workflow, file map, local development, deployment, and extension points.

## Project Overview

AI_Platform is a modular system for orchestrating AI tools and services. The repository is organized into a small HTTP gateway/UI, a core orchestrator that composes tasks and agents, an MCP server for model/context protocol support, and a set of pluggable tools for specialized tasks (QA, research, coding, DB access).

Key goals:
- Modular components that can run locally or in containers
- Pluggable tools and services with clear interfaces
- Docker-ready for easy deployment

## High-Level Architecture

```mermaid
graph LR
  subgraph Gateway
    GW[Gateway (core/gateway/main.py)]
    Static[Static UI Files]
  end

  subgraph Orchestrator
    OR[Orchestrator (orchestrator/main.py)]
    AGG[Aggregator]
    EXEC[Executor]
    STATE[State Manager]
  end

  subgraph MCP
    MCP[MCP Server (mcp_server/main.py)]
  end

  subgraph Core
    CORE[Core (core/)]
    CONFIG[Config]
  end

  subgraph Tools
    Tools[tools/*]
  end

  GW --> OR
  OR --> MCP
  OR --> Tools
  CORE --> GW
  CORE --> OR
  Tools --> OR
  MCP --> OR
  Static --> GW
```

## Workflow / Request Flow

1. A user or client calls the Gateway (HTTP UI or API) served by `core/gateway/main.py`.
2. The Gateway forwards the request to the Orchestrator (`orchestrator/main.py`).
3. The Orchestrator evaluates the request, delegates to one or more services:
   - The `executor.py` runs tasks using tool adapters.
   - `aggregator.py` combines results from multiple services.
   - `state.py` maintains workflow state between steps.
4. For LLM interactions or structured multi-agent coordination, the Orchestrator interacts with the `mcp_server`.
5. Pluggable tools in `tools/` (e.g., `qa_tool`, `research_tool`, `db_tool`, `coding_tool`) process specialized tasks and return results to the Orchestrator.
6. Results are returned to the Gateway and presented to the user.

## File / Folder Map (high level)

- `main.py` — Root entrypoint (convenience script / supervisor)
- `requirements.txt` — Python dependencies
- `docker-compose.yml` — Compose stack for local deployment
- `Dockerfile` — Root Dockerfile for packaging (if used)

- `core/`
  - `config/` — configuration files and environment templates
  - `gateway/` — HTTP gateway / static UI
    - `main.py` — gateway server
    - `static/` — UI assets (`index.html`, `index.js`, `index.css`)

- `mcp_server/`
  - `main.py` — Model Context Protocol server
  - `Dockerfile` — packaging for MCP component

- `orchestrator/`
  - `main.py` — orchestrator entrypoint
  - `aggregator.py` — gathers/merges tool responses
  - `executor.py` — executes tasks and calls tools
  - `graph.py` — optional DAG/graph utilities
  - `llm.py` — LLM adapter and helpers
  - `mcp_client.py` — client for `mcp_server`
  - `state.py` — workflow state management
  - `services/` — small specialized services
    - `intent_analyzer.py`
    - `route_planner.py`
    - `task_decomposer.py`

- `security/`
  - `guard.py` — authorization / policy enforcement helpers

- `utils/`
  - `logger.py` — central logging utilities

- `tools/` — pluggable tool adapters
  - `coding_tool/`, `db_tool/`, `qa_tool/`, `research_tool/` — each exposes an adapter (`main.py`) used by the orchestrator

## Important Files (quick links)

- Gateway server: [core/gateway/main.py](core/gateway/main.py)
- Gateway UI: [core/gateway/static/index.html](core/gateway/static/index.html)
- Orchestrator entrypoint: [orchestrator/main.py](orchestrator/main.py)
- Orchestrator executor: [orchestrator/executor.py](orchestrator/executor.py)
- MCP server: [mcp_server/main.py](mcp_server/main.py)
- Tools folder: [tools](tools)
- Root runner: [main.py](main.py)

## Local Development

Prerequisites:
- Python 3.10+ (or the version pinned in `requirements.txt`)
- Docker & Docker Compose (for containerized run)

Create and activate a virtual environment, install deps:

```bash
python -m venv .venv
.
# Windows PowerShell
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

Run the gateway locally (example):

```bash
python core/gateway/main.py
```

Run the orchestrator locally (example):

```bash
python orchestrator/main.py
```

Run the MCP server locally (example):

```bash
python mcp_server/main.py
```

NOTE: Each component may accept environment variables or flags—see their `main.py` files for details.

## Containerized Deployment

To run everything with Docker Compose (recommended for full system):

```bash
docker-compose up --build
```

This will build images from the included `Dockerfile`s and start the Gateway, Orchestrator, MCP server, and any other configured services.

## Extending & Adding Tools

To add a new tool adapter:
1. Create a new folder under `tools/` (e.g., `tools/my_tool/`).
2. Implement a `main.py` that exposes a consistent adapter API (input → output dict). Look at `tools/qa_tool/main.py` and `tools/research_tool/main.py` for examples.
3. Wire the tool into `orchestrator/executor.py` so it can be invoked by name.

Design recommendations:
- Keep adapter interfaces simple and serializable (JSON-friendly)
- Make calls idempotent where possible
- Keep side-effects contained to the tool's module

## Testing & Debugging

- Use Python logging via `utils/logger.py` to trace flows.
- Orchestrator provides `state.py` for reproducing workflows; persist state to debug complex interactions.
- Add unit tests for services in `orchestrator/services/` and tools.

## Security & Access Control

- `security/guard.py` contains authorization checks. Review and extend for production use.
- Sanitize and validate all external inputs at the Gateway layer.

## Common Tasks & Commands

- Build and run locally (containers): `docker-compose up --build`
- Install deps: `pip install -r requirements.txt`
- Run a single component: `python <component>/main.py` (e.g., `python orchestrator/main.py`)

## Contributors & Next Steps

- Suggested next steps:
  - Add CI to run unit tests and linting.
  - Add example integration test that starts gateway + orchestrator + a tool.
  - Document configuration environment variables in `core/config/`.

If you want, I can also:
- Add a CONTRIBUTING.md with contribution guidelines
- Scaffold unit tests and a minimal CI pipeline

---

Generated on: 2026-06-25
