import pymongo

PORT = 2000
DATABASE_NAME = "user_data"
COLLECTION_NAME = "fatigue"


client = pymongo.MongoClient(f"mongodb+srv://pi:raspberry@cluster0.xify2pw.mongodb.net/{DATABASE_NAME}")
database = client[DATABASE_NAME]
fatigue_collection = database[COLLECTION_NAME]

fatigue_collection.insert_one({"hello": "world"})