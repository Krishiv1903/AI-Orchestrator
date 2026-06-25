from core.orchestrator.llm import llm
import ast
from langsmith import traceable
from core.utils.logger import setup_logger

logger = setup_logger("router")


@traceable(run_type="llm")
def route_tasks(state):
    tasks = state.get("tasks", [])

    logger.info(f"Routing tasks: {tasks}")

    response = llm.invoke(f"""
        You are an AI router.

        Available tools:
        - coding_tool → coding, frontend, backend, APIs
        - research_tool → evaluate, research, analysis, analyze, compare, find best strategy, daily conversation, general questions etc
        - qa_tool → testing, validation, bug checking
        - db_tool → database, SQL, schema, storage
        Match EACH task to ONE best tool.
                          
        Rules:       
        - Greetings or casual conversation → research_tool
        - Non-technical real-world questions → research_tool
        - Words like "best", "suggest", "recommend", "find", "movie", "compare", "evaluate" → research_tool
        - SQL schema or database design → db_tool
        - Coding related → coding_tool
        - Testing → qa_tool
        - Research → research_tool


        IMPORTANT:
        - Return ONLY a Python list
        - Length MUST equal number of tasks
        - EACH task gets EXACTLY ONE tool

        Example:
        Tasks: ["research UI", "build backend", "test system", "build database"]
        Output: ["research_tool", "coding_tool", "qa_tool", "db_tool"]

        Tasks: {tasks}
    """)

    raw_output = response.content.strip()
    logger.info(f"LLM raw output: {raw_output}")

    try:
        tools = ast.literal_eval(raw_output)

        if not isinstance(tools, list) or len(tools) != len(tasks):
            raise ValueError("Invalid tool list")

        logger.info(f"Tools selected (LLM): {tools}")
    except Exception as e:
        logger.warning(f"Router fallback triggered: {str(e)}")

        tools = []
        for task in tasks:
            # task_lower = task.lower()
            # if "research" in task_lower:
            #     tools.append("research_tool")
            # elif "test" in task_lower:
            #     tools.append("qa_tool")
            # elif "database" in task_lower or "sql" in task_lower:
            #     tools.append("db_tool")
            # else:
            #     tools.append("coding_tool")

            
            t = task.lower()

            if any(word in t for word in [
                "hi", "hello", "hey", "bye",
                "good morning", "good evening",
                "thank you", "thanks", "how are you"
            ]):
                tools.append("research_tool")

            elif any(word in t for word in [
                "research", "best", "suggest", "recommend",
                "find", "movie", "compare", "list",
                "what", "which", "who", "evaluate"
            ]):
                tools.append("research_tool")

            elif any(word in t for word in ["test", "testing", "qa"]):
                tools.append("qa_tool")

            elif any(word in t for word in ["database", "sql", "schema"]):
                tools.append("db_tool")

            elif any(word in t for word in [
                "frontend", "backend", "api", "code", "build"
            ]):
                tools.append("coding_tool")

            else:
                tools.append("research_tool")

        logger.info(f"Tools selected (fallback): {tools}")

    return {
        "selected_tools": tools
    }
