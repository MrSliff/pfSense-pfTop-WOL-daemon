from operator import truediv
import os
from time import sleep
from daemonize import Daemonize
from pythonping import ping
import paho.mqtt.client as mqtt
import requests

######## SETTINGS #################

DEBUG = False

#Which services should be used (True/False)
WOL= False #Not implemented yet!
MQTT = False
WEBHOOK = True
CLIENT_ACTIVITY = True

#Which host IP to wakeup
host = "192.168.20.3" 

#Call a webhook on an external client (like a "fake" power button which is pressed)
#The external client is programmed to do whatever you program it to do
if WEBHOOK:
    webhook_url = "http://192.168.50.158/wakeup"

#Publish to MQTT for external clients which listen to it
if MQTT:
    mqtt_config = {"host": "192.168.20.35", "port": 1883, "keepalive": 60} # Set up mqtt
    mqtt_device_topic = "unraid_wakeup" #the main MQTT topic
    mqtt_subtopic = {"state": "/state", "wakeup": "/wakeup"} #The subtopics the MQTT client publishes its messages to

#Ping these clients to wake up the server/host if the clients are available
#It is recommended to set static IP addresses on the clients
if CLIENT_ACTIVITY:
    clients = ["192.168.30.100","192.168.40.10","192.168.40.11"]

#Set sleep time for daemon in seconds
sleep_time = 1 

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
    mqtt_client.connect(mqtt_config["host"],mqtt_config["port"],mqtt_config["keepalive"])
    mqtt_client.loop_start()

####################################

def main ():
    while True:
        
        host_online = ping(host,count=5).success()
        
        if DEBUG:
            print(host_online)
        
        if not host_online:

            if MQTT:
                mqtt_client.publish(mqtt_state_topic, "off")

            if len(os.popen('pftop -b -a -f "dst host ' + host + '" | grep 2:0').readlines()) > 0:

                #if WOL:
                    #do something

                if WEBHOOK:
                    requests.get(webhook_url)

                if MQTT:
                    mqtt_client.publish(mqtt_wakeup_topic, "wakeup")
                
                if DEBUG:
                    print("Waking up by pftop state")
                
                sleep(240)

            if CLIENT_ACTIVITY:
                for client in clients:
                    if ping(client,count=2).success():
                        WAKEUP = True
                        
                if WAKEUP:
                    WAKEUP = False    
                    #if WOL:
                        #do something
                    if WEBHOOK:
                        requests.get(webhook_url)
                    if MQTT: 
                        mqtt_client.publish(mqtt_wakeup_topic, "wakeup")
                        
                    if DEBUG:
                        print("Waking up by client activity")
                    
                    sleep(240)

        else:

            if MQTT:
                mqtt_client.publish(mqtt_state_topic, "on")
            
            print("Host online, sleeping for 240s")
                
            sleep(240)
        
        sleep(sleep_time)

if DEBUG:
    main()
else:
    daemon = Daemonize(app="pftop_wake", pid=pid, action=main)
    daemon.start()