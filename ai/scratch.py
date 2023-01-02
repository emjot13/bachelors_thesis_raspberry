import threading
import time



x = 0


def l():
    while True:
        print(x)
        time.sleep(2)


t = threading.Thread(target=l)
t.start()

while True:
    x += 1
    time.sleep(0.2)