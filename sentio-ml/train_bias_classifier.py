"""
Fine-tune DistilBERT for multi-label cognitive bias classification.

Input:  data/synthetic/bias_training_v1.jsonl
Output: models/bias-classifier/  (saved as HuggingFace model directory)

Usage:
    cd sentio-ml
    python train_bias_classifier.py
    python train_bias_classifier.py --epochs 3 --batch 16 --threshold 0.4
"""
import json
import argparse
import logging
from pathlib import Path

import numpy as np
import torch
from datasets import Dataset
from sklearn.model_selection import train_test_split
from sklearn.metrics import f1_score, classification_report
from transformers import (
    AutoTokenizer,
    AutoModelForSequenceClassification,
    TrainingArguments,
    Trainer,
    EarlyStoppingCallback,
)

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
log = logging.getLogger(__name__)

BASE_MODEL = "distilbert-base-uncased"
DATA_PATH  = Path("data/synthetic/bias_training_v1.jsonl")
OUT_DIR    = Path("models/bias-classifier")

BIAS_LABELS = [
    "confirmation_bias", "attribution_error", "all_or_nothing",
    "catastrophizing", "mind_reading", "overgeneralization",
    "emotional_reasoning", "should_statements", "labeling",
    "personalization", "availability_bias", "anchoring_bias",
    "dunning_kruger", "sunk_cost_fallacy", "fundamental_attribution",
]
N_LABELS = len(BIAS_LABELS)
LABEL2ID = {l: i for i, l in enumerate(BIAS_LABELS)}


def load_dataset(path: Path) -> tuple[list[str], list[list[float]]]:
    texts, labels = [], []
    with open(path, encoding="utf-8") as f:
        for line in f:
            item = json.loads(line)
            vec = [0.0] * N_LABELS
            primary = item.get("primary_bias", "")
            if primary in LABEL2ID:
                vec[LABEL2ID[primary]] = 1.0
            for co in item.get("co_occurring", []):
                if co in LABEL2ID:
                    vec[LABEL2ID[co]] = 1.0
            texts.append(item["text"])
            labels.append(vec)
    return texts, labels


def tokenize(batch, tokenizer):
    return tokenizer(batch["text"], truncation=True, padding="max_length", max_length=256)


def compute_metrics(eval_pred, threshold=0.45):
    logits, true_labels = eval_pred
    probs = torch.sigmoid(torch.tensor(logits)).numpy()
    preds = (probs >= threshold).astype(int)
    macro_f1 = f1_score(true_labels, preds, average="macro", zero_division=0)
    micro_f1 = f1_score(true_labels, preds, average="micro", zero_division=0)
    return {"macro_f1": macro_f1, "micro_f1": micro_f1}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--epochs",    type=int,   default=5)
    parser.add_argument("--batch",     type=int,   default=16)
    parser.add_argument("--lr",        type=float, default=2e-5)
    parser.add_argument("--threshold", type=float, default=0.45)
    parser.add_argument("--seed",      type=int,   default=42)
    args = parser.parse_args()

    if not DATA_PATH.exists():
        log.error(f"Training data not found at {DATA_PATH}")
        log.error("Run `python data/generate_training_data.py` first.")
        return

    log.info("Loading data…")
    texts, labels = load_dataset(DATA_PATH)
    log.info(f"  {len(texts)} examples across {N_LABELS} classes")

    X_train, X_test, y_train, y_test = train_test_split(
        texts, labels, test_size=0.15, random_state=args.seed, shuffle=True
    )
    X_train, X_val, y_train, y_val = train_test_split(
        X_train, y_train, test_size=0.15 / 0.85, random_state=args.seed
    )
    log.info(f"  Train={len(X_train)}, Val={len(X_val)}, Test={len(X_test)}")

    tokenizer = AutoTokenizer.from_pretrained(BASE_MODEL)

    def make_hf_dataset(texts, labels):
        ds = Dataset.from_dict({"text": texts, "labels": labels})
        return ds.map(lambda b: tokenize(b, tokenizer), batched=True)

    train_ds = make_hf_dataset(X_train, y_train)
    val_ds   = make_hf_dataset(X_val,   y_val)
    test_ds  = make_hf_dataset(X_test,  y_test)

    log.info(f"Loading base model: {BASE_MODEL}")
    model = AutoModelForSequenceClassification.from_pretrained(
        BASE_MODEL,
        num_labels=N_LABELS,
        problem_type="multi_label_classification",
        id2label={i: l for i, l in enumerate(BIAS_LABELS)},
        label2id=LABEL2ID,
    )

    training_args = TrainingArguments(
        output_dir=str(OUT_DIR),
        num_train_epochs=args.epochs,
        per_device_train_batch_size=args.batch,
        per_device_eval_batch_size=args.batch,
        learning_rate=args.lr,
        warmup_ratio=0.1,
        weight_decay=0.01,
        eval_strategy="epoch",
        save_strategy="epoch",
        load_best_model_at_end=True,
        metric_for_best_model="macro_f1",
        greater_is_better=True,
        logging_steps=20,
        seed=args.seed,
        fp16=torch.cuda.is_available(),
        report_to="none",
    )

    trainer = Trainer(
        model=model,
        args=training_args,
        train_dataset=train_ds,
        eval_dataset=val_ds,
        tokenizer=tokenizer,
        compute_metrics=lambda ep: compute_metrics(ep, args.threshold),
        callbacks=[EarlyStoppingCallback(early_stopping_patience=2)],
    )

    log.info("Training…")
    trainer.train()

    log.info("Evaluating on test set…")
    preds_raw = trainer.predict(test_ds)
    probs = torch.sigmoid(torch.tensor(preds_raw.predictions)).numpy()
    preds = (probs >= args.threshold).astype(int)
    true  = np.array(y_test)

    macro_f1 = f1_score(true, preds, average="macro", zero_division=0)
    log.info(f"Test Macro F1: {macro_f1:.4f}")
    log.info("\nPer-class report:")
    print(classification_report(true, preds, target_names=BIAS_LABELS, zero_division=0))

    log.info(f"Saving model to {OUT_DIR}…")
    trainer.save_model(str(OUT_DIR))
    tokenizer.save_pretrained(str(OUT_DIR))

    # Save threshold and label map for the inference app
    config_extra = {"inference_threshold": args.threshold, "bias_labels": BIAS_LABELS}
    with open(OUT_DIR / "sentio_config.json", "w") as f:
        json.dump(config_extra, f, indent=2)

    log.info("Done.")


if __name__ == "__main__":
    main()
