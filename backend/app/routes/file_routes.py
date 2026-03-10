from fastapi import APIRouter, Depends
from datetime import datetime, timedelta
from app.database.mongodb import files_collection
from app.utils.dependencies import get_current_user
from app.models.file_model import FileCreate

router = APIRouter()

@router.post("/upload")
def create_file(file:FileCreate, current_user= Depends(get_current_user)):
    
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
    
    result = files_collection.insert_one(file_data)
    
    return{
        "message": "File uploaded successfully",
        "file_id": str(result.inserted_id),
        "expiry_time": expiry_time.isoformat()
    }