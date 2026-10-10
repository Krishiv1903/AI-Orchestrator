import requests
import os
from langsmith import traceable


@traceable(run_type="retriever")
def call_tool(tool, payload):

    MCP_URL = os.getenv("MCP_SERVER_URL")

    if not MCP_URL:
        raise ValueError("MCP_SERVER_URL is missing")

    response = requests.post(
        f"{MCP_URL}/mcp",
        json={
            "type": "tool_call",
            "tool": tool,
            "input": payload
        },
        headers={"x-api-key": os.getenv("GATEWAY_API_KEY", "")},
        timeout=120,
    )
    response.raise_for_status()

    return response.json()
