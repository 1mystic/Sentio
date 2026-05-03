"""
Sentio BiasClassifier — HuggingFace Space (Gradio API)

Endpoint consumed by sentio-api/services/bias_classifier.py:
  POST /classify  body: {"text": "..."} → {"biases": [{label, confidence}]}

The model directory is uploaded to this Space alongside this app.py.
Set HF_MODEL_PATH env var to override the default "./model" path.
"""
import os
import json
import logging
from pathlib import Path

import torch
import gradio as gr
from transformers import AutoTokenizer, AutoModelForSequenceClassification

logging.basicConfig(level=logging.INFO)
log = logging.getLogger(__name__)

MODEL_PATH = os.getenv("HF_MODEL_PATH", "./model")
SENTIO_CONFIG = Path(MODEL_PATH) / "sentio_config.json"

log.info(f"Loading model from {MODEL_PATH}…")
tokenizer = AutoTokenizer.from_pretrained(MODEL_PATH)
model = AutoModelForSequenceClassification.from_pretrained(MODEL_PATH)
model.eval()

# Load inference config saved during training
if SENTIO_CONFIG.exists():
    with open(SENTIO_CONFIG) as f:
        cfg = json.load(f)
    THRESHOLD = cfg.get("inference_threshold", 0.45)
    BIAS_LABELS = cfg.get("bias_labels", list(model.config.id2label.values()))
else:
    THRESHOLD = 0.45
    BIAS_LABELS = list(model.config.id2label.values())

log.info(f"Model loaded. {len(BIAS_LABELS)} labels, threshold={THRESHOLD}")


def classify(text: str, threshold: float = THRESHOLD) -> dict:
    """Return detected biases with confidence scores."""
    if not text or not text.strip():
        return {"biases": [], "error": None}

    inputs = tokenizer(
        text,
        return_tensors="pt",
        truncation=True,
        max_length=256,
        padding=True,
    )
    with torch.no_grad():
        logits = model(**inputs).logits
    probs = torch.sigmoid(logits).squeeze().tolist()

    biases = [
        {"label": label, "confidence": round(prob, 4)}
        for label, prob in zip(BIAS_LABELS, probs)
        if prob >= threshold
    ]
    biases.sort(key=lambda x: x["confidence"], reverse=True)
    return {"biases": biases, "error": None}


# Gradio interface (also serves as the API endpoint)
def _classify_ui(text: str) -> str:
    result = classify(text)
    return json.dumps(result, indent=2)


demo = gr.Interface(
    fn=_classify_ui,
    inputs=gr.Textbox(label="Journal entry or text", lines=6, placeholder="Enter text to analyze…"),
    outputs=gr.Code(label="Detected biases (JSON)", language="json"),
    title="Sentio BiasClassifier",
    description="Identifies cognitive biases in text. Returns bias labels and confidence scores.",
    examples=[
        ["I knew this project would fail — I've seen it happen to every team that tries this approach."],
        ["My manager gave me constructive feedback but I can tell she thinks I'm incompetent."],
        ["I invested six months in this relationship so I have to make it work."],
    ],
    api_name="classify",
)

if __name__ == "__main__":
    demo.launch()
