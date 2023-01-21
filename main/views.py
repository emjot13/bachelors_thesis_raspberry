from django.shortcuts import render
from django.http import HttpResponse

from django.shortcuts import render, redirect

from ai.fatigue_detection.main import FatigueDetector

import os
import threading
import database.client as database
import database.client_games as database_games
import utils.main as utils


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
        

        # print(closed_eyes_seconds_threshold, fps, eye_aspect_ratio_threshold, yawn_threshold, database_writes_frequency)
        # print(type(closed_eyes_seconds_threshold), type(fps), type(eye_aspect_ratio_threshold), yawn_threshold, database_writes_frequency)


        detector = FatigueDetector(closed_eyes_seconds_threshold, fps, eye_aspect_ratio_threshold, yawn_threshold, database_writes_frequency)
        detector_thread = threading.Thread(target = detector.run)
        detector_thread.start()


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

#-----------------------GAMES------------------------

def games(request):
    return render(request, 'games.html')

def mathgame(request):
    if request.method == 'POST':
        date = request.POST.get('data')
        game = request.POST.get('game')
        score = request.POST.get('score')
        database_games.insert_data(date, game, score)
        return redirect(games)
    return render(request, 'math_game.html')

def memorygame(request):
    if request.method == 'POST':
        date = request.POST.get('data')
        game = request.POST.get('game')
        score = request.POST.get('score')
        database_games.insert_data(date, game, score)
        return redirect(games)
    return render(request, 'memory_game.html')
