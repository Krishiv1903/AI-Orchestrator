from fastapi import FastAPI
from pydantic import BaseModel
from core.orchestrator.llm import llm
from langsmith import traceable
from fastapi import Header, HTTPException
from dotenv import load_dotenv
import os
from core.utils.logger import setup_logger

logger = setup_logger("coding_tool")

load_dotenv("AI_Platform\core\config\.env")

API_KEY = os.getenv("GATEWAY_API_KEY")

app = FastAPI()

class ToolRequest(BaseModel):
    task: str
    code_context: dict | None = None 

@app.post("/execute")
@traceable(run_type="tool")
def execute(req: ToolRequest, authorization: str = Header(None)):

    logger.info(f"Request received | task={req.task}")

    if not authorization or not authorization.startswith("Bearer "):
        logger.warning("Missing Authorization header, Unauthorized")
        raise HTTPException(status_code=401, detail="Unauthorized")
    token = authorization.split(" ")[1]
    if token != API_KEY:
        logger.warning("Invalid Token")
        raise HTTPException(status_code=401, detail="Invalid token")

    logger.info("Authorization successful")

    task = req.task
    code_context = req.code_context
    
    context_text = ""
    if isinstance(code_context, dict):
        context_text = code_context.get("research_output", "")
    elif code_context:
        context_text = str(code_context)

    logger.info(f"Context received: {context_text}")

    if context_text:
        prompt = f"""
            You are an expert frontend/backend developer.

            You are given:
            1. A task
            2. Context from previous step

            Your job:
            - Select the BEST TECHNOLOGY (framework or language)

            IMPORTANT RULES:
            - If context mentions a specific technology (React, Angular, C#, etc.) → RETURN THAT ✅
            - DO NOT convert framework to language ❌
            - DO NOT change React → JavaScript ❌
            - DO NOT change Angular → TypeScript ❌
            - Use EXACT term from context ✅

            STRICT OUTPUT RULES:
            - Output ONLY ONE word or phrase
            - NO explanation
            - NO reasoning
            - NO extra text

            Examples:
            Output: React
            Output: Angular
            Output: C#
            Output: Python

            Context:
            {context_text}

            Task:
            {task}

            Final Output:
        """
    else:
        prompt = f"""
            You are an expert software classifier.

            Your job is to identify the programming language or technology mentioned in the task.

            Rules:
            - Return ONLY the language name
            - If multiple technologies, return all names in one string
            - If no technology is mentioned return a commonly used modern language
            - No explanation

            Examples:
            Task: "build backend in C#"
            Output: C#

            Task: "create API using Node.js"
            Output: Node.js

            Task: "write python script"
            Output: Python

            Task: "build backend"
            Output: "Most recent famous compatitble backend language to be returned"

            Now analyze:

            Task: {task}
        """

    try:
        logger.info("Calling LLM")

        response = llm.invoke(prompt)
        raw_output = response.content.strip()

        logger.info(f"LLM output: {raw_output}")

        output = raw_output.split("\n")[0].replace("**", "").strip()

        logger.info(f"Final output: {output}")

        return {
            "task": task,
            "identified_language": response.content.strip()
        }

    except Exception as e:
        logger.error(f"LLM execution failed: {str(e)}")

        return {
            "error": "LLM failed",
        }
           



# uvicorn tools.coding_tool.main:app --port 9001
