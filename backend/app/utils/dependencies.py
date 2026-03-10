from fastapi import HTTPException, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from app.utils.token import SECRET_KEY, ALGORITHM
from app.database.mongodb import users_collection
from jose import jwt, JWTError
from bson import ObjectId
 
security = HTTPBearer()

async def get_current_user(credentials:HTTPAuthorizationCredentials = Depends(security)):
    
    token = credentials.credentials
    
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id:str = payload.get("user_id")
        
        if user_id is None:
            raise HTTPException(status_code=401, detail="Invalid token")
        
    except JWTError:
        raise HTTPException(status_code=401, detail="invalid token")
    
    user = await users_collection.find_one({"_id": ObjectId(user_id)})
    
    if not user:
        raise HTTPException(status_code=401, detail="user not found")
    
    return user