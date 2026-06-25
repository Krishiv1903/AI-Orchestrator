from langchain_groq import ChatGroq
import os


llm = ChatGroq(
    model="llama-3.3-70b-versatile",
    temperature=0.3
)