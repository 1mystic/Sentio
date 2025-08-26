from fastapi import APIRouter

router = APIRouter()

@router.get("/")
async def get_learning_modules():
    """Get learning modules"""
    return {"message": "Learning modules endpoint"}

@router.get("/{module_id}")
async def get_module_detail():
    """Get module detail"""
    return {"message": "Module detail endpoint"}
