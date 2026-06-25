from core.orchestrator.llm import llm
import ast
from langsmith import traceable
from core.utils.logger import setup_logger

logger = setup_logger("decomposer")


@traceable(run_type="llm")
def decompose_tasks(state):
    prompt = state["user_prompt"]

    logger.info(f"Decomposing prompt: {prompt}")

    response = llm.invoke(f"""
        You are an AI planner.

        Your job is to break a user request into meaningful tasks.
        

        RULES:
        - If the request is SIMPLE (e.g., write code, explain, answer, test), RETURN ONE TASK ONLY.
        - If the request contains MULTIPLE actions (e.g., research + build + test), split into tasks. For queries like compare and find best among, such queries must not be split
        - If multiple programing languages are there segragate them on bases of database(sql, nosql, mongodb, etc) and coding(html, react, js, node, express, cpp, c#, java, python, etc) to call the respective agent.
        - Backend and database are different (C#, python, etc) should go to coding agent, (sql, mongodb, nosql languages) should go to db agent and are different tasks.
        - Do NOT include high-level tasks if they are already broken down.

        Return ONLY a Python list.

        Examples:

        Prompt: "Write a Python function to reverse a string"
        Output: ["write a Python function to reverse a string"]

        Prompt: "Research UI practices and build a dashboard"
        Output: ["research UI practices", "build dashboard"]
                          
        Prompt: "build full stack app using C#, React, SQL"
        Output: ["build backend using C#", "build frontend using React", "design database using SQL"]
        NOT: ["build full app", "build backend using C#", "build frontend using React", "design database using SQL"]

        Now process:

        Prompt: {prompt}
    """)

    raw_output = response.content.strip()
    logger.info(f"LLM raw output: {raw_output}")

    try:
        tasks = ast.literal_eval(raw_output)
        logger.info(f"Parsed tasks: {tasks}")
    except Exception as e:
        logger.warning(f"Decomposition fallback triggered: {str(e)}")
        tasks = [prompt]
        logger.info(f"Fallback tasks: {tasks}")

    return {"tasks": tasks}

