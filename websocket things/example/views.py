from django.shortcuts import render

def hello(request):
    return render(request, "hello.html", context={"name": "Websocket"})