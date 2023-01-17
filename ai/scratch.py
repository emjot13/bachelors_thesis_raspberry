import threading
# import time



# x = 0


# def l():
#     while True:
#         print(x)
#         time.sleep(2)


# t = threading.Thread(target=l)
# t.start()

# while True:
#     x += 1
#     time.sleep(0.2)


var = 5


def printit():
  global var
  threading.Timer(5.0, printit).start()
  print("Hello, World!", var)

printit()

import time

for i in range(1000000):
    time.sleep(2)
    var = i