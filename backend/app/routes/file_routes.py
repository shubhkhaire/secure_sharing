from fastapi import APIRouter, Depends, UploadFile, File
from datetime import datetime, timedelta
from app.database.mongodb import files_collection
from app.utils.dependencies import get_current_user
from app.models.file_model import FileCreate
from app.models.share_model import ShareRequest
from bson import ObjectId
from fastapi.responses import FileResponse
from uuid import uuid4
import os 
from app.utils.security import hash_password, verify_password

router = APIRouter()


@router.post("/upload")
async def upload_file(file: UploadFile = File(...), current_user= Depends(get_current_user)):
    file_path = f"uploads/{file.filename}"
    
    with open(file_path, "wb") as buffer:
        content = await file.read()
        buffer.write(content)
    expiry_time = datetime.utcnow() + timedelta(hours=8)
        
    file_data={
    "file_name": uuid4().hex + "_" + file.filename,
    "original_name": file.filename,
    "file_path": file_path,
    "owner_id": str(current_user["_id"]),
    "file_size": len(content),
    "created_at": datetime.utcnow(),
    "download_count": 0,
    "download_limit": 5,
    "expiry_time": expiry_time
    }

    result = await files_collection.insert_one(file_data)
    
    return{
        "message": "file uploaded successfully",
        "file_id": str(result.inserted_id)
    }

    
@router.get("/")
async def list_files(current_user = Depends(get_current_user)):
    files = files_collection.find({"owner_id": str(current_user["_id"])})
    result = []
    
    async for file in files:
        result.append({
            "file_id": str(file["_id"]),
            "file_name": file["file_name"],
            "original_name": file["original_name"],
            "file_size": file["file_size"],
            "expiry_time": file["expiry_time"].isoformat(),
            "created_at": file["created_at"].isoformat()
        })
    return result


@router.delete("/delete/{file_id}")
async def delete_file(file_id: str, current_user = Depends(get_current_user)):
    file = await files_collection.find_one({"_id": ObjectId(file_id), "owner_id": str(current_user["_id"])})
    
    if not file:
        return{"message": "file not found or you do not have permission to delete this file."}
    
    await files_collection.delete_one({"_id":ObjectId(file_id)})
    
    return{"message": "file deleted successfully."}



@router.post("/share/{file_id}")
async def share_file(
    file_id: str,
    data: ShareRequest,
    current_user = Depends(get_current_user)
    ):
    
    file = await files_collection.find_one({"_id":ObjectId(file_id)})
    if not file:
        return{"message": "file not found or you do not have permission to share this file."}
    
    if file["expiry_time"] < datetime.utcnow():
        return{"message": "file has expired and cannot be shared."}
    
    expiry_time = datetime.utcnow() + timedelta(hours=data.expiry_hours)
    
    password_hash = hash_password(data.password)
    if password_hash != file.get(password_hash):
        
        files_collection.update_one(
        {"_id": ObjectId((file_id))},
            {
                "$set": {"password_hash": password_hash,
                "expiry_time": expiry_time,
                "download_limit": data.download_limit
                }
            }
        )

    
        
    return{
        "file_id": str(file["_id"]),
        "download_url": f"http://localhost:8000/files/download/{file_id}"
    }
    

@router.get("/download/{file_id}")
# @router.post("/download/{file_id}")
async def download_file(file_id: str, password: str = None):
    file = await files_collection.find_one({"_id": ObjectId(file_id)})
    
    if not file:
        return{"message": "file not found."}
    
    if file["expiry_time"] < datetime.utcnow():
        return{"message": "file has expired and cannot be downloaded."}
    
    if file["download_count"] >= file["download_limit"]:
        return{"message": "download limit reached for this file."}
    
    if file.get("password_hash"):
        if not password or not verify_password(password, file["password_hash"]):
            return{"message": "incorrect password."}
    
    
    file_path = f"uploads/{file['original_name']}"
    
    await files_collection.update_one({"_id": ObjectId(file_id)}, {"$inc": {"download_count": 1}})

    return FileResponse(path= file_path, filename=file["original_name"])


def cleanup_expired_files():
    expired_files = files_collection.find({"expiry_time": {"$lt": datetime.utcnow()}})
    for file in expired_files:
        file_path = f"uploads/{file['original_name']}"
        if os.path.exists(file_path):
            os.remove(file_path)
        files_collection.delete_one({"_id": file["_id"]})