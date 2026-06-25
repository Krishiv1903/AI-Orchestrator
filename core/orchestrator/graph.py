from langgraph.graph import StateGraph, END
from core.orchestrator.state import OrchestratorState

# from core.orchestrator.services.intent_analyzer import analyze_intent
from core.orchestrator.services.task_decomposer import decompose_tasks
from core.orchestrator.services.route_planner import route_tasks
from core.orchestrator.executor import execute_tools
from core.orchestrator.aggregator import aggregate

builder = StateGraph(OrchestratorState)

# Nodes
# builder.add_node("intent", analyze_intent)
builder.add_node("decompose", decompose_tasks)
builder.add_node("route", route_tasks)
builder.add_node("execute", execute_tools)
builder.add_node("aggregate", aggregate)

# Flow
builder.set_entry_point("decompose")

# builder.add_edge("intent", "decompose")
builder.add_edge("decompose", "route")
builder.add_edge("route", "execute")
builder.add_edge("execute", "aggregate")
builder.add_edge("aggregate", END)

graph = builder.compile()