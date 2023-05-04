import paho.mqtt.client as mqtt 


class Mqtt_Client:
    def __init__(self, name):
        mqtt_broker ="localhost" 
        self.mqtt_client = mqtt.Client(name)
        self.mqtt_client.connect(mqtt_broker)
        return self.mqtt_client


# mqtt_broker ="localhost" 

# mqtt_client = mqtt.Client("Temperature_Inside")
# mqtt_client.connect(mqtt_broker) 