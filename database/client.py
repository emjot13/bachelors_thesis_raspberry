from copy import copy, deepcopy

import pymongo
from datetime import datetime, timedelta
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

def find_data_intervals_date_range(interval, start_date=None, end_date=None):
    items = []
    if interval is None:
        interval = 15
    if start_date is None:
        start_date = datetime(2020, 1, 1)
    else:
        start_date = datetime.strptime(start_date, '%Y-%m-%d')
    if end_date is None or end_date == "":
        end_date = start_date + timedelta(days=1)
    else:
        end_date = datetime.strptime(end_date, '%Y-%m-%d')

    start_date += timedelta(hours=8)

    result = fatigue_collection.aggregate([
        {
            '$match': {'day': {'$gte': start_date, '$lte': end_date},
                       }

        },
    ])
    result_copy = deepcopy(list(result))
    for res in range(0, len(list(result_copy)), interval*6):
        data_to_append = {}
        for field in list(result_copy)[res]:
            data_to_append[field] = list(result_copy)[res][field]
        items.append(data_to_append)

    return items



def find_data_in_date_range(start_date, end_date):
    end_date += ' 23:59:59'
    start_date = datetime.strptime(start_date, '%Y-%m-%d')
    end_date = datetime.strptime(end_date, '%Y-%m-%d %H:%M:%S')
    result = fatigue_collection.aggregate([
        {
            '$match': {
                'day': {'$gte': start_date, '$lte': end_date}
            }
        },
        {
            '$group': {
                '_id': {
                    'date': {'$dateToString': {'format': '%Y-%m-%d', 'date': '$day'}},
                    'hour': {'$hour': '$day'}

                },
                'sleep': {'$max': '$sleep'},
                'yawns': {'$max': '$yawns'},
                'start_time': {'$min': '$day'},
                'end_time': {'$max': '$day'}

            },
        },

        {
            '$group': {
                '_id': '$_id.date',
                'total_sleep': {'$max': '$sleep'},
                'total_yawns': {'$max': '$yawns'},
                'start_time': {'$min': '$start_time'},
                'end_time': {'$max': '$end_time'},
                'hours': {
                    '$push': {
                        '_id': '$_id.hour',
                        'sleep': '$sleep',
                        'yawns': '$yawns'
                    }
                }
            }
        },
        {
            '$addFields': {
                'working_time': {'$subtract': ['$end_time', '$start_time']}
            }

        },
        {
            '$addFields': {
                'avg_yawns_per_hour': {
                    '$round': [{'$divide': ['$total_yawns', {'$divide': ['$working_time', 3600000]}]}, 2]},
                'avg_sleep_per_hour': {
                    '$round': [{'$divide': ['$total_sleep', {'$divide': ['$working_time', 3600000]}]}, 2]}

            }

        },
        {
            '$sort': {
                '_id': 1,
            }
        },

        {
            '$project': {
                'day': '$_id',
                '_id': 0,
                'avg_yawns_per_hour': 1,
                'avg_sleep_per_hour': 1,
                # 'working_time': 1,
                'hours': 1,
                'start_time': {'$dateToString': {'format': '%H-%M-%S', 'date': '$start_time'}},
                'end_time': {'$dateToString': {'format': '%H-%M-%S', 'date': '$end_time'}},
                # 'hour': '$hours._id',
                'total_yawns': 1,
                'total_sleep': 1

            }
        },

    ])

    result = list(result)
    # print(result)

    for day in result:
        hours = sorted(day["hours"], key=lambda x: x["_id"])
        hours[0]["increase_sleep"], hours[0]["increase_yawns"] = hours[0]["sleep"], hours[0]["yawns"]
        hours[0]["hour"] = hours[0].pop("_id")

        for i in range(1, len(hours)):
            hours[i]["increase_sleep"] = hours[i]["sleep"] - hours[i - 1]["sleep"]
            hours[i]["increase_yawns"] = hours[i]["yawns"] - hours[i - 1]["yawns"]
            hours[i]["hour"] = hours[i].pop("_id")
        day["hours"] = hours

    # print(result)

    return result

