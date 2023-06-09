from django.shortcuts import render
from django.http import HttpResponse

from django.shortcuts import render, redirect

from ai.fatigue_detection.main import FatigueDetector

import os
import threading
import database.client as database
import database.client_games as database_games
import utils.main as utils
import json

# from  .fatigue_service import FatigueDetectorService
import hardware.distance as distance
import hardware.photoresistor as room_light
from django.http import StreamingHttpResponse
import time
import datetime
import paho.mqtt.client as mqtt
from django.views.decorators.http import condition
# from mqtt.led import LedLight
# from mqtt_v2.photoresistor_config import MqttSubscriber
from .services.fatigue_service import FatigueDetectorService
from .services.photoresistor_config_service import PhotoresistorConfigService
from .services.distance_sensor_config_service import DistanceSensorConfigService
from .services.photoresistor_red_light_service import PhotoresistorRedLedService
from .services.distance_sensor_red_led_service import DistanceSensorRedLedService


from .services.utils.hardware_config import min_max_values_for_hardware_component, modify_min_max_values_for_hardware_component, HardwareComponent 

from django.http import HttpResponse



photoresistor_config_service = PhotoresistorConfigService()
def photoresistor_stream(request):
    print("called stream")
    def event_stream():
        print("In event stream")
        print("running: ", photoresistor_config_service.is_running)
        while photoresistor_config_service.is_running:
            value = photoresistor_config_service.photoresistor_config_current_value()
            print("backend: ", value)
            time.sleep(1)
            yield 'data: %s\n\n' % value       
    return StreamingHttpResponse(event_stream(), content_type='text/event-stream')
    
def photoresistor_config(request):
    if request.method == 'POST':
        data = request.POST
        action = data.get('action')
        min_threshold = data.get('minThreshold')
        max_threshold = data.get('maxThreshold')

        print(action, min_threshold)
        if action == 'start':
            photoresistor_config_service.initialize_photoresistor_config()
            photoresistor_config_service.start_photoresistor_config()

        if action == 'stop':
            photoresistor_config_service.stop_photoresistor_config()

        if min_threshold and max_threshold:
            print(min_threshold, max_threshold)
            modify_min_max_values_for_hardware_component(HardwareComponent.Photoresistor, min_threshold, max_threshold)
            return render(request, 'photoresistor_config.html', {"current_min_threshold": min_threshold, "current_max_threshold": max_threshold})

    current_min_threshold, current_max_threshold = min_max_values_for_hardware_component(HardwareComponent.Photoresistor)
    return render(request, 'photoresistor_config.html', {"current_min_threshold": current_min_threshold, "current_max_threshold": current_max_threshold})



# photoresistor_config_service = PhotoresistorConfigService()
distance_sensor_config_service = DistanceSensorConfigService()
def distance_sensor_stream(request):
    print("called stream")
    def event_stream():
        print("In event stream")
        while distance_sensor_config_service.is_running:
            value = distance_sensor_config_service.distance_sensor_config_current_value()
            print("backend: ", value)
            time.sleep(1)
            yield 'data: %s\n\n' % value       
    return StreamingHttpResponse(event_stream(), content_type='text/event-stream')


# red_light_service = RedLightForDistanceSensorService()
def distance_sensor_config(request):
    if request.method == 'POST':
        data = request.POST
        action = data.get('action')
        min_threshold = data.get('minThreshold')
        max_threshold = data.get('maxThreshold')

        print(action, min_threshold)
        if action == 'start':
            # red_light_service.initialize_led_light()
            # red_light_service.start_led_light()

            distance_sensor_config_service.initialize_distance_sensor_config()
            distance_sensor_config_service.start_distance_sensor_config()

        if action == 'stop':
            distance_sensor_config_service.stop_distance_sensor_config()
            # red_light_service.stop_led_light()


        if min_threshold and max_threshold:
            print(min_threshold, max_threshold)
            modify_min_max_values_for_hardware_component(HardwareComponent.Distance_sensor, min_threshold, max_threshold)
            return render(request, 'distance_sensor_config.html', {"current_min_threshold": min_threshold, "current_max_threshold": max_threshold})

    current_min_threshold, current_max_threshold = min_max_values_for_hardware_component(HardwareComponent.Distance_sensor)
    return render(request, 'distance_sensor_config.html', {"current_min_threshold": current_min_threshold, "current_max_threshold": current_max_threshold})








def start(request):
    return render(request, "start.html")


detector_service = FatigueDetectorService()
photoresistor_red_led_service = PhotoresistorRedLedService()
distance_sensor_red_led_service = DistanceSensorRedLedService()
def start_detecting(request):
    photoresistor_red_led_service.initialize_photoresistor_red_led()
    photoresistor_red_led_service.start_photoresistor_red_led()
    # print("non-blocking 1")

    distance_sensor_red_led_service.initialize_distance_sensor_red_led()
    distance_sensor_red_led_service.start_distance_sensor_red_led()
    detector_service.start_detector()
    return redirect(start)

def stop_detecting(request):
    photoresistor_red_led_service.stop_photoresistor_red_led()
    distance_sensor_red_led_service.stop_distance_sensor_red_led()
    detector_service.stop_detector()
    return redirect(start)



def detection_conf(request):
    if request.method == "POST":
        data = request.POST

        closed_eyes_seconds_threshold = int(data.get("closed_eyes_seconds_threshold"))
        fps = int(data.get("fps"))
        eye_aspect_ratio_threshold = float(data.get("eye_aspect_ratio_threshold"))
        yawn_threshold = int(data.get("yawn_threshold"))
        database_writes_frequency = int(data.get("database_frequency"))
        params = [
            closed_eyes_seconds_threshold,
            fps, 
            eye_aspect_ratio_threshold,
            yawn_threshold,
            database_writes_frequency
        ]

        detector_service.initialize_detector(params)

        # screen_distance = threading.Thread(target = distance.proper_distance_from_screen)
        # screen_distance.start()

        # proper_room_light = threading.Thread(target = room_light.check_room_light)
        # proper_room_light.start()

        return render(request, "start.html")

    return render(request, "detection_conf.html")        

def shutdown(request):
    if request.method == "POST":
        os.system("sudo shutdown now")
    return render(request, "start.html")



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
        labels = [item['hour'] for item in first[0]['hours']]
        data_yawns_first = [item['yawns'] for item in first[0]['hours']]
        data_sleep_first = [item['sleep'] for item in first[0]['hours']]

        data_yawns_second = [item['yawns'] for item in second[0]['hours']]
        data_sleep_second = [item['sleep'] for item in second[0]['hours']]

        print(f"labels: {labels}")
        context = {
            'message': 'These are your tiredness stats',
            'items': first,
            'chart_data': {
                'labels': labels,
                'datasets': [{
                    'label': 'Yawns',
                    'data': data_yawns_first,
                    'backgroundColor': 'rgba(255, 99, 132, 0.2)',
                    'borderColor': 'rgba(255, 99, 132, 1)',
                },
                    {
                    'label': 'Closed eyes',
                    'data': data_sleep_first,
                    'backgroundColor': 'rgba(55, 199, 132, 0.2)',
                    'borderColor': 'rgba(55, 199, 132, 1)',
                    }
                ]
            }
        }
        summary = utils.lifestyle_summary(first, second)
        #games--------
        first_game_math = database_games.find_data_in_date_range(start_date, end_date, "math")
        second_game_math = database_games.find_data_in_date_range(start_date1, end_date1, "math")
        first_game_memory = database_games.find_data_in_date_range(start_date, end_date, "memory")
        second_game_memory = database_games.find_data_in_date_range(start_date1, end_date1, "memory")
        summary_games = {"first": {"math": round(first_game_math[0]['average_score'], 2), "memory": round(first_game_memory[0]['average_score'],2)},
         "second": {"math": round(second_game_math[0]['average_score'],2), "memory": round(second_game_memory[0]['average_score'],2)}
        }
        #print("summary_games =",summary_games)
        
        # print(data)
        return render(request, "lifestyle_analysis.html", {"data": zip(first, second), "summary": summary, "summary_games": summary_games, "context": context})



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


#-----------------------GAMES------------------------

def games(request):
    return render(request, 'games.html')

def mathgame(request):
    if request.method == 'POST':
        date = request.POST.get('data')
        game = request.POST.get('game')
        score = request.POST.get('score')
        database_games.insert_data(date, game, float(score))
        return redirect(games)
    return render(request, 'math_game.html')

def memorygame(request):
    if request.method == 'POST':
        date = request.POST.get('data')
        game = request.POST.get('game')
        score = request.POST.get('score')
        database_games.insert_data(date, game, float(score))
        return redirect(games)
    return render(request, 'memory_game.html')
