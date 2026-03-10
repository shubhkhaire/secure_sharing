import os
from pymongo import MongoClient
from dotenv import load_dotenv

load_dotenv()

MONGO_URL = os.getenv("MONGODB_URL")
DB_NAME = os.getenv("DB_NAME")

client = MongoClient(MONGO_URL)

db = client[DB_NAME]

users_collection = db["users"]
files_collection = db["files"]