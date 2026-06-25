from fastapi import FastAPI
from core.orchestrator.graph import graph
from core.orchestrator.state import OrchestratorState
from pydantic import BaseModel
from dotenv import load_dotenv
from core.security.guard import is_safe_prompt
from langsmith import traceable
from core.utils.logger import setup_logger
import os

logger = setup_logger("orchestrator")


load_dotenv("AI_Platform\core\config\.env")

class RunRequest(BaseModel):
    prompt: str

app = FastAPI()

@app.post("/run")
@traceable(run_type="chain")
async def run(req: RunRequest):
    logger.info(f"Received request by orchestrator: {req.prompt}")
    is_safe, message = is_safe_prompt(req.prompt)
    
    if not is_safe:
        logger.warning(f"Unsafe prompt blocked: {message}")
        return {
            "error": message
        }


    initial_state: OrchestratorState = {
        "user_prompt": req.prompt,
        "intent": "",
        "tasks": [],
        "selected_tools": [],
        "outputs": {}
    }

    try:
        logger.info("Starting graph execution")

        result = await graph.ainvoke(initial_state)

        logger.info("Graph execution completed")

        return result["outputs"]

    except Exception as e:
        logger.error(f"Error during orchestration: {str(e)}")

        return {
            "error": "Orchestration failed",
            "details": str(e)
        }

# uvicorn core.orchestrator.main:app --reload --port 8002
