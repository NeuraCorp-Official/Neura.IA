from dotenv import load_dotenv
from pathlib import Path
import os
from pymongo import MongoClient

load_dotenv(dotenv_path=Path(__file__).parent / ".env")

uri = os.environ.get("MONGODB_URI")
print("URI:", uri)

client = MongoClient(uri)
client.admin.command('ping')
print("✅ MongoDB conectado!")