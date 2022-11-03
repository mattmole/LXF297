import requests
from datetime import datetime
import hashlib
import configparser
import rrdtool
import time

class writeRRDTool:
	def __init__(self, rrdFile, dloadSpeed, cpuTemp):
		self.rrdFile = rrdFile
		self.dloadSpeed = dloadSpeed
		self.cpuTemp = cpuTemp

		self.writeRRDVal()
	def writeRRDVal(self):
		if self.dloadSpeed != 'NaN' and self.cpuTemp != 'NaN':
			rrdtool.update(self.rrdFile, 'N:%f:%f' %(self.dloadSpeed, self.cpuTemp))
		elif self.dloadSpeed == 'Nan' and self.cpuTemp != 'NaN':
			rrdtool.update(self.rrdFile, 'N:%f:%s' %(self.dloadSpeed, 'U'))
		elif self.dloadSpeed != 'Nan' and self.cpuTemp == 'NaN':
			rrdtool.update(self.rrdFile, 'N:%s:%f' %('U', self.cpuTemp))
		else:
			rrdtool.update(self.rrdFile, 'N:%s:%s' %('U', 'U'))
			
class tempCheck:
	def __init__(self, cpuTempFile = ""):
		self.cpuTempFile = cpuTempFile
		self.readCpuTemp()

	# Read the temperature of the CPU and then write it to the RRD database
	def readCpuTemp(self):
		
		cpuTemp = open("/sys/class/thermal/thermal_zone0/temp","r")
		try:
			cpuTemp = float(cpuTemp.read().strip())/1000
			return [0, cpuTemp]
		except:
			return [-1, "NaN"]

class readConfig:
	def __init__(self, configFile= "speedCheck.conf"):
		self.configFile = configFile
		self.config=None
		self.readConfig()
		
	def readConfig(self):
		config = configparser.ConfigParser()
		try:
			config.read(self.configFile)
		except:
			print("File cannot be found")
		else:
			self.config = config
		return config

class speedCheck:
	def __init__(self,config = None):
		self.config=config
		self.result = None
		
	def testSpeed(self,fileSize):
		self.result = None
		fileUrl = None
		fileMD5 = None		
		
		if fileSize=="10M":
			try:
				fileURL = self.config.get("Files","10MFile")
				fileMD5 = self.config.get("Files","10MCSum")
			except:
				print("Config file is not defined")
				exit
				
		dt1 = datetime.now()
		response=None
		try:
			response = requests.get(fileURL)
			
			if response.status_code >= 400:
				print("HTTP status error")
				return [-1, "HTTP status error"]
		except requests.exceptions.ConnectionError:
			print("Connection Error")
			return [-1,"Connection Error"]
		except requests.exceptions.HTTPError:
			print("HTTP Error")
			return [-1, "HTTP Error"]
		except requests.exceptions.Timeout:
			print("Timeout error")
			return [-1,"Timeout error"]

		else:	
			data = ""
			dt2 = datetime.now()
			m = hashlib.md5()
			data = response.content
			m.update(data)

			sizeMB = len(data)/(1024*1024)
			time = (dt2-dt1).total_seconds()
			
			#Check to see if the MD5 sum matches. If not, then return an error
			if m.hexdigest() != fileMD5:
				print("MD5 error")
				return [-1, "MD5 error"]
			
			#Calculate the speed if the time is greater than 0s
			speed=0
			if time >0:
				speed = sizeMB / time
				print ("%f MB/s %ibytes %iMb %fs %s"%(speed,len(data),sizeMB, time, m.hexdigest()))
				print (dt2-dt1)
				speedBS = len(data)/time
				self.result=speedBS
				return [0,speedBS]
			else:
				return [-1,"NaN"]
		
	def loopResult(self,delay):
		while 1:
			self.testSpeed("10M")
			self.writeResult()
			time.sleep(delay)


#For one off
oneShot = False
if oneShot:
	configReader = readConfig("speedCheckSample.conf")
	dloadSpeed = speedCheck(configReader.config)
	cpuTemp = tempCheck()

	speedResult = dloadSpeed.testSpeed("10M")
	tempResult = cpuTemp.readCpuTemp()
	writeResult = writeRRDTool(configReader.config.get("Config","rrd"),speedResult[1],tempResult[1])

#Or, for looped
looped = True
while looped:
	configReader = readConfig("speedCheckSample.conf")
	dloadSpeed = speedCheck(configReader.config)
	cpuTemp = tempCheck()

	speedResult = dloadSpeed.testSpeed("10M")
	tempResult = cpuTemp.readCpuTemp()
	writeResult = writeRRDTool(configReader.config.get("Config","rrd"),speedResult[1],tempResult[1])
	time.sleep(30)