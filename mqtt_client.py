#instalar libreria pip install paho-mqtt para el broker publico
from paho.mqtt import client as mqtt_client
import random

#clase que tiene metodos para conectar al broker publico y mandar la informacion que se desee
#esta clase es usado en CamaraArucoTopt.py
class cliente:
    def __init__(self, broker = 'broker.hivemq.com', port = 1883, topic = "huber/#", client_id = f'python-mqtt-{random.randint( 0, 1000)}'):
        self.broker = broker
        self.port = port
        self.topic = topic
        self.client_id = client_id
    def get_broker(self):
        return self.broker
    def get_port(self):
        return self.port
    def get_topic(self):
        return self.topic
    def get_id(self):
        return self.client_id
    def set_topic(self,topic):
        self.topic=topic    
    def set_msg(self, msg):
        self.msg = msg
    def get_msg(self):
        return self.msg
    def connect_client(self, list):
        #conectar
        client = mqtt_client.Client(self.get_id())
        client.connect(self.get_broker(), self.get_port())
        client.loop_start()
       
        #publicar
        for info in list:
            self.set_topic("huber/"+str(info["ID"]))
            prom = info["coordenadas"][0][0]
            prom1 = info["coordenadas"][0][1]
            prom2 = info["coordenadas"][1][0]
            prom3 = info["coordenadas"][1][1]
            prom4 = info["coordenadas"][2][0]
            prom5 = info["coordenadas"][2][1]
            prom6 = info["coordenadas"][3][0]
            prom7 = info["coordenadas"][3][1]
            Angle = info["angulo"]

            client.publish(self.get_topic(), "Coordenada x1: " + str(prom) + " Coordenada y1: " + str(prom1) + 
            " Coordenada x2: " + str(prom2) + " Coordenada y2: " + str(prom3) + " Coordenada x3: " + str(prom4) + 
            " Coordenada y3: " + str(prom5) + " Coordenada x4: " + str(prom6) + " Coordenada y4: " + str(prom7) + 
            " Angulo: " + str(Angle) + " ID: " + str(info["ID"]) )
        
        client.loop_stop()
