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
    path('memorygame', views.memorygame, name='memorygame')
]
