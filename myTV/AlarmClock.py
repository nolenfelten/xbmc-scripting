# AlarmClock.py
# AlarmClock.py
#
# Functions to Save, Load, Set and Cancel XBMC Alarm Clocks.
#
# Existing Alarms can be setup at XBMC startup by putting the following line in autoexec.py
#
# xbmc.executescript('q:\\scripts\\mytv\\AlarmClock.py')

__title__ = "AlarmClock"
__author__ = 'BigBellyBilly [BigBellyBilly@gmail.com]'
__date__ = '14-02-2008'

import sys,os.path
import xbmc, xbmcgui, time

try:
	__scriptname__ = sys.modules[ "__main__" ].__scriptname__
	DIR_CACHE = sys.modules[ "__main__" ].DIR_CACHE
	xbmc.output("Imported From: " + __scriptname__ + " title: " + __title__ + " Date: " + __date__)
	__language__ = sys.modules[ "__main__" ].__language__
except:
	__scriptname__ = "myTV"
	xbmc.output("Loading: " + __title__ + " Date: " + __date__)
	DIR_HOME = os.getcwd().replace( ";", "" )
	DIR_RESOURCES = os.path.join( DIR_HOME , "resources" )
	DIR_RESOURCES_LIB = os.path.join( DIR_RESOURCES , "lib" )
	DIR_USERDATA = os.path.join( "T:\\script_data", __scriptname__ )
	DIR_CACHE = os.path.join( DIR_USERDATA, "cache" )
	sys.path.insert(0, DIR_RESOURCES_LIB)
	try:
		# 'resources' now auto appended onto path
		__language__ = xbmc.Language( DIR_HOME ).getLocalizedString
		if not __language__( 0 ): raise
	except:
		print "AlarmClock() failed to get builtin xbmc.Language() or strings not parsed from path - upgrade XBMC"


class AlarmClock:
	def __init__(self):

		self.FILE_PREFIX = 'alarm_'
		self.alarms = {}

	##############################################################################################################
	def setSavedAlarms(self):
		self.loadAlarms()
		if self.alarms:
			self.setAlarms()

	##############################################################################################################
	# load alarmclock files into dict using alarmName as key
	def loadAlarms(self):
		xbmc.output("> loadAlarms()")
		self.alarms = {}
		alarmsList = []
		currentTime = time.mktime(time.localtime())

		for f in os.listdir(DIR_CACHE):
			if f.startswith(self.FILE_PREFIX):
				try:
					doc = file(os.path.join(DIR_CACHE, f)).read()
					startTime, alarmDets = doc.split("~")
					minsDelta = int((int(startTime) - currentTime) /60)
					if minsDelta > 0:
						alarmsList.append([startTime, alarmDets])
				except:
					pass

		# sort to startTime desc
		if alarmsList:
			alarmsList.sort()
			alarmsList.reverse()
			for alarm in alarmsList:
				self.alarms[alarm[0]] = alarm[1]

		xbmc.output("< loadAlarms() alarm count=" + str(len(self.alarms)))
		return self.alarms


	##############################################################################################################
	def setAlarms(self):
		xbmc.output("> setAlarms()")
		currentTime = time.mktime(time.localtime())
		for startTime, alarmDets in self.alarms.items():
			minsDelta = int((int(startTime) - currentTime) /60)
			if minsDelta > 0:
				self.setAlarm(startTime, alarmDets, minsDelta)
		xbmc.output("< setAlarms()")


	##############################################################################################################
	def setAlarm(self, startTime, alarmDets, minsDelta):
		xbmc.output("> setAlarm() startTime="+str(startTime) + " minsDelta=" + str(minsDelta))
		success = False
		try:
			# set builtin cmd
			execCMD = 'XBMC.Notification("myTV Alarm",'+alarmDets+'")'
			xbmc.executebuiltin('XBMC.AlarmClock('+str(startTime)+','+execCMD+','+str(minsDelta)+')')
			self.alarms[startTime] = alarmDets
			success = True
		except: pass
		xbmc.output("< setAlarm() success="+str(success))
		return success

	#################################################################################################################
	# Set an XBMC AlarmClock - uses prog starttime secs as alarm name
	# save to a file in cache. this will allow the exit routine to housekeep old files.
	#################################################################################################################
	def saveAlarm(self, startTime, title , chName):
		xbmc.output("> saveAlarm() startTime="+str(startTime))
		success = False

		fileDate = time.strftime("%Y%m%d",time.localtime(startTime))
		alarmName = str(startTime)
		fn = os.path.join(DIR_CACHE, self.FILE_PREFIX+fileDate+'.' + alarmName)
		currentTime = time.mktime(time.localtime())
		minsDelta = int((startTime - currentTime) /60)
		displayDate = time.strftime("%d/%m/%y %H:%M %p" ,time.localtime(startTime))
		xbmc.log("fn=" + fn)

		if minsDelta < 1:
			xbmcgui.Dialog().ok(__language__(516), __language__(125))
		elif os.path.isfile(fn) and os.path.getsize(fn) > 0:
			xbmcgui.Dialog().ok(__language__(516),  __language__(126), title, displayDate + ", " + chName)
		elif xbmcgui.Dialog().yesno(__language__(516) + '?', title, displayDate + ", " + chName):
			try:
				# set builtin cmd
				alarmDets = title + ", " + displayDate + ", " + chName
				self.setAlarm(alarmName, alarmDets, minsDelta)
				# save to alarm file
				fp = open(fn,"w")
				fp.write(alarmName + '~' + alarmDets)
				fp.close()
				success = True
			except:
				xbmcgui.Dialog().ok(__language__(516), "Failed to save Alarm to file:", fn)

		xbmc.output("< saveAlarm() success="+str(success))
		return success

	##############################################################################################################
	def cancelAlarm(self, index):
		xbmc.output("> cancelAlarm() index="+str(index))
		success = False
		try:
			alarmName = self.alarms.keys()[index]
			xbmc.executebuiltin('XBMC.CancelAlarm('+ alarmName + ')')
			del self.alarms[alarmName]
			fileDate = time.strftime("%Y%m%d", time.localtime(int(alarmName)))
			filename = os.path.join(DIR_CACHE, self.FILE_PREFIX + fileDate + '.' + alarmName)
			os.remove(filename)
			success = True
		except:
			messageOK(__language__(517), __language__(122))
		xbmc.output("< cancelAlarm() success="+str(success))
		return success

########################################################################################################
# Determine if standalone startup or imported
########################################################################################################
if __name__ == '__main__':
	alarmClock = AlarmClock().setSavedAlarms()
	del alarmClock
