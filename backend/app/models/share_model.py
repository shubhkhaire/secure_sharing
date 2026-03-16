import pydantic
from pydantic import BaseModel
from typing import Optional

class ShareRequest(BaseModel):
    password: Optional[str] = None
    expiry_hours: Optional[int] = 24
    download_limit: Optional[int] = 5
    