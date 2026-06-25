from core.orchestrator.mcp_client import call_tool
from core.utils.logger import setup_logger

logger = setup_logger("executor")

def execute_tools(state):
    tasks = state.get("tasks", [])
    tools = state.get("selected_tools", [])
    prev_output = None

    outputs = {}

    logger.info(f"Executing tools | tasks={tasks} | tools={tools}")

    for i, (task, tool) in enumerate(zip(tasks, tools)):
        key = f"{tool}_{i}"

        try:
            payload = {"task": task}
            if prev_output:
                payload["code_context"] = prev_output
                print(f"Passing context to {tool}: {prev_output}")
                logger.info(f"Passing context to {tool}: {prev_output}")

            logger.info(f"Calling tool: {tool} | payload={payload}")
            result = call_tool(tool, payload)

            if isinstance(result, dict) and result.get("type") == "error":
                
                error_msg = result.get("output", {}).get("error", "Unknown error")
                logger.warning(f"Tool error | tool={tool} | error={error_msg}")

                outputs[key] = {
                    "error": error_msg
                }
                prev_output = None
            else:
                output = result.get("output", result)
                logger.info(f"Tool success | tool={tool} | output={output}")
                outputs[key] = output
                prev_output = output

        except Exception as e:
            logger.error(f"Execution failure | tool={tool} | error={str(e)}")

            outputs[key] = {
                "error": str(e)
            }
            prev_output = None
    logger.info(f"Execution completed | outputs={outputs}")

    return {"outputs": outputs}