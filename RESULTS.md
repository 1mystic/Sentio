# Sentio — Eval Results

Populate this file by running the eval scripts from `sentio-api/`:

```bash
# RAG retrieval eval (precision@3 + MRR before/after Cohere rerank)
python scripts/eval_rag.py

# Bias classifier eval (30-entry per-class human-agreement)
python scripts/eval_bias.py
```

Each script appends its section below and writes a companion JSON file
(`scripts/rag_eval_results.json` and `scripts/bias_eval_results.json`).

---

*Results sections will appear here after the scripts are run against the live Supabase instance.*
