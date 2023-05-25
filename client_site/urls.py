from django.urls import path

from . import views

urlpatterns = [
    path('', views.start, name='start'),
    path("shutdown", views.shutdown, name="shutdown"),
    path("stop_detecting", views.stop_detecting, name="stop_detecting"),
    path("start_detecting", views.start_detecting, name="start_detecting"),
    path('tiredness', views.tiredness, name='tiredness'),
    path('lifestyle', views.lifestyle, name='lifestyle'),
    path('detection_conf', views.detection_conf, name="detection_conf"),
    path('games', views.games, name='games'),
    path('mathgame', views.mathgame, name='mathgame'),
    path('memorygame', views.memorygame, name='memorygame'),
    path('photoresistor_stream/', views.photoresistor_stream, name='photoresistor_stream'),
    path('photoresistor_config/', views.photoresistor_config, name='photoresistor_config'),
    path('distance_sensor_stream/', views.distance_sensor_stream, name='distance_sensor_stream'),
    path('distance_sensor_config/', views.distance_sensor_config, name='distance_sensor_config'),
    # path('mqtt/<topic>/', views.mqtt_sse, name='mqtt_sse'),
    # path('mqtt-data/', views.mqtt_subscribe, name='mqtt_data')

]
