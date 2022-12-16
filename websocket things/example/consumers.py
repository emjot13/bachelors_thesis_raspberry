from channels.generic.websocket import WebsocketConsumer
import json
from time import sleep

class WSConsumer(WebsocketConsumer):
    def connect(self):
        self.accept()
        for i in range(1,10):
            self.send(json.dumps({'message': i}))
            sleep(1)
        