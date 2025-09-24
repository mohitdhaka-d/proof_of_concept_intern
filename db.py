from pymongo import MongoClient
from pymongo.errors import ConnectionFailure
from dotenv import load_dotenv
load_dotenv()
import os

try:
    # Create MongoDB client
    client = MongoClient(os.getenv("MONGODB_URI"), serverSelectionTimeoutMS=5000)
    # Test connection
    client.admin.command("ping")
    print("✅ Database connected successfully!")

    # Select DB and Collection
    db = client["chatbot_emails"]
    collection = db["sent_mails"]

except ConnectionFailure as e:
    print("❌ Database connection failed:", e)
    collection = None
