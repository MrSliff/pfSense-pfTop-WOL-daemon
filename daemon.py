import os

host = "192.168.20.3"

result = os.popen('pftop -b -a -f "dst host "' + host)

print(result)