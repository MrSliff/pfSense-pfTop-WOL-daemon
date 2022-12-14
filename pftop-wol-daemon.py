from operator import truediv
import os
from time import sleep
from daemonize import Daemonize
import paho.mqtt.client as mqtt
import requests
import logging

######## SETTINGS #################

DEBUG = True
LOGGING = True

#Which services should be used (True/False)
WOL= False #Not implemented yet!
MQTT = False
WEBHOOK = True
CLIENT_ACTIVITY = True

#Which host IP to wakeup
host_wakeup = "192.168.20.3" 

#Which host IPs to monitor for activity to wakeup host
host_activity = ["192.168.20.3",
                 "192.168.20.16",
                 "192.168.20.18",
                 "192.168.20.21",
                 "192.168.20.22",
                 "192.168.20.50",
                 "192.168.20.51",
                 "192.168.20.60",
                 "192.168.20.174",
                 "10.100.0.10",
                 "10.100.0.11",
                 "10.100.0.12"]

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

if LOGGING:
    Log_Format = "%(levelname)s %(asctime)s - %(message)s"

    logging.basicConfig(filename = "/custom/pfSense-pfTop-WOL-daemon/logfile.log",
                    filemode = "w",
                    format = Log_Format, 
                    level = logging.INFO)

    logger = logging.getLogger()

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

    WAKEUP = False
    PFTOP_ACTIVE = False

    while True:
        
        HOST_UP = True if os.system("ping -c 1 " + host_wakeup.strip(";")) == 0 else False

        if not HOST_UP:

            if DEBUG:
                print("Host offline, checking client activity")

            if MQTT:
                mqtt_client.publish(mqtt_state_topic, "off")
                
            for host in host_activity:
                if len(os.popen('pftop -b -a -f "dst host ' + host + '" | grep 2:0').readlines()) > 0:
                    PFTOP_ACTIVE = True
                    if DEBUG:
                        #print(os.popen('pftop -b -a -f "dst host ' + host + '" | grep 2:0').readlines())
                        print("Activity on "+ host + ", waking up host")
                    if LOGGING:
                        logger.info("Activity on "+ host + ", waking up host")
                    break
            
            if PFTOP_ACTIVE:
                
                PFTOP_ACTIVE = False                   
                #if WOL:
                    #do something                
                if WEBHOOK:
                    requests.get(webhook_url)
                if MQTT:
                    mqtt_client.publish(mqtt_wakeup_topic, "wakeup")                
                if DEBUG:
                    print("Waking up by pftop state")
                while not HOST_UP:
                    HOST_UP = True if os.system("ping -c 1 " + host_wakeup.strip(";")) == 0 else False

            elif CLIENT_ACTIVITY:
                for client in clients:
                    if DEBUG:
                        print("Pinging Client " + client)
                    CLIENT_UP  = True if os.system("ping -c 1 " + client.strip(";")) == 0 else False
                    if CLIENT_UP:
                        WAKEUP = True
                        if DEBUG:
                            print("Client "+ client +" is online, waking up host")
                        if LOGGING:
                            logger.info("Client "+ client +" is online, waking up host")
                        break
                        
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
                
                    while not HOST_UP:
                        HOST_UP = True if os.system("ping -c 1 " + host_wakeup.strip(";")) == 0 else False                    

        else:

            if MQTT:
                mqtt_client.publish(mqtt_state_topic, "online")
            
            while HOST_UP:
                HOST_UP = True if os.system("ping -c 1 " + host_wakeup.strip(";")) == 0 else False
                if DEBUG:
                    print("Host is online, doing nothing")
                if LOGGING:
                    logger.info("Host is online, doing nothing")
                sleep(1)
                
            print("Host just went offline, sleeping for 240 seconds")
            
            sleep(240)
        
        sleep(sleep_time)

if DEBUG:
    main()
else:
    daemon = Daemonize(app="pftop_wake", pid=pid, action=main)
    daemon.start()