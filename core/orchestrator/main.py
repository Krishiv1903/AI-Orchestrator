from fastapi import FastAPI, Header, HTTPException
from core.orchestrator.graph import graph
from core.orchestrator.state import OrchestratorState
from pydantic import BaseModel
from dotenv import load_dotenv
from core.security.guard import is_safe_prompt
from langsmith import traceable
from core.utils.logger import setup_logger
import os

logger = setup_logger("orchestrator")


load_dotenv()

class RunRequest(BaseModel):
    prompt: str

app = FastAPI()

@app.post("/run")
@traceable(run_type="chain")
async def run(req: RunRequest, x_api_key: str | None = Header(default=None)):
    if not os.getenv("GATEWAY_API_KEY") or x_api_key != os.getenv("GATEWAY_API_KEY"):
        raise HTTPException(status_code=401, detail="Invalid API Key")

    logger.info("Received request by orchestrator")
    initial_state: OrchestratorState = {
        "user_prompt": req.prompt,
        "intent": "",
        "tasks": [],
        "selected_tools": [],
        "outputs": {}
    }

    try:
        is_safe, message = is_safe_prompt(req.prompt)
        if not is_safe:
            logger.warning("Unsafe prompt blocked")
            raise HTTPException(status_code=400, detail=message)

        logger.info("Starting graph execution")

        result = await graph.ainvoke(initial_state)

        logger.info("Graph execution completed")

        return result["outputs"]

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error during orchestration: {str(e)}")
        raise HTTPException(status_code=500, detail="Orchestration failed") from e
