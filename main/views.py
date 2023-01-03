from django.shortcuts import render
from django.http import HttpResponse

from django.shortcuts import render, redirect

from ai.main import main
import os
import threading
import database.client as database


def start(request):
    if request.method == "POST":
        m = threading.Thread(target = main)
        m.start()
    # print("here")

    return render(request, "start.html")

def shutdown(request):
    if request.method == "POST":
        os.system("sudo shutdown now")
    return render(request, "start.html")

def pause(request):
    if request.method == "POST":
        pause = "logical_files/pause"
        with open(pause, mode = "a"): pass
    
    return redirect(start)

items = [
    {"day": '11-02-2022', "yawns": 5, "sleep": 10}, {"day": '12-02-2022', "yawns": 4, "sleep": 8}, {"day": '13-02-2022', "yawns": 11, "sleep": 14},
    {"day": '11-02-2022', "yawns": 5, "sleep": 10}, {"day": '12-02-2022', "yawns": 4, "sleep": 8}, {"day": '13-02-2022', "yawns": 11, "sleep": 14},
    {"day": '11-02-2022', "yawns": 5, "sleep": 10}, {"day": '12-02-2022', "yawns": 4, "sleep": 8}, {"day": '13-02-2022', "yawns": 11, "sleep": 14},
 ]



def tiredness(request):
    data = database.get_all_data()
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
