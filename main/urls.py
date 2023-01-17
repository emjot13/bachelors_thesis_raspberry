from django.urls import path

from . import views

urlpatterns = [
    path('', views.start, name='start'),
    path("shutdown", views.shutdown, name="shutdown"),
    path("pause", views.pause, name="pause"),
    path('tiredness', views.tiredness, name='tiredness'),
    path('lifestyle', views.lifestyle, name='lifestyle'),
    path('detection_conf', views.detection_conf, name="detection_conf")
]
