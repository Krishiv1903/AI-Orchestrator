# AI Orchestrator

An AI workflow application with a browser chat UI, a FastAPI gateway, an orchestrator, an MCP-style tool dispatcher, and coding, research, database, and QA tools.

**Deployed URL:** https://ai-orchestrator-d2xh.onrender.com/

## Architecture

The four existing services remain separate FastAPI applications in the codebase, but the production entry point mounts them in one process and one Render web service. The gateway serves the UI and forwards authenticated requests to the orchestrator; the orchestrator calls the MCP dispatcher, which routes to the selected tool. Internal HTTP calls use loopback URLs on the same Render-assigned `PORT`.

```text
Browser -> Gateway/UI -> Orchestrator -> MCP dispatcher -> Tools
                  One Render free web service
```

The app uses Groq for model calls. A Groq API key is required for chat/task execution. LangSmith tracing is optional and disabled unless configured separately.

## Deploy free on Render

1. Push this repository to GitHub and choose **New + > Blueprint** in Render. Connect the repository and deploy the Blueprint from `render.yaml`.
2. In the Render service's Environment settings, provide:
   - `GROQ_API_KEY`: your Groq API key.
   - `GATEWAY_API_KEY`: a long, unique value that users must enter to use the chat.
3. Save the environment changes and wait for the service to become Live. Render uses the root `Dockerfile`, assigns `PORT`, and checks `/healthz`.
4. Replace the URL placeholder at the top of this README with the service URL shown by Render.

No paid Render services or external database are required. The free web service may spin down while idle, so the first request after inactivity can take longer. The model provider may have its own usage limits or terms.

## Run locally

From the repository root, create a local environment file and add your own keys:

```powershell
Copy-Item .env.example .env
```

Then start the same single-service setup used for deployment:

```powershell
docker compose up --build
```

Open `http://localhost:10000`. Enter the configured `GATEWAY_API_KEY` in the chat input before sending a prompt. To stop the service, run `docker compose down`.

To run without Docker, install `requirements.txt` in a Python 3.11 environment and start:

```powershell
uvicorn core.deployment:app --host 0.0.0.0 --port 10000
```

## Configuration

| Variable | Required | Purpose |
| --- | --- | --- |
| `GROQ_API_KEY` | For AI requests | Authenticates model requests. |
| `GATEWAY_API_KEY` | Yes | Protects the gateway and internal service routes. |
| `GROQ_MODEL` | No | Groq model name; defaults to `llama-3.3-70b-versatile`. |
| `PORT` | Set by Render | Port used by the web server and internal service calls. |

Copy `.env.example` to `.env` only for local development. Do not commit real credentials or put them in source code, the UI, or a public repository.

## Project layout

```text
core/
  deployment.py          Single-process production entry point
  gateway/               Public API and static chat UI
  orchestrator/          Workflow graph, routing, and MCP client
  mcp_server/             Tool dispatcher
  security/               Prompt safety checks
  utils/                  Logging
tools/
  coding_tool/
  db_tool/
  qa_tool/
  research_tool/
Dockerfile                Production image for the combined service
docker-compose.yml        Local single-container run
render.yaml               Free Render Blueprint
```
