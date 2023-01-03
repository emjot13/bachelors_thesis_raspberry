import pymongo
from datetime import datetime

PORT = 27017
DATABASE_NAME = "user_data"
COLLECTION_NAME = "fatigue"

client = pymongo.MongoClient(f"mongodb://localhost:{PORT}")
database = client[DATABASE_NAME]
fatigue_collection = database[COLLECTION_NAME]

# fatigue_collection.insert_one({"id": USER_ID, "yawning": 0, "sleep": 0})




def insert_data(yawns, sleep):
    date = datetime.now().replace(microsecond=0)
    fatigue_collection.insert_one({"day": date, "yawns": yawns, "sleep": sleep})
    print("INSERTED")
    print("---------------------------------")




def get_all_data():
    data = fatigue_collection.find({})
    return list(data)

