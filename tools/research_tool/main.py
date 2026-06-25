from fastapi import FastAPI
from pydantic import BaseModel
from core.orchestrator.llm import llm
from langsmith import traceable
from fastapi import Header, HTTPException
from dotenv import load_dotenv
import os
from core.utils.logger import setup_logger

logger = setup_logger("research_tool")

load_dotenv("AI_Platform\core\config\.env")

API_KEY = os.getenv("GATEWAY_API_KEY")

import re

app = FastAPI()


class ToolRequest(BaseModel):
    task: str
    code_context: str | None = None

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
    code_context = getattr(req, "code_context", None)

    task_lower = re.sub(r"[^\w\s]", "", task.lower()).strip()
    is_conversational = any(word in task_lower for word in [
        "hi", "hello", "hey", "bye",
        "good morning", "good evening",
        "thank you", "thanks", "how are you"
    ])
    
    logger.info(f"Is conversational: {is_conversational}")

    if is_conversational:
        prompt = f"""
            You are a conversational chatbot.

            Your task is to respond like a human assistant in a friendly way.

            IMPORTANT RULES:
            - DO NOT say "no question provided"
            - DO NOT analyze the input
            - DO NOT behave like a research assistant
            - Just respond naturally like in a chat

            Examples:
            User: hi
            Response: Hello! How can I help you? 😊

            User: how are you?
            Response: I'm doing great, thanks for asking! How can I help you today?

            User: thank you
            Response: You're welcome! 😊

            Now respond:

            User: {task}
            Response:
        """
    elif code_context:
        prompt = f"""
            You are a technical research assistant.

            You are given BOTH:
            1. A task
            2. Code or technical context

            Provide relevant insights or guidance based on BOTH.

            Rules:
            - Focus on improving or analyzing the given code/context

            Task: {task}
            Code Context: {code_context}
        """
    else:
        prompt = f"""
            You are a research assistant.

            Provide key insights, facts, or analysis for the following task.

            Rules:
            - Max 1 line
            - No unnecessary explanations
            - Be direct and useful

            Task: {task}
        """

    try:
        logger.info("Calling LLM")
        response = llm.invoke(prompt)
        raw_output = response.content.strip()
        logger.info(f"LLM raw output: {raw_output}")
        output = response.content.strip().replace('"', '')
        logger.info(f"Final output: {output}")

        return {
            "task": task,
            "research_output": output
        }
    
    except Exception as e:
        logger.error(f"Research tool execution failed: {str(e)}")

        return {
            "error": "Research tool failed",
            "details": str(e)
        }


# uvicorn tools.research_tool.main:app --port 9002