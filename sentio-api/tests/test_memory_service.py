"""Unit tests for memory_service.py.

Covers:
- _importance() heuristic scoring
- retrieve_memory() graceful degradation when embedder/RPC unavailable
- save_episode() skips when messages is empty
- consolidate_user_episodes() skips when < 2 unconsolidated episodes
- get_user_memory() returns correct shape on empty state
- delete_memory_item() rejects unknown source type
- The decay formula itself (pure math, no I/O)

All Supabase and Anthropic calls are patched; no network required.
"""

import asyncio
import math
import pytest
from unittest.mock import AsyncMock, MagicMock, patch


# ──────────────────────────────────────────────────────────────────────────────
# Helpers
# ──────────────────────────────────────────────────────────────────────────────

def run(coro):
    return asyncio.run(coro)


# ──────────────────────────────────────────────────────────────────────────────
# _importance()
# ──────────────────────────────────────────────────────────────────────────────

def test_importance_minimum():
    from services.memory_service import _importance
    assert _importance([]) == 0.5


def test_importance_scales_with_turns():
    from services.memory_service import _importance
    msgs = [{"role": "user", "content": "hi"}, {"role": "assistant", "content": "hello"}] * 5
    score = _importance(msgs)
    assert score > 0.5
    assert score <= 2.0


def test_importance_boosted_by_bias_mention():
    from services.memory_service import _importance
    msgs_no_bias = [
        {"role": "user", "content": "tell me about the weather"},
        {"role": "assistant", "content": "it is sunny today"},
    ]
    msgs_bias = [
        {"role": "user", "content": "tell me about bias"},
        {"role": "assistant", "content": "confirmation bias is a cognitive pattern"},
    ]
    assert _importance(msgs_bias) > _importance(msgs_no_bias)


def test_importance_capped_at_two():
    from services.memory_service import _importance
    # Very long session with many bias mentions
    msgs = [
        {"role": "user", "content": "bias"},
        {"role": "assistant", "content": "cognitive bias pattern tendency confirmation catastrophiz"},
    ] * 20
    assert _importance(msgs) == 2.0


# ──────────────────────────────────────────────────────────────────────────────
# Decay formula (pure math — no I/O)
# ──────────────────────────────────────────────────────────────────────────────

def test_decay_formula_episode_halflife():
    """Episode half-life ≈ 14 days at λ=0.05."""
    lambda_ep = 0.05
    age_days = math.log(2) / lambda_ep
    decay = math.exp(-lambda_ep * age_days)
    assert abs(decay - 0.5) < 0.001


def test_decay_formula_fact_halflife():
    """Fact half-life ≈ 140 days at λ=0.005."""
    lambda_fact = 0.005
    age_days = math.log(2) / lambda_fact
    decay = math.exp(-lambda_fact * age_days)
    assert abs(decay - 0.5) < 0.001


def test_decay_score_composite():
    """score = cosine × exp(-λ×age) × importance follows expected ordering."""
    lambda_ep = 0.05

    def score(cosine, age, importance):
        return cosine * math.exp(-lambda_ep * age) * importance

    # Recent, high similarity beats old, high similarity
    assert score(0.9, 1, 1.0) > score(0.9, 30, 1.0)
    # Higher importance breaks tie at same cosine + age
    assert score(0.8, 5, 1.5) > score(0.8, 5, 1.0)
    # Low cosine never beats high cosine even if newer
    assert score(0.3, 0, 2.0) < score(0.8, 2, 1.0)


# ──────────────────────────────────────────────────────────────────────────────
# save_episode() — graceful degradation
# ──────────────────────────────────────────────────────────────────────────────

def test_save_episode_noop_on_empty_messages():
    """save_episode returns immediately when messages=[]."""
    with patch("services.memory_service._summarise_conversation", new_callable=AsyncMock) as mock_sum:
        from services.memory_service import save_episode
        run(save_episode("user-1", "conv-1", []))
        mock_sum.assert_not_called()


def test_save_episode_noop_when_summary_fails():
    """save_episode exits cleanly when _summarise_conversation returns None."""
    msgs = [{"role": "user", "content": "hi"}, {"role": "assistant", "content": "hello"}]
    with patch("services.memory_service._summarise_conversation", new_callable=AsyncMock, return_value=None):
        with patch("services.memory_service._get_embedder", return_value=None):
            from services.memory_service import save_episode
            run(save_episode("user-1", "conv-1", msgs))  # should not raise


def test_save_episode_noop_when_no_embedder():
    """save_episode exits cleanly when embedder is unavailable."""
    msgs = [{"role": "user", "content": "hi"}, {"role": "assistant", "content": "hello"}]
    with patch("services.memory_service._summarise_conversation", new_callable=AsyncMock, return_value="A summary."):
        with patch("services.memory_service._get_embedder", return_value=None):
            from services.memory_service import save_episode
            run(save_episode("user-1", "conv-1", msgs))  # should not raise


# ──────────────────────────────────────────────────────────────────────────────
# retrieve_memory() — graceful degradation
# ──────────────────────────────────────────────────────────────────────────────

def test_retrieve_memory_returns_empty_when_no_embedder():
    with patch("services.memory_service._get_embedder", return_value=None):
        from services.memory_service import retrieve_memory
        result = run(retrieve_memory("user-1", "some query"))
    assert result == ""


def test_retrieve_memory_returns_empty_on_rpc_failure():
    mock_embedder = MagicMock()
    mock_embedder.encode.return_value = MagicMock(tolist=lambda: [0.0] * 384)

    mock_supabase = MagicMock()
    mock_supabase.rpc.return_value.execute.side_effect = Exception("DB down")

    with patch("services.memory_service._get_embedder", return_value=mock_embedder):
        with patch("services.memory_service.get_supabase", return_value=mock_supabase):
            from services.memory_service import retrieve_memory
            result = run(retrieve_memory("user-1", "query"))
    assert result == ""


def test_retrieve_memory_formats_output():
    """When RPC returns data, output should contain memory labels."""
    mock_embedder = MagicMock()
    # encode().tolist() path used inside run_in_executor lambda
    mock_embedder.encode.return_value.tolist.return_value = [0.1] * 384

    mock_rpc_result = MagicMock()
    mock_rpc_result.data = [
        {"id": "ep-1", "source": "episode", "content": "User discussed anxiety.", "age_days": 2.0, "score": 0.8},
        {"id": "fa-1", "source": "fact", "content": "Tends to catastrophize.", "age_days": 45.0, "score": 0.6},
    ]
    mock_supabase = MagicMock()
    # First rpc call → match_memory result; subsequent rpc calls → increment_fact_access
    mock_supabase.rpc.return_value.execute.return_value = mock_rpc_result

    with patch("services.memory_service._get_embedder", return_value=mock_embedder):
        with patch("services.memory_service.get_supabase", return_value=mock_supabase):
            from services.memory_service import retrieve_memory
            # Use asyncio.run() to avoid event-loop mock interference
            result = asyncio.run(retrieve_memory("user-1", "anxiety"))

    assert "REMEMBERED" in result or "KNOWN PATTERN" in result


# ──────────────────────────────────────────────────────────────────────────────
# consolidate_user_episodes() — early exit when < 2 episodes
# ──────────────────────────────────────────────────────────────────────────────

def test_consolidate_skips_with_fewer_than_two_episodes():
    mock_supabase = MagicMock()
    mock_supabase.table.return_value.select.return_value.eq.return_value.eq.return_value\
        .lt.return_value.execute.return_value.data = [
        {"id": "ep-1", "summary": "Only one episode."}
    ]
    with patch("services.memory_service.get_supabase", return_value=mock_supabase):
        from services.memory_service import consolidate_user_episodes
        result = run(consolidate_user_episodes("user-1"))
    assert result == 0


# ──────────────────────────────────────────────────────────────────────────────
# get_user_memory() — shape
# ──────────────────────────────────────────────────────────────────────────────

def test_get_user_memory_shape_on_empty_db():
    mock_supabase = MagicMock()
    # Both queries return empty
    mock_supabase.table.return_value.select.return_value\
        .eq.return_value.eq.return_value\
        .order.return_value.limit.return_value.execute.return_value.data = []

    with patch("services.memory_service.get_supabase", return_value=mock_supabase):
        from services.memory_service import get_user_memory
        result = run(get_user_memory("user-1"))

    assert "episodes" in result
    assert "facts" in result
    assert isinstance(result["episodes"], list)
    assert isinstance(result["facts"], list)


# ──────────────────────────────────────────────────────────────────────────────
# delete_memory_item() — rejects unknown source
# ──────────────────────────────────────────────────────────────────────────────

def test_delete_memory_item_rejects_unknown_source():
    mock_supabase = MagicMock()
    with patch("services.memory_service.get_supabase", return_value=mock_supabase):
        from services.memory_service import delete_memory_item
        result = run(delete_memory_item("user-1", "some-id", "unknown"))
    assert result is False
