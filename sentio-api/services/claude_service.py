"""LLM wrapper for Sentio AI features — streaming chat, journal reflections, Socratic mode."""
import os
import json
from typing import AsyncGenerator
from services.llm_client import stream_text, complete_text

# Override with CLAUDE_MODEL env var (Anthropic) or FALLBACK_MODEL (OpenRouter).
# See services/llm_client.py for full provider-switching instructions.

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
    memory_context: str = "",
) -> str:
    context_parts: list[str] = []
    if memory_context:
        context_parts.append(f"What Sentio remembers about this user:\n{memory_context}")
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
    memory_context: str = "",
) -> AsyncGenerator[str, None]:
    system = _build_system(rag_context, bias_fingerprint, journal_themes, memory_context)
    async for chunk in stream_text(system, [{"role": "user", "content": user_message}], max_tokens=1024):
        yield chunk


async def generate_journal_reflections(
    entry_text: str,
    detected_biases: list[dict],
) -> list[str]:
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
        text = await complete_text(
            system="You are a reflective journaling coach. Generate precise, grounded reflection questions.",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=300,
        )
        lines = [l.strip() for l in text.strip().split('\n') if l.strip()]
        return lines[:3] if lines else _fallback_questions(bias_names)
    except Exception:
        return _fallback_questions(bias_names)


async def stream_socratic_response(
    message: str,
    conversation_history: list,
    domain: str,
    next_state: str,
    quality_score: float,
    misconception: str | None,
    clarity_score: int,
    bias_scores: dict,
    journal_themes: list,
) -> AsyncGenerator[str, None]:
    STATE_INSTRUCTIONS: dict[str, str] = {
        "PROBE": "Ask what the user already thinks. Do NOT explain. ONE focused question about their prior understanding. Begin: 'Before I respond...' or 'What's your intuition about...'",
        "DEEPEN": "Acknowledge ONE thing they got right, then probe deeper. Ask about edge cases or mechanisms.",
        "SCAFFOLD": "User is confused. Give ONE minimal foothold — a simpler analogy or hint. 'Let me give you a starting point: [hint]. Given that, what do you think follows?'",
        "RECTIFY": f"There is a misconception: '{misconception or 'unclear reasoning'}'. Address gently without saying 'you're wrong'. Guide them to discover the error themselves.",
        "REDIRECT": "They've drifted off-topic. Gently redirect: 'Interesting — how does that relate to [original concept]?'",
        "CONSOLIDATE": "Rich discussion so far. Offer to synthesise: 'We've covered a lot of ground. Want me to put together what you've figured out?'",
        "COMPLETE": "Session complete. Warm closing. Acknowledge what they discovered themselves. Suggest generating their insight card.",
    }

    high_bias = [k for k, v in (bias_scores or {}).items() if v > 60]

    system = f"""You are Sentio's Socratic Guide — a Socratic AI tutor that builds genuine understanding through dialogue.

CURRENT DIALOGUE STATE: {next_state}
YOUR INSTRUCTION: {STATE_INSTRUCTIONS.get(next_state, STATE_INSTRUCTIONS['PROBE'])}

SESSION CONTEXT:
- Domain: {domain}
- Clarity score: {clarity_score}/100
- Response quality: {quality_score:.2f}/1.0
- User's notable cognitive patterns: {', '.join(high_bias) if high_bias else 'not yet established'}
- Recent journal themes: {', '.join(journal_themes[:3]) if journal_themes else 'none'}

ABSOLUTE RULES:
1. NEVER directly answer the question until state is CONSOLIDATE or COMPLETE
2. NEVER say 'you're wrong' or 'that's incorrect' — guide them to discover errors
3. NEVER diagnose or provide clinical advice
4. Keep responses under 120 words — density over volume
5. End every response with exactly one question (except COMPLETE state)
6. If a cognitive bias connection arises naturally, note it once — gently, as a lens not a label"""

    messages = conversation_history + [{"role": "user", "content": message}]
    async for chunk in stream_text(system, messages, max_tokens=300):
        yield chunk


async def generate_socratic_insight_card(
    conversation_history: list,
    concept: str,
    domain: str,
) -> dict:
    recent = conversation_history[-10:]
    summary_lines = [f"{m['role'].upper()}: {m['content'][:200]}" for m in recent]
    conversation_summary = "\n".join(summary_lines)

    user_messages = [m["content"] for m in conversation_history if m["role"] == "user"]
    strong = [m for m in user_messages if any(kw in m.lower() for kw in ["because", "therefore", "since", "which means", "however", "specifically"])]
    gaps = [m for m in user_messages if any(kw in m.lower() for kw in ["not sure", "don't know", "confused", "maybe", "i think"])]

    prompt = f"""Based on this Socratic conversation, generate a precise insight card.

Domain: {domain}
Main concept: {concept}
Conversation:
{conversation_summary}

User's strongest reasoning: {' | '.join(strong[:3]) if strong else 'building understanding'}
User's hesitations: {' | '.join(gaps[:3]) if gaps else 'none noted'}

Respond with ONLY valid JSON, no markdown:
{{
  "concept": "the main concept explored",
  "insight": "2-3 sentences of what the user now genuinely understands, written directly to them. Reference their actual reasoning.",
  "gaps": ["concrete adjacent concept 1", "concept 2", "concept 3"],
  "clarity_score": 0,
  "next_question": "one natural follow-up question to start their next session"
}}

Rules:
- insight must reference their actual words/reasoning, not be generic
- gaps: concrete concept names only
- clarity_score: 0-100 integer (0-40 surface, 41-70 conceptual, 71-90 analytical, 91-100 synthesis)"""

    try:
        text = await complete_text(
            system="You generate precise, non-generic insight cards from Socratic tutoring sessions.",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=400,
        )
        clean = text.replace("```json", "").replace("```", "").strip()
        return json.loads(clean)
    except Exception:
        return {
            "concept": concept,
            "insight": "You explored this concept through dialogue and built initial understanding.",
            "gaps": [],
            "clarity_score": 40,
            "next_question": f"What aspect of {concept} would you like to explore next?",
        }


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
