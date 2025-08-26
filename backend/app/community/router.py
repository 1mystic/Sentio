from fastapi import APIRouter

router = APIRouter()

@router.get("/posts")
async def get_community_posts():
    """Get community posts"""
    return {"message": "Community posts endpoint"}

@router.post("/posts")
async def create_community_post():
    """Create community post"""
    return {"message": "Create community post endpoint"}
