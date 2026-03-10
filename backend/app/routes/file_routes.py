from fastapi import APIRouter, Depends
from datetime import datetime, timedelta
from app.database.mongodb import files_collection
from app.utils.dependencies import get_current_user
from app.models.file_model import FileCreate
from bson import ObjectId

router = APIRouter()

@router.post("/upload")
async def create_file(file:FileCreate, current_user= Depends(get_current_user)):
    
    expiry_time = datetime.utcnow() + timedelta(hours= file.expiry_time)
    
    file_data= {
        "file_name": file.filename,
        "file_size": file.filesize,
        "owner_id": str(current_user["_id"]),
        "expiry_time": expiry_time,
        "download_count": 0,
        "download_limit": 5,
        "expiry_time": expiry_time,
        "created_at": datetime.utcnow()
    }
    
    result = await files_collection.insert_one(file_data)
    
    return{
        "message": "File uploaded successfully",
        "file_id": str(result.inserted_id),
        "expiry_time": expiry_time.isoformat()
    }
    
@router.get("/")
async def list_files(current_user = Depends(get_current_user)):
    files = files_collection.find({"owner_id": str(current_user["_id"])})
    result = []
    
    async for file in files:
        result.append({
            "file_id": str(file["_id"]),
            "file_name": file["file_name"],
            "file_size": file["file_size"],
            "expiry_time": file["expiry_time"].isoformat(),
            "created_at": file["created_at"].isoformat()

        })
    return result


@router.delete("/{file_id}")
async def delete_file(file_id: str, current_user = Depends(get_current_user)):
    file = await files_collection.find_one({"_id": ObjectId(file_id), "owner_id": str(current_user["_id"])})
    
    if not file:
        return{"message": "file not found or you do not have permission to delete this file."}
    
    await files_collection.delete_one({"_id":ObjectId(file_id)})
    
    return{"message": "file deleted successfully."}

