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
            '$addFields':{
                'working_time': { '$subtract': [ '$end_time', '$start_time' ] }
             }

            },
                    {
            '$addFields':{
                'avg_yawns_per_hour': { '$divide': [ '$total_yawns', {'$divide': ['$working_time', 3600000]}] },
                'avg_sleep_per_hour': { '$divide': [ '$total_sleep', {'$divide': ['$working_time', 3600000]}] }


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


    for day in result:
        # day["day"] = day.pop("_id")
        hours = day["hours"]
        hours[0]["increase_sleep"], hours[0]["increase_yawns"] = 0, 0
        hours[0]["hour"] = hours[0].pop("_id")
        
        for i in range(1, len(hours)):
            hours[i]["increase_sleep"] = hours[i]["sleep"] - hours[i - 1]["sleep"]
            hours[i]["increase_yawns"] = hours[i]["yawns"] - hours[i - 1]["yawns"]
            hours[i]["hour"] = hours[i].pop("_id")

    print(result)


    return result
    







# {'_id': ObjectId('63bb500a5f7ba69e8dc5be69'), 'day': datetime.datetime(2020, 3, 11, 8, 58, 20), 'yawns': 51, 'sleep': 53}
# {'_id': ObjectId('63bb500a5f7ba69e8dc5be6a'), 'day': datetime.datetime(2020, 3, 11, 10, 58, 30), 'yawns': 51, 'sleep': 53}
# {'_id': ObjectId('63bb500a5f7ba69e8dc5be6b'), 'day': datetime.datetime(2020, 3, 11, 15, 58, 40), 'yawns': 51, 'sleep': 53}
# {'_id': ObjectId('63bb500a5f7ba69e8dc5be6c'), 'day': datetime.datetime(2020, 3, 12, 8, 58, 50), 'yawns': 51, 'sleep': 53}
# {'_id': ObjectId('63bb500a5f7ba69e8dc5be6d'), 'day': datetime.datetime(2020, 3, 12, 10, 59), 'yawns': 51, 'sleep': 53}
# {'_id': ObjectId('63bb500a5f7ba69e8dc5be6e'), 'day': datetime.datetime(2020, 3, 12, 15, 59, 10), 'yawns': 51, 'sleep': 53}
# {'_id': ObjectId('63bb500a5f7ba69e8dc5be6f'), 'day': datetime.datetime(2020, 3, 13, 8, 59, 20), 'yawns': 51, 'sleep': 53}
# {'_id': ObjectId('63bb500a5f7ba69e8dc5be70'), 'day': datetime.datetime(2020, 3, 13, 10, 59, 30), 'yawns': 51, 'sleep': 53}
# {'_id': ObjectId('63bb500a5f7ba69e8dc5be71'), 'day': datetime.datetime(2020, 3, 13, 15, 59, 40), 'yawns': 51, 'sleep': 53}
# {'_id': ObjectId('63bb500a5f7ba69e8dc5be72'), 'day': datetime.datetime(2020, 3, 14, 8, 59, 50), 'yawns': 51, 'sleep': 54}
# {'_id': ObjectId('63bb500a5f7ba69e8dc5be73'), 'day': datetime.datetime(2020, 3, 14, 10, 0), 'yawns': 51, 'sleep': 54}






# [{'_id': '2020-01-14', 'max_sleep': 77, 'max_yawns': 75, 'hours': [{'_id': 9, 'sleep': 16, 'yawns': 17}, {'_id': 16, 'sleep': 77, 'yawns': 75}, {'_id': 14, 'sleep': 67, 'yawns': 65}, {'_id': 10, 'sleep': 28, 'yawns': 28}, {'_id': 12, 'sleep': 47, 'yawns': 43}, {'_id': 8, 'sleep': 12, 'yawns': 12}, {'_id': 11, 'sleep': 39, 'yawns': 36}, {'_id': 15, 'sleep': 77, 'yawns': 75}, {'_id': 13, 'sleep': 56, 'yawns': 53}]}, {'_id': '2020-01-15', 'max_sleep': 54, 'max_yawns': 53, 'hours': [{'_id': 13, 'sleep': 36, 'yawns': 39}, {'_id': 15, 'sleep': 54, 'yawns': 53}, {'_id': 8, 'sleep': 7, 'yawns': 8}, {'_id': 10, 'sleep': 21, 'yawns': 21}, {'_id': 11, 'sleep': 24, 'yawns': 24}, {'_id': 16, 'sleep': 54, 'yawns': 53}, {'_id': 9, 'sleep': 13, 'yawns': 14}, {'_id': 14, 'sleep': 47, 'yawns': 48}, {'_id': 12, 'sleep': 29, 'yawns': 30}]}, {'_id': '2020-01-10', 'max_sleep': 57, 'max_yawns': 55, 'hours': [{'_id': 10, 'sleep': 20, 'yawns': 21}, {'_id': 14, 'sleep': 49, 'yawns': 48}, {'_id': 15, 'sleep': 57, 'yawns': 55}, {'_id': 12, 'sleep': 35, 'yawns': 34}, {'_id': 9, 'sleep': 9, 'yawns': 10}, {'_id': 11, 'sleep': 28, 'yawns': 28}, {'_id': 16, 'sleep': 57, 'yawns': 55}, {'_id': 8, 'sleep': 5, 'yawns': 6}, {'_id': 13, 'sleep': 42, 'yawns': 40}]}, {'_id': '2020-01-12', 'max_sleep': 61, 'max_yawns': 59, 'hours': [{'_id': 16, 'sleep': 61, 'yawns': 59}, {'_id': 8, 'sleep': 6, 'yawns': 7}, {'_id': 9, 'sleep': 18, 'yawns': 19}, {'_id': 13, 'sleep': 45, 'yawns': 42}, {'_id': 12, 'sleep': 41, 'yawns': 40}, {'_id': 14, 'sleep': 52, 'yawns': 53}, {'_id': 10, 'sleep': 23, 'yawns': 24}, {'_id': 15, 'sleep': 61, 'yawns': 59}, {'_id': 11, 'sleep': 33, 'yawns': 33}]}, {'_id': '2020-01-11', 'max_sleep': 54, 'max_yawns': 52, 'hours': [{'_id': 10, 'sleep': 20, 'yawns': 19}, {'_id': 14, 'sleep': 49, 'yawns': 48}, {'_id': 12, 'sleep': 33, 'yawns': 31}, {'_id': 15, 'sleep': 54, 'yawns': 52}, {'_id': 16, 'sleep': 54, 'yawns': 52}, {'_id': 8, 'sleep': 7, 'yawns': 5}, {'_id': 13, 'sleep': 41, 'yawns': 41}, {'_id': 11, 'sleep': 28, 'yawns': 26}, {'_id': 9, 'sleep': 13, 'yawns': 13}]}, {'_id': '2020-01-13', 'max_sleep': 49, 'max_yawns': 54, 'hours': [{'_id': 8, 'sleep': 7, 'yawns': 7}, {'_id': 14, 'sleep': 42, 'yawns': 46}, {'_id': 16, 'sleep': 49, 'yawns': 54}, {'_id': 9, 'sleep': 12, 'yawns': 14}, {'_id': 12, 'sleep': 28, 'yawns': 32}, {'_id': 11, 'sleep': 23, 'yawns': 28}, {'_id': 13, 'sleep': 35, 'yawns': 40}, {'_id': 15, 'sleep': 49, 'yawns': 54}, {'_id': 10, 'sleep': 18, 'yawns': 22}]}]