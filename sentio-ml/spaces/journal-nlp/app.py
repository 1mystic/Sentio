"""
Sentio JournalNLP — HuggingFace Space (Gradio API)

Endpoint consumed by sentio-api/services/journal_nlp.py:
  POST /analyze  body: {"text": "..."} → {"emotions": [...], "themes": [...]}

Pipeline:
  1. GoEmotions classifier (bhadresh-savani/distilbert-base-uncased-emotion)
  2. KeyBERT theme extraction (all-MiniLM-L6-v2)
"""
import json
import logging

import gradio as gr
from transformers import pipeline
from keybert import KeyBERT

logging.basicConfig(level=logging.INFO)
log = logging.getLogger(__name__)

EMOTION_MODEL = "bhadresh-savani/distilbert-base-uncased-emotion"
EMBED_MODEL   = "all-MiniLM-L6-v2"

log.info("Loading emotion classifier…")
emotion_pipe = pipeline(
    "text-classification",
    model=EMOTION_MODEL,
    return_all_scores=True,
    truncation=True,
    max_length=512,
)

log.info("Loading KeyBERT…")
kw_model = KeyBERT(model=EMBED_MODEL)
log.info("Models ready.")


def analyze(text: str) -> dict:
    if not text or not text.strip():
        return {"emotions": [], "themes": [], "dominant_emotion": None, "error": None}

    # Emotion classification — top 3 from 6-class GoEmotions distillation
    emotion_scores = emotion_pipe(text[:512])[0]
    top_emotions = sorted(emotion_scores, key=lambda x: x["score"], reverse=True)[:3]
    emotions = [
        {"label": e["label"], "score": round(e["score"], 4)}
        for e in top_emotions
    ]

    # Theme / keyword extraction using MMR for diversity
    keywords = kw_model.extract_keywords(
        text,
        keyphrase_ngram_range=(1, 2),
        stop_words="english",
        use_mmr=True,
        diversity=0.5,
        top_n=5,
    )
    themes = [{"phrase": kw, "relevance": round(score, 4)} for kw, score in keywords]

    return {
        "emotions": emotions,
        "themes": themes,
        "dominant_emotion": emotions[0]["label"] if emotions else None,
        "error": None,
    }


def _analyze_ui(text: str) -> str:
    return json.dumps(analyze(text), indent=2)


demo = gr.Interface(
    fn=_analyze_ui,
    inputs=gr.Textbox(label="Journal entry", lines=6, placeholder="Write about your day…"),
    outputs=gr.Code(label="Analysis result (JSON)", language="json"),
    title="Sentio JournalNLP",
    description="Emotion classification + keyword theme extraction for journal entries.",
    examples=[
        ["Today I had a really hard meeting. My boss criticized my work and I felt completely worthless afterwards."],
        ["I finally finished the project I've been working on for months. Proud but also exhausted."],
    ],
    api_name="analyze",
)

if __name__ == "__main__":
    demo.launch()
