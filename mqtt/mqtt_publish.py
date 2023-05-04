import paho.mqtt.client as mqtt 
from random import randrange, uniform
import time

mqttBroker ="localhost" 

client = mqtt.Client("raspberry-ha")
client.connect(mqttBroker) 

while 1:
    randNumber = uniform(20.0, 21.0)
    client.publish("TEMPERATURE", randNumber)
    print("Just published " + str(randNumber) + " to topic TEMPERATURE")
    time.sleep(1)