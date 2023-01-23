import pymongo
from datetime import datetime
import random as rd
from datetime import date, timedelta

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
    #print(result)
    return result

def generate_mock_data():
    start_date = '01/01/20 08:01:00'
    end_date = '12/31/20 15:59:00'
    start_date = datetime.strptime(start_date, '%m/%d/%y %H:%M:%S')
    end_date = datetime.strptime(end_date, '%m/%d/%y %H:%M:%S')

    with open("mock_data_games.txt", "w") as f:
        delta = timedelta(days=1)
        while start_date <= end_date:
            math_score = rd.randint(0, 400) / 100
            memory_score = rd.randint(8, 30)
            f.write(f"{start_date},math, {math_score}\n")
            f.write(f"{start_date},memory, {memory_score}\n")
            start_date += delta


def populate_database_with_mock_data():
    with open("mock_data_games.txt", "r") as f:
        for line in f.readlines():
            line = line.split(",")
            date = datetime.strptime(line[0], '%Y-%m-%d %H:%M:%S')
            game = line[1]
            score = float(line[2])
            games_collection.insert_one({"date": date, "game": game, "score": float(score)})

            # date = datetime.strptime(line[0], '%d-%B-%Y %A')

            # print(date)


# generate_mock_data()
# populate_database_with_mock_data()