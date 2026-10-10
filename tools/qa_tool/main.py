from fastapi import FastAPI
from pydantic import BaseModel
from core.orchestrator.llm import get_llm
from langsmith import traceable
from fastapi import Header, HTTPException
from dotenv import load_dotenv
import os
from core.utils.logger import setup_logger

logger = setup_logger("qa_tool")

load_dotenv()

API_KEY = os.getenv("GATEWAY_API_KEY")

app = FastAPI()

class ToolRequest(BaseModel):
    task: str

@app.post("/execute")
@traceable(run_type="tool")
def execute(req: ToolRequest, authorization: str | None = Header(default=None)):

    logger.info(f"Request received | task={req.task}")

    if not API_KEY or not authorization or not authorization.startswith("Bearer "):
        logger.warning("Missing or invalid Authorization header")
        raise HTTPException(status_code=401, detail="Unauthorized")
    token = authorization.split(" ")[1]
    if token != API_KEY:
        logger.warning("Invalid token attempt")
        raise HTTPException(status_code=401, detail="Invalid token")
    logger.info("Authorization successful")
    task = req.task

    try:
        logger.info("Calling LLM for QA test point")
         
        response = get_llm().invoke(f"""
            You are a QA Engineer.
            List ONLY 1 key test points.

            No explanation. One line.

            Task: {task}
        """)

        raw_output = response.content.strip()
        logger.info(f"LLM output: {raw_output}")
        output = raw_output.split("\n")[0].replace("**", "").strip()
        logger.info(f"Final test point: {output}")

        return {
            "task": task,
            "identified_language": response.content.strip()
        }
    
    except Exception as e:
        logger.error(f"QA tool execution failed: {str(e)}")

        raise HTTPException(status_code=502, detail="LLM execution failed") from e
