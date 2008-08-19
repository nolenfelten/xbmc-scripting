############################################################################################################
# TV Data source: au_XMLTV
#
# Notes:
# Provides Australia XML tv data from http://xmltv.locost7.info
#
# CHANGELOG
# 29-07-08 Created
############################################################################################################

from mytvLib import *
from bbbGUILib import *

import xbmcgui, re, time
from string import split, replace, find, rfind, atoi, zfill
from os import path
import zipstream
import gc	# garbage collection

__language__ = sys.modules["__main__"].__language__

# DO NOT CHANGE THIS CODE - IT IS NOW CONFIGURABLE ONLY THROU MYTV CONFIG MENU !!
REGIONS = [
'ACT', 
'Adelaide',					# SA - Adelaide
'Brisbane',						# Queensland - Brisbane
'CentralCoastNSW',
'Darwin',						# NT - Darwin
'EasternVictoria',
'Geelong',
'GoldCoast',
'Hobart'	,					# Tasmania - Hobart
'Melbourne'	,				# Victoria - Melbourne
'Newcastle',
'Perth'	,					# WA - Perth
'RegionalQLD',
'RegionalWA',
'SouthEastSA',
'SouthernNSW',
'WesternVictoria'
]

class ListingData:
	def __init__(self, cache):
		debug("> ListingData.__init__")

		# EG channels URL
		# http://xmltv.locost7.info/Adelaide

		self.cache = cache
		self.name = os.path.splitext(os.path.basename( __file__))[0]	# get filename without path & ext
		self.CHANNELS_FILENAME = os.path.join(cache,"Channels_"+ self.name + ".dat")
		self.BASE_URL = 'http://xmltv.locost7.info/'
		self.isConfigured = False
		self.lastUpdate = 0

		self.rssparser = None
		rssItems = []

		debug("< __init__")

	def getName(self):
		return self.name

	def setup(self):
		debug("ListingData.setup()")
		self.channelURL = self.BASE_URL + '%s/Oztivo%s.zip' % (self.region,self.region)
		self.archiveFN = os.path.join(self.cache, os.path.basename(self.channelURL))
		self.xmlFN = ""
		debug("channelURL=%s\narchiveFN=%s" % ( self.channelURL, self.archiveFN) )

	# download or load if exists, a list of all available channels.
	# return: list [chID, chName]
	def getChannels(self):
		debug("> ListingData.getChannels()")

		channels = []
		if not fileExist(self.CHANNELS_FILENAME):
			# get todays data file and extract channels from that
			dialogProgress.create(self.name, __language__(212))
			self.lastUpdate = self.getLastUpdate()
			if self.lastUpdate:
				self.xmlFN = os.path.join(self.cache, "%s_%s.xml" % (self.region, self.lastUpdate))
				if self.getArchive():
					# not real XML parsing, just use regex, its quicker !
					# chID, chName
					doc = readFile(self.xmlFN)
					matches = findAllRegEx(doc, 'Channel id="(.*?)".*?name>(.*?)<')
					if matches:
						for chID, chName in matches:
							channels.append([chID, chName])
						channels = writeChannelsList(self.CHANNELS_FILENAME, channels)

				self.xmlFN = "" # cancel xml filename will cause it to process it
			dialogProgress.close()
		else:
			channels = readChannelsList(self.CHANNELS_FILENAME)

		debug("< ListingData.getChannels() ch count=%s" % len(channels))
		return channels

	# get current region archive, unpack and rename using todays date
	def getArchive(self):
		debug("> ListingData.getArchive() archiveFN=%s" % self.archiveFN)
		success = False
		dialogProgress.update(0, "Downloading Zip file ...", self.channelURL, self.archiveFN, )
#		if fileExist(self.archiveFN) or fetchURL(self.channelURL, self.archiveFN, isBinary=True):
		if fetchURL(self.channelURL, self.archiveFN, isBinary=True):
			# unpack archive
			success, installed_path = unzip(self.cache, self.archiveFN, False, "Unzipping file...")
			if success:
				try:
					fromFN = os.path.join(self.cache, self.region + '.xml')
					deleteFile(self.xmlFN)
					os.rename(fromFN, self.xmlFN)
					debug("XML renamed to %s" % self.xmlFN)
					success = fileExist(self.xmlFN)
				except:
					handleException("getArchive()")

		if not success:
			messageOK("Download File Failed!", self.channelURL, os.path.basename(self.archiveFN))
			
		debug("< ListingData.getArchive() success=%s" % success)
		return success

	# download the lastUpdate file which contains a date eg. Mon 29/7/08
	def getLastUpdate(self):
		debug("> ListingData.getLastUpdate()")
		lastUpdate = 0
		url = self.BASE_URL + 'lastupdate.txt'
		dialogProgress.update(0, "Fetching LastUpdate date ...", url, " ")
		doc = fetchURL(url)
#		doc = 'Fri 01/08/2008'
		if doc:
			try:
				tm = time.strptime(strip(doc),"%a %d/%m/%Y")						# string to time_tm
				lastUpdate =  int(time.strftime("%Y%m%d", tm))				# tm to formatted str, to int
			except:
				pass

		if not lastUpdate:
			messageOK("LastUpdate Download Failed!","Failed to get Last Update Date.", url)
		debug("< ListingData.getLastUpdate() lastUpdate=%s" % lastUpdate)
		return lastUpdate

	# download channel data, using either dayDelta or dataDate.
	# filename = filename to save downloaded data file as.
	# chID = unique channel ID, used to reference channel in URL.
	# chName = display name of channel
	# dayDelta = day offset from today. ie 0 is today, 1 is tomorrow ...
	# fileDate = use to calc programme start time in secs since epoch.
	# return Channel class or -1 if http fetch error, or None for other
	#
	def getChannel(self, filename, chID, chName, dayDelta, fileDate):
		debug("ListingData.getChannel() dayDelta: %s chID=%s fileDate=%s" % (dayDelta,chID,fileDate))

		# if we have the xml filename then we've prev got latest xml and processed it.
		# no new data will be found from re-processing it, so return empty
		if self.xmlFN and self.lastUpdate and fileExist(self.xmlFN):
			debug("already have xmlFN and lastUpdate and fileexists, dont process again, return empty")
			return []	# empty

		progList = []
		DATE_TIME_SZ = 12
		DATE_SZ = 8
		logFreeMem("getChannel() start")

		# get last online update date
		self.xmlFN = ""
		if not self.lastUpdate:
			self.lastUpdate = self.getLastUpdate()
			if not self.lastUpdate:
				return None	# error

		debug("find a xml file thats newer that LastUpdate date: %s" % self.lastUpdate)
		files = listDir(self.cache, ".xml", "%s_\d+" % self.region)
		files.reverse()
		debug("XML files available=%s" % files)
		for f in files:
			if (int(f[-DATE_SZ:]) >= self.lastUpdate):		# compare YYYYMMDD from end of filename
				self.xmlFN = os.path.join(self.cache, f + '.xml')
				break

		if not self.xmlFN:
			debug("no XML newer than %s, download latest ZIP" % self.lastUpdate)
			self.xmlFN = os.path.join(self.cache, "%s_%s.xml" % (self.region, self.lastUpdate))
			if not self.getArchive():	# DL , unzip , rename to todays xml
				return None	# error

		dialogProgress.update(0, "Parsing XML file:", self.xmlFN )
		xml = readFile(self.xmlFN)
		if not xml:
			debug( "XML file empty!")
			return []
		logFreeMem("getChannel() after read XML")

		# process all channels all dates in XML, so we don't have to do it again
		saveChannels = {}
		CHANNEL_RE = 'programme start="(\d\d\d\d\d\d\d\d\d\d\d\d).*?stop="(\d\d\d\d\d\d\d\d\d\d\d\d).*?channel="(.*?)".*?title>(.*?)</title>(.*?)</programme'
		channelList = readChannelsList(self.CHANNELS_FILENAME)
		matches = findAllRegEx(xml, CHANNEL_RE)
		if matches:
			debug("programme matches=%s" % len(matches) )
			for match in matches:
				try:
	#					print match
					startDateTime = match[0]
					stopDateTime = match[1]
					progChID = match[2]
					title = decodeEntities(match[3])
					otherInfo = decodeEntities(match[4])
					startDate = startDateTime[:DATE_SZ]
					if not startDateTime or not title or not progChID:
						continue

					# look for other data
					desc = searchRegEx(otherInfo, 'desc>(.*?)</')
					subTitle = searchRegEx(otherInfo, 'sub-title>(.*?)</')
					genre = searchRegEx(otherInfo, 'category>(.*?)</')

					# convert to secs
					startTimeSecs = time.mktime(time.strptime(startDateTime,"%Y%m%d%H%M"))
					stopTimeSecs = time.mktime(time.strptime(stopDateTime,"%Y%m%d%H%M"))

					progInfo = {
							TVData.PROG_STARTTIME : float(startTimeSecs),
							TVData.PROG_ENDTIME : float(stopTimeSecs),
							TVData.PROG_TITLE : title,
							TVData.PROG_DESC : desc,
							TVData.PROG_GENRE : genre,
							TVData.PROG_SUBTITLE : subTitle
						}
#					print "%s_%s %s" % (progChID, startDate, progInfo)

					if progChID == chID and startDate == fileDate:
						progList.append(progInfo)
					else:
						chid_date = "%s_%s" % (progChID, startDate)
						if saveChannels.has_key(chid_date):
							saveChannels[chid_date].append(progInfo)
						else:
							saveChannels[chid_date] = [ progInfo ]
				except:
					print "parse error %s" % match

			# save data to flat chID / date file
			dialogProgress.update(0, "Saving files ...")
			for chid_date, progs in saveChannels.items():
				# parse chid_yyymmdd
				progChID = chid_date[:-(DATE_SZ+1)]			# extract chID
				startDate = chid_date[-DATE_SZ:]			# extract yyyymmdd
				fn = os.path.join(self.cache, "%s_%s.dat" % (progChID, startDate))
				saveChannelToFile(progs, fn)

		del channelList
		del saveChannels
		gc.collect()
		# if no progs for chID / date, create empty prog, this will be saved to file
		# whcih will prevent it from attempting to find/parse for it on next start.
		if not progList:
			startTimeSecs = time.mktime(time.strptime(time.strftime(fileDate+"000000"),"%Y%m%d%H%M%S"))
			stopTimeSecs = startTimeSecs + TVTime.DAY_SECS
			progList = [ createEmptyProg(startTimeSecs, stopTimeSecs, True) ]

		logFreeMem("getChannel() end")
		return progList


	#
	# Download url and regex parse it to extract description.
	#
	def getLink(self, link, title):
		return ''

	############################################################################################################
	# load, if not exist ask, then save
	############################################################################################################
	def config(self, reset=False):
		debug("> ListingData.config() reset=%s" % reset)

		CONFIG_SECTION = 'DATASOURCE_' + self.name
		CONFIG_KEY_REGION = 'region'
		self.region = config.action(CONFIG_SECTION, CONFIG_KEY_REGION)

		if reset or not self.region:
			try:
				selectedPos = REGIONS.index(self.region)
			except:
				selectedPos = 0
			selectDialog = DialogSelect()
			selectDialog.setup("Region:", width=300, rows=len(REGIONS), panel=DIALOG_PANEL)
			selectedPos, action = selectDialog.ask(REGIONS, selectedPos)
			if selectedPos >= 0:
				self.region = REGIONS[selectedPos]
				config.action(CONFIG_SECTION, CONFIG_KEY_REGION, self.region, mode=ConfigHelper.MODE_WRITE)
				deleteFile(self.CHANNELS_FILENAME)

		if self.region:
			self.isConfigured = True
			self.setup()
		else:
			self.isConfigured = False
		debug("< ListingData.config() isConfigured=%s" % self.isConfigured)
		return self.isConfigured


#################################################################################################################
def unzip(extract_path, filename, silent=False, msg=""):
	""" unzip an archive, using ChunkingZipFile to write large files as chunks if necessery """
	debug("> unzip() extract_path=%s fn=%s" % (extract_path, filename))
	success = False
	cancelled = False
	installed_path = ""

	zip=zipstream.ChunkingZipFile(filename, 'r')
	namelist = zip.namelist()
	names=zip.namelist()
	infos=zip.infolist()
	max_files = len(namelist)
	debug("max_files=%s" % max_files)

	for file_count, entry in enumerate(namelist):
		info = infos[file_count]

		if not silent:
			percent = int( file_count * 100.0 / max_files )
			root, name = os.path.split(entry)
			dialogProgress.update( percent, msg, root, name)
			if ( dialogProgress.iscanceled() ):
				cancelled = True
				break

		filePath = os.path.join(extract_path, entry)
		if filePath.endswith('/'):
			if not os.path.isdir(filePath):
				os.makedirs(filePath)
		elif (info.file_size + info.compress_size) > 25000000:
			debug( "LARGE FILE: f sz=%s  c sz=%s  reqd sz=%s %s" % (info.file_size, info.compress_size, (info.file_size + info.compress_size), entry ))
			outfile=file(filePath, 'wb')
			fp=zip.readfile(entry)
			fread=fp.read
			ftell=fp.tell
			owrite=outfile.write
			size=info.file_size

			# write out in chunks
			while ftell() < size:
				hunk=fread(4096)
				owrite(hunk)

			outfile.flush()
			outfile.close()
		else:
			file(filePath, 'wb').write(zip.read(entry))

	if not cancelled:
		success = True
		if namelist[0][-1] in ('\\/'):
			namelist[0] = namelist[0][-1]
		installed_path = os.path.join(extract_path, namelist[0])
	
	zip.close()
	del zip
	debug("< unzip() success=%s installed_path=%s" % (success, installed_path))
	return success, installed_path

