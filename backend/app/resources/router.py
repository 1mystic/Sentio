from fastapi import APIRouter

router = APIRouter()

@router.get("/professionals")
async def search_professionals():
    """Search mental health professionals"""
    return {"message": "Search professionals endpoint"}

@router.get("/educational")
async def get_educational_materials():
    """Get educational materials"""
    return {"message": "Educational materials endpoint"}

@router.get("/crisis")
async def get_crisis_resources():
    """Get crisis resources"""
    return {"message": "Crisis resources endpoint"}
