import os

host = "192.168.20.3"

#result = os.popen('pftop -b -a -f "dst host "' + host + ' | grep 4:4')
output = os.popen('pftop -b -a -f "dst host "' + host).read().split()

print (output[1])