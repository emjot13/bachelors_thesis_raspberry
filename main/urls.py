from django.urls import path

from . import views

urlpatterns = [
    path('', views.start, name='start'),
    path("shutdown", views.shutdown, name="shutdown"),
    path("pause", views.pause, name="pause"),
    path('tiredness', views.tiredness, name='tiredness'),
    path('lifestyle', views.lifestyle, name='lifestyle'),
    path('detection_conf', views.detection_conf, name="detection_conf"),
    path('admin', views.admin, name="admin"),
    path('games', views.games, name='games'),
    path('mathgame', views.mathgame, name='mathgame'),
    path('memorygame', views.memorygame, name='memorygame')
]
