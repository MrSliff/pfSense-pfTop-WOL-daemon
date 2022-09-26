import os
from time import sleep
from daemonize import Daemonize
from pythonping import ping
import paho.mqtt.client as mqtt

######## SETTINGS ##################

host = "192.168.20.3" # Which host IP to listen for activity

mqtt_config = ["host": "192.168.20.35", "port": 1883, "keepalive": 60] # Set up mqtt

mqtt_device_topic = [""]
mqtt_subtopic = ["state": "/state", "wakeup": "/wakeup"]

sleep_time = 1 #Set sleep time for daemon in seconds (standard 1s)

#####################################

pid = "/tmp/pftop_wake.pid"

############# MQTT ################

def on_connect(client, userdata, flags, rc):
    print("Connected with result code "+str(rc))

mqtt_client = mqtt.Client()
mqtt_client.on_connect = on_connect
mqtt_client.connect(mqtt_config["host"], mqtt_config["port"],mqtt_config["keepalive"])
mqtt_client.loop_start()

####################################

def main ():
    while True:
        
        if not ping(host,count=2).success():

            if len(os.popen('pftop -b -a -f "dst host "' + host + ' | grep 2:0').readlines()) > 0:

                mqtt_client.publish()
        
        sleep(sleep_time)

daemon = Daemonize(app="pftop_wake", pid=pid, action=main)
daemon.start()