import os

import requests
from dotenv import load_dotenv
from fastapi import FastAPI, Header, HTTPException
from langsmith import traceable
from pydantic import BaseModel

from core.utils.logger import setup_logger

logger = setup_logger("mcp")
load_dotenv()

API_KEY = os.getenv("GATEWAY_API_KEY")


def _tool_endpoint(env_name: str) -> str:
    base_url = os.getenv(env_name)
    if not base_url:
        raise RuntimeError(f"{env_name} is required")
    return f"{base_url.rstrip('/')}/execute"


TOOL_ENDPOINTS = {
    "coding_tool": _tool_endpoint("CODING_TOOL_URL"),
    "research_tool": _tool_endpoint("RESEARCH_TOOL_URL"),
    "db_tool": _tool_endpoint("DB_TOOL_URL"),
    "qa_tool": _tool_endpoint("QA_TOOL_URL"),
}

app = FastAPI()


class MCPRequest(BaseModel):
    type: str
    tool: str
    input: dict


@app.post("/mcp")
@traceable(run_type="retriever")
def handle_mcp(req: MCPRequest, x_api_key: str | None = Header(default=None)):
    if not API_KEY or x_api_key != API_KEY:
        raise HTTPException(status_code=401, detail="Invalid API Key")

    logger.info("Received MCP request | tool=%s", req.tool)
    tool_url = TOOL_ENDPOINTS.get(req.tool)
    if not tool_url:
        logger.warning("Tool not found: %s", req.tool)
        raise HTTPException(status_code=404, detail="Tool not found")

    try:
        response = requests.post(
            tool_url,
            json=req.input,
            headers={"Authorization": f"Bearer {API_KEY}"},
            timeout=120,
        )
        response.raise_for_status()
        return {
            "type": "tool_response",
            "tool": req.tool,
            "output": response.json(),
        }
    except (requests.RequestException, ValueError) as exc:
        logger.error("Error calling tool %s: %s", req.tool, exc)
        raise HTTPException(status_code=502, detail="Tool execution failed") from exc
