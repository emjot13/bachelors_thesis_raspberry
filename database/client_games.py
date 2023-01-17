import pymongo
from datetime import datetime

PORT = 27017
DATABASE_NAME = "user_data"
COLLECTION_NAME = "games"

client = pymongo.MongoClient(f"mongodb://localhost:{PORT}")
database = client[DATABASE_NAME]
games_collection = database[COLLECTION_NAME]

def insert_data(date, game, score):
    date = datetime.now().replace(microsecond=0)
    games_collection.insert_one({"date": date, "game": game, "score": score})
    print("INSERTED")
    print("---------------------------------")


def get_all_data():
    data = games_collection.find({})
    return list(data)