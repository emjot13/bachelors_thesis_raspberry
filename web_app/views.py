from django.shortcuts import render
from django.http import HttpResponse

from django.shortcuts import render, redirect

from ai.main import main
import os
import threading




def start(request):
    if request.method == "POST":
        m = threading.Thread(target = main)
        m.start()
    print("here")

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
