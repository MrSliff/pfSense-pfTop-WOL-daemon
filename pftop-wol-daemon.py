import os
from time import sleep
from daemonize import Daemonize
from pythonping import ping
import paho.mqtt.client as mqtt
import requests

######## SETTINGS #################

WOL= False
MQTT = False
WEBHOOK = True

host = "192.168.20.3" # Which host IP to listen for activity

if WEBHOOK:
    webhook_url = "http://192.168.50.158/wakeup"

if MQTT:
    mqtt_config = {"host": "192.168.20.35", "port": 1883, "keepalive": 60} # Set up mqtt
    
    mqtt_device_topic = "unraid_wakeup"
    mqtt_subtopic = {"state": "/state", "wakeup": "/wakeup"}

sleep_time = 1 #Set sleep time for daemon in seconds (standard 1s)

#####################################

pid = "/tmp/pftop_wake.pid"

############# MQTT ################

if MQTT:
    def on_connect(client, userdata, flags, rc):
        print("Connected with result code "+str(rc))
    
    mqtt_state_topic = mqtt_device_topic + mqtt_subtopic["state"]
    mqtt_wakeup_topic = mqtt_device_topic + mqtt_subtopic["wakeup"]

    mqtt_client = mqtt.Client()
    mqtt_client.on_connect = on_connect
    mqtt_client.connect(mqtt_config["host"], mqtt_config["port"],mqtt_config["keepalive"])
    mqtt_client.loop_start()

####################################

def main ():
    while True:
        
        if not ping(host,count=2).success():

            if MQTT:
                mqtt_client.publish(mqtt_state_topic, "off")

            if len(os.popen('pftop -b -a -f "dst host "' + host + ' | grep 2:0').readlines()) > 0:

                if WEBHOOK:
                    requests.get(webhook_url)

                if MQTT:
                    mqtt_client.publish(mqtt_wakeup_topic, "wakeup")

        else:

            if MQTT:
                mqtt_client.publish(mqtt_state_topic, "on")
        
        sleep(sleep_time)

daemon = Daemonize(app="pftop_wake", pid=pid, action=main)
daemon.start()