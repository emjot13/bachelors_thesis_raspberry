import pymongo

PORT = 2000
DATABASE_NAME = "user_data"
COLLECTION_NAME = "fatigue"
USER_ID = 0

client = pymongo.MongoClient(f"mongodb+srv://pi:raspberry@cluster0.xify2pw.mongodb.net/{DATABASE_NAME}")
database = client[DATABASE_NAME]
fatigue_collection = database[COLLECTION_NAME]

fatigue_collection.insert_one({"id": USER_ID, "yawning": 0, "sleep": 0})




def insert_data(data):
    fatigue_collection.update_one({"id": USER_ID}, {"$set": data})
    print("INSERTED")
    print("---------------------------------")
