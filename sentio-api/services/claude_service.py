"""Claude API wrapper with streaming."""
import os
import anthropic
from typing import AsyncGenerator

# Override with CLAUDE_MODEL env var; default is a widely-available, cost-effective model
_CLAUDE_MODEL = os.getenv("CLAUDE_MODEL", "claude-3-5-sonnet-20241022")

# The system prompt is large and static — mark it for caching.
# Anthropic caches up to 4 content blocks per request.
SYSTEM_PROMPT_TEXT = """You are Sentio's AI Guide — an expert in cognitive psychology, behavioral science, and metacognition.

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

Always be warm, intellectually curious, grounded in evidence. Keep responses concise (2-4 paragraphs max unless the user asks for detail).

IMPORTANT: You are an educational tool, not a therapist. Make this clear if users start treating you as one."""


def _build_system(
    rag_context: str = "",
    bias_fingerprint: dict | None = None,
    journal_themes: list | None = None,
) -> str:
    """Build the system prompt string, injecting dynamic user context."""
    context_parts: list[str] = []
    if bias_fingerprint:
        context_parts.append(f"User's bias profile: {bias_fingerprint}")
    if journal_themes:
        context_parts.append(f"Recent journal themes: {', '.join(journal_themes)}")
    if rag_context:
        context_parts.append(f"Relevant knowledge articles:\n{rag_context}")

    if context_parts:
        return SYSTEM_PROMPT_TEXT + "\n\nContext for this conversation:\n" + "\n\n".join(context_parts)
    return SYSTEM_PROMPT_TEXT


async def stream_response(
    user_message: str,
    rag_context: str = "",
    bias_fingerprint: dict | None = None,
    journal_themes: list | None = None,
) -> AsyncGenerator[str, None]:
    """Stream a Claude response token-by-token with prompt caching on the system prompt.

    Yields plain text chunks. The caller is responsible for safety-checking.
    """
    client = anthropic.AsyncAnthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))
    system = _build_system(rag_context, bias_fingerprint, journal_themes)

    async with client.messages.stream(
        model=_CLAUDE_MODEL,
        max_tokens=1024,
        system=system,
        messages=[{"role": "user", "content": user_message}],
    ) as stream:
        async for text in stream.text_stream:
            yield text


async def generate_journal_reflections(
    entry_text: str,
    detected_biases: list[dict],
) -> list[str]:
    """Generate 3 grounded reflection questions for a journal entry.

    Returns a list of 3 question strings.
    Falls back to generic questions if Claude is unavailable.
    """
    client = anthropic.AsyncAnthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))

    bias_names = [b.get("bias") or b.get("bias_id", "") for b in detected_biases if b]
    bias_context = f"Detected cognitive biases: {', '.join(bias_names)}" if bias_names else ""

    prompt = f"""A user wrote the following journal entry:

<entry>
{entry_text[:2000]}
</entry>

{bias_context}

Generate exactly 3 follow-up reflection questions that will help them examine this entry more deeply. The questions should:
- Be grounded in the specific content of their entry (not generic)
- Gently surface the cognitive biases detected without labeling the person
- Encourage self-compassion and curiosity, not self-criticism
- Be open-ended (no yes/no questions)

Return ONLY the 3 questions, one per line, no numbering, no preamble."""

    try:
        response = await client.messages.create(
            model=_CLAUDE_MODEL,
            max_tokens=300,
            system="You are a reflective journaling coach. Generate precise, grounded reflection questions.",
            messages=[{"role": "user", "content": prompt}],
        )
        lines = [l.strip() for l in response.content[0].text.strip().split('\n') if l.strip()]
        return lines[:3] if lines else _fallback_questions(bias_names)
    except Exception:
        return _fallback_questions(bias_names)


def _fallback_questions(bias_names: list[str]) -> list[str]:
    questions = [
        "What assumptions were you making in this situation that you didn't question at the time?",
        "If a close friend described this same situation to you, what would you tell them?",
        "What information might change your perspective if you knew it back then?",
    ]
    if "confirmation-bias" in bias_names or "confirmation_bias" in bias_names:
        questions[0] = "What evidence did you overlook or dismiss that might have changed your thinking?"
    if "fundamental-attribution-error" in bias_names:
        questions[1] = "What situational factors might explain the other person's behavior that you didn't consider?"
    return questions
