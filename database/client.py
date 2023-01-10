import pymongo
from datetime import datetime
import random as rd

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



def generate_mock_data():
    start_date = '01/01/20 08:00:00'
    end_date = '12/31/20 16:00:00'
    start_date = datetime.strptime(start_date, '%m/%d/%y %H:%M:%S')
    end_date = datetime.strptime(end_date, '%m/%d/%y %H:%M:%S')

    start_date_ts = int(datetime.timestamp(start_date))
    end_date_ts = int(datetime.timestamp(end_date))

    with open("mock_data.txt", "w") as f:
        for day in range(start_date_ts, end_date_ts, 3600 * 24):
            fatigue = rd.randint(97, 98) / 100

            sleep, yawns = 0, 0
            for working_hours in range(day, day + 3600 * 8 + 1, 10):
                chance = rd.random()
                if chance > fatigue:
                    chance1 = rd.random()
                    if chance1 < 0.8:
                        sleep += 1 
                        yawns += 1
                    if 0.8 <= chance1 < 0.9:
                        sleep += 1
                    if 0.9 <= chance1 < 1:
                        yawns += 1
                f.write(f"{datetime.fromtimestamp(working_hours)}, {yawns}, {sleep}\n")


def populate_database_with_mock_data():
    with open("mock_data.txt", "r") as f:
        for line in f.readlines():
            line = line.split(",")
            date = datetime.strptime(line[0], '%Y-%m-%d %H:%M:%S')
            yawns = int(line[1])
            sleep = int(line[2])
            fatigue_collection.insert_one({"day": date, "yawns": yawns, "sleep": sleep})

            # date = datetime.strptime(line[0], '%d-%B-%Y %A')

            # print(date)


# generate_mock_data()
# populate_database_with_mock_data()

def find_data_by_day(day):
    start_date = '12/31/20 08:00:00'
    end_date = '12/31/20 17:00:00'
    start_date = datetime.strptime(start_date, '%m/%d/%y %H:%M:%S')
    end_date = datetime.strptime(end_date, '%m/%d/%y %H:%M:%S')

    query = {"day": {"$gte": start_date, "$lt": end_date}}
    import time
    start = time.time()
    docs = fatigue_collection.find(query)
    end = time.time()
    print(end - start)
    return docs

find_data_by_day("2020-01-01")