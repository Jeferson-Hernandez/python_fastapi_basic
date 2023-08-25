from pymongo import MongoClient
import settings

client = MongoClient(settings.mongodb_uri)
db = client.fastapi_users
users_collection = db["users"]

try:
    client.admin.command('ping')
    print("Pinged your deployment. You successfully connected to MongoDB!")
except Exception as e:
    print(e)