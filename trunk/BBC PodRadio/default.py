# A script to play BBC Podcasts (WindowXML version)
#
# NOTES:
# - See readme.txt for indepth instructions/information.
#
# This was developed using xbmc_pc.exe
#
# Written By BigBellyBilly
# bigbellybilly AT gmail DOT com	- bugs, comments, ideas ...
#
# THANKS:
# To everyone who's ever helped in anyway, or if I've used code from your own scripts, MUCH APPRECIATED!
#
# CHANGELOG: see changelog.txt
#

import xbmc, xbmcgui
import sys, os, os.path
from string import replace,split,find,capwords

# Script constants
__scriptname__ = "BBC PodRadio"
__author__ = 'BigBellyBilly [BigBellyBilly@gmail.com]'
__url__ = "http://code.google.com/p/xbmc-scripting/"
__svn_url__ = "http://xbmc-scripting.googlecode.com/svn/trunk/BBC%20PodRadio"
__date__ = '13-01-2008'
__version__ = "2.2"
xbmc.output( __scriptname__ + " Version: " + __version__  + " Date: " + __date__)

# Shared resources
DIR_HOME = os.getcwd().replace( ";", "" )
DIR_RESOURCES = os.path.join( DIR_HOME , "resources" )
DIR_RESOURCES_LIB = os.path.join( DIR_RESOURCES , "lib" )
DIR_USERDATA = os.path.join( "T:\\script_data", __scriptname__ )
sys.path.insert(0, DIR_RESOURCES_LIB)

# Custom libs
import language
__language__ = language.Language().localized

from bbbLib import *
import update

# dialog object for the whole app
dialogProgress = xbmcgui.DialogProgress()

try: Emulating = xbmcgui.Emulating
except: Emulating = False

#################################################################################################################
# MAIN
#################################################################################################################
class BBCPodRadio(xbmcgui.WindowXML):
	# control id's
	CLBL_DATASOURCE = 21
	CLBL_VERSION = 22
	CLBL_TITLE = 23
	CLBL_DESC = 24
	CFLBL_NOWPLAYING = 25
	CLST_SOURCE = 60
	CLST_DIR = 70
	CLST_CAT = 80
	CLST_STREAM = 90
	CGROUP_LIST_CAT = 2200
	CGROUP_LIST_STREAM = 3000


	def __init__( self, *args, **kwargs ):
		debug("> BBCPodRadio().__init__")
		try:
			if Emulating: xbmcgui.Window.__init__(self)
		except: pass

		self.startup = True
		self.controlID = 0

		self.IMG_PODCAST = "bpr-podcast.png"
		self.IMG_RADIO = "bpr-radio.png"
	
		self.URL_HOME = 'http://www.bbc.co.uk/'
		self.URL_POD_HOME = self.URL_HOME + 'radio/podcasts/directory/'
		self.URL_RADIO_HOME = self.URL_HOME + 'radio/aod/index_noframes.shtml'		
		self.URL_RADIO_LIVE_HOME = self.URL_HOME + 'radio/aod/networks/$STATION/live.shtml'		

		self.SOURCE_POD = __language__(200)
		self.SOURCE_RADIO = __language__(201)
		self.SOURCE_RADIO_LIVE = __language__(202)
		self.source = ""

		# PODCATS DIRECTORY LIST OPTIONS
		self.POD_DIR_OPT_BROWSE_RADIO = __language__(203)
		self.POD_DIR_OPT_BROWSE_GENRE = __language__(204)
		self.POD_DIR_OPT_BROWSE_AZ = __language__(205)

		self.directoriesDict = {}
		self.directoriesDict[self.SOURCE_POD] = {self.POD_DIR_OPT_BROWSE_RADIO : self.URL_POD_HOME + 'station/',
												self.POD_DIR_OPT_BROWSE_GENRE : self.URL_POD_HOME + 'genre/',
												self.POD_DIR_OPT_BROWSE_AZ : self.URL_POD_HOME + 'title/'}

		# RADIO DIRECTORY LIST OPTIONS
		self.RADIO_DIR_OPT_BROWSE_RADIO = __language__(206)
		self.RADIO_DIR_OPT_BROWSE_MUSIC = __language__(207)
		self.RADIO_DIR_OPT_BROWSE_SPEECH = __language__(208)

		self.directoriesDict[self.SOURCE_RADIO] = {self.RADIO_DIR_OPT_BROWSE_RADIO : self.URL_RADIO_HOME,
												self.RADIO_DIR_OPT_BROWSE_MUSIC : self.URL_RADIO_HOME,
												self.RADIO_DIR_OPT_BROWSE_SPEECH : self.URL_RADIO_HOME}


		# RADIO LIVE DIRECTORY LIST OPTIONS
		self.RADIO_LIVE_DIR_OPT_BROWSE_RADIO = __language__(209)

		self.directoriesDict[self.SOURCE_RADIO_LIVE] = {self.RADIO_LIVE_DIR_OPT_BROWSE_RADIO : self.URL_RADIO_HOME}


		# dict to hold a dict for each category within a directory
		# additional categories added as each directory selected and downloaded
		# to be populated as found
		self.categoriesDict = { self.SOURCE_POD : {},
								self.SOURCE_RADIO : {},
								self.SOURCE_RADIO_LIVE: {}
							}
		
		# PODCAST REC
		self.STREAM_DETAILS_TITLE = 0
		self.STREAM_DETAILS_STREAMURL = 1
		self.STREAM_DETAILS_IMGURL = 2
		self.STREAM_DETAILS_IMG_FILENAME = 3
		self.STREAM_DETAILS_STATION = 4
		self.STREAM_DETAILS_SHORTDESC = 5
		self.STREAM_DETAILS_DUR = 6
		self.STREAM_DETAILS_DATE = 7
		self.STREAM_DETAILS_LONGDESC = 8

		self.rssparser = RSSParser2()

		debug("< __init__")


	#################################################################################################################
	def onInit( self ):
		debug("> onInit() startup="+str(self.startup))
		if self.startup:
			xbmcgui.lock()
			self.startup = False
			self.getControl( self.CLBL_VERSION ).setLabel( "v" + __version__ )
			self.getControl( self.CLST_SOURCE ).addItem( xbmcgui.ListItem( self.SOURCE_POD, "", self.IMG_PODCAST, self.IMG_PODCAST) )
			self.getControl( self.CLST_SOURCE ).addItem( xbmcgui.ListItem( self.SOURCE_RADIO, "", self.IMG_RADIO, self.IMG_RADIO) )
			self.getControl( self.CLST_SOURCE ).addItem( xbmcgui.ListItem( self.SOURCE_RADIO_LIVE, "", self.IMG_RADIO, self.IMG_RADIO) )
			self.getControl( self.CLST_SOURCE ).setVisible( True )

			self.clearAll()
			xbmcgui.unlock()

		debug("< onInit()")


	#################################################################################################################
	def onAction(self, action):
		buttonCode =  action.getButtonCode()
		actionID   =  action.getId()
		if not actionID:
			return
#		debug( "onAction(): actionID=%i buttonCode=%i controlID %i" % (actionID,buttonCode,self.controlID) )

		if ( buttonCode in EXIT_SCRIPT or actionID in EXIT_SCRIPT):
			self.close()
		elif action == 0:
			return
		elif (action in MOVEMENT_UP or action in MOVEMENT_DOWN):
			debug("MOVEMENT_UP or MOVEMENT_DOWN")
			if self.controlID == self.CLST_STREAM and self.streamDetails:
				idx = self.getControl( self.CLST_STREAM ).getSelectedPosition()
				desc = self.streamDetails[idx][self.STREAM_DETAILS_SHORTDESC]
				self.getControl( self.CLBL_DESC ).setLabel(desc)
		elif (action in MOVEMENT_LEFT or action in MOVEMENT_RIGHT):
			debug("MOVEMENT_LEFT or MOVEMENT_RIGHT")
			self.isFocusNavLists = ( not self.controlID in (self.CLST_STREAM, self.CGROUP_LIST_STREAM) )
		elif action == ACTION_PARENT_DIR:		# B button
			debug("ACTION_PARENT_DIR")
			xbmc.Player().stop()
			self.showNowPlaying(True)			# clears
		elif action in (ACTION_Y_BUTTON, ACTION_X_BUTTON):
			debug("ACTION_Y_BUTTON or ACTION_X_BUTTON")
			if self.streamDetails:				# only toggle if streams available
				self.toggleNavListFocus()

	#################################################################################################################
	def onClick(self, controlID):
#		debug( "onclick(): control %i" % controlID )

		if (controlID == self.CLST_SOURCE):
			debug("CLST_SOURCE")
			self.isFocusNavLists = True
			self.source = self.getControl( self.CLST_SOURCE ).getSelectedItem().getLabel()
			self.clearAll()
			self.showDirectory()
			self.getControl( self.CLBL_TITLE ).setLabel(self.source)
			if self.source == self.SOURCE_RADIO_LIVE:
				self.onClick(self.CLST_DIR)

		elif (controlID == self.CLST_DIR):
			debug("CLST_DIR")
			self.isFocusNavLists = True
			self.clearCategory()
			directory = self.getControl( self.CLST_DIR ).getSelectedItem().getLabel()
			self.getControl( self.CLBL_TITLE ).setLabel(self.source + " > " + directory)
			if self.getCategories(directory):
				self.showCategory(directory)

		elif (controlID == self.CLST_CAT):
			debug("CLST_CAT")
			self.isFocusNavLists = True
			self.clearStream()
			directory = self.getControl( self.CLST_DIR ).getSelectedItem().getLabel()
			category = self.getControl( self.CLST_CAT ).getSelectedItem().getLabel()
			self.getControl( self.CLBL_TITLE).setLabel(self.source + " > " + directory + " > " + category)
			if self.source == self.SOURCE_POD:
				success = self.getStreamsPodcast(directory, category)
			elif self.source == self.SOURCE_RADIO:
				success = self.getStreamsRadio(directory, category)
			else:
				success = self.getStreamsRadioLive(directory, category)
			if success:
				self.showStreams()
				# force play stream now if live radio
				if self.source == self.SOURCE_RADIO_LIVE:
					self.onClick(self.CLST_STREAM)

		elif (controlID == self.CLST_STREAM):
			debug("CLST_STREAM")
			self.isFocusNavLists = False
			self.showNowPlaying(True)	# clear
			idx = self.getControl( self.CLST_STREAM ).getSelectedPosition()
			title = self.streamDetails[idx][self.STREAM_DETAILS_TITLE]
			self.getControl( self.CLBL_TITLE).setLabel(title)
			self.getControl( self.CLBL_DESC).setLabel("Downloading stream,  please wait ...")
			if self.playStream(idx):
				if self.source == self.SOURCE_RADIO:
					# redraw stream list as we've got more info
					self.getControl( self.CLST_STREAM).reset()
					self.getIcons(idx)
					self.showStreams()
					self.getControl( self.CLST_STREAM).selectItem(idx)
				self.getControl( self.CLBL_DESC).setLabel(self.streamDetails[idx][self.STREAM_DETAILS_SHORTDESC])
				self.showNowPlaying()
			else:
				self.getControl(self.CLBL_DESC).setLabel("")


	###################################################################################################################
	def onFocus(self, controlID):
		debug("onFocus(): controlID %i" % controlID)
		self.controlID = controlID

	###################################################################################################################
	def exit(self):
		debug ("exit()")
		self.close()

	####################################################################################################################
	def clearAll(self):
		debug("clearAll()")
		xbmcgui.lock()

		self.clearDirectory()

		self.getControl( self.CLBL_DATASOURCE ).setLabel(self.source)
		if not self.source:
			self.getControl( self.CLBL_TITLE ).setLabel(__language__(100))

		self.isFocusNavLists = True
		self.streamDetails = []
		if not xbmc.Player().isPlaying():
			self.getControl(self.CFLBL_NOWPLAYING).reset()

		self.setFocus(self.getControl(self.CLST_SOURCE))
		xbmcgui.unlock()

	####################################################################################################################
	def clearDirectory(self):
		debug("clearDirectory()")
		self.clearCategory()
		try:
			self.getControl( self.CLST_DIR ).reset()
			self.getControl( self.CLST_DIR ).setVisible(False)
			self.getControl( self.CLST_DIR ).selectItem(0)
		except: pass

	####################################################################################################################
	def clearCategory(self):
		debug("clearCategory()")
		self.clearStream()
		try:
			self.getControl( self.CLST_CAT ).reset()
			self.getControl( self.CGROUP_LIST_CAT ).setVisible( False )
			self.getControl( self.CLST_CAT ).selectItem(0)
		except: pass

	####################################################################################################################
	def clearStream(self):
		debug("clearStream()")
		try:
			self.getControl( self.CLST_STREAM ).reset()
			self.getControl( self.CGROUP_LIST_STREAM ).setVisible( False )
			self.getControl( self.CLST_STREAM ).selectItem(0)
		except: pass
		self.getControl( self.CLBL_TITLE ).setLabel("")
		self.getControl( self.CLBL_DESC ).setLabel("")

	####################################################################################################################
	def showDirectory(self):
		debug("> showDirectory()")
		# add items to NAV LIST DIRECTORY
		menu = self.directoriesDict[self.source].keys()
		menu.sort()
		for opt in menu:
			self.getControl( self.CLST_DIR ).addItem(xbmcgui.ListItem(opt))

		self.getControl( self.CLST_DIR ).setVisible(True)
		self.getControl( self.CLST_DIR ).selectItem(0)
		self.getControl( self.CLBL_DESC ).setLabel("Select a Directory")
		self.isFocusNavLists = True
		self.setFocus(self.getControl( self.CLST_DIR ))
		debug("< showDirectory()")

	####################################################################################################################
	def showCategory(self, directory):
		debug("> showCategory() directory="+directory)

		menu = self.categoriesDict[self.source][directory].keys()
		menu.sort()
		for opt in menu:
			self.getControl( self.CLST_CAT ).addItem(xbmcgui.ListItem(opt))

		self.getControl( self.CGROUP_LIST_CAT ).setVisible(True)
		self.getControl( self.CLST_CAT ).selectItem(0)
		self.getControl( self.CLBL_DESC ).setLabel("Select a Category")
		self.isFocusNavLists = True
		self.setFocus(self.getControl( self.CLST_CAT ))
		debug("< showCategory()")

	############################################################################################################
	def showStreams(self):
		debug("> showStreams()")

		if self.streamDetails:
			for pcd in self.streamDetails:
				label1 = "%s.  %s.  %s" % (pcd[self.STREAM_DETAILS_TITLE],
										   pcd[self.STREAM_DETAILS_STATION],
										   pcd[self.STREAM_DETAILS_SHORTDESC])
				label2 = "%s  %s" % (pcd[self.STREAM_DETAILS_DATE], pcd[self.STREAM_DETAILS_DUR])
				li = xbmcgui.ListItem(label1, label2, \
									pcd[self.STREAM_DETAILS_IMG_FILENAME], \
									pcd[self.STREAM_DETAILS_IMG_FILENAME])
				self.getControl( self.CLST_STREAM ).addItem(li)

			self.getControl( self.CGROUP_LIST_STREAM ).setVisible(True)
			self.getControl( self.CLST_STREAM ).selectItem(0)
			self.getControl( self.CLBL_DESC ).setLabel("Select a Stream to play")
			self.isFocusNavLists = False
			self.setFocus(self.getControl( self.CLST_STREAM ))

		debug("< showStreams()")

	########################################################################################################################
	def getCategories(self, directory):
		debug("> getCategories() directory="+directory)

		success = False
		try:
			categoryDict = self.categoriesDict[self.source][directory]
		except:
			# category not stored, download categories for selected directory
			debug("category missing, download it")
			url = self.directoriesDict[self.source][directory]
			categoryDict = {}

			dialogProgress.create(__language__(403), __language__(407), directory)
			doc = fetchURL(url)
			if doc and doc != -1:
				if self.source == self.SOURCE_POD:
					startStr = '<h3>Browse podcasts'
					endStr = '</div'
					regex = 'href="(.*?)">(.*?)<'
				elif self.source == self.SOURCE_RADIO:
					# all sections on one page. Just get relevant directory section
					if directory == self.RADIO_DIR_OPT_BROWSE_RADIO:
						startStr = '>CHOOSE A RADIO STATION<'
					elif directory == self.RADIO_DIR_OPT_BROWSE_MUSIC:
						startStr = '>MUSIC:<'
					elif directory == self.RADIO_DIR_OPT_BROWSE_SPEECH:
						startStr = '>SPEECH:<'
					endStr = '</ul>'
					regex = 'href="(.*?)".*?>(.*?)<'
				elif self.source == self.SOURCE_RADIO_LIVE:
					# PICK LIVE RADIO BY STATION
					startStr = '>CHOOSE A RADIO STATION<'
					endStr = '</ul>'
					regex = 'href="(.*?)".*?>(.*?)<'
				else:
					print "unknown source", self.source

				matches = parseDocList(doc, regex, startStr, endStr)
				if matches:
					for match in matches:
						if self.source == self.SOURCE_RADIO_LIVE:
							station = match[0].split('/')[-2]
							url = self.URL_RADIO_LIVE_HOME.replace('$STATION', station)
						else:
							url = self.URL_HOME + match[0]

						title = cleanHTML(decodeEntities(match[1]))
						categoryDict[title] = url

					self.categoriesDict[self.source][directory] = categoryDict

			dialogProgress.close()
		# load into categories nav list
		if categoryDict:
			success = True
		else:
			messageOK(__language__(402),__language__(404))

		debug("< getCategories() success="+str(success))
		return success


	############################################################################################################
	def getStreamsPodcast(self, directory, category):
		debug("> getStreamsPodcast() directory=" + directory + " category="+category)

		success = False
		self.streamDetails = []

		try:
			url = self.categoriesDict[self.source][directory][category]
		except:
			messageOK(__language__(402),__language__(300),category)
		else:
			dialogProgress.create(__language__(403), __language__(407), directory + ' > ' + category)
			doc = fetchURL(url)
			dialogProgress.close()
			if doc and doc != -1:
				try:
					# get XML url
					xmlURL = searchRegEx(doc, 'feedurl=(.*?xml)')
					if not xmlURL:
						raise

					# process html for img links
					htmlInfoDict = {}
					regex = '<h3>(.*?)</h3>.*?img src="(.*?)".*?alt="(.*?)"'
					matches = parseDocList(doc, regex, 'results_cells', 'begin footer')
					for match in matches:
						# make filename a combination of img alt and file ext
						altName = decodeEntities(match[2]) + imgURL[-4:]
						imgFilename = os.path.join(DIR_CACHE, xbmc.makeLegalFilename(altName))
						print title,imgURL,altName,imgFilename
						htmlInfoDict[ title ] = [imgURL,imgFilename]

					# fetch & process XML
					feedElementList = ['title','description','pubDate','link','itunes:duration','itunes:author']
					success = self.rssparser.feed(url=xmlURL)
					if success:
						rssItems = self.rssparser.parse("item", feedElementList)
						for rssItem in rssItems:
							title = rssItem.getElement(feedElementList[0])
							longDesc = rssItem.getElement(feedElementList[1])
							showDate = rssItem.getElement(feedElementList[2])
							mediaURL = rssItem.getElement(feedElementList[3])
							duration = rssItem.getElement(feedElementList[4])
							station = rssItem.getElement(feedElementList[5])
							shortDesc = longDesc[:40]

							print title,station,shortDesc,duration,showDate,longDesc,mediaURL
							# update stored details
							if htmlInfoDict.has_key(title):
								imgURL,imgFilename = htmlInfoDict[title]
							else:
								imgURL = ''
								imgFilename = self.IMG_PODCAST
							self.streamDetails.append([title,mediaURL,imgURL,imgFilename,station,shortDesc,duration,showDate,longDesc])
				except:
					print sys.exc_info()[ 1 ]
					print "bad scrape", match

				if not self.streamDetails:
					messageOK(__language__(301), directory + " > " + category )
				else:
					success = True

		debug("< getStreamsPodcast() success="+str(success))
		return success


	############################################################################################################
	def getStreamsRadio(self, directory, category):
		debug("> getStreamsRadio() directory=" + directory + " category="+category)

		success = False
		self.streamDetails = []

		try:
			url = self.categoriesDict[self.source][directory][category]
		except:
			messageOK(__language__(402),__language__(300),category)
		else:
			dialogProgress.create(__language__(403), __language__(407), directory + ' > ' + category)
			doc = fetchURL(url)
			if doc and doc != -1:
				# some streams consist of a link, name, desc
				# some also have multiple links. one per day.

				# Find stream block
				startStr = 'ALL SHOWS'
				endStr = '</ul>'
				regexStreams = '<li>(.*?<)/li'
				regexLinks = 'href="(.*?)".*?>(.*?)</a>(.*?)<'

				streamMatches = parseDocList(doc, regexStreams, startStr, endStr)
				MATCH_TOTAL = len(streamMatches)
				count = 0
				for streamMatch in streamMatches:
					try:
						streamTitle = ''
						streamDesc = ''

						# get all links for stream
						linkMatches = findAllRegEx(streamMatch, regexLinks)
						MAX = len(linkMatches)
						for idx in range(MAX):
							linkMatch = linkMatches[idx]
							mediaURL = self.URL_HOME + linkMatch[0]
							title = cleanHTML(decodeEntities(linkMatch[1]))
							shortDesc = cleanHTML(decodeEntities(linkMatch[2]))
							# if mutliple links, get first match details to be used on other matches
							if idx == 0 and MAX > 1:
								streamTitle = title
								streamDesc = shortDesc
								continue
							elif idx == 1:		# just put desc on first occurance
								title = "%s (%s)" % (streamTitle, title)
								shortDesc = streamDesc
							elif idx > 1:
								title = "%s (%s)" % (streamTitle, title)

							self.streamDetails.append([title,mediaURL,'',self.IMG_RADIO,'',shortDesc,'','',''])
					except:
						print "getStreamsRadio() bad streamMatch", streamMatch

			dialogProgress.close()
			if not self.streamDetails:
				messageOK(__language__(301), directory + " > " + category )
			else:
				success = True

		debug("< getStreamsRadio() success="+str(success))
		return success


	############################################################################################################
	def getStreamsRadioLive(self, directory, category):
		debug("> getStreamsRadioLive() directory=" + directory + " category="+category)

		success = False
		self.streamDetails = []

		try:
			url = self.categoriesDict[self.source][directory][category]
		except:
			messageOK(__language__(402),__language__(300),category)
		else:
			self.streamDetails.append([category + ' Live',url,'',self.IMG_RADIO,'','','','',''])
			success = True

		debug("< getStreamsRadioLive() success="+str(success))
		return success


	############################################################################################################
	def toggleNavListFocus(self, focusNavLists=None):
		if focusNavLists == None:			# toggle
			self.isFocusNavLists = not self.isFocusNavLists
		else:								# force state
			self.isFocusNavLists = focusNavLists

		if self.isFocusNavLists:
			debug("set focus to NAV LISTS")
			self.setFocus(self.getControl( self.CLST_CAT ))
		else:
			debug("set focus to CONTENT")
			self.setFocus(self.getControl( self.CLST_STREAM ))

	############################################################################################################
	# 1. download stream URL
	# 2. regex to find .rpm link
	# 3. download .rpm link and read rtsp URL from it
	# 4. read rtsp link and extra .ra URL (realaudio)
	# eg . rtsp://rmv8.bbc.net.uk/radio2/r2_alfie.ra?BBC-UID=b4b67453bb304bea9849307f215fd3791027bd97d0a021579a046100f3a5e9a6&SSO2-UID='
	# becomes rtsp://rmv8.bbc.net.uk/radio2/r2_alfie.ra
	# 5. play rtsp URL
	############################################################################################################
	def playStream(self, idx):
		debug("> playStream()")
		debug("source=" + self.source)

		mediaURL = ''
		rpmURL = ''
		audioStream = ''
		url = self.streamDetails[idx][self.STREAM_DETAILS_STREAMURL]
		title = self.streamDetails[idx][self.STREAM_DETAILS_TITLE]
		dialogProgress.create(__language__(403), __language__(407), title)
		doc = fetchURL(url, encodeURL=False)		# prevents removal of ?
		dialogProgress.close()
		if doc:
			if self.source == self.SOURCE_POD:
				regex = 'class="description">(.*?)<.*?class="download".*?href="(.*?)"'
				matches = findAllRegEx(doc, regex)
				if matches:
					# update long desc with better long desc from the subscriptions page
					longDesc = cleanHTML(decodeEntities(matches[0][0]))
					self.streamDetails[idx][self.STREAM_DETAILS_LONGDESC] = longDesc
					mediaURL = matches[0][1]
			elif self.source == self.SOURCE_RADIO:
				if find(doc, 'aod/shows/images') != -1:
					regex = 'AudioStream.*?"(.*?)".*?showtitle.*?txinfo.*?>(.*?)</span.*?img src="(.*?)".*?<td.*?>(.*?)<'
				else:
					regex = 'AudioStream.*?"(.*?)"'
				matches = findAllRegEx(doc, regex)

				try:
					if not matches:
						raise
					match = matches[0]
					dur = ''
					station = ''
					txDate =  ''
					txTime = ''
					imgURL = ''
					longDesc = ''
					if isinstance(match, str):
						rpmURL = self.URL_HOME + match + '.rpm'
						station = match.split('/')[-2]
					else:
						rpmURL = self.URL_HOME + match[0] + '.rpm'
						imgURL = self.URL_HOME + match[2]
						longDesc = cleanHTML(decodeEntities(match[3]))
						station = match[0].split('/')[-2]

						# break down txinfo if possible
						txinfo = match[1].replace('\n','')
						txinfoMatches = findAllRegEx(txinfo, '(.*?)<.*?>.*?((?:Sat|Sun|Mon|Tue|Wed|Thu|Fri).*?)-(.*?)$')
						if txinfoMatches:
							debug("full txinfo")
							dur = cleanHTML(txinfoMatches[0][0])
							txDate =  cleanHTML(decodeEntities(txinfoMatches[0][1]))
							txTime = cleanHTML(decodeEntities(txinfoMatches[0][2]))
						else:
							debug("minimal txinfo")
							txinfoMatches = findAllRegEx(txinfo, '(.*?)<.*?>(.*?)$')
							dur = cleanHTML(txinfoMatches[0][0])
							txDate =  cleanHTML(decodeEntities(txinfoMatches[0][1]))

#					print "txinfo split=", dur, station, txDate, txTime
					self.streamDetails[idx][self.STREAM_DETAILS_DUR] = dur
					self.streamDetails[idx][self.STREAM_DETAILS_STATION] = capwords(station)
					self.streamDetails[idx][self.STREAM_DETAILS_DATE] = txDate + ' ' + txTime
					self.streamDetails[idx][self.STREAM_DETAILS_IMGURL] = imgURL
					self.streamDetails[idx][self.STREAM_DETAILS_IMG_FILENAME] = os.path.join(DIR_CACHE, os.path.basename(imgURL))
					self.streamDetails[idx][self.STREAM_DETAILS_LONGDESC] = longDesc

				except:
					print "playStream() bad scrape"

				# download .rpm URL to extract rtsp URL
				if rpmURL:
					rtspDoc = fetchURL(rpmURL)
					mediaURL = searchRegEx(rtspDoc, '(rtsp.*?)\?')
			else:
				# RADIO LIVE - just find media link
				matches = findAllRegEx(doc, 'AudioStream.*?"(.*?)"')
				rpmURL = self.URL_HOME + matches[0] + '.rpm'

				# download .rpm URL to extract rtsp URL
				rtspDoc = fetchURL(rpmURL)
				mediaURL = searchRegEx(rtspDoc, '(rtsp://rmlive.*?)\?')
				if not mediaURL:
					mediaURL = searchRegEx(rtspDoc, '(rtsp.*?)\?')

		debug( "mediaURL=" + mediaURL)
		if mediaURL:
			try:
				xbmc.Player().play(mediaURL)
			except:
				debug( "playback failed" )
		else:
			if find(doc, "no episodes") != -1:
				messageOK(__language__(302),__language__(303))
			else:
				messageOK(__language__(402),_language__(304))

		if not xbmc.Player().isPlaying():
			mediaURL = ''

		debug("< playStream() mediaURL="+mediaURL)
		return mediaURL

	############################################################################################################
	def showNowPlaying(self, clear=False):
		debug("> showNowPlaying() clear="+str(clear))

		self.getControl( self.CFLBL_NOWPLAYING ).reset()
		if not clear:
			idx = self.getControl( self.CLST_STREAM ).getSelectedPosition()
			pcd =  self.streamDetails[idx]
			text = "Now playing: %s.  %s.  %s.  %s.  %s." % (pcd[self.STREAM_DETAILS_TITLE],
															 pcd[self.STREAM_DETAILS_STATION],
															 pcd[self.STREAM_DETAILS_DATE],
															 pcd[self.STREAM_DETAILS_DUR],
															 pcd[self.STREAM_DETAILS_LONGDESC])
			self.getControl( self.CFLBL_NOWPLAYING ).addLabel(text)
		debug("< showNowPlaying()")

	############################################################################################################
	def getIcons(self, streamDetailsIdx=None):
		debug("> getIcons()")

		def _getIcon(url, fn):
			if not fileExist(fn):
				result = fetchURL(url, fn, isImage=True)
			else:
				result = True
			debug("_getIcon=" + str(result))
			return result

		if streamDetailsIdx == None:
			# get all missing icons 
			for pcd in self.streamDetails:
				fn = pcd[self.STREAM_DETidxAILS_IMG_FILENAME]
				url = pcd[self.STREAM_DETAILS_IMGURL]
				if not _getIcon(url, fn):
					if self.source == self.SOURCE_POD:
						pcd[self.STREAM_DETAILS_IMG_FILENAME] = self.IMG_PODCAST
					else:
						pcd[self.STREAM_DETAILS_IMG_FILENAME] = self.IMG_RADIO
		else:
			pcd = self.streamDetails[streamDetailsIdx]
			fn = pcd[self.STREAM_DETAILS_IMG_FILENAME]
			url = pcd[self.STREAM_DETAILS_IMGURL]
			if not _getIcon(url, fn):
				if self.source == self.SOURCE_POD:
					self.streamDetails[streamDetailsIdx][self.STREAM_DETAILS_IMG_FILENAME] = self.IMG_PODCAST
				else:
					self.streamDetails[streamDetailsIdx][self.STREAM_DETAILS_IMG_FILENAME] = self.IMG_RADIO

		debug("< getIcons()")

######################################################################################
def updateScript(isSilent=True):
	""" Check and update script from svn """
	debug( "> updateScript() isSilent="+str(isSilent))

	updated = False
	up = update.Update(__language__, __scriptname__)
	version = up.getLatestVersion()
	xbmc.output("Current Version: " + __version__ + " Tag Version: " + version)
	if version != "-1":
		if __version__ < version:
			if ( dialogYesNo( __language__(0), \
				  "%s %s %s." % ( __language__( 1006 ), version, __language__( 1002 ), ), __language__( 1003 ),\
				  "", noButton=__language__( 501 ), \
				  yesButton=__language__( 500 ) ) ):
				updated = True
				up.makeBackup()
				up.issueUpdate(version)
		elif not isSilent:
			dialogOK(__language__(0), __language__(1000))
	elif not isSilent:
		dialogOK(__language__(0), __language__(1030))

#		del up
	debug( "< updateScript() updated="+str(updated))
	return updated

#######################################################################################################################    
# BEGIN !
#######################################################################################################################
if __name__ == '__main__':
	makeScriptDataDir() 

	# check for script update
	scriptUpdated = updateScript()
	if not scriptUpdated:
		if not installPlugin('music', checkInstalled=True):
			installPlugin('music')

		w = BBCPodRadio("script-BBC_PodRadio-main.xml", DIR_RESOURCES)
		w.doModal()
		del w 

# clean up on exit
moduleList = ['bbbLib','update','language']
for m in moduleList:
	try:
		del sys.modules[m]
	except: pass

xbmc.output("script exit and housekeeping")
# remove globals
try:
	del dialogProgress
except: pass
