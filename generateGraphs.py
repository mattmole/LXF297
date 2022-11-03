#This script can be used to generate plots based on different RRAs, within a database file. Not all RRAs were initialised within the article, so some graphs may not work as expected.
import rrdtool
import configparser

config=None
config = configparser.ConfigParser()
try:
	config.read("speedCheck.conf")
except:
	print("File cannot be found")
else:
	config = config

graphName="speed"
graphExt="png"
graphTitle="Download speed from GitHub pages"
graphWidth=1000
graphHeight=600

try:
	graphName=config.get("Graph","graphName")
except:
	pass

try:
	graphExt=config.get("Graph","graphExt")
except:
	pass
	
try:
	graphTitle=config.get("Graph","graphTitle")
except:
	pass
	
try:
	graphWidth=config.get("Graph","graphWidth")
except:
	pass
	
try:
	graphHeight=config.get("Graph","graphHeight")
except:
	pass

for sched in ['daily' , 'weekly', 'monthly','yearly']:

	if sched == 'weekly':
		period = 'w'
	elif sched == 'daily':
		period = 'd'
	elif sched == 'monthly':
		period = 'm'
	elif sched == 'yearly':
		period = 'y'

	ret = rrdtool.graph( "%s-%s.%s"%(graphName,sched,graphExt), "--start", "-1%s"%period, "--vertical-label=Num",
	"-w %s"%graphWidth,
	"-h %s"%graphHeight,
	"-t %s - %s"%(graphTitle,sched),
	"-v MB/s",
	"--slope-mode",
	"DEF:m1_num=target.rrd:speed:AVERAGE",
	"DEF:m1_max=target.rrd:speed:MAX",
	"DEF:m1_min=target.rrd:speed:MIN",
	"CDEF:maxMB=m1_max,1048576,/",
	"CDEF:minMB=m1_min,1048576,/",
	"LINE3:m1_num#0000FF:Avg",
	"GPRINT:maxMB:MAX:Max %6.2lf MB/s",
	"GPRINT:minMB:MIN:Min %6.2lf MB/s")