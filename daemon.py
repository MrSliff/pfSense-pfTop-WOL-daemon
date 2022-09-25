import os
from daemonize import Daemonize
from time import sleep

host = "192.168.20.3"

sleep_time = 1

pid = "/tmp/pftop_wake.pid"

def main ():
    while True:
        
        #output = os.popen('pftop -b -a -f "dst host "' + host + ' | grep 4:4')
        output = os.popen('pftop -b -a -f "dst host "' + host + ' | grep 2:0').readlines()

        for i in output:
            print (i)

        print (len(output))
        
        sleep(sleep_time)

daemon = Daemonize(app="pftop_wake", pid=pid, action=main)
daemon.start()