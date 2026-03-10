from fastapi import FastAPI
from app.database.mongodb import  db
from app.routes.auth_routes import router as auth_router
from app.routes.user_routes import router as user_router

app = FastAPI(title="secure file sharing api")

app.include_router(auth_router, prefix="/auth", tags=["auth"])
app.include_router(user_router, prefix="/users", tags=["users"])

@app.get("/")
def root():
    return {"message" : "secure file sharing running"}

@app.get("/health")
def health_check():
    return {"status": "healthy"}



