
def lifestyle_summary(date_range_1, date_range_2):
    total_sleep_1, total_yawns_1 = 0, 0
    total_sleep_2, total_yawns_2 = 0, 0
    days_1, days_2 = len(date_range_1), len(date_range_2)

    for day in date_range_1:
        total_sleep_1 += day["total_sleep"]
        total_yawns_1 += day["total_yawns"]

    for day in date_range_2:
        total_sleep_2 += day["total_sleep"]
        total_yawns_2 += day["total_yawns"]

    average_sleep1 = round(total_sleep_1 / days_1, 2)
    average_yawns1 = round(total_sleep_1 / days_1, 2)
    average_sleep2 = round(total_yawns_2 / days_2, 2)
    average_yawns2 = round(total_yawns_2 / days_2, 2)

    summary = {
        "first": {
            "total_sleep": total_sleep_1,
            "total_yawns": total_yawns_1,
            "average_sleep": average_sleep1,
            "average_yawns": average_yawns1,
            "start": date_range_1[0]["day"],
            "end": date_range_1[-1]["day"] 

        },
        "second": {
            "total_sleep": total_sleep_2,
            "total_yawns": total_yawns_2,
            "average_sleep": average_sleep2,
            "average_yawns": average_yawns2,
            "start": date_range_2[0]["day"],
            "end": date_range_2[-1]["day"] 

        }
    }
    
    print(summary)

    return summary