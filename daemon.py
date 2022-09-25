import os

host = "192.168.20.3"

result = os.popen('pftop -b -a -f "dst host "' + host + ' | grep 4:4')


print (result.read())

print("Established connections: " + len(result))

result.close()