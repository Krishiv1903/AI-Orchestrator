from typing import TypedDict, List, Dict

class OrchestratorState(TypedDict):
    user_prompt: str
    intent: str
    tasks: List[str]
    selected_tools: List[str]
    outputs: Dict[str, str]