import logging
from services.supabase_client import get_supabase

logger = logging.getLogger(__name__)

# Which bias categories are cognitively "adjacent" to each other
CATEGORY_ADJACENCY: dict[str, list[str]] = {
    "memory":   ["belief", "decision"],
    "social":   ["self", "belief"],
    "decision": ["memory", "reasoning"],
    "self":     ["social", "belief"],
    "belief":   ["reasoning", "social"],
    "reasoning": ["decision", "belief"],
}


async def recommend_bias_to_explore(user_id: str) -> dict | None:
    """Return the next bias the user should read about.

    Strategy:
    1. If no profile exists yet, return the first bias in the database.
    2. Otherwise, find the user's top-scoring bias and suggest an adjacent one.
    """
    supabase = get_supabase()

    try:
        profile = (
            supabase.table("user_bias_profiles")
            .select("bias_scores")
            .eq("user_id", user_id)
            .execute()
        )

        if not profile.data or not profile.data[0].get("bias_scores"):
            # New user — suggest the foundational bias
            first = (
                supabase.table("biases")
                .select("id,slug,name,category")
                .order("name")
                .limit(1)
                .execute()
            )
            if first.data:
                b = first.data[0]
                return {
                    "bias_id": b["id"],
                    "slug": b["slug"],
                    "name": b["name"],
                    "reason": "Start here — a foundational bias worth knowing.",
                }
            return None

        bias_scores: dict = profile.data[0]["bias_scores"]
        top_bias_id = max(bias_scores, key=lambda k: bias_scores[k])

        # Bias score keys are signal names (confirmation_bias) — convert to slug (confirmation-bias)
        slug_guess = top_bias_id.replace('_', '-')
        top_bias_resp = (
            supabase.table("biases")
            .select("id,slug,name,category")
            .eq("slug", slug_guess)
            .execute()
        )
        if not top_bias_resp.data:
            return None

        top = top_bias_resp.data[0]
        adjacent_categories = CATEGORY_ADJACENCY.get(top["category"], ["belief"])

        adjacent_resp = (
            supabase.table("biases")
            .select("id,slug,name,category")
            .eq("category", adjacent_categories[0])
            .neq("id", top_bias_id)
            .limit(1)
            .execute()
        )
        if adjacent_resp.data:
            a = adjacent_resp.data[0]
            return {
                "bias_id": a["id"],
                "slug": a["slug"],
                "name": a["name"],
                "reason": f"Adjacent to your top detected bias: {top['name']}",
            }

    except Exception as e:
        logger.error(f"recommend_bias_to_explore error: {e}")

    return None


async def recommend_assessment(user_id: str) -> dict | None:
    """Return the next assessment the user hasn't completed yet."""
    supabase = get_supabase()

    try:
        completed = (
            supabase.table("assessment_results")
            .select("assessment_id")
            .eq("user_id", user_id)
            .execute()
        )
        completed_ids = [r["assessment_id"] for r in (completed.data or [])]

        query = supabase.table("assessments").select(
            "id,slug,title,estimated_minutes"
        )
        if completed_ids:
            # Supabase PostgREST: not.in.(val1,val2,...)
            query = query.not_.in_("id", completed_ids)

        result = query.limit(1).execute()
        if result.data:
            a = result.data[0]
            return {
                "assessment_id": a["id"],
                "slug": a["slug"],
                "title": a["title"],
                "estimated_minutes": a.get("estimated_minutes", 10),
            }

    except Exception as e:
        logger.error(f"recommend_assessment error: {e}")

    return None
