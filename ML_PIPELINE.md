# Sentio — ML/DL Pipeline Specification
## Every Model, Dataset, Training Plan & Integration

---

## Overview

Sentio's ML layer is designed to be **portfolio-grade** — each model demonstrates a distinct DL/ML skill and uses **publicly available datasets** combined with curated domain data. Models are versioned, validated, and deployed in a way that shows production readiness.

```
PUBLIC DATASETS          DOMAIN DATA                MODELS
─────────────────        ───────────────────────    ─────────────────────
SemEval (bias)    →      Bias-annotated journals  → BiasClassifier (DLM)
GoEmotions        →      Sentio journal entries   → JournalNLP (DLM)
Survey data       →      Assessment results       → ArchetypeModel (unsup)
Interaction logs  →      User-bias interactions   → RecommendationEngine
Activity streams  →      Engagement events        → EngagementPredictor
Psychology corpus →      Curated articles         → RAG Knowledge Base
```

---

## Model 1: BiasClassifier (Core, Portfolio Highlight)

### What It Does
Identifies cognitive biases present in free-text journal entries or responses. Returns: `[{bias_label, confidence, text_span}]`

### Why It's Impressive
- Multi-label text classification on a novel, domain-specific task
- Shows: transfer learning, custom training data construction, multi-label output heads
- Real-world impact: the core differentiator of Sentio

### Architecture
```
Input text (journal entry or response)
        ↓
DistilBERT base (pre-trained)
        ↓
Custom classification head:
  - Dropout(0.3)
  - Linear(768 → 256) → ReLU
  - Linear(256 → N_BIASES)  # multi-label sigmoid
        ↓
Threshold (0.45 per label) → bias predictions
        ↓
Span extraction (attention rollout for interpretability)
```

### Dataset Construction Plan

**Phase 1 — Bootstrap with Public Data**
| Dataset | Source | Use |
|---|---|---|
| CrowS-Pairs | NYU (HuggingFace) | Social/stereotyping biases baseline |
| BiasBench | ACL 2023 | Multi-dimensional bias evaluation |
| SBIC (Social Bias Inference Corpus) | allenai/social_bias_frames (HF) | Social bias in text |
| WinoBias | HuggingFace datasets | Gender bias examples |
| SemEval 2019 Task 7 | SemEval | Rumour stance (confirmation bias proxy) |

**Phase 2 — Domain Construction (Weeks 2-4)**
```python
# Bias label set (start with 15 most common, expand to 30)
BIAS_LABELS = [
    "confirmation_bias",       # Seeking info confirming existing beliefs
    "attribution_error",       # Blaming others, not circumstances
    "all_or_nothing",          # Black-and-white thinking
    "catastrophizing",         # Worst-case assumption
    "mind_reading",            # Assuming others' thoughts
    "overgeneralization",      # One event → universal rule
    "emotional_reasoning",     # Feeling true = being true
    "should_statements",       # Rigid rules about self/others
    "labeling",                # Reducing self/others to a trait
    "personalization",         # Taking blame for external events
    "availability_bias",       # Recent/vivid events weighted high
    "anchoring_bias",          # Over-relying on first piece of info
    "dunning_kruger",          # Overconfidence in low-knowledge areas
    "sunk_cost_fallacy",       # Continuing due to past investment
    "fundamental_attribution"  # Underweighting situational factors
]

# Data generation pipeline
# 1. GPT-4/Claude generates 50 examples per bias (with explicit bias labels)
# 2. Human review (you + 2 friends) validate each example
# 3. Augment with paraphrase (back-translation via OPUS-MT)
# Result: ~750 labeled examples (50 per class × 15 classes)
```

**Phase 3 — Active Learning (Post-MVP)**
- Real user journal entries (with consent) → flag uncertain predictions → human review → retrain

### Training Configuration
```python
# train_bias_classifier.py
from transformers import DistilBertForSequenceClassification, TrainingArguments
import torch

MODEL_CONFIG = {
    "base_model": "distilbert-base-uncased",
    "num_labels": 15,          # expand later
    "problem_type": "multi_label_classification",
    "hidden_dropout_prob": 0.3,
}

TRAINING_CONFIG = TrainingArguments(
    output_dir="./sentio-bias-classifier",
    num_train_epochs=5,
    per_device_train_batch_size=16,
    learning_rate=2e-5,
    warmup_steps=100,
    weight_decay=0.01,
    evaluation_strategy="epoch",
    save_strategy="best",
    load_best_model_at_end=True,
    metric_for_best_model="f1",
)

# Loss: BCEWithLogitsLoss (multi-label)
# Optimizer: AdamW
# Scheduler: linear warmup + cosine decay
```

### Validation Strategy
```
Train/Val/Test split: 70/15/15
Primary metric: Macro F1 (handles class imbalance)
Secondary: Per-class F1, Precision, Recall
Baseline: Keyword-matching classifier (must beat by >15% F1)
Target: Macro F1 ≥ 0.65 (acceptable for novel task)
Interpretability: Attention rollout for span highlighting
```

### MLflow Tracking
```python
with mlflow.start_run(run_name="bias-clf-v1"):
    mlflow.log_params(TRAINING_CONFIG.__dict__)
    mlflow.log_metric("macro_f1", val_f1)
    mlflow.log_metric("per_class_f1", per_class_f1)
    mlflow.pytorch.log_model(model, "bias-classifier")
```

### Deployment
- HuggingFace Spaces (Gradio API) — free tier sufficient
- Endpoint: `POST /classify` → `{text: str}` → `[{bias, confidence, span}]`
- Latency target: <1s for entries up to 500 words

---

## Model 2: JournalNLP (Sentiment + Themes)

### What It Does
- Sentiment analysis (valence + arousal, not just pos/neg)
- Theme extraction (key topics in journal entry)
- Emotion classification (GoEmotions taxonomy: 28 emotions)

### Architecture
```
Input: Journal text
        ↓
Sentence splitting (nltk)
        ↓
    ┌───────────────────────────────┐
    │ DistilBERT fine-tuned on      │
    │ GoEmotions (28 emotion labels)│
    └───────────────────────────────┘
        ↓                     ↓
Emotion scores          KeyBERT themes
(per sentence)          (MMR diversity)
        ↓                     ↓
    Aggregate → Entry-level emotion profile
              → Top 5 themes
              → Dominant emotional tone
```

### Datasets
| Dataset | Source | Size | Use |
|---|---|---|---|
| GoEmotions | google-research-datasets/go_emotions (HF) | 58K examples | Fine-tune emotion classifier |
| SemEval 2018 Task 1 | SemEval | Multi-label affect | Validation |

### Implementation
```python
# Two-stage pipeline
from transformers import pipeline
from keybert import KeyBERT

# Stage 1: Emotion classification
emotion_classifier = pipeline(
    "text-classification",
    model="bhadresh-savani/distilbert-base-uncased-emotion",
    return_all_scores=True
)

# Stage 2: Theme extraction
kw_model = KeyBERT(model='all-MiniLM-L6-v2')

def analyze_journal_entry(text: str) -> dict:
    # Emotions
    emotions = emotion_classifier(text[:512])[0]
    top_emotions = sorted(emotions, key=lambda x: x['score'], reverse=True)[:3]
    
    # Themes
    keywords = kw_model.extract_keywords(
        text,
        keyphrase_ngram_range=(1, 2),
        stop_words='english',
        use_mmr=True,
        diversity=0.5,
        top_n=5
    )
    
    # Sentiment
    sentiment = compute_valence_arousal(emotions)
    
    return {
        "top_emotions": top_emotions,
        "themes": [kw for kw, score in keywords],
        "sentiment": sentiment,
        "word_count": len(text.split())
    }
```

---

## Model 3: ArchetypeModel (Unsupervised — Impressive for Portfolio)

### What It Does
Clusters users into **cognitive archetypes** based on their assessment results and bias profile. Example archetypes:
- "The Pattern-Seeker" (high confirmation + availability bias)
- "The Self-Critic" (high self-attribution + should-statements)
- "The Optimist" (low catastrophizing, high positive framing)
- "The Overthinker" (high anxiety-adjacent biases)

### Why It's Impressive
- Unsupervised clustering is harder to explain than supervised → good interview talking point
- Shows: dimensionality reduction, density-based clustering, interpretable cluster labeling
- Real product value: personalizes experience without requiring labels

### Architecture
```python
# Feature vector per user
user_features = {
    "bias_scores": [0.0..1.0] * N_BIASES,         # from BiasClassifier
    "assessment_scores": {                          # from validated tools
        "need_for_cognition": 0.0..1.0,
        "cognitive_flexibility": 0.0..1.0,
        "metacognitive_awareness": 0.0..1.0,
    },
    "journal_emotion_profile": [0.0..1.0] * 28,   # avg GoEmotions
    "behavioral_traits": {
        "journaling_frequency": float,
        "assessment_completion": float,
    }
}

# Pipeline
StandardScaler()
    ↓
UMAP(n_components=10, n_neighbors=15, min_dist=0.1)
    ↓
HDBSCAN(min_cluster_size=10, min_samples=5)
    ↓
Archetype labeling (manual + LLM-assisted for top centroid features)
    ↓
Store archetype_id + confidence in user_bias_profiles
```

### Validation
- Silhouette score (target ≥ 0.35)
- Cluster stability (bootstrap resampling: same users in same cluster >80% of runs)
- Qualitative: do cluster centroids make psychological sense? (review with psychology literature)

### Schedule
- Runs as GitHub Actions batch job (weekly)
- Triggers: ≥50 new users with completed assessments OR weekly on schedule
- Model artifacts stored in HuggingFace Hub

---

## Model 4: Recommendation Engine

### What It Does
Recommends: (a) which bias to explore next, (b) which assessment to take, (c) which therapist to consider

### Architecture: Hybrid (Content + Collaborative)

**Bias Exploration Recommendations**
```python
# Content-based: exploit known bias relationships
def recommend_bias_to_explore(user_bias_profile):
    dominant_biases = get_top_biases(user_bias_profile, n=3)
    
    # Strategy 1: Adjacent biases (same cognitive category)
    adjacent = get_biases_by_category(dominant_biases[0].category)
    
    # Strategy 2: Root biases (address causes, not symptoms)
    root_biases = get_related(dominant_biases, relationship="root_cause")
    
    # Strategy 3: Unexplored (biases not yet encountered by user)
    unexplored = get_unexplored(user_id, all_biases)
    
    return rank_by_educational_value(adjacent + root_biases + unexplored)
```

**Assessment Recommendations**
```python
# Rule-based + utility scoring
def recommend_assessment(user):
    completed = get_completed_assessments(user.id)
    candidates = [a for a in ALL_ASSESSMENTS if a.id not in completed]
    
    # Score by: alignment with dominant bias category + time since last + diversity
    scores = {}
    for a in candidates:
        alignment = bias_assessment_alignment(user.bias_profile, a.target_biases)
        recency_bonus = 1.0 if not recently_completed(user.id, a.category) else 0.5
        scores[a.id] = alignment * recency_bonus
    
    return sorted(candidates, key=lambda a: scores[a.id], reverse=True)[:3]
```

**Collaborative Filtering (Post-MVP)**
```python
# Matrix factorization: users × biases → interaction scores
# Dataset: user_id, bias_id, interaction_type (viewed/assessed/journaled_about)
# Model: implicit ALS (Alternating Least Squares)
# Library: implicit (open-source, fast)
# Triggers when: ≥200 active users with ≥10 bias interactions each
```

---

## Model 5: EngagementPredictor

### What It Does
Predicts: likelihood of user dropout in next 7 days → triggers re-engagement nudge

### Architecture
```python
# Features per user (computed daily)
features = {
    "days_since_last_login": int,
    "days_since_last_journal": int,
    "assessment_completion_rate": float,
    "streak_length": int,
    "streak_broken_recently": bool,
    "onboarding_completeness": float,
    "bias_profile_confidence": float,
    "session_length_trend": float,    # increasing/decreasing
}

# Model: XGBoost classifier
# Label: churned = no login in next 7 days
# Training data: historical user activity logs (simulate initially)
# Deploy: FastAPI endpoint, called by scheduled job (daily)
# MLflow: track AUC-ROC, precision@7day, recall@7day
```

### Training Data Bootstrap
```python
# Phase 1: Synthetic data (weeks 1-2)
# Simulate realistic user engagement patterns
# Use engagement research: Fogg's behavior model as feature engineering guide

# Phase 2: Real data (post-beta launch)
# 20-50 beta users × 30 days = 600-1500 daily feature rows
# Minimum viable training set: 500 rows with 10% churn rate
```

---

## Model 6: AI Guide (RAG — Claude Integration)

### Knowledge Base Construction

**Sources for psychology corpus:**
| Source | Content | Format | Volume |
|---|---|---|---|
| Wikipedia Psychology | Bias definitions, history | Auto-scraped | ~200 articles |
| Simply Psychology | Accessible explanations | Manual curated | ~100 articles |
| Thinking, Fast and Slow summaries | Kahneman's framework | Manual | 20 summaries |
| APA Dictionary of Psychology | Definitions | API scrape | ~500 terms |
| PsyArXiv preprints (open access) | Research evidence | Selective | ~50 papers |

**Embedding Pipeline**
```python
from sentence_transformers import SentenceTransformer

model = SentenceTransformer('all-MiniLM-L6-v2')  # 384-dim, fast, free

def embed_and_store(articles):
    for article in articles:
        chunks = chunk_text(article.content, max_tokens=256, overlap=32)
        for chunk in chunks:
            embedding = model.encode(chunk)
            supabase.table('knowledge_articles').insert({
                'content': chunk,
                'embedding': embedding.tolist(),
                'source': article.source,
                'title': article.title
            }).execute()
```

**RAG Query Pipeline**
```python
async def rag_query(user_query: str, user_context: dict) -> str:
    # 1. Embed query
    query_embedding = embedder.encode(user_query)
    
    # 2. Retrieve (pgvector cosine similarity)
    results = supabase.rpc('match_knowledge', {
        'query_embedding': query_embedding.tolist(),
        'match_threshold': 0.7,
        'match_count': 10
    }).execute()
    
    # 3. ReRank (Cohere)
    reranked = cohere_client.rerank(
        query=user_query,
        documents=[r['content'] for r in results.data],
        top_n=3
    )
    
    # 4. Build context
    rag_context = "\n\n".join([r.document['text'] for r in reranked.results])
    
    # 5. Claude generation (streaming)
    response = await claude_stream(
        system=SYSTEM_PROMPT.format(
            bias_fingerprint=user_context['bias_fingerprint'],
            journal_themes=user_context['journal_themes'],
            rag_context=rag_context
        ),
        user_message=user_query
    )
    
    return response
```

---

## Public Dataset Registry

Complete list of datasets used or planned:

```
Bias Detection:
├── allenai/social_bias_frames          (HuggingFace Hub)
├── nyu-mll/crowspairs                  (HuggingFace Hub)
├── WinoBias                            (winoground.github.io)
└── SemEval 2019 Task 7                 (semeval.github.io)

Emotion/Sentiment:
├── google-research-datasets/go_emotions (HuggingFace Hub)
├── SemEval 2018 Task 1 (EI-reg)        (semeval.github.io)
└── dair-ai/emotion                     (HuggingFace Hub)

Engagement/Behavior:
└── Synthetic (generated from behavior models + seeded with real patterns)

NLP Utilities:
├── sentence-transformers/all-MiniLM-L6-v2  (HF Hub, embedding)
└── distilbert-base-uncased              (HF Hub, base model)
```

---

## ML Engineering Practices (For Portfolio)

### Reproducibility
```
sentio-ml/
├── data/
│   ├── raw/                 (gitignored, download scripts provided)
│   ├── processed/           (versioned with DVC)
│   └── synthetic/           (committed — small, for bootstrap)
├── notebooks/
│   ├── 01_bias_data_exploration.ipynb
│   ├── 02_bias_classifier_training.ipynb
│   ├── 03_journal_nlp_pipeline.ipynb
│   └── 04_archetype_clustering.ipynb
├── src/
│   ├── data/                (dataset loaders + preprocessors)
│   ├── models/              (model definitions)
│   ├── training/            (training loops)
│   └── evaluation/          (metrics + validation)
├── configs/                 (YAML configs per model)
├── mlflow/                  (tracking server setup)
├── requirements.txt
└── README.md                (how to reproduce all results)
```

### Version Control for Models
- Training runs tracked in MLflow
- Model artifacts in HuggingFace Hub (public repo: `atharv-khare/sentio-bias-classifier`)
- Data versions tracked with DVC (points to remote storage)
- Every model card includes: architecture, dataset, metrics, limitations, ethical considerations

### Interview Talking Points Per Model
**BiasClassifier:**
> "I fine-tuned DistilBERT on a multi-label cognitive bias detection task. The main challenge was constructing training data for a novel domain — I combined public bias datasets (CrowS-Pairs, SBIC) with 750 custom examples I generated and validated. I achieved macro F1 of 0.67 on a held-out test set. Key learnings: multi-label thresholding, class imbalance handling with weighted BCE loss, and interpretability via attention rollout."

**ArchetypeModel:**
> "I used UMAP + HDBSCAN to cluster users into cognitive archetypes based on their assessment results and detected bias patterns. The main challenge was validating unsupervised outputs — I used silhouette score plus bootstrap stability analysis, and cross-referenced clusters with known psychology archetypes from the literature. This showed up as interpretable user profiles in the product."

**RAG Pipeline:**
> "I built a RAG system using pgvector for retrieval and Cohere for re-ranking, feeding into Claude for generation. The key design decision was chunking strategy — 256-token chunks with 32-token overlap prevented context fragmentation. I evaluated retrieval quality using a held-out QA set derived from psychology textbooks."
