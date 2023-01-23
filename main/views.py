from django.shortcuts import render
from django.http import HttpResponse

from django.shortcuts import render, redirect

from ai.fatigue_detection.main import FatigueDetector

import os
import threading
import database.client as database
import utils.main as utils
#
# import hardware.distance as distance
# import hardware.photoresistor as room_light


def start(request):
    return render(request, "start.html")

def detection_conf(request):
    if request.method == "POST":
        data = request.POST
        closed_eyes_seconds_threshold = int(data.get("closed_eyes_seconds_threshold"))
        fps = int(data.get("fps"))
        eye_aspect_ratio_threshold = float(data.get("eye_aspect_ratio_threshold"))
        yawn_threshold = int(data.get("yawn_threshold"))
        database_writes_frequency = int(data.get("database_frequency"))
        
        detector = FatigueDetector(closed_eyes_seconds_threshold, fps, eye_aspect_ratio_threshold, yawn_threshold, database_writes_frequency)
        detector_thread = threading.Thread(target = detector.run)
        detector_thread.start()

        screen_distance = threading.Thread(target = distance.proper_distance_from_screen)
        screen_distance.start()

        proper_room_light = threading.Thread(target = room_light.check_room_light)
        proper_room_light.start()


        return render(request, "start.html")



    return render(request, "detection_conf.html")        

def shutdown(request):
    if request.method == "POST":
        os.system("sudo shutdown now")
    return render(request, "start.html")

def pause(request):
    if request.method == "POST":
        pause = "logical_files/pause"
        with open(pause, mode = "a"): pass
    
    return redirect(start)



def lifestyle(request):
    if request.method == "GET":
        return render(request, "lifestyle_analysis.html")
    if request.method == "POST":
        start_date = request.POST.get("start")
        end_date = request.POST.get("end")
        start_date1 = request.POST.get("start1")
        end_date1 = request.POST.get("end1")

        first = database.find_data_in_date_range(start_date, end_date)
        second = database.find_data_in_date_range(start_date1, end_date1)
        # print(list(zip(first, second)))
        summary = utils.lifestyle_summary(first, second)
        
        # print(data)
        return render(request, "lifestyle_analysis.html", {"data": zip(first, second), "summary": summary})

def admin(request):
    if request.method == "GET":
        start_date = request.GET.get("start_date", None)
        end_date = request.GET.get("end_date", None)
        users_data = database.get_admin_data_between_dates(start_date=start_date, end_date=end_date)
        users_data = dict(sorted(users_data.items()))
        for day in users_data:
            users_data[day]['hours'] = sorted(users_data[day]['hours'], key=lambda x: x['hour'])
        users_data_list = []
        for day in users_data:
            obj = users_data[day]
            obj['day'] = day
            users_data_list.append(obj)
        context = {
            'items': users_data_list,
        }
        return render(request, "admin_view.html", context)


def tiredness(request):
    # data = database.get_all_data()
    # print(data, type(data))
    labels = [item['day'].strftime("%m/%d/%Y, %H:%M:%S") for item in data]
    # old_days = [item['day'] for item in items]

    # print(days)
    # print(old_days)
    context = {
        'message': 'These are your tiredness stats',
        'items': data,
        'chart_data': {
    'labels': labels,
    'datasets': [{
        'label': 'Yawns',
        'data': [item['yawns'] for item in data],
        'backgroundColor': 'rgba(255, 99, 132, 0.2)',
        'borderColor': 'rgba(255, 99, 132, 1)',
    }]
}
    }
    return render(request, 'tiredness_stats.html', context)
