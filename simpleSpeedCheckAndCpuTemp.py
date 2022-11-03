import requests
from datetime import datetime
import hashlib
import rrdtool
import time

#Variables to store useful information
dloadFileUrl = "http://mattmole.co.uk/LXF297/speedTest.10M"
dloadFileCheckSum = "f1c9645dbc14efddc7d8a322685f26eb"
rrdFilePath="target.rrd"

#Download the file and work out how long it took, to calculate the speed
dt1 = datetime.now()
response=None
response = requests.get(dloadFileUrl)

if response.status_code >= 400:
    print("HTTP status error")

dt2 = datetime.now()
m = hashlib.md5()
data = response.content
m.update(data)

sizeMB = len(data)/(1024*1024)
time = (dt2-dt1).total_seconds()

#Check to see if the MD5 sum matches. If not, then return an error
if m.hexdigest() != dloadFileCheckSum:
    print("MD5 error")

#Calculate the speed if the time is greater than 0s
speed=0
if time >0:
    speed = sizeMB / time
    print ("%f MB/s %ibytes %iMb %fus %s"%(speed,len(data),sizeMB, time, m.hexdigest()))
    print (dt2-dt1)
    speed = len(data)/time


# Read the temperature of the CPU and then write it to the RRD database
try:
    temp = open("/sys/class/thermal/thermal_zone0/temp","r")
    temp = float(temp.read().strip())/1000
    print (temp)
except: 
    temp = "U"

if time == 0 and temp == "U":
    output = rrdtool.update(rrdFilePath, 'N:%s:%s' %("U",temp))
else:
    output = rrdtool.update(rrdFilePath, 'N:%s:%s' %(speed,temp))