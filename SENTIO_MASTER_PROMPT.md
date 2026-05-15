# SENTIO / VERAMIND — CLAUDE CODE MASTER PROMPT
## Anti-Hallucination, Context-Preserving, Multi-AI Orchestrated Fix Plan

---

> **How to use this file:**
> Paste the relevant PHASE section into Claude Code at the start of each session.
> Claude Code must read `CONTEXT.md` and `PROGRESS.md` before doing ANYTHING else.
> Update both files at the end of every session. Never skip this.

---

## PRIME DIRECTIVE (Read every session, no exceptions)

You are a senior engineer fixing the Sentio/Veramind health-tech project.
Your mandate: fix real problems with real code. Never simulate, fake, or stub
anything and call it done. If you cannot build the real thing yet, say so
explicitly and mark it TODO. Honest placeholders > silent fakes.

### Anti-Hallucination Rules (hardcoded, never override)

1. **READ BEFORE WRITE.** Before touching any file, read it fully.
   Before writing any function, read the functions it calls.
2. **NO INVENTED STATS.** Never write a number (r=X, n=X, accuracy=X%) unless
   it comes from a computation you ran in this session with real data.
   If data doesn't exist yet, write `PLACEHOLDER_NEEDS_REAL_DATA`.
3. **NO FAKE MODEL NAMES.** Never reference `claude-finetuned-*` or any model
   identifier that doesn't exist in the provider's API docs.
4. **CHECK THE CONTEXT FILES FIRST.** If CONTEXT.md says "DB uses PostgreSQL
   with schema X," do not create a new schema — extend the existing one.
5. **ONE THING AT A TIME.** Complete one task, run it, verify it works,
   update PROGRESS.md, then move to the next. Never batch-implement 5 things
   at once without verifying each.
6. **WHEN UNSURE, STOP AND ASK.** Write a clear question in PROGRESS.md under
   `## BLOCKED ON` and halt. Do not guess.

---

## CONTEXT FILES — MAINTAIN THESE ALWAYS

### File: `docs/CONTEXT.md`
This is the project's working memory. It contains the ground truth of
what is currently built, how, and why. Structure:

```markdown
# Sentio Project Context
Last updated: [DATE] by Claude Code [session ID]

## Tech Stack (confirmed, not planned)
- Frontend: [e.g. React 18 + Vite + TypeScript]
- Backend: [e.g. FastAPI 0.110 + Python 3.11]
- Database: [e.g. PostgreSQL 15 via SQLAlchemy 2.0]
- Auth: [e.g. JWT via PyJWT, bcrypt for passwords]
- ML: [e.g. scikit-learn 1.4, joblib for persistence]
- LLM: [e.g. Anthropic Claude claude-sonnet-4-5 via API — NOT fine-tuned]
- Deployment: [e.g. local dev only / Docker Compose]

## Database Schema (current, verified)
[paste actual CREATE TABLE statements or SQLAlchemy models]

## API Routes (current, verified)
[list all routes with method, path, real vs stub status]

## ML Models (current state)
[what models exist, where saved, last trained, validation metrics]

## Environment Variables Required
[list all .env keys the app needs]

## Known Issues (open)
[running list — add when found, remove when fixed]
```

### File: `docs/PROGRESS.md`
Session-by-session log. Append, never overwrite.

```markdown
# Progress Log

## Session [N] — [DATE]
### What was done
- [specific thing] — REASON: [why this was the right approach]
### Files changed
- [path]: [what changed and why]
### Tests run
- [command]: [result]
### What to do NEXT (first task for next session)
- [specific, unambiguous task]
### BLOCKED ON (if anything)
- [clear question or dependency]

---
```

---

## PHASE 0 — PROJECT AUDIT & SETUP
### Session goal: Understand exactly what exists before changing anything

```
CLAUDE CODE INSTRUCTIONS — PHASE 0

1. Read ALL files in the repo. Do not skip any directory.
   List every file in CONTEXT.md under "## File Inventory".

2. For each API endpoint, determine: does it return REAL computed data
   or HARDCODED/RANDOM data? Mark each route in CONTEXT.md as:
   [REAL] / [STUB-HARDCODED] / [STUB-RANDOM] / [BROKEN]

3. For the ML pipeline, determine:
   - Is there any trained model file (.pkl, .pt, .onnx, .h5)?
   - Is there any training data file (.csv, .jsonl, .parquet)?
   - Is there any training script?
   Mark each as [EXISTS] or [MISSING] in CONTEXT.md under "## ML Audit"

4. For the database:
   - Does a real DB connection exist? (not SQLite in-memory)
   - Are there migration files?
   - Do tables actually persist between restarts?
   Mark as [REAL-PERSISTENT] / [IN-MEMORY] / [MISSING]

5. For authentication:
   - Is there JWT or session auth on ANY route?
   Mark as [IMPLEMENTED] / [MISSING]

6. Document every overclaim found in README/docs:
   Copy the claim → mark [OVERCLAIM: reason] in CONTEXT.md

7. Write PROGRESS.md Session 0 entry with full findings.

8. DO NOT CHANGE ANY CODE IN PHASE 0. Audit only.

Output: CONTEXT.md and PROGRESS.md fully populated.
Next phase will be unlocked after this is complete.
```

---

## PHASE 1 — CRITICAL SAFETY & HONESTY FIXES
### Priority: Remove dangerous claims, add crisis safety, fix auth
### Estimated: 2–3 sessions

---

### P1-TASK-1: Remove All Overclaims from Public Docs

```
CLAUDE CODE INSTRUCTIONS — P1-TASK-1

CONTEXT: Read docs/CONTEXT.md section "## Overclaims" first.

TASK: In README.md and any other public-facing docs, find and fix:

1. Replace every instance of:
   - "fine-tuned Claude" / "finetuned" / "claude-*-finetuned-*"
   → with: "Claude claude-sonnet-4-5 with domain-specialized system prompt engineering"

2. Replace every invented statistic:
   - "r=0.72" / "n=20 pilot" / "25% improvement" / "80% of time"
   → with: "[VALIDATION PENDING — see docs/ML_VALIDATION_PLAN.md]"

3. Replace every unverified claim about psychologist review:
   → "Intervention texts are designed based on published CBT/MBSR/ACT
      literature. Independent clinical review is planned before public launch."

4. In all Python/JS files, find any hardcoded model name like
   "claude-opus-4-5-finetuned-veramind" and replace with the actual
   model being used (check Anthropic docs for current model names).

VERIFY: `grep -r "finetuned\|fine_tuned\|r=0\.\|n=20\|pilot" .`
        → should return 0 results in source code after this task.

UPDATE: PROGRESS.md with what was changed and why.
```

---

### P1-TASK-2: Crisis Detection Safety Layer

```
CLAUDE CODE INSTRUCTIONS — P1-TASK-2

CONTEXT: This is the highest-priority ethical requirement.
         Read backend/app/services/ (or equivalent) before starting.

TASK: Create a crisis detection module.

File to create: backend/app/services/safety.py

Content requirements:
1. A `CrisisDetector` class with method `check(text: str) -> CrisisResult`
2. CrisisResult is a dataclass: {is_crisis: bool, severity: str, matched_keywords: list}
3. Keyword list (Hindi + English, India-specific):
   - HIGH: ["suicide", "kill myself", "end my life", "want to die",
            "khud ko maarna", "jeena nahi", "zindagi khatam", "harm myself"]
   - MEDIUM: ["hopeless", "no point", "nobody cares", "can't go on",
              "give up on life", "utterly alone"]
4. If is_crisis=True, the API MUST NOT pass the text to Claude.
   Instead return a structured crisis response with:
   - iCall India: 9152987821
   - Vandrevala Foundation: 1860-2662-345
   - NIMHANS: 080-46110007
   - Message: "I hear that you're going through something very hard.
               Please reach out to a counselor who can really help."

5. Add a middleware or dependency that runs CrisisDetector on ALL
   user-generated text before any Claude API call.

6. Log crisis events to DB table `safety_events`:
   {id, timestamp, severity, user_id_hash (NOT raw ID — hash it for privacy),
    matched_keywords, action_taken}
   Do NOT log the actual user text.

VERIFY:
- Unit test: `test_crisis_detection.py` with 10 test cases
- Run it: `pytest tests/test_crisis_detection.py -v`
- All 10 must pass before marking done.

UPDATE: PROGRESS.md. Note which test cases you wrote and why.
```

---

### P1-TASK-3: JWT Authentication

```
CLAUDE CODE INSTRUCTIONS — P1-TASK-3

CONTEXT: Read CONTEXT.md "## API Routes" to see all unprotected routes.
         Read the existing user model/schema if it exists.

TASK: Implement JWT auth on all protected routes.

1. Install: `pip install python-jose[cryptography] passlib[bcrypt]`
   Add to requirements.txt.

2. Create backend/app/core/auth.py:
   - `create_access_token(user_id: str) -> str` (24hr expiry)
   - `verify_token(token: str) -> str | None` (returns user_id or None)
   - `get_current_user` FastAPI dependency that reads Bearer token

3. Create /auth/register and /auth/login endpoints:
   - Register: hash password with bcrypt, store in users table, return JWT
   - Login: verify password, return JWT
   - Never store plaintext passwords. Never log passwords.

4. Apply `Depends(get_current_user)` to ALL routes that touch user data:
   - /api/stress/*
   - /api/habits/*
   - /api/insights/*
   - /api/coach/*
   - /api/mood/*

5. In every protected handler, scope ALL DB queries to current_user.id:
   WRONG: `db.query(StressEvent).all()`
   RIGHT: `db.query(StressEvent).filter(StressEvent.user_id == current_user.id).all()`

VERIFY:
- `curl -X GET /api/stress/history` → should return 401
- `curl -X POST /auth/login -d {...}` → should return JWT
- `curl -H "Authorization: Bearer <token>" /api/stress/history` → should return 200
- Document the curl commands in PROGRESS.md with actual outputs.

UPDATE: PROGRESS.md with all changed files.
```

---

### P1-TASK-4: Real Database Setup

```
CLAUDE CODE INSTRUCTIONS — P1-TASK-4

CONTEXT: Read CONTEXT.md "## Database" section first.
         If a DB already exists, EXTEND it — do not recreate.

TASK: Set up persistent PostgreSQL with real schema.

1. If Docker available: create docker-compose.yml with postgres:15 service.
   If not: use SQLite for local dev but document it as "dev only, prod=PostgreSQL"

2. Create SQLAlchemy models in backend/app/models/:

   users.py:
   - id (UUID), email, hashed_password, created_at, is_active

   stress_events.py:
   - id, user_id (FK), timestamp, raw_features (JSONB), computed_score (float),
     model_version (str), source ("keystroke"/"self_report")

   habit_logs.py:
   - id, user_id (FK), habit_name, completed_at, streak_day (int),
     discontinued_at (nullable)

   interventions.py:
   - id, user_id (FK), technique_name, delivered_at, user_stress_at_delivery,
     user_stress_30min_after (nullable — filled by follow-up), user_rated_helpful (bool nullable)

   mood_entries.py:
   - id, user_id (FK), timestamp, mood_score (1-10), mood_label, note_text

   safety_events.py:
   - id, user_id_hash, timestamp, severity, matched_keywords (ARRAY), action_taken

   assessment_results.py:
   - id, user_id (FK), assessment_type ("PSS10"/"GAD7"/"PHQ9"),
     completed_at, score, responses (JSONB), interpretation (str)

3. Create Alembic migration: `alembic init alembic` → `alembic revision --autogenerate`
   Run it: `alembic upgrade head`
   Verify tables exist: `\dt` in psql

4. Add DB connection to .env.example (never commit real credentials):
   DATABASE_URL=postgresql://user:password@localhost:5432/sentio

VERIFY: Start the app → it should connect to DB without errors.
        Insert a test user → restart app → user should still exist.
UPDATE: CONTEXT.md with the actual schema. PROGRESS.md with what changed.
```

---

## PHASE 2 — REAL ML PIPELINE
### Priority: Build the actual keystroke stress model
### Estimated: 3–4 sessions

---

### P2-TASK-1: Keystroke Feature Extraction Pipeline

```
CLAUDE CODE INSTRUCTIONS — P2-TASK-1

CONTEXT: Read CONTEXT.md. Read the frontend keystroke JS component.
         Read the existing /api/stress endpoint.

TASK: Build the end-to-end keystroke data pipeline.

PART A — Frontend (sends real data):

In the TypeState component (wherever keystroke events are captured):
1. Collect these events on each keydown/keyup:
   {key, event_type ("down"/"up"), timestamp_ms (Date.now()), is_backspace (bool)}

2. Buffer events in a local array. Every 30 seconds OR when buffer hits 50 events:
   POST to /api/v1/events/keypress with body:
   {session_id: uuid, events: [...], window_start_ms, window_end_ms}

3. Clear buffer after successful POST.

4. CRITICAL: Remove old event listener on component unmount:
   return () => { document.removeEventListener('keydown', handler); }

PART B — Backend (stores and computes features):

Create backend/app/services/keystroke_features.py:

Function: `extract_features(events: list[dict]) -> dict`
Compute:
- mean_iki_ms: mean inter-key interval (time between consecutive keydowns)
- std_iki_ms: standard deviation of IKI
- backspace_rate: backspaces / total keys (0.0 to 1.0)
- typing_speed_wpm: words per minute (words = total chars / 5)
- iki_cv: coefficient of variation (std/mean) — proxy for rhythm consistency
- pause_count: number of pauses > 2000ms between keys
- session_duration_ms

Store to DB: stress_events table with source="keystroke",
raw_features=computed dict, computed_score=NULL (filled by model in next task)

VERIFY:
1. Open the app, type for 30 seconds
2. Check DB: `SELECT * FROM stress_events ORDER BY timestamp DESC LIMIT 5;`
   → should show real rows with real feature values
3. Verify removeEventListener works: check browser memory profiler — no leak
UPDATE: PROGRESS.md with sample feature values from a real typing session.
```

---

### P2-TASK-2: Stress Model Training Data Collection

```
CLAUDE CODE INSTRUCTIONS — P2-TASK-2

CONTEXT: Read docs/ML_VALIDATION_PLAN.md if it exists.
         Read backend/app/services/keystroke_features.py (from P2-TASK-1).

TASK: Create the data collection infrastructure for model training.

WHY THIS BEFORE THE MODEL: You cannot train without data. This task creates
the scaffolding to collect labeled data from real sessions.

1. Create a Self-Labeling Endpoint — POST /api/v1/assess/self-rate:
   Body: {stress_level: int (1-10), session_id: str}
   This lets you label your own sessions after typing.

2. Create a Data Export Script — scripts/export_training_data.py:
   Joins stress_events (features) with self-ratings.
   Outputs: data/training/keystroke_stress_labeled.csv
   Columns: mean_iki_ms, std_iki_ms, backspace_rate, typing_speed_wpm,
            iki_cv, pause_count, self_rated_stress (1-10)

3. Create the PSS-10 Questionnaire endpoint — POST /api/v1/assess/pss10:
   Accept all 10 PSS item responses (0-4 scale each).
   Score correctly: items 4,5,7,8 are REVERSE scored (score = 4 - response).
   Total = sum of all 10 scores (0-40).
   Interpretation:
     0-13: low stress
     14-26: moderate stress
     27-40: high perceived stress
   Store to assessment_results table.
   CITE in code comment: Cohen, S., Kamarck, T., & Mermelstein, R. (1983).
   A global measure of perceived stress. Journal of Health and Social Behavior, 24, 385–396.

4. Create docs/DATA_COLLECTION_GUIDE.md:
   Instructions for collecting your own labeled sessions:
   "Type for 2-3 minutes on any task. After each session, self-rate stress 1-10.
    Aim for 50+ sessions across different stress levels.
    Mix: coding, writing emails, free writing, during-meeting notes."

VERIFY: Run export script → CSV file created → has correct columns.
NOTE IN PROGRESS.md: "Model training cannot start until N=50 labeled sessions
are collected. Data collection guide is in docs/DATA_COLLECTION_GUIDE.md"
```

---

### P2-TASK-3: Train the Real Stress Model

```
CLAUDE CODE INSTRUCTIONS — P2-TASK-3

PREREQUISITE: data/training/keystroke_stress_labeled.csv must exist
              with at least 40 rows. If it doesn't, STOP and note in PROGRESS.md:
              "BLOCKED: Need N>=40 labeled sessions. Currently have N=[count]."
              Do not proceed with fake data.

TASK: Train a real stress prediction model.

File: scripts/train_stress_model.py

1. Load data: pd.read_csv('data/training/keystroke_stress_labeled.csv')
   Print: shape, describe(), any nulls.

2. Features X: [mean_iki_ms, std_iki_ms, backspace_rate, typing_speed_wpm, iki_cv, pause_count]
   Target y: self_rated_stress (continuous 1-10)

3. Preprocessing:
   - StandardScaler on X (always scale before regression)
   - Check for outliers: drop rows where any feature is > 3 std devs from mean

4. Model selection — try all three, pick best:
   from sklearn.linear_model import Ridge
   from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor

   For each, use 5-fold cross-validation:
   scores = cross_val_score(model, X_scaled, y, cv=5, scoring='r2')
   Print: f"{model_name}: R² = {scores.mean():.3f} ± {scores.std():.3f}"

5. Select the model with highest mean R². Train on 80% of data.
   Evaluate on held-out 20%:
   - R² score (print exact value)
   - Pearson r (scipy.stats.pearsonr)
   - RMSE
   Print ALL metrics. Write them to data/training/model_metrics.json.
   NEVER round up or exaggerate metrics.

6. Save model:
   import joblib
   joblib.dump({'model': best_model, 'scaler': scaler,
                'feature_names': X.columns.tolist(),
                'metrics': metrics_dict,
                'trained_on_n': len(X),
                'trained_at': datetime.now().isoformat()},
               'models/stress_model_v1.pkl')

7. Update backend/app/services/stress_inference.py:
   Load the pkl file. Expose predict(features_dict) -> float.
   Update the /api/stress/score endpoint to call this — real inference, not random.

VERIFY: Hit /api/stress/score with real feature values.
        The response should change based on different inputs.
        Document actual R² in PROGRESS.md and CONTEXT.md.
        Note: "Model trained on N=[actual count] sessions. R²=[actual value].
               This is preliminary — more data needed for robust validation."
```

---

### P2-TASK-4: PSS-10 vs Model Correlation (Honest Validation)

```
CLAUDE CODE INSTRUCTIONS — P2-TASK-4

PREREQUISITE: Users must have completed both PSS-10 AND keystroke sessions.
              If no overlap exists yet, STOP — note in PROGRESS.md.

TASK: Compute honest correlation between model output and PSS-10.

File: scripts/validate_vs_pss10.py

1. Query: users who have both assessment_results (PSS10) AND stress_events
   Join on user_id, match by date proximity (within same day).

2. For each matched pair:
   model_score = mean of that user's stress_events.computed_score for the day
   pss_score = their PSS10 score for that period

3. Compute Pearson r with scipy.stats.pearsonr.
   Print: r, p-value, N (number of matched pairs).

4. Write results to data/validation/pss10_correlation.json:
   {"pearson_r": [actual], "p_value": [actual], "n_pairs": [actual],
    "computed_at": "[date]", "interpretation": "preliminary/insufficient_data/acceptable"}

5. Update README with ACTUAL value:
   "Preliminary validation: r=[actual] (N=[actual], p=[actual]).
    Acceptable threshold for digital biomarkers is r≥0.50.
    [BELOW THRESHOLD / MEETS THRESHOLD] — more data collection ongoing."

RULE: If N < 15, write: "Insufficient data for meaningful correlation.
      Collecting more sessions." Do not publish a correlation based on <15 pairs.
```

---

## PHASE 3 — FRONTEND REALITY BRIDGE
### Priority: Connect UI to real backend data
### Estimated: 2–3 sessions

---

### P3-TASK-1: Replace All Hardcoded Chart Data

```
CLAUDE CODE INSTRUCTIONS — P3-TASK-1

CONTEXT: Read CONTEXT.md "## API Routes" section.
         Read each dashboard component file before changing it.

TASK: Every chart must fetch from real API endpoints.

FOR EACH chart component:
1. Find the hardcoded data array (e.g. `const stressData = [72, 68, 81, ...]`)
2. Create an API endpoint that returns this data from DB for current user
3. Replace the hardcoded array with:
   const [data, setData] = useState(null)
   const [loading, setLoading] = useState(true)
   const [error, setError] = useState(null)
   useEffect(() => {
     fetch('/api/v1/analytics/stress?days=30', {
       headers: { Authorization: `Bearer ${getToken()}` }
     })
     .then(r => r.ok ? r.json() : Promise.reject(r.status))
     .then(d => { setData(d); setLoading(false); })
     .catch(e => { setError(e); setLoading(false); })
   }, [])

4. Add loading state: show skeleton (use the shimmer CSS from design system)
5. Add error state: show "Unable to load data. Try refreshing."
6. Add empty state: show "No data yet. Start a session to see your trends."

Charts to fix (list all found during Phase 0 audit):
- Stress trend line chart
- Habit heatmap
- Mood donut/pie chart
- Session frequency bar chart
- Any others found in Phase 0

VERIFY: Open browser DevTools → Network tab → reload dashboard.
        You should see real API calls. Screenshot this for your portfolio.
UPDATE: PROGRESS.md with each chart fixed and the API endpoint created.
```

---

### P3-TASK-2: PSS-10 Onboarding Flow

```
CLAUDE CODE INSTRUCTIONS — P3-TASK-2

CONTEXT: Read the existing onboarding/assessment UI if it exists.
         Read the PSS-10 endpoint created in P2-TASK-2.

TASK: Build real PSS-10 assessment as onboarding step.

The 10 PSS questions (exact wording from Cohen et al. 1983):
1. "In the last month, how often have you been upset because of something that happened unexpectedly?"
2. "In the last month, how often have you felt that you were unable to control the important things in your life?"
3. "In the last month, how often have you felt nervous and stressed?"
4. "In the last month, how often have you felt confident about your ability to handle your personal problems?" [REVERSE]
5. "In the last month, how often have you felt that things were going your way?" [REVERSE]
6. "In the last month, how often have you been able to control irritations in your life?" [REVERSE - note: some versions mark this differently]
7. "In the last month, how often have you felt that you were on top of things?" [REVERSE]
8. "In the last month, how often have you been angered because of things that were outside of your control?"
9. "In the last month, how often have you felt difficulties were piling up so high that you could not overcome them?"
10. "In the last month, how often have you felt that you were able to control the way you spend your time?" [REVERSE]

Response options: 0=Never, 1=Almost Never, 2=Sometimes, 3=Fairly Often, 4=Very Often

Reverse scoring: items 4, 5, 6, 7, 10 — score = 4 - response

Add a note below the form: "PSS-10 (Cohen et al., 1983) is a validated
screening tool. This is not a diagnosis. Scores above 26 suggest high
perceived stress — we recommend speaking with a mental health professional."

After submission: show interpretation + baseline stored message.
Add a "Reassess in 4 weeks" reminder.

VERIFY: Complete the PSS-10 → check DB assessment_results table for new row.
        Score computation is correct for a known test case.
```

---

## PHASE 4 — LLM INTEGRATION (HONEST)
### Priority: Real Claude integration, properly described
### Estimated: 1–2 sessions

---

### P4-TASK-1: Claude Coaching Integration (Accurate)

```
CLAUDE CODE INSTRUCTIONS — P4-TASK-1

CONTEXT: Read the existing coaching/AI chat component and backend handler.
         Read the CrisisDetector from P1-TASK-2 — it MUST run first.

TASK: Clean up and properly implement the Claude coaching layer.

1. Rename any "fine-tuned" references:
   - File: backend/app/services/coach.py (or equivalent)
   - The model to use: "claude-sonnet-4-5" (verify this is current in Anthropic docs)

2. Build a proper context injection system:
   Function: build_coaching_context(user_id: str, user_message: str) -> dict

   Gather from DB (real queries, not hardcoded):
   - user's last 7 stress scores (from stress_events)
   - user's last completed PSS-10 score (from assessment_results)
   - user's active habits and streak lengths (from habit_logs)
   - last 3 interventions delivered and whether user marked them helpful
   - user's stated values/goals (from user profile)

   Build system prompt:
   """You are a mental health coach trained in CBT, MBSR, and ACT techniques.
   You do NOT diagnose. You do NOT replace therapy. You coach and support.

   User context (last 7 days):
   - Average stress: {avg_stress:.1f}/10
   - PSS-10 score: {pss_score}/40 ({interpretation})
   - Active habits: {habit_summary}
   - What helped recently: {helpful_interventions}

   Evidence base for your responses:
   - CBT (Beck & Clark, 1997): Thought records, cognitive restructuring
   - MBSR (Kabat-Zinn, 1998): Mindfulness, body scan, breathing
   - ACT (Hayes et al., 2016): Values clarification, defusion
   - Tiny Habits (Fogg, 2019): B=MAP framework

   Safety rules (non-negotiable):
   - Never diagnose a mental health condition
   - Never suggest medication
   - Always include "consider speaking with a professional" if stress > 7/10
   - If user expresses suicidal ideation, do not engage — the system will
     intercept this before it reaches you
   """

3. Rate limiting: max 10 coaching messages per user per day.
   Track in DB. Return 429 with message if exceeded.

4. Log every Claude call to DB:
   {user_id, timestamp, tokens_used, model_used, stress_context_at_time}
   Never log the actual message content (privacy).

VERIFY: Send a message through the coach → check DB logs table for the entry.
        Verify rate limiting: send 11 messages → 11th should return 429.
```

---

## PHASE 5 — ML/DL ADVANCED MODELS
### Multi-AI Orchestration Plan

---

### ARCHITECTURE: What Claude Code Manages vs. What Gets Delegated

```
Claude Code (you) manages:
- All project infrastructure, integration, file structure
- Python/JS code that runs in the Sentio repo
- Training pipelines, data schemas, API wrappers
- Final integration of any model output into the app
- CONTEXT.md and PROGRESS.md always

Delegated to other AIs (see task cards below):
- Large-scale training data generation (Gemini)
- Model architecture research (Gemini/Qwen)
- Fine-tuning open models (separate Colab/GPU session)

RULE: Outputs from delegated tasks must be reviewed and tested before
      integration. Never blindly paste AI-generated code without reading it.
      Every delegated output gets its own PROGRESS.md entry.
```

---

### DELEGATION TASK A — FOR GEMINI 1.5 PRO / GEMINI 2.0
#### Task: Generate PSS-10 Calibrated Training Data

```
PROMPT TO SEND TO GEMINI:

You are a clinical psychology data engineer creating synthetic training data
for a stress coaching AI system. Generate a dataset of 200 user state →
ideal coaching response pairs.

Each row must have:
1. user_context (JSON):
   {
     "avg_stress_7d": float (1-10),
     "pss10_score": int (0-40),
     "active_habits": list of strings,
     "recent_interventions": [{"technique": str, "helped": bool}],
     "mood_today": str,
     "days_since_last_meditation": int,
     "work_context": str,
     "sleep_quality_3d": float (1-5)
   }

2. ideal_coach_response (string):
   A 2-4 sentence response from a CBT/MBSR/ACT trained coach.
   Must: (a) acknowledge the specific context, (b) suggest ONE technique,
   (c) explain WHY that technique fits this context,
   (d) never diagnose, never prescribe medication.

3. technique_used: one of ["CBT_thought_record", "MBSR_breathing",
   "ACT_values", "Tiny_Habits", "behavioral_activation", "psychoeducation"]

4. evidence_citation: the actual paper behind the technique used.

Coverage requirements:
- 40 low stress cases (avg_stress < 4), 100 moderate (4-7), 60 high (>7)
- Represent diverse contexts: student, professional, parent, chronic stress
- Include 20 cases where the coach should recommend professional help
- Include 10 cases testing the boundary (not diagnosing, but referring)

Output format: JSONL (one JSON object per line). No markdown fences.
Name the file: interventions_training_v1.jsonl

WHAT CLAUDE CODE DOES WITH THIS OUTPUT:
1. Save to data/training/interventions_training_v1.jsonl
2. Validate schema: every row has all required fields
3. Spot-check 20 random rows for clinical appropriateness
4. Document: "Generated by Gemini 1.5 Pro on [date] — synthetic, not from
   real users — used for prompt optimization, not model fine-tuning claims"
5. Use this data to evaluate Claude's coaching responses via automated scoring
```

---

### DELEGATION TASK B — FOR QWEN2.5 / DEEPSEEK-R1
#### Task: Keystroke Dynamics Model Architecture Research

```
PROMPT TO SEND TO QWEN or DEEPSEEK:

I am building a stress detection system using keystroke dynamics.
My features are: mean_iki_ms, std_iki_ms, backspace_rate, typing_speed_wpm,
iki_cv, pause_count (computed over 30-second windows).
My target: stress score (1-10, self-rated, continuous regression).
Expected training data: 50-200 labeled sessions.

Task: Write me a complete, runnable PyTorch model for this task.

Requirements:
1. Since my dataset is small (50-200 samples), the model MUST avoid overfitting.
   Use appropriate regularization.
2. Include a Bayesian or uncertainty-aware layer so I can output not just a
   point estimate but a confidence interval (useful for health app UX).
3. The model must be saveable with torch.save and loadable for inference.
4. Include a training loop with early stopping.
5. Include a simple evaluation function that returns: R², RMSE, 95% CI width.
6. The code must run on CPU (no CUDA dependency — my server is CPU-only).

Also provide:
- Explanation of why you chose this architecture for small tabular data
- What feature engineering could improve performance
- When I should consider switching to a larger/different model

Output: Complete Python file, ready to save as train_keystroke_model.py

WHAT CLAUDE CODE DOES WITH THIS OUTPUT:
1. Read the code fully. Verify it runs: `python train_keystroke_model.py --dry-run`
2. Note the architecture choice in CONTEXT.md under "## ML Models"
3. Replace the scikit-learn model from P2-TASK-3 IF this outperforms it on R²
4. Document in PROGRESS.md: "Qwen-suggested architecture tested on [date].
   R² = [actual]. Decision: [kept/replaced sklearn model]. Reason: [why]."
```

---

### DELEGATION TASK C — FOR GEMINI / ANY LARGE-CONTEXT MODEL
#### Task: Validate Intervention Text for Clinical Appropriateness

```
PROMPT TO SEND TO GEMINI (with 1M context window):

You are a clinical psychologist reviewing AI-generated coaching text.
I will give you a list of intervention responses generated for a mental health
coaching app. For each one, evaluate:

1. Is this clinically appropriate? (Yes/No/Partially)
2. Does it diagnose a mental health condition? (this is FORBIDDEN — flag if yes)
3. Does it recommend medication or clinical procedures? (FORBIDDEN — flag if yes)
4. Is the technique attribution correct? (Does it actually reflect CBT/MBSR/ACT?)
5. Safety rating: Safe / Caution / Unsafe
6. Suggested edit if needed (brief)

[PASTE the 200 rows from interventions_training_v1.jsonl here]

Output: JSON array, one review object per input row.
Include counts: n_safe, n_caution, n_unsafe, n_needs_edit

WHAT CLAUDE CODE DOES WITH THIS OUTPUT:
1. Save review to data/validation/intervention_clinical_review.json
2. Remove any rows rated "Unsafe"
3. Apply suggested edits to "Caution" rows
4. Update README: "Intervention library reviewed by Gemini clinical appropriateness
   checker on [date]. N=200, Safe=[n], Caution+fixed=[n], Removed=[n].
   This is AI review, not human clinical review — plan for human review before
   public launch."
5. Note: This is NOT the same as a real psychologist review. Document accordingly.
```

---

### FINE-TUNING PLAN (Future — When Data Is Ready)

```
WHEN TO FINE-TUNE: Only after you have at least 150 high-quality, clinically
reviewed (user_context, ideal_response) pairs. Before that, prompt engineering
is more effective.

OPTION A: Fine-tune a small open model (recommended for portfolio)
- Model: Qwen2.5-1.5B-Instruct or Llama-3.2-3B-Instruct (free, runnable on Colab)
- Method: LoRA (PEFT) — efficient, no full model needed
- Tool: HuggingFace PEFT library + Google Colab (free T4 GPU)
- Training data: the 150+ validated (context, response) pairs from Task A
- What to claim: "LoRA fine-tuned Qwen2.5-1.5B on 150 domain-specific
  coaching examples. Base model: Qwen/Qwen2.5-1.5B-Instruct.
  Fine-tuning improved specificity score by [actual measured delta]."

FINE-TUNING TASK CARD (for Claude Code to execute when ready):

File: scripts/finetune_coach_model.py

1. pip install peft transformers trl datasets torch
2. Load base model: AutoModelForCausalLM.from_pretrained("Qwen/Qwen2.5-1.5B-Instruct")
3. LoRA config: r=16, alpha=32, target_modules=["q_proj","v_proj"]
4. Format data as instruction tuning: {"instruction": system_prompt + user_context,
   "response": ideal_coach_response}
5. Train with TRL SFTTrainer, max_steps=500, eval every 50 steps
6. Save adapter: model.save_pretrained("models/coach_lora_v1/")
7. Evaluate: BLEU-4, BERTScore, and manual 20-response review
8. Document in CONTEXT.md: actual training metrics, base model, LoRA config,
   training data size

WHAT TO NEVER CLAIM:
- Do not call this "a fine-tuned Claude model"
- Do not claim HIPAA compliance for a Colab-trained model
- Do not use real user data for training without consent

OPTION B: If Claude fine-tuning becomes available
- Wait for Anthropic to release fine-tuning API (not available as of May 2026)
- Check: https://docs.anthropic.com — if fine-tuning appears, follow their guide
- Until then: do not claim "fine-tuned Claude" anywhere
```

---

## PHASE 6 — PORTFOLIO POLISH
### After all core fixes are complete

---

### P6-TASK-1: README Honest Rewrite

```
CLAUDE CODE INSTRUCTIONS — P6-TASK-1

TASK: Rewrite README.md with an honest, impressive structure.

Section: "What's Actually Built"
- List features with [IMPLEMENTED] / [PROTOTYPED] / [PLANNED] tags
- No invented metrics

Section: "ML Architecture"
- Describe the real keystroke pipeline
- State actual model: "Ridge/RF regression, scikit-learn, trained on N=[actual] sessions"
- State actual R²: "[actual value]"

Section: "LLM Integration"
- State accurately: "Claude claude-sonnet-4-5 with domain-specific system prompt engineering"
- Describe the context injection system
- Describe the crisis safety layer

Section: "Evidence Base"
- List each technique with its actual citation
- Include PSS-10 citation if implemented

Section: "What's Next"
- LoRA fine-tuning plan (honest future work)
- Human clinical review before public launch
- Larger data collection for model improvement

HOW TO SOUND IMPRESSIVE WITHOUT LYING:
"I built a real keystroke dynamics pipeline that extracts 7 physiological
features from typing behavior and feeds them into a validated regression model."
This is true, specific, and impressive — even if R² is only 0.45.
```

---

### P6-TASK-2: Demo Recording Script

```
CLAUDE CODE INSTRUCTIONS — P6-TASK-2

Create: docs/DEMO_SCRIPT.md

The demo must show these things (because they prove real implementation):
1. Open browser DevTools → Network tab VISIBLE
2. Log in → show the JWT in the Authorization header of subsequent requests
3. Type for 30 seconds → pause → show the POST to /api/v1/events/keypress in Network tab
4. Show the stress score update — and note it changed based on typing
5. Open DB viewer → show the stress_events row that was just created
6. Complete a PSS-10 → show the score calculated correctly
7. Send a message to the coach → show the context injection working
   (add a debug mode that shows what context was sent, toggle off in prod)
8. Trigger a crisis keyword in the coach (use a test phrase) → show the
   safety response and helpline display
9. Show DB → safety_events table → the event was logged

WHY: This demo sequence is impossible to fake. Each step requires real infrastructure.
     If you can demo this, you have a real project.
```

---

## SESSION MANAGEMENT PROTOCOL

### Starting every Claude Code session:

```
1. Read docs/CONTEXT.md fully (5 min)
2. Read the last 3 entries in docs/PROGRESS.md (3 min)
3. Note the "What to do NEXT" from last session
4. Read the files you'll be modifying BEFORE modifying them
5. Then start work
```

### Ending every Claude Code session:

```
1. Run all existing tests: `pytest tests/ -v`
2. Note any failures in PROGRESS.md
3. Update CONTEXT.md if any tech stack / schema changed
4. Write PROGRESS.md entry: what was done, why, what's next
5. Commit: `git add docs/ && git commit -m "docs: update context and progress [phase]-[task]"`
6. Never leave a session with broken tests uncommitted
```

### When stuck:

```
Write in PROGRESS.md:
## BLOCKED ON — [date]
Question: [specific question]
Context: [what you've read, what you've tried]
Options considered: [option A, option B]
Recommendation: [which option seems better and why]

Then stop. Do not guess. Do not hallucinate a solution.
```

---

## QUICK REFERENCE: AI TASK ALLOCATION

| Task | Best AI | Why |
|------|---------|-----|
| Project code, integration | **Claude Code** | Context window, code execution, file management |
| Large synthetic dataset gen | **Gemini 1.5/2.0 Pro** | 1M context, instruction following, JSON output |
| ML architecture research | **Qwen2.5 / DeepSeek-R1** | Strong on math/code, runs locally, free |
| Clinical text review | **Gemini 1.5 Pro** | Long-context batch processing |
| LoRA fine-tuning | **Qwen2.5-1.5B + Colab** | Free GPU, real fine-tuning capability |
| UI component generation | **Claude claude-sonnet-4-5** | Best HTML/CSS/React output |
| Research paper summaries | **Gemini 2.0 Flash** | Fast, good at summarization |
| Security review | **Claude claude-sonnet-4-5** | Best at spotting vulnerabilities |

---

## FINAL REMINDER

The goal is not a perfect project. The goal is an honest project where every
claim is backed by code, every metric is computed from real data, and every
"future work" is labeled as such. That project gets you hired. The fake one
gets you exposed in the first technical screen.

Build small. Build real. Document everything.
```

---

*This master prompt was generated on 2026-05-15 based on a critical technical audit of the Sentio/Veramind repository. Update the task statuses in PROGRESS.md as you complete each phase.*
