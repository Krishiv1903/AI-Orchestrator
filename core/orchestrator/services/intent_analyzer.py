# from core.orchestrator.llm import llm

# from langsmith import traceable


# @traceable(run_type="llm")
# def analyze_intent(state):
#     prompt = state["user_prompt"]

#     response = llm.invoke(f"""
#         You are an intent analyzer
#         Classify the intent of this prompt into one or more of:
#         - Coding
#         - research
#         - Q/A
#         - Database
                          

#         Return ONLY the label.

#         Prompt: {prompt}
#     """)

#     return {
#         "intent": response.content,
#         "routing_history": state.get("routing_history", []) + ["intent_detected"]
#     }