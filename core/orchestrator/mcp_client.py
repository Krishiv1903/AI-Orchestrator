import requests
import os
from dotenv import load_dotenv
from pathlib import Path
from langsmith import traceable


BASE_DIR = Path(__file__).resolve().parent.parent.parent

env_path = BASE_DIR / "core" / "config" / ".env"

load_dotenv(dotenv_path=env_path)

@traceable(run_type="retriever")
def call_tool(tool, payload):

    MCP_URL = os.getenv("MCP_SERVER_URL")

    if not MCP_URL:
        raise ValueError(f"MCP_SERVER_URL is missing! Looked in: {env_path}")

    response = requests.post(
        f"{MCP_URL}/mcp",
        json={
            "type": "tool_call",
            "tool": tool,
            "input": payload
        },
        timeout=10
    )

    return response.json()
