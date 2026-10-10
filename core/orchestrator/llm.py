from langchain_groq import ChatGroq
import os
from functools import lru_cache


@lru_cache(maxsize=1)
def get_llm() -> ChatGroq:
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        raise RuntimeError("GROQ_API_KEY is required to run AI tasks")

    return ChatGroq(
        model=os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile"),
        temperature=0.3,
        api_key=api_key,
    )