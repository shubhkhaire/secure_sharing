from fastapi import APIRouter, HTTPException
from app.models.user_model import UserLogin, UserRegister
from app.utils.token import create_access_token
from app.utils.security import hash_password, verify_password
from app.database.mongodb import users_collection

router = APIRouter()

@router.post("/register")
def register_user(user: UserRegister):
    existing_user = users_collection.find_one({"email": user.email})
    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    hashed_password = hash_password(user.password)
    
    user_data = {
        "email": user.email,
        "password": hashed_password,
    }
    
    users_collection.insert_one(user_data)
    return {"message": "User registered successfully"}
    
       
@router.post("/login")
def login_user(user:UserLogin):
    db_user = users_collection.find_one({"email": user.email})
    if not db_user:
        raise HTTPException(status_code = 400, detail="Invalid email or password")
    if not verify_password(user.password, db_user["password"]):
        raise HTTPException(status_code=400, detail="Invalid email or password")
     
    token = create_access_token({"user_id": str(db_user["_id"])})
    return{"access_token": token, "token_type": "bearer"}