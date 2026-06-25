from fastapi import FastAPI
from pydantic import BaseModel
from core.orchestrator.llm import llm
from langsmith import traceable
from fastapi import Header, HTTPException
from dotenv import load_dotenv
import os
from core.utils.logger import setup_logger

logger = setup_logger("qa_tool")

load_dotenv("AI_Platform\core\config\.env")

API_KEY = os.getenv("GATEWAY_API_KEY")

app = FastAPI()

class ToolRequest(BaseModel):
    task: str

@app.post("/execute")
@traceable(run_type="tool")
def execute(req: ToolRequest, authorization: str = Header(None)):

    logger.info(f"Request received | task={req.task}")

    if not authorization or not authorization.startswith("Bearer "):
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
         
        response = llm.invoke(f"""
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

        return {
            "error": "QA tool failed",
            "details": str(e)
        }


# uvicorn tools.qa_tool.main:app --port 9004
