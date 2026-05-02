import os
import anthropic
from typing import AsyncGenerator

SYSTEM_PROMPT = """You are Sentio's AI Guide — an expert in cognitive psychology, behavioral science, and metacognition.

Your role:
- Help users understand cognitive biases and how they manifest in real life
- Answer questions about psychology concepts grounded in research
- Gently illuminate patterns you notice in what users share
- Guide users toward self-reflection, NOT toward conclusions about themselves

You NEVER:
- Diagnose mental health conditions
- Provide therapy or clinical advice
- Make definitive claims about a user's psychology
- Suggest medications or clinical treatments

When users show signs needing professional support, say:
"This sounds like something worth exploring with a therapist. Sentio's therapist directory can connect you with a specialist."

Always be warm, intellectually curious, and grounded in evidence."""


async def stream_response(
    user_message: str,
    rag_context: str = "",
    bias_fingerprint: dict | None = None,
    journal_themes: list | None = None,
) -> AsyncGenerator[str, None]:
    """Stream a Claude response token-by-token.

    Yields plain text chunks as they arrive from the Anthropic API.
    The caller is responsible for safety-checking each chunk before
    forwarding it to the client.
    """
    client = anthropic.AsyncAnthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))

    context_parts: list[str] = []
    if bias_fingerprint:
        context_parts.append(f"User's current bias profile: {bias_fingerprint}")
    if journal_themes:
        context_parts.append(f"Recent journal themes: {', '.join(journal_themes)}")
    if rag_context:
        context_parts.append(f"Relevant knowledge:\n{rag_context}")

    full_system = SYSTEM_PROMPT
    if context_parts:
        full_system += "\n\nContext for this conversation:\n" + "\n".join(context_parts)

    async with client.messages.stream(
        model="claude-sonnet-4-6",
        max_tokens=1024,
        system=full_system,
        messages=[{"role": "user", "content": user_message}],
    ) as stream:
        async for text in stream.text_stream:
            yield text
