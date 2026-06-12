"""
Sentio API load test — Locust

Usage:
    cd sentio-api
    export SENTIO_TOKEN="<supabase-jwt-for-test-user>"
    locust -f scripts/locustfile.py --host https://<your-hf-space>.hf.space \
           --users 25 --spawn-rate 5 --run-time 60s --headless \
           --html scripts/locust_report_25.html
    # Repeat with --users 50 for the 50-user run.

Required env vars:
    SENTIO_TOKEN   Supabase JWT for the test user (create a dedicated load-test account)

Metrics captured:
    P50 and P95 response time for:
      - POST /journal          (entry creation, returns 201 immediately)
      - GET  /journal          (list entries, paginated)
      - POST /ai/chat          (SSE stream, consumed to completion)
      - GET  /journal/themes   (aggregate query)

The SSE chat task is lower-weight (1 vs 3) because each stream holds a connection
for ~3–10 s.  Adjust weights if the HF Space concurrency limit is < 10.
"""
import os
import uuid
from locust import HttpUser, task, between, events

_TOKEN = os.environ.get("SENTIO_TOKEN", "")
_HEADERS = {"Authorization": f"Bearer {_TOKEN}", "Content-Type": "application/json"}

# Sample journal texts for POST /journal — varied enough to exercise the classifier
_JOURNAL_TEXTS = [
    "I knew the project would fail from the start. Everyone disagreed but I was right.",
    "My team keeps making the same mistakes. I never do things that poorly.",
    "I only remember the times things went wrong this week. Everything feels hopeless.",
    "The first estimate I heard for the deadline stuck with me even though it was wrong.",
    "Everyone at the meetup seemed to agree with the new framework, so I adopted it too.",
    "I spent three months on this feature. Even though requirements changed, we should ship it.",
    "My colleague seemed confident so I assumed his numbers were correct without checking.",
    "I feel overwhelmed but I think I handled today's presentation pretty well overall.",
    "Reflecting on the week: I learned that slowing down often speeds up the outcome.",
    "I caught myself assuming the worst before the meeting even started. Trying to reframe.",
]

_CHAT_MESSAGES = [
    "What is confirmation bias and how can I overcome it?",
    "I've been feeling anxious about decisions lately. Any advice?",
    "How does journaling help with self-awareness?",
    "Can you explain cognitive distortions in simple terms?",
    "What strategies help with anchoring bias in negotiations?",
]


class SentioUser(HttpUser):
    """Simulates a typical Sentio user: journal + chat mix."""

    wait_time = between(1, 3)

    def on_start(self) -> None:
        self._entry_ids: list[str] = []
        self._session_id = str(uuid.uuid4())

    @task(3)
    def create_journal_entry(self) -> None:
        text = _JOURNAL_TEXTS[hash(str(uuid.uuid4())) % len(_JOURNAL_TEXTS)]
        with self.client.post(
            "/journal/",
            json={"content": text},
            headers=_HEADERS,
            catch_response=True,
            name="POST /journal",
        ) as resp:
            if resp.status_code == 201:
                data = resp.json()
                if data.get("id"):
                    self._entry_ids.append(data["id"])
                resp.success()
            elif resp.status_code == 200 and resp.json().get("crisis_resources"):
                resp.success()  # safety gate fired — not an error
            else:
                resp.failure(f"Unexpected status {resp.status_code}")

    @task(3)
    def list_journal_entries(self) -> None:
        with self.client.get(
            "/journal/?limit=20&offset=0",
            headers=_HEADERS,
            catch_response=True,
            name="GET /journal",
        ) as resp:
            if resp.status_code == 200:
                resp.success()
            else:
                resp.failure(f"Unexpected status {resp.status_code}")

    @task(2)
    def get_journal_themes(self) -> None:
        with self.client.get(
            "/journal/themes",
            headers=_HEADERS,
            catch_response=True,
            name="GET /journal/themes",
        ) as resp:
            if resp.status_code == 200:
                resp.success()
            else:
                resp.failure(f"Unexpected status {resp.status_code}")

    @task(1)
    def chat_stream(self) -> None:
        """POST /ai/chat — SSE stream.  Consume all chunks, then close."""
        msg = _CHAT_MESSAGES[hash(str(uuid.uuid4())) % len(_CHAT_MESSAGES)]
        # Use a stable session UUID for the whole user session (Option B)
        with self.client.post(
            "/ai/chat",
            json={"message": msg, "conversation_id": self._session_id},
            headers=_HEADERS,
            stream=True,
            catch_response=True,
            name="POST /ai/chat (SSE)",
            timeout=30,
        ) as resp:
            if resp.status_code not in (200, 201):
                resp.failure(f"Unexpected status {resp.status_code}")
                return
            consumed = 0
            for chunk in resp.iter_content(chunk_size=512):
                consumed += len(chunk)
                if consumed > 32_768:  # 32 KB cap per stream
                    break
            resp.success()


@events.quitting.add_listener
def on_quit(environment, **_kwargs) -> None:
    """Print P50/P95 summary to stdout when the test ends."""
    stats = environment.stats
    print("\n=== Sentio Load Test Results ===")
    for name, entry in stats.entries.items():
        p50 = entry.get_response_time_percentile(0.50)
        p95 = entry.get_response_time_percentile(0.95)
        print(f"  {name[1]:40s}  P50={p50:6.0f}ms  P95={p95:6.0f}ms  RPS={entry.current_rps:.1f}  err={entry.num_failures}")
    print("================================\n")
