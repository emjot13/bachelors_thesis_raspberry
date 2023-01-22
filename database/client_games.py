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

def find_data_in_date_range(start_date, end_date, game):
    end_date += ' 23:59:59'
    start_date = datetime.strptime(start_date, '%Y-%m-%d')
    end_date = datetime.strptime(end_date, '%Y-%m-%d %H:%M:%S')
    result = games_collection.aggregate([
    {
        '$match': {
            'date': {'$gte': start_date, '$lte': end_date},
            'game': game
        }
    },
    {
        '$group': {
            '_id': None,
            'average_score': {'$avg': '$score'}
        }
    }
])
    result = list(result)
    return result