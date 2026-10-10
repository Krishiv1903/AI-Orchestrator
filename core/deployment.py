import os

from dotenv import load_dotenv
from fastapi import FastAPI

load_dotenv()

port = os.getenv("PORT", "10000")
base_url = f"http://127.0.0.1:{port}"

os.environ.setdefault("ORCHESTRATOR_URL", f"{base_url}/internal/orchestrator")
os.environ.setdefault("MCP_SERVER_URL", f"{base_url}/internal/mcp")
os.environ.setdefault("CODING_TOOL_URL", f"{base_url}/internal/tools/coding")
os.environ.setdefault("RESEARCH_TOOL_URL", f"{base_url}/internal/tools/research")
os.environ.setdefault("DB_TOOL_URL", f"{base_url}/internal/tools/db")
os.environ.setdefault("QA_TOOL_URL", f"{base_url}/internal/tools/qa")

from core.gateway.main import app as gateway_app
from core.mcp_server.main import app as mcp_app
from core.orchestrator.main import app as orchestrator_app
from tools.coding_tool.main import app as coding_tool_app
from tools.db_tool.main import app as db_tool_app
from tools.qa_tool.main import app as qa_tool_app
from tools.research_tool.main import app as research_tool_app

app = FastAPI(title="AI Orchestrator")


@app.get("/healthz", include_in_schema=False)
def health_check() -> dict[str, str]:
    return {"status": "ok"}


app.mount("/internal/orchestrator", orchestrator_app, name="orchestrator")
app.mount("/internal/mcp", mcp_app, name="mcp")
app.mount("/internal/tools/coding", coding_tool_app, name="coding-tool")
app.mount("/internal/tools/research", research_tool_app, name="research-tool")
app.mount("/internal/tools/db", db_tool_app, name="db-tool")
app.mount("/internal/tools/qa", qa_tool_app, name="qa-tool")
app.mount("/", gateway_app, name="gateway")
