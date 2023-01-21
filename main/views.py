from django.shortcuts import render
from django.http import HttpResponse

from django.shortcuts import render, redirect

from ai.main import main
import os
import threading
import database.client as database
import utils.main as utils
import json


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


def tiredness(request):

    if request.method == "GET":
        interval = request.GET.get("time_interval", None)
        start_date = request.GET.get("start_date", None)
        end_date = request.GET.get("end_date", None)
        if interval:
            interval = int(interval)

        data = database.find_data_intervals_date_range(interval=interval, start_date=start_date, end_date=end_date)
        labels = [item['day'].strftime("%m/%d/%Y %H:%M:%S") for item in data]
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
                },
                    {
                    'label': 'Closed eyes',
                    'data': [item['sleep'] for item in data],
                    'backgroundColor': 'rgba(55, 199, 132, 0.2)',
                    'borderColor': 'rgba(55, 199, 132, 1)',
                    }
                ]
            }
        }
        return render(request, 'tiredness_stats.html', context)
