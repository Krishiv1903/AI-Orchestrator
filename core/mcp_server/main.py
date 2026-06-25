from fastapi import FastAPI
from pydantic import BaseModel
import requests 
import os
from dotenv import load_dotenv
from langsmith import traceable
from core.utils.logger import setup_logger
logger = setup_logger("mcp")

load_dotenv("AI_Platform\core\config\.env")

API_KEY = os.getenv("GATEWAY_API_KEY")

app = FastAPI()

TOOL_ENDPOINTS = {
    "coding_tool": f"{os.getenv('CODING_TOOL_URL')}/execute",
    "research_tool": f"{os.getenv('RESEARCH_TOOL_URL')}/execute",
    "db_tool": f"{os.getenv('DB_TOOL_URL')}/execute",
    "qa_tool": f"{os.getenv('QA_TOOL_URL')}/execute"
}

class MCPRequest(BaseModel):
    type: str
    tool: str
    input: dict

@app.post("/mcp")
@traceable(run_type="retriever")
def handle_mcp(req: MCPRequest):

    logger.info(f"Received MCP request | tool={req.tool}")

    tool_url = TOOL_ENDPOINTS.get(req.tool)

    if not tool_url:
        logger.warning(f"Tool not found: {req.tool}")
        return {
            "type": "error",
            "output": {"error": "Tool not found"}
        }

    try:
        logger.info(f"Calling tool at {tool_url}")
        response = requests.post(
            tool_url,
            json=req.input,  
            headers={
                "Authorization": f"Bearer {API_KEY}"
            },
            timeout=10
        )
        logger.info(f"Received response from tool: {req.tool}")
        return {
            "type": "tool_response",
            "tool": req.tool,
            "output": response.json()
        }
    except Exception as e:
        logger.error(f"Error calling tool {req.tool}: {str(e)}")
        return {
            "type": "error",
            "output": {"error": str(e)}
        }

# uvicorn core.mcp_server.main:app --reload --port 8001