from pydantic import BaseModel
from typing import Optional

class FileCreate(BaseModel):
    filename: str
    filesize: int
    # content_type: str
    expiry_time: int = 24
    password: Optional[str] = None
    
