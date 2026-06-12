"""
Unified LLM client — Anthropic primary, OpenRouter fallback.

Priority (checked at each call, so hot-switchable via env vars):
  1. ANTHROPIC_API_KEY set  → Anthropic SDK, model = CLAUDE_MODEL
  2. OPENROUTER_API_KEY set → OpenRouter OpenAI-compat endpoint, model = FALLBACK_MODEL

Switching when Anthropic credits expire (no code change needed):
  1. In HF Space → Settings → Repository secrets:
       - Clear / remove  ANTHROPIC_API_KEY
       - Add             OPENROUTER_API_KEY   (get one free at openrouter.ai)
       - Optionally set  FALLBACK_MODEL       (default: google/gemini-flash-1.5-exp  ← free tier)
         Other good options: openai/gpt-4o-mini · anthropic/claude-haiku-4-5 (via OR credits)
                             x-ai/grok-beta · meta-llama/llama-3.1-8b-instruct:free
  2. Click Restart Space — done.

FALLBACK_MODEL examples that work well for Sentio's prompts:
  google/gemini-flash-1.5-exp       free, fast, good instruction following
  openai/gpt-4o-mini                cheap, very reliable JSON output
  anthropic/claude-haiku-4-5        same model via OpenRouter credits
  meta-llama/llama-3.1-8b-instruct:free  fully free, smaller quality
"""
import os
import logging
from typing import AsyncGenerator

logger = logging.getLogger(__name__)

_DEFAULT_ANTHROPIC_MODEL = "claude-haiku-4-5-20251001"
_DEFAULT_FALLBACK_MODEL  = "google/gemini-flash-1.5-exp"


def _provider() -> tuple[str, str]:
    """Returns ('anthropic', model) or ('openrouter', model)."""
    if os.getenv("ANTHROPIC_API_KEY"):
        return "anthropic", os.getenv("CLAUDE_MODEL", _DEFAULT_ANTHROPIC_MODEL)
    if os.getenv("OPENROUTER_API_KEY"):
        model = os.getenv("FALLBACK_MODEL", _DEFAULT_FALLBACK_MODEL)
        logger.info(f"[LLM] Using OpenRouter fallback — model={model}")
        return "openrouter", model
    raise RuntimeError(
        "No LLM API key configured. Set ANTHROPIC_API_KEY or OPENROUTER_API_KEY in HF Space secrets."
    )


def has_llm() -> bool:
    """True if at least one provider key is configured."""
    return bool(os.getenv("ANTHROPIC_API_KEY") or os.getenv("OPENROUTER_API_KEY"))


# ── Streaming ──────────────────────────────────────────────────────────────────

async def _stream_anthropic(
    system: str, messages: list, model: str, max_tokens: int
) -> AsyncGenerator[str, None]:
    import anthropic as _anthropic
    client = _anthropic.AsyncAnthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))
    async with client.messages.stream(
        model=model, max_tokens=max_tokens, system=system, messages=messages
    ) as s:
        async for text in s.text_stream:
            yield text


async def _stream_openrouter(
    system: str, messages: list, model: str, max_tokens: int
) -> AsyncGenerator[str, None]:
    from openai import AsyncOpenAI
    client = AsyncOpenAI(
        base_url="https://openrouter.ai/api/v1",
        api_key=os.getenv("OPENROUTER_API_KEY"),
    )
    full_messages = [{"role": "system", "content": system}] + messages
    stream = await client.chat.completions.create(
        model=model, max_tokens=max_tokens, messages=full_messages, stream=True
    )
    async for chunk in stream:
        delta = chunk.choices[0].delta.content
        if delta:
            yield delta


async def stream_text(
    system: str,
    messages: list,
    max_tokens: int = 1024,
) -> AsyncGenerator[str, None]:
    """Stream LLM response text chunks. Provider chosen from env vars."""
    provider, model = _provider()
    if provider == "anthropic":
        async for chunk in _stream_anthropic(system, messages, model, max_tokens):
            yield chunk
    else:
        async for chunk in _stream_openrouter(system, messages, model, max_tokens):
            yield chunk


# ── Non-streaming completion ───────────────────────────────────────────────────

async def complete_text(
    system: str,
    messages: list,
    max_tokens: int = 400,
) -> str:
    """Return a complete LLM response as a string. Provider chosen from env vars."""
    provider, model = _provider()

    if provider == "anthropic":
        import anthropic as _anthropic
        client = _anthropic.AsyncAnthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))
        resp = await client.messages.create(
            model=model, max_tokens=max_tokens, system=system, messages=messages
        )
        return resp.content[0].text if resp.content else ""

    else:
        from openai import AsyncOpenAI
        client = AsyncOpenAI(
            base_url="https://openrouter.ai/api/v1",
            api_key=os.getenv("OPENROUTER_API_KEY"),
        )
        full_messages = [{"role": "system", "content": system}] + messages
        resp = await client.chat.completions.create(
            model=model, max_tokens=max_tokens, messages=full_messages
        )
        return resp.choices[0].message.content or ""
