from fastapi import APIRouter, Header, HTTPException, Query, status
from pydantic import BaseModel
from services.supabase_client import get_supabase
from services.safety import safety
from services.badge_engine import check_and_award_badges
from routers._auth_helpers import get_user_id
import logging

logger = logging.getLogger(__name__)
router = APIRouter()

PAGE_SIZE = 20


# ---------------------------------------------------------------------------
# Request models
# ---------------------------------------------------------------------------

class ThreadCreate(BaseModel):
    title: str
    body: str


class ReplyCreate(BaseModel):
    body: str
    parent_reply_id: str | None = None


# ---------------------------------------------------------------------------
# Topics
# ---------------------------------------------------------------------------

@router.get("/topics")
async def list_topics():
    supabase = get_supabase()
    result = supabase.table("community_topics").select("*").order("title").execute()
    return result.data or []


@router.get("/topics/{slug}")
async def get_topic(slug: str, page: int = Query(1, ge=1)):
    supabase = get_supabase()
    topic = supabase.table("community_topics").select("*").eq("slug", slug).single().execute()
    if not topic.data:
        raise HTTPException(status_code=404, detail="Topic not found")

    offset = (page - 1) * PAGE_SIZE
    # Fetch threads without embedded profile join to avoid PostgREST schema-cache issues
    # after fresh FK migration. Author display names are resolved separately.
    threads = (
        supabase.table("community_threads")
        .select("id,title,author_id,upvotes,reply_count,is_pinned,is_locked,created_at")
        .eq("topic_id", topic.data["id"])
        .order("is_pinned", desc=True)
        .order("created_at", desc=True)
        .range(offset, offset + PAGE_SIZE - 1)
        .execute()
    )
    thread_rows = threads.data or []

    # Batch-resolve display names for authors present in this page
    if thread_rows:
        author_ids = list({t["author_id"] for t in thread_rows if t.get("author_id")})
        try:
            profile_res = supabase.table("profiles").select("id,display_name,full_name").in_("id", author_ids).execute()
            profile_map = {p["id"]: p for p in (profile_res.data or [])}
        except Exception:
            profile_map = {}
        for t in thread_rows:
            t["profiles"] = profile_map.get(t.get("author_id"), {})

    return {"topic": topic.data, "threads": thread_rows, "page": page}


# ---------------------------------------------------------------------------
# Threads
# ---------------------------------------------------------------------------

@router.post("/topics/{slug}/threads", status_code=status.HTTP_201_CREATED)
async def create_thread(slug: str, data: ThreadCreate, authorization: str | None = Header(None)):
    user_id = get_user_id(authorization)

    sr = safety.check_input(data.title + " " + data.body)
    if sr.action == "REDIRECT":
        raise HTTPException(status_code=422, detail=sr.message)

    supabase = get_supabase()
    topic = supabase.table("community_topics").select("id").eq("slug", slug).single().execute()
    if not topic.data:
        raise HTTPException(status_code=404, detail="Topic not found")

    result = supabase.table("community_threads").insert({
        "topic_id": topic.data["id"],
        "author_id": user_id,
        "title": data.title,
        "body": data.body,
    }).execute()

    if not result.data:
        raise HTTPException(status_code=500, detail="Failed to create thread")

    # Increment topic thread count
    try:
        supabase.rpc("increment_topic_thread_count", {"p_topic_id": topic.data["id"]}).execute()
    except Exception:
        pass

    try:
        await check_and_award_badges(user_id, supabase)
    except Exception as e:
        logger.warning(f"Badge check after thread create failed: {e}")

    return result.data[0]


@router.get("/threads/{thread_id}")
async def get_thread(thread_id: str):
    supabase = get_supabase()
    thread = (
        supabase.table("community_threads")
        .select("*")
        .eq("id", thread_id)
        .single()
        .execute()
    )
    if not thread.data:
        raise HTTPException(status_code=404, detail="Thread not found")

    replies = (
        supabase.table("community_replies")
        .select("*")
        .eq("thread_id", thread_id)
        .order("created_at")
        .execute()
    )
    reply_rows = replies.data or []

    # Batch-resolve display names without relying on PostgREST embedded joins
    all_author_ids = list(({thread.data.get("author_id")} | {r.get("author_id") for r in reply_rows}) - {None})
    profile_map: dict = {}
    if all_author_ids:
        try:
            pres = supabase.table("profiles").select("id,display_name,full_name").in_("id", all_author_ids).execute()
            profile_map = {p["id"]: p for p in (pres.data or [])}
        except Exception:
            pass

    thread_data = dict(thread.data)
    thread_data["profiles"] = profile_map.get(thread_data.get("author_id"), {})
    for r in reply_rows:
        r["profiles"] = profile_map.get(r.get("author_id"), {})

    return {"thread": thread_data, "replies": reply_rows}


@router.delete("/threads/{thread_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_thread(thread_id: str, authorization: str | None = Header(None)):
    user_id = get_user_id(authorization)
    supabase = get_supabase()
    thread = supabase.table("community_threads").select("author_id").eq("id", thread_id).single().execute()
    if not thread.data:
        raise HTTPException(status_code=404, detail="Thread not found")
    if thread.data["author_id"] != user_id:
        raise HTTPException(status_code=403, detail="Not your thread")
    supabase.table("community_threads").delete().eq("id", thread_id).execute()


# ---------------------------------------------------------------------------
# Replies
# ---------------------------------------------------------------------------

@router.post("/threads/{thread_id}/replies", status_code=status.HTTP_201_CREATED)
async def add_reply(thread_id: str, data: ReplyCreate, authorization: str | None = Header(None)):
    user_id = get_user_id(authorization)

    sr = safety.check_input(data.body)
    if sr.action == "REDIRECT":
        raise HTTPException(status_code=422, detail=sr.message)

    supabase = get_supabase()
    thread = supabase.table("community_threads").select("id,is_locked").eq("id", thread_id).single().execute()
    if not thread.data:
        raise HTTPException(status_code=404, detail="Thread not found")
    if thread.data.get("is_locked"):
        raise HTTPException(status_code=403, detail="Thread is locked")

    result = supabase.table("community_replies").insert({
        "thread_id": thread_id,
        "author_id": user_id,
        "body": data.body,
        "parent_reply_id": data.parent_reply_id,
    }).execute()

    if not result.data:
        raise HTTPException(status_code=500, detail="Failed to add reply")

    # Increment reply count on thread
    try:
        supabase.rpc("increment_thread_reply_count", {"p_thread_id": thread_id}).execute()
    except Exception:
        pass

    try:
        await check_and_award_badges(user_id, supabase)
    except Exception as e:
        logger.warning(f"Badge check after reply create failed: {e}")

    return result.data[0]


@router.delete("/replies/{reply_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_reply(reply_id: str, authorization: str | None = Header(None)):
    user_id = get_user_id(authorization)
    supabase = get_supabase()
    reply = supabase.table("community_replies").select("author_id").eq("id", reply_id).single().execute()
    if not reply.data:
        raise HTTPException(status_code=404, detail="Reply not found")
    if reply.data["author_id"] != user_id:
        raise HTTPException(status_code=403, detail="Not your reply")
    supabase.table("community_replies").delete().eq("id", reply_id).execute()


# ---------------------------------------------------------------------------
# Upvotes
# ---------------------------------------------------------------------------

@router.post("/threads/{thread_id}/upvote")
async def upvote_thread(thread_id: str, authorization: str | None = Header(None)):
    user_id = get_user_id(authorization)
    supabase = get_supabase()
    existing = (
        supabase.table("community_upvotes")
        .select("user_id")
        .eq("user_id", user_id)
        .eq("target_type", "thread")
        .eq("target_id", thread_id)
        .execute()
    )
    if existing.data:
        supabase.table("community_upvotes").delete().eq("user_id", user_id).eq("target_type", "thread").eq("target_id", thread_id).execute()
        supabase.rpc("decrement_thread_upvote", {"p_thread_id": thread_id}).execute()
        return {"action": "removed"}
    supabase.table("community_upvotes").insert({"user_id": user_id, "target_type": "thread", "target_id": thread_id}).execute()
    supabase.rpc("increment_thread_upvote", {"p_thread_id": thread_id}).execute()
    return {"action": "added"}


@router.post("/replies/{reply_id}/upvote")
async def upvote_reply(reply_id: str, authorization: str | None = Header(None)):
    user_id = get_user_id(authorization)
    supabase = get_supabase()
    existing = (
        supabase.table("community_upvotes")
        .select("user_id")
        .eq("user_id", user_id)
        .eq("target_type", "reply")
        .eq("target_id", reply_id)
        .execute()
    )
    if existing.data:
        supabase.table("community_upvotes").delete().eq("user_id", user_id).eq("target_type", "reply").eq("target_id", reply_id).execute()
        supabase.rpc("decrement_reply_upvote", {"p_reply_id": reply_id}).execute()
        return {"action": "removed"}
    supabase.table("community_upvotes").insert({"user_id": user_id, "target_type": "reply", "target_id": reply_id}).execute()
    supabase.rpc("increment_reply_upvote", {"p_reply_id": reply_id}).execute()
    return {"action": "added"}


# ---------------------------------------------------------------------------
# Badges (view another user's earned badges — own badges via GET /users/me/badges)
# ---------------------------------------------------------------------------

@router.get("/users/{user_id}/badges")
async def user_badges(user_id: str):
    supabase = get_supabase()
    result = supabase.table("user_badges").select("badge_id,awarded_at").eq("user_id", user_id).execute()
    return result.data or []
