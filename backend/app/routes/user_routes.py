from fastapi import APIRouter, Depends
from app.utils.dependencies import get_current_user

router = APIRouter()

@router.get("/me")
def read_current_user(current_user = Depends(get_current_user)):
    return {"email": current_user["email"], "id": str(current_user["_id"])}