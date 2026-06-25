def is_safe_prompt(prompt: str) -> tuple[bool, str]:

    blocked = ["hack", "crash", "exploit", "attack"]

    if any(word in prompt.lower() for word in blocked):
        return False, "❌ Unsafe request blocked"

    from core.orchestrator.llm import llm

    response = llm.invoke(f"""
        Is this request harmful or unsafe?

        Reply ONLY SAFE or UNSAFE.

        Prompt: {prompt}
    """)

    if "UNSAFE" in response.content.upper():
        return False, "❌ Unsafe request blocked"

    return True, ""