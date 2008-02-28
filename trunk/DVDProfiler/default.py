"""
 Python XBMC script to view your DVDProfiler collection or somebody elses online collection.

 see readme.txt
 
 THANKS:
 To everyone who's ever helped in anyway, or if I've used code from your own scripts, MUCH APPRECIATED!

 Please don't alter or re-publish this script without authors persmission.

 CHANGELOG see changelog.txt
"""

# Python 2.4 libs
import xbmc, xbmcgui
import sys,os.path,re,urlparse,fileinput
from os import path
from string import find, strip, split, lower, replace
from shutil import rmtree

# Script doc constants
__scriptname__ = "DVDProfiler"
__version__ = '1.6'
__author__ = 'BigBellyBilly [BigBellyBilly@gmail.com]'
__date__ = '22-01-2008'
xbmc.output(__scriptname__ + " Version: " + __version__ + " Date: " + __date__)

# Shared resources
DIR_HOME = os.getcwd().replace( ";", "" )
DIR_RESOURCES = os.path.join( DIR_HOME , "resources" )
DIR_RESOURCES_LIB = os.path.join( DIR_RESOURCES , "lib" )
DIR_USERDATA = os.path.join( "T:\\script_data", __scriptname__ )

DIR_GFX = os.path.join( DIR_RESOURCES , "gfx" )             
DIR_IMG_CACHE = os.path.join(DIR_USERDATA, "images")
DIR_CACHE = os.path.join(DIR_USERDATA, "cache")

sys.path.insert(0, DIR_RESOURCES_LIB)

# Custom libs
import language
__language__ = language.Language().localized

import update                                       # script update module
from bbbLib import *								# requires __language__ to be defined
from bbbGUILib import *
from IMDbWin import IMDbWin
from smbLib import *
import time

# GLOBALS
KEYS_FILE = os.path.join( DIR_CACHE , 'keys.dat' )
COLLECTION_FLAT_FILE = os.path.join( DIR_CACHE, 'collection.dat' )
BASE_URL_INTER = "www.intervocative.com"
BASE_URL_INVOS = "www.invelos.com"

# GFX
NOIMAGE_FILENAME = os.path.join( DIR_GFX , 'noimage.png' )
TICK_FILENAME = os.path.join( DIR_GFX , 'tick.png' )

try: Emulating = xbmcgui.Emulating
except: Emulating = False

#################################################################################################################
class DVDProfiler(xbmcgui.Window):
	def __init__(self, *args, **kwargs):
		if Emulating: xbmcgui.Window.__init__(self)
		debug("> DVDProfiler().init")

		self.ready = False
		setResolution(self)

		# settings keys
		self.SETTING_SMB_USE = "smb_enabled"
		self.SETTING_SMB_PATH = "smb_path"
		self.SETTING_SMB_PC_IP = "smb_pc_ip"
		self.SETTING_SMB_FILENAME = "smb_filename"
		self.SETTING_SMB_COLLECTION_DIR = "smb_collection_dir"
		self.SETTING_SMB_IMAGES_DIR = "smb_images_dir"
		self.SETTING_SMB_DVDPRO_SHARE = "smb_dvdpro_share"
		self.SETTING_SMB_MOVIES_SHARE = "smb_movies_share"
		self.SETTING_START_MODE = "start_mode"
		self.SETTING_CHECK_SCRIPT_UPDATE_STARTUP = "check_script_update_startup"

		# default values
		self.SETTINGS_FILENAME = os.path.join( DIR_USERDATA, "settings.txt" )
		self.START_MODE_MENU = __language__(604)
		self.START_MODE_SMB = __language__(650)
		self.START_MODE_LOCAL = __language__(651)
		self.START_MODE_ONLINE = __language__(652)

		self.SETTINGS_DEFAULTS = {
			self.SETTING_SMB_USE : True,
			self.SETTING_SMB_PATH : "smb://user:pass@OFFICE",
			self.SETTING_SMB_PC_IP : "",		# empty so smb details incomplete by default
			self.SETTING_SMB_FILENAME :  "collection.xml",
			self.SETTING_START_MODE : "MENU",
			self.SETTING_SMB_COLLECTION_DIR : "EXPORT",
			self.SETTING_SMB_IMAGES_DIR : "IMAGES",
			self.SETTING_SMB_DVDPRO_SHARE : "DVD Profiler",
			self.SETTING_SMB_MOVIES_SHARE : "My Videos",
			self.SETTING_CHECK_SCRIPT_UPDATE_STARTUP : False,	# No
			}

		# SETTINGS
		self.reset()

		debug("< DVDProfiler().init ready="+str(self.ready))

	######################################################################################
	def _initSettings( self, forceReset=False ):
		debug("> _initSettings() forceReset="+str(forceReset))
		changed = False

		if forceReset:
			self.settings = {}
		elif not self.settings:
			self.settings = loadFileObj( self.SETTINGS_FILENAME, {} )

		# put default values into any settings that are missing
		for key, defaultValue in self.SETTINGS_DEFAULTS.items():
			if forceReset or not self.settings.has_key( key ) or self.settings[key] in [None,""]:
				self.settings[key] = defaultValue
				changed = True
				debug( "setting reset: " + key + " = " + str(defaultValue))

		if changed or not fileExist(self.SETTINGS_FILENAME):
			saveFileObj(self.SETTINGS_FILENAME, self.settings)

		debug( "< _initSettings() changed="+str(changed))
		return changed

	##############################################################################################
	def isReady(self):
		return self.ready

	###################################################################################################
	def onAction(self, action):

		if action == ACTION_PREVIOUS_MENU:
			debug("ACTION_PREVIOUS_MENU")
			self.close()

		elif not self.ready or action == 0:
			return

		self.ready = False
		if action == ACTION_SHOW_INFO or action == ACTION_REMOTE_INFO or action == ACTION_STOP:
			debug("ACTION_SHOW_INFO or ACTION_REMOTE_INFO or ACTION_STOP")
			if self.mainMenu():             # restart ?
				if not self.startup():
					self.reset()
		elif action == ACTION_X_BUTTON or action == ACTION_STOP:
			debug("ACTION_X_BUTTON")
			if self.isOnlineOnly or self.onlineAliasData:
				aliasData = ManageOnlineCollection().ask()
				if aliasData:							# only action/save if alias selected
					self.onlineAliasData = aliasData
					if not self.startup():
						self.reset()
			elif not self.onlineAliasData:
				self.doFilters()
		elif action == ACTION_Y_BUTTON or action == ACTION_PAUSE:
			debug("ACTION_Y_BUTTON")
			if not self.onlineAliasData:
				colNo = self.lastCollNo
			else:
				colNo = self.lastOnlineCollNo
			title = self.dvdCollection.getDVDKey(colNo)[self.dvdCollection.KEYS_DATA_SORTTITLE]
			win = IMDbWin().ask(title)
			del win
		elif action == ACTION_SELECT_ITEM:
			debug("ACTION_A_BUTTON")
		elif action == ACTION_PARENT_DIR:			# B btn
			debug("ACTION_PARENT_DIR")
			if not self.isOnlineOnly:
				if self.selectedGenres or self.selectedTags:
					self.selectedGenres = []
					self.selectedTags = []
					self.setupTitles()				# setup lists
				elif self.onlineAliasData:
					# online - back to own collection
					self.onlineAliasData = []
					if not self.startup():
						self.reset()

		self.ready = True

	##############################################################################################
	def onControl(self, control):
		if not self.ready:
			return
		self.ready = False

		if control == self.titlesCL:				# select title
			debug("titlesCL")
			# if selecting same title, attempt playback
			colNo = self.titlesCL.getSelectedItem().getLabel2()
			if colNo == self.lastCollNo or colNo == self.lastOnlineCollNo:
				if not self.onlineAliasData:
					debug("same colNo selcted, playback requesed, colNo: " + str(colNo))
					try:
						location = self.dvdCollection.getDVDData(self.dvdCollection.LOCATION)[0]
						debug("location=" + location);
						if not location: raise
					except:
						dialogOK(__language__(210),__language__(211))
					else:
						smbPath = "%s/%s/%s" % (self.settings[self.SETTING_SMB_PATH], \
												self.settings[self.SETTING_SMB_MOVIES_SHARE],
												location)
						debug(smbPath)
						result = xbmc.Player().play(smbPath)
						if not xbmc.Player().isPlaying():
							dialogOK(__language__(210),__language__(212),smbPath)
			elif not self.showDVD():
				self.reset()
		elif control == self.sortColCB:				# sort by column btn
			debug("sortColCB")
			self.sortByTitle = not self.sortByTitle
			if not self.setupTitles():
				self.reset()
		elif control == self.sortDirCB:				# sort asc/desc btn
			debug("sortDirCB")
			self.sortAsc = not self.sortAsc
			if not self.setupTitles():
				self.reset()
		elif control == self.filtersCB:				# filters btn
			debug("filtersCB")
			self.doFilters()

		self.ready = True

	###################################################################################################
	def reset(self):
		debug("> reset()")
		self.dvdCollection = None
		self.sortByTitle = True
		self.sortAsc = True
		self.lastCollNo = 0
		self.lastOnlineCollNo = 0
		self.remote = None
		self.onlineAliasData = []
		self.selectedGenres = {}
		self.selectedTags = {}
		self.settings = {}
		self.localCollectionFilename = os.path.join(DIR_CACHE,"collection.xml")

		makeScriptDataDir() 
		makeDir(DIR_IMG_CACHE)
		makeDir(DIR_CACHE)

		self._initSettings(forceReset=False)

		# check for script update
		scriptUpdated = False
		if self.settings[self.SETTING_CHECK_SCRIPT_UPDATE_STARTUP]:	# check for update ?
			scriptUpdated = update_script(False, False)

		if not scriptUpdated and self.startupMenu():
			self.ready = True
		else:
			self.close()
		debug("< reset()")


	##############################################################################################
	def startupMenu(self):
		debug("> startupMenu()")
		success = False
		menu = [ self.START_MODE_SMB, self.START_MODE_LOCAL, self.START_MODE_ONLINE]

		selectedPos = 0
		startupMode = self.settings[self.SETTING_START_MODE]
		while not success:
			self.isOnlineOnly = False
			self.onlineAliasData = []

			if startupMode == self.START_MODE_MENU:
				selectDialog = DialogSelect()
				selectDialog.setup(__language__(213), width=300, rows=len(menu),banner=LOGO_FILENAME)
				selectedPos, action = selectDialog.ask(menu, selectedPos)
				if selectedPos < 0:
					break
				startupMode = menu[selectedPos]
			
			# start according to startupMode
			if startupMode == self.START_MODE_SMB:								# SMB
				self.settings[self.SETTING_SMB_USE] = True
				success = self.startup()
			elif startupMode == self.START_MODE_LOCAL:							# LOCAL
				self.settings[self.SETTING_SMB_USE] = False
				success = self.startup()
			elif startupMode == self.START_MODE_ONLINE:							# ONLINE
				self.settings[self.SETTING_SMB_USE] = False
				self.isOnlineOnly = True
				self.onlineAliasData = ManageOnlineCollection().ask()
				if self.onlineAliasData:
					success = self.startup()

			if not success:
				startupMode = self.START_MODE_MENU

		debug("< startupMenu() success="+str(success))
		return success

	##############################################################################################
	def startup(self):
		debug("> startup()")
		success = False
		self.dvdCollection = None
		self.sortByTitle = True
		self.sortAsc = True

		if self.onlineAliasData:
			debug("ONLINE collection")
			self.dvdCollection = DVDCollectionOnline(self.onlineAliasData)
			if self.dvdCollection and self.dvdCollection.getCollectionSize() > 0:
				success = True
		elif self.settings[self.SETTING_SMB_USE]:
			debug("SMB collection")
			if self.startupSMB() and self.settings[self.SETTING_SMB_USE]:	# continue if not been disabled
				self.dvdCollection = DVDCollectionXML(self.localCollectionFilename)
				if self.dvdCollection and self.dvdCollection.getCollectionSize() > 0:
					success = True
				else:
					dialogOK(__language__(101),__language__(102))
		else:
			debug("LOCAL collection")
			if fileExist(self.localCollectionFilename):
				self.dvdCollection = DVDCollectionXML(self.localCollectionFilename)
				if self.dvdCollection and self.dvdCollection.getCollectionSize() > 0:
					success = True
			if not success:
				dialogOK(__language__(101),__language__(103), self.localCollectionFilename)

		# final check
		if success:
			self.setupDisplay()
			self.setupTitles()
		debug("< startup() success="+str(success))
		return success

	##############################################################################################
	def _checkSMBSettings(self):
		success = False
		try:
			if self.settings[self.SETTING_SMB_PATH] and \
					self.settings[self.SETTING_SMB_PC_IP] and \
					self.settings[self.SETTING_SMB_FILENAME] and \
					self.settings[self.SETTING_SMB_COLLECTION_DIR] and \
					self.settings[self.SETTING_SMB_IMAGES_DIR] and \
					self.settings[self.SETTING_SMB_DVDPRO_SHARE] :
				success = True
		except: pass
		debug("_checkSMBSettings() success="+str(success))
		return success

	##############################################################################################
	def startupSMB(self, forceConfig=False):
		debug("> startupSMB() forceConfig="+str(forceConfig))
		success = False

		while not success:
			if forceConfig or not self._checkSMBSettings():
				if not forceConfig:
					dialogOK(__language__(104),__language__(105))
				self.configSMB()
				forceConfig = False
				continue									# loop to re-check SMB setup

			if not self.settings[self.SETTING_SMB_USE]:		# SMB disabled
				break

			# check SMB
			smbPath = "%s/%s" % (self.settings[self.SETTING_SMB_PATH], self.settings[self.SETTING_SMB_DVDPRO_SHARE])
			self.remote, remoteInfo = smbConnect(self.settings[self.SETTING_SMB_PC_IP], smbPath)
			if not self.remote or not remoteInfo:
				title = __language__(106)
			else:
				smbPath = self.makeDVDProSMBPath()
				if not fileExist(self.localCollectionFilename) or \
						isNewSMBFile(smbPath, self.localCollectionFilename, \
							self.remote, self.settings[self.SETTING_SMB_PC_IP]):
					success = self.fetchCollectionSMB(True)
					if not success:
						title = __language__(107)
				else:
					success = True

			# report failure reason
			if not success:
				if xbmcgui.Dialog().yesno(title, __language__(214)):
					forceConfig = True
				else:
					self.settings[self.SETTING_SMB_USE] = False
					break

		debug("< startupSMB() success="+str(success))
		return success

	##############################################################################################
	def setupDisplay(self):
		debug("> setupDisplay()")

		# SKIN HEADER SZ
		headerH = 40

		# DRAW AREA DIMS
		displayX = 1
		displayY = headerH
		displayH = (REZ_H - displayY)
		displayW = REZ_W
		debug("displayX: " + str(displayX) + "  displayY: " + str(displayY) \
			+ "  displayH: " + str(displayH) + "  displayW: " + str(displayW))

		animAttrTime = "250"
		
		xbmcgui.lock()

		if isMC360():
			# gfx files come with actual MC360 installation
			try:
				debug("drawing mc360 specific gfx")
				self.addControl(xbmcgui.ControlImage(0,0, REZ_W, REZ_H, 'background-blue.png'))
#				self.addControl(xbmcgui.ControlImage(18,0, 720,REZ_H, xbmc.getInfoLabel('Skin.String(Media)')))
				self.addControl(xbmcgui.ControlImage(70, 0, 16, 54, 'bkgd-whitewash-glass-top-left.png'))
				self.addControl(xbmcgui.ControlImage(86, 0, 667, 54, 'bkgd-whitewash-glass-top-middle.png'))
				self.addControl(xbmcgui.ControlImage(753, 0, 16, 54, 'bkgd-whitewash-glass-top-right.png'))
				self.addControl(xbmcgui.ControlImage(70, 427, 16, 54, 'bkgd-whitewash-glass-bottom-left.png'))
				self.addControl(xbmcgui.ControlImage(86, 427, 667, 54, 'bkgd-whitewash-glass-bottom-middle.png'))
				self.addControl(xbmcgui.ControlImage(753, 427, 667, 54, 'bkgd-whitewash-glass-bottom-right.png'))
				self.addControl(xbmcgui.ControlImage(60, 0, 32, REZ_H, 'background-overlay-whitewash-left.png'))
				self.addControl(xbmcgui.ControlImage(92, 0, 628, REZ_H, 'background-overlay-whitewash-centertile.png'))
				self.addControl(xbmcgui.ControlImage(-61, 0, 128, REZ_H, 'blades-runner-left.png'))
				self.addControl(xbmcgui.ControlImage(18, 0, 80, REZ_H, 'blades-size4-header.png'))
				self.addControl(xbmcgui.ControlLabel(75, (200),0, 0, __language__(0), \
													 font=FONT18,textColor='0xFF000000',angle=270))
			except:
				xbmcgui.unlock()
				handleException("MC360 Skin")
		else:
			# NON MC360
			# BACKG
			try:
				self.removeControl(self.backgroundCI)
			except: pass
			try:
				self.backgroundCI = xbmcgui.ControlImage(0,0, displayW, displayH, BACKGROUND_FILENAME)
				self.addControl(self.backgroundCI)
			except: pass

			# HEADER
			try:
				self.removeControl(self.headerCI)
			except: pass
			try:
				self.headerCI = xbmcgui.ControlImage(0, 0,  displayW, headerH, HEADER_FILENAME)
				self.addControl(self.headerCI)
				self.headerCI.setAnimations([('WindowOpen', 'effect=slide start=0,-70 acceleration=-1.1 time='+animAttrTime),
											 ('WindowClose', 'effect=slide end=0,-70 acceleration=-1.1 time='+animAttrTime)])
			except: pass

		# LOGO
		logoW = 166
		logoH = headerH -2
		try:
			self.removeControl(self.logo)
		except: pass
		try:
			self.logo = xbmcgui.ControlImage(0, 0, logoW, logoH, LOGO_FILENAME)#, aspectRatio=2)
			self.addControl(self.logo)
			self.logo.setAnimations([('WindowOpen', 'effect=rotate start=90 center=0,0 time='+animAttrTime),
									 ('WindowClose', 'effect=rotate end=90 center=0,0 time='+animAttrTime)])
		except: pass

		# DATA SOURCE
		try:
			self.removeControl(self.datasourceCL)
		except: pass
		if self.onlineAliasData:
			user, host = self.onlineAliasData
			text = user + ' (' + host	+ ')'	# url
		elif self.settings[self.SETTING_SMB_USE]:
			text = self.settings[self.SETTING_SMB_PC_IP]
		else:
			text = 'Local Only'
		dataSourceW = 210
		self.datasourceCL = xbmcgui.ControlLabel(REZ_W, 0, dataSourceW, 10, text, \
												FONT10, '0xFFFFFFCC', alignment=XBFONT_RIGHT)
		self.addControl(self.datasourceCL)
		animAttrStrWO = 'effect=slide start=%d,0 acceleration=-1.1 time=%s' % (REZ_W, animAttrTime)
		animAttrStrWC = 'effect=slide end=%d,0 acceleration=-1.1 time=%s' % (REZ_W, animAttrTime)
		self.datasourceCL.setAnimations([('WindowOpen', animAttrStrWO), ('WindowClose', animAttrStrWC) ])

		# TITLE
		try:
			self.removeControl(self.title)
		except: pass
		x = displayX + logoW + 5
		w = displayW - x
		self.title = xbmcgui.ControlLabel(x, 5, w, 25, 'Please wait ...', FONT14, '0xFFFFFF33')
		self.addControl(self.title)
		self.title.setAnimations([('WindowOpen', 'effect=slide start=0,-70 acceleration=-1.1 time='+animAttrTime),
								  ('WindowClose', 'effect=slide end=0,-70 acceleration=-1.1 time='+animAttrTime)])

		# IMAGE BACKG
		try:
			self.removeControl(self.coverBackCI)
		except: pass
		try:
			imageW = 160
			imageH = 250
			ypos = displayY+5
			self.coverBackCI = xbmcgui.ControlImage(displayX, ypos, \
											imageW+4, imageH+4, FRAME_NOFOCUS_LRG_FILENAME)
			self.addControl(self.coverBackCI)
			self.coverBackCI.setAnimations([('WindowOpen', 'effect=zoom start=20 center=80,125 time='+animAttrTime),
								  ('WindowClose', 'effect=zoom end=20 center=80,125 time='+animAttrTime)])
		except: pass

		# IMAGE
		try:
			self.removeControl(self.coverCI)
		except: pass
		try:
			self.coverCI = xbmcgui.ControlImage(displayX+2, ypos+2, \
											imageW, imageH, FRAME_NOFOCUS_FILENAME,aspectRatio=2)
			self.addControl(self.coverCI)
			self.coverCI.setAnimations([('WindowOpen', 'effect=zoom start=20 center=80,125 time='+animAttrTime),
									('WindowClose', 'effect=zoom end=0 center=80,125 time='+animAttrTime)])
		except: pass

		# TITLES LIST BACKG
		try:
			self.removeControl(self.titlesBackCI)
		except: pass
		try:
			sortBtnH = 15
			ypos += imageH + 5
			listSpinH = 20
			listW = int(displayW /2) -2
			listH = (REZ_H - ypos - sortBtnH) -2
			listY = ypos
			self.titlesBackCI = xbmcgui.ControlImage(displayX, listY, listW, \
											listH, FRAME_NOFOCUS_LRG_FILENAME)
			self.addControl(self.titlesBackCI)
			titlesAnim = [('WindowOpen', 'effect=slide start=-'+str(listW)+',0 acceleration=-1.1 time='+animAttrTime), 
							('WindowClose', 'effect=slide end=-'+str(listW)+',0 acceleration=-1.1 time='+animAttrTime)]
			self.titlesBackCI.setAnimations(titlesAnim)
		except: pass

		# TITLES LIST
		try:
			self.removeControl(self.titlesCL)
		except: pass
		try:
			self.titlesCL = xbmcgui.ControlList(displayX+2, listY+2, listW-4, listH+listSpinH, \
												space=0,itemHeight=19,font=FONT10, \
												itemTextXOffset=0, itemTextYOffset=0, alignmentY=XBFONT_CENTER_Y)
			self.addControl(self.titlesCL)
			self.titlesCL.setPageControlVisible(False)
			self.titlesCL.setAnimations(titlesAnim)
		except: pass

		# SORT BY COLUMN 
		try:
			self.removeControl(self.sortColCB)
		except: pass
		xpos = displayX
		ypos += listH
		btnW = int(listW/3)-5
		# lbl indicates 'what it will do' by pressing it
		self.sortColCB = xbmcgui.ControlButton(xpos, ypos, btnW, sortBtnH, '', \
											   font=FONT10, alignment=XBFONT_CENTER_X|XBFONT_CENTER_Y)
		self.addControl(self.sortColCB)
		bottomBtnAnim = [('WindowOpen', 'effect=slide start=0,15 acceleration=-1.1 time='+animAttrTime),
							('WindowClose', 'effect=slide end=0,15 acceleration=-1.1 time='+animAttrTime)]
		self.sortColCB.setAnimations(bottomBtnAnim)

		# SORT DIRECTION
		try:
			self.removeControl(self.sortDirCB)
		except: pass
		xpos += btnW + 5
		# lbl indicates 'what it will do' by pressing it
		self.sortDirCB = xbmcgui.ControlButton(xpos, ypos, btnW, sortBtnH, '',\
											   font=FONT10, alignment=XBFONT_CENTER_X|XBFONT_CENTER_Y)
		self.addControl(self.sortDirCB)
		self.sortDirCB.setAnimations(bottomBtnAnim)

		# FILTERS
		try:
			self.removeControl(self.filtersCB)
		except: pass
		xpos += btnW + 5
		# lbl indicates 'what it will do' by pressing it
		self.filtersCB = xbmcgui.ControlButton(xpos, ypos, btnW, sortBtnH, '',\
											   font=FONT10, alignment=XBFONT_CENTER_X|XBFONT_CENTER_Y)
		self.addControl(self.filtersCB)
		self.filtersCB.setAnimations(bottomBtnAnim)

		# OVERVIEW - lbl
		try:
			self.removeControl(self.overviewLbl)
		except: pass
		xpos = displayX + imageW +10
		ypos = displayY +10
		overviewW = REZ_W - xpos
		overviewLblH = 20
		self.overviewLbl = xbmcgui.ControlLabel(xpos, ypos, overviewW, overviewLblH, 'Overview:', FONT10, '0xFFFFFFFF')
		self.addControl(self.overviewLbl)
		overviewAnim = [('WindowOpen', 'effect=slide start='+str(REZ_W)+',0 acceleration=-1.1 time='+animAttrTime),
					('WindowClose', 'effect=slide end='+str(REZ_W)+',0 acceleration=-1.1 time='+animAttrTime)]
		self.overviewLbl.setAnimations(overviewAnim)

		# OVERVIEW - data
		try:
			self.removeControl(self.overviewCTB)
		except: pass
		ypos += overviewLblH
		overviewH = imageH - 30
		self.overviewCTB = xbmcgui.ControlTextBox(xpos, ypos, overviewW, overviewH, FONT10, '0xFFFFFF66')
		self.addControl(self.overviewCTB)
		self.overviewCTB.setAnimations(bottomBtnAnim)
		self.overviewCTB.setAnimations(overviewAnim)

		# CAST/CREDITS LIST BACKG
		try:
			self.removeControl(self.castBackCI)
		except: pass
		ypos = listY
		xpos = displayX + listW + 2
		self.castBackCI = xbmcgui.ControlImage(xpos, ypos, listW, listH, FRAME_NOFOCUS_LRG_FILENAME)
		self.addControl(self.castBackCI)
		castAnim = [('WindowOpen', 'effect=slide start='+str(REZ_W)+',0 acceleration=-1.1 time='+animAttrTime),
					('WindowClose', 'effect=slide end='+str(REZ_W)+',0 acceleration=-1.1 time='+animAttrTime)]
		self.castBackCI.setAnimations(castAnim)

		# CAST/CREDITS LIST
		try:
			self.removeControl(self.castCL)
		except: pass
		try:
			self.castCL = xbmcgui.ControlList(xpos+2, ypos+2, listW-4, listH+listSpinH, \
												space=0,itemHeight=19,font=FONT10, \
												itemTextXOffset=0, itemTextYOffset=0, alignmentY=XBFONT_CENTER_Y)
			self.addControl(self.castCL)
			self.castCL.setPageControlVisible(False)
			self.castCL.setAnimations(castAnim)
		except: pass

		# MENU BTNS at bottom of screen
		ypos += listH +2
		btnW = 15
		btnH = 15
		# white - MENU
		try:
			self.removeControl(self.whiteCI)
		except: pass
		self.whiteCI = xbmcgui.ControlImage(xpos, ypos, btnW, btnW, BTN_WHITE_FILENAME)
		self.addControl(self.whiteCI)
		self.whiteCI.setAnimations(bottomBtnAnim)

		try:
			self.removeControl(self.whiteLbl)
		except: pass
		xpos += btnW +1
		lblW = 38
		self.whiteLbl = xbmcgui.ControlLabel(xpos, ypos, lblW, 10, 'Menu', \
											FONT10, '0xFF00FFFF', alignment=XBFONT_CENTER_Y|XBFONT_LEFT)
		self.addControl(self.whiteLbl)
		self.whiteLbl.setAnimations(bottomBtnAnim)

		# Y - IMDb
		try:
			self.removeControl(self.yCI)
		except: pass
		xpos += lblW
		self.yCI = xbmcgui.ControlImage(xpos, ypos, btnW, btnH, BTN_Y_FILENAME)
		self.addControl(self.yCI)
		self.yCI.setAnimations(bottomBtnAnim)

		try:
			self.removeControl(self.yLbl)
		except: pass
		xpos += btnW +1
		self.yLbl = xbmcgui.ControlLabel(xpos, ypos, lblW, 10, 'IMDb', \
										FONT10, '0xFF00FFFF', alignment=XBFONT_CENTER_Y|XBFONT_LEFT)
		self.addControl(self.yLbl)
		self.yLbl.setAnimations(bottomBtnAnim)

		# A - SELECT/PLAYBACK - if not online viewing
		try:
			self.removeControl(self.aCI)
		except: pass
		xpos += lblW
		self.aCI = xbmcgui.ControlImage(xpos, ypos, btnW, btnH, BTN_A_FILENAME)
		self.addControl(self.aCI)
		self.aCI.setAnimations(bottomBtnAnim)

		try:
			self.removeControl(self.aLbl)
		except: pass
		xpos += btnW +1
		lblW = 75
		if self.isOnlineOnly or self.onlineAliasData:
			text = 'Select'
		else:
			text = 'Select/Play'
		self.aLbl = xbmcgui.ControlLabel(xpos, ypos, lblW, 10, text, \
										FONT10, '0xFF00FFFF', alignment=XBFONT_CENTER_Y|XBFONT_LEFT)
		self.addControl(self.aLbl)
		self.aLbl.setAnimations(bottomBtnAnim)

		# X - ONLINE or FILTERS - depends on startup mode
		try:
			self.removeControl(self.xCI)
		except: pass
		xpos += lblW +1
		self.xCI = xbmcgui.ControlImage(xpos, ypos, btnW, btnH, BTN_X_FILENAME)
		self.addControl(self.xCI)
		self.xCI.setAnimations(bottomBtnAnim)

		try:
			self.removeControl(self.xLbl)
		except: pass
		xpos += btnW +1
		lblW = 65
		if self.isOnlineOnly or self.onlineAliasData:
			text = 'Alias'
		else:
			text = 'Filters'
		self.xLbl = xbmcgui.ControlLabel(xpos, ypos, lblW, 10, text, \
										FONT10, '0xFF00FFFF', alignment=XBFONT_CENTER_Y|XBFONT_LEFT)
		self.addControl(self.xLbl)
		self.xLbl.setAnimations(bottomBtnAnim)

		# B btn only displayed when currently viewing an online collection
		try:
			self.removeControl(self.bCI)
		except: pass
		xpos += lblW +1
		self.bCI = xbmcgui.ControlImage(xpos, ypos, btnW, btnH, BTN_B_FILENAME)
		self.addControl(self.bCI)
		self.bCI.setVisible(False)
		self.bCI.setAnimations(bottomBtnAnim)

		try:
			self.removeControl(self.bLbl)
		except: pass
		xpos += btnW +1
		lblW = 70
		self.bLbl = xbmcgui.ControlLabel(xpos, ypos, lblW, 10, '', \
										FONT10, '0xFF00FFFF', alignment=XBFONT_CENTER_Y|XBFONT_LEFT)
		self.addControl(self.bLbl)
		self.bCI.setVisible(False)
		self.bLbl.setAnimations(bottomBtnAnim)

		# navigation
		self.titlesCL.setNavigation(self.overviewCTB, self.sortColCB, self.sortColCB, self.castCL)
		self.overviewCTB.setNavigation(self.titlesCL, self.titlesCL, self.castCL, self.titlesCL)
		self.castCL.setNavigation(self.overviewCTB, self.sortColCB, self.titlesCL, self.overviewCTB)
		self.sortColCB.setNavigation(self.titlesCL, self.titlesCL, self.titlesCL, self.sortDirCB)
		self.sortDirCB.setNavigation(self.titlesCL, self.titlesCL, self.sortColCB, self.filtersCB)
		self.filtersCB.setNavigation(self.titlesCL, self.titlesCL, self.sortDirCB, self.castCL)

		self.setFocus(self.titlesCL)
		xbmcgui.unlock()

		debug("< setupDisplay()")

	###################################################################################################
	def doFilters(self):
		debug("> doFilters()")

		# make dict - set enabled items from last time filters was shown
		genresDict = {}
		for genre in self.dvdCollection.filterGenres:
			genresDict[genre] = (genre in self.selectedGenres)

		tagsDict = {}
		for tag in self.dvdCollection.filterTags:
			tagsDict[tag] = (tag in self.selectedTags)

		win = Filters()
		self.selectedGenres, self.selectedTags = win.ask(genresDict, tagsDict)
		del win
		# ALL is same as no filter selecting for genres.
		if len(self.selectedGenres) == len(self.dvdCollection.filterGenres):
			self.selectedGenres = []

		self.setupTitles()		# setup lists
		debug("< doFilters()")

	###################################################################################################
	def updateFilterBtn(self, filterCount):
		debug("> updateFilterBtn()")
		isEnabled = ( not self.onlineAliasData and self.dvdCollection.keys != {} )
		self.filtersCB.setVisible(isEnabled)
		self.filtersCB.setEnabled(isEnabled)
		if isEnabled:
			text = 'Filters: '+ str(filterCount) + '\\' + str(len(self.dvdCollection.keys))
			self.filtersCB.setLabel(text)
		debug("< updateFilterBtn()")

	##############################################################################################
	def setupTitles(self):
		debug("> setupTitles()")

		if self.sortByTitle:
			text = "Sort By #"
		else:
			text = "Sort By Title"
		try:
			self.sortColCB.setLabel(text)
		except: pass # old builds dont support this

		if self.sortAsc:
			text = "Descending"
		else:
			text = "Ascending"
		try:
			self.sortDirCB.setLabel(text)
		except: pass # old builds dont support this

		filterCount = self.loadTitlesCL(self.sortByTitle, self.sortAsc)
		self.updateFilterBtn(filterCount)
		if filterCount:
			success = self.showDVD()
		else:
			self.clearControls()
			success = True

		# update A btn according to online status
		if self.isOnlineOnly or self.onlineAliasData:
			text = 'Select'
		else:
			text = 'Select/Play'
		self.aLbl.setLabel(text)

		# update B btn label
		if self.selectedGenres or self.selectedTags:
			text = 'Clear Filters'
		elif not self.isOnlineOnly and self.onlineAliasData:
			text = 'My Profile'
		else:
			text = ''
		self.bLbl.setLabel(text)
		self.bCI.setVisible(text != '')
		self.bLbl.setVisible(text != '')

		debug("< setupTitles()")
		return success

	###################################################################################################
	def loadTitlesCL(self, sortByTitles=True, sortAsc=True):
		debug ("> loadTitlesCL() sortByTitles="+str(sortByTitles) + " sortAsc="+str(sortAsc))

		def sortItemsAsc(x, y):
			return cmp(x[1],y[1])

		def sortItemsDesc(x, y):
			return cmp(y[1],x[1])

		self.titlesCL.reset()

		# FILTERS -  make a dict just containing those matching filter
		filterDict = {}
		if self.onlineAliasData or not self.selectedGenres and not self.selectedTags:
			# no filters selected  - match ALL
			debug("match ALL")
			filterDict = self.dvdCollection.keys
		else:
			# examine filters - for each dvd
			debug("using filters")
			for key, data in self.dvdCollection.keys.items():
				add = False
				# match genre or incl. ALL if no genres selected
				genres = data[self.dvdCollection.KEYS_DATA_GENRES]
				if not self.selectedGenres:		# no selected genres also == ALL selected
					add = True
				elif not genres:
					# dvd has no genres, incl only when 'no genres' selected
					if self.dvdCollection.GENRE_NONE in self.selectedGenres:
						add = True
				else:
					# examine all genres for this dvd
					for genre in genres:
						if genre in self.selectedGenres:
							add = True
							break		# matched, stop processing dvd genres

				# if added, and dvd has tags, sub filter against tags
				if add and self.selectedTags:
					tags = data[self.dvdCollection.KEYS_DATA_TAGS]
					# dvd has tags, check for match
					add = False			# reset, as it must now also have one of the selected tags
					# examine all tags for this dvd
					for tag in tags:
						if tag in self.selectedTags:
							add = True
							break		# matched, stop processing dvd tags

				if add:
					filterDict[int(key)] = data

		if filterDict:
			selectedPos = 0
			if not sortByTitles:
				sortList = filterDict.keys()
				self.title.setLabel('Sorting by Collection Number ...')
				sortList.sort()
				if not sortAsc:
					sortList.reverse()

				# [(collNo, ['sorttitle','id',sorttitle,genres,tags)]
				for i in range(len(sortList)):
					collNo = sortList[i]
					title = self.dvdCollection.getDVDKey(collNo)[self.dvdCollection.KEYS_DATA_SORTTITLE]
					self.titlesCL.addItem(xbmcgui.ListItem(title, str(collNo)))
					if not self.onlineAliasData and collNo == self.lastCollNo:
						selectedPos = i
			else:
				sortList = filterDict.items()
				if sortAsc:
					self.title.setLabel('Sorting by TITLE. Ascending ...')
					sortList.sort(sortItemsAsc)
				else:
					self.title.setLabel('Sorting by TITLE. Descending ...')
					sortList.sort(sortItemsDesc)

				# [(collNo, ['sorttitle','id',title,genres,tags)]
				for i in range(len(sortList)):
					collNo = sortList[i][0]
					title = sortList[i][1][self.dvdCollection.KEYS_DATA_SORTTITLE]
					self.titlesCL.addItem(xbmcgui.ListItem(title, str(collNo)))
					if not self.onlineAliasData and collNo == self.lastCollNo:
						selectedPos = i

#			if selectedPos >= len(filterDict):
#				selectedPos = 0
#			debug("selectedPos=" +str(selectedPos))
			self.titlesCL.selectItem(0)

		filterCount = len(filterDict)
		debug ("< loadTitlesCL() filerCount=" + str(filterCount))
		return filterCount

	##############################################################################################
	def makeDVDProSMBPath(self):
		return "%s/%s/%s/%s" % (self.settings[self.SETTING_SMB_PATH], \
								self.settings[self.SETTING_SMB_DVDPRO_SHARE],
								self.settings[self.SETTING_SMB_COLLECTION_DIR], \
								self.settings[self.SETTING_SMB_FILENAME])

	##############################################################################################
	def clearControls(self, clearTitles=False):
		debug("> clearControls()")
		self.title.setLabel('')
#		self.coverCI.setImage(FRAME_NOFOCUS_FILENAME)
		self.coverCI.setVisible(False)
		self.overviewCTB.reset()
		if clearTitles:
			self.titlesCL.reset()
			self.datasourceCL.setLabel('')
		self.castCL.reset()
		debug("< clearControls()")

	###################################################################################################
	def fetchCollectionSMB(self, forceNew=False):
		debug ("> fetchCollectionSMB() forceNew="+str(forceNew))

		if forceNew:
			self.deleteLocalCollection()
			success = False
		else:
			success = fileExist(self.localCollectionFilename)

		if not success:
			dialogProgress.create(__language__(215), __language__(100))
			# remove any old parsed files
			deleteFile(KEYS_FILE)
			deleteFile(COLLECTION_FLAT_FILE)

			# fetch from SMB
			smbPath = self.makeDVDProSMBPath()
			success = smbFetchFile(smbPath, self.localCollectionFilename, \
							self.remote, self.settings[self.SETTING_SMB_PC_IP])
			dialogProgress.close()
		else:
			debug("local xml already exists")
		debug ("< fetchCollectionSMB() success="+str(success))
		return success

	###################################################################################################
	def deleteLocalCollection(self):
		debug("deleteLocalCollection()")
		# remove any old parsed files
		deleteFile(self.localCollectionFilename)
		deleteFile(KEYS_FILE)
		deleteFile(COLLECTION_FLAT_FILE)

	###################################################################################################
	def showDVD(self):
		debug ("> showDVD()")

		selectedPos = self.titlesCL.getSelectedPosition()
		title = self.titlesCL.getSelectedItem().getLabel()
		collNum = self.titlesCL.getSelectedItem().getLabel2()
		if not self.onlineAliasData:
			self.lastCollNo = collNum
		else:
			self.lastOnlineCollNo = collNum
		debug("selectedPos="+str(selectedPos) + \
			  " collNum=" + collNum + " lastCollNo=" +str(self.lastCollNo) + \
			  " lastOnlineCollNo=" +str(self.lastOnlineCollNo))

		self.clearControls()

		# load data into controls
		self.title.setLabel(__language__(100))
		success = self.dvdCollection.parseDVD(collNum)
		if not success:
			debug ("< showDVD() failed to parseDVD")
			return False

		if Emulating:
			for key, value in self.dvdCollection.dvdDict.items():
				print key, '=', value

		#######################################################
		# extract text from object which could be a list of lists of strings etc
		def _getItemsText(key, joinCh=","):
			text = ''
			try:
				for item in self.dvdCollection.getDVDData(key):
					if not isinstance(item,str):
						text = joinCh.join(item)
					else:
						text = item
			except:
				text = 'N/A'
			return text
		#######################################################

		xbmcgui.lock()
		self.title.setLabel(title)

		# cast list
		debug("build cast list")
		self.castCL.reset()
		self.castCL.addItem(xbmcgui.ListItem('CAST:'))
		self.castCL.addItem(xbmcgui.ListItem('ACTOR','ROLE'))
		try:
			for items in self.dvdCollection.getDVDData(self.dvdCollection.ACTORS):
				if items:
					if not isinstance(items,str):
						itemCount = len(items)
						if itemCount == 1:
							name = items[0]
							role = ''
						else:
							name = ' '.join(items[0:itemCount-1])
							role = items[-1]
					else:
						name = items
						role = ''
					self.castCL.addItem(xbmcgui.ListItem(name, role))
		except:
			self.castCL.addItem(xbmcgui.ListItem('N/A'))
		else:
			debug("cast done OK")

		# append credits
		debug("build credits")
		self.castCL.addItem(xbmcgui.ListItem('CREW:'))
		self.castCL.addItem(xbmcgui.ListItem('NAME','POSITION'))
		try:
			for items in self.dvdCollection.getDVDData(self.dvdCollection.CREDITS):
				if items:
					if not isinstance(items,str):
						itemCount = len(items)
						if itemCount == 1:
							name = items[0]
							role = ''
						else:
							name = ' '.join(items[0:itemCount-1])
							role = items[-1]
					else:
						name = items
						role = ''
					self.castCL.addItem(xbmcgui.ListItem(name, role))
		except:
			handleException()
			self.castCL.addItem(xbmcgui.ListItem('N/A'))
		else:
			debug("credits done OK")


		# overview (also incorperating additional information)
		self.overviewCTB.reset()
		text = ''
		try:
			text += _getItemsText(self.dvdCollection.OVERVIEW)
		except: text += "N/A"

		text += '\n\nAdditional Information:'
		try:
			text += '\nRating:  '
			text += _getItemsText(self.dvdCollection.RATING)
		except: text += "N/A"

		try:
			text += '\nRuntime:  '
			mins = _getItemsText(self.dvdCollection.RUNNINGTIME)
			if mins and mins != 'N/A' and find(mins,'min') == -1:
				mins += ' mins'
			text += mins
		except: text += "N/A"

		try:
			text += '\nRegion:  '
			text += _getItemsText(self.dvdCollection.REGION)
		except: text += "N/A"

		try:
			text += '\nProd Year:  ' 
			text += _getItemsText(self.dvdCollection.PRODYEAR)
		except: text += "N/A"

		try:
			text += '\nReleased:  '
			text += _getItemsText(self.dvdCollection.RELEASED)
		except: text += "N/A"

		try:
			text += '\nGenre:  '
			text += _getItemsText(self.dvdCollection.GENRE)
		except: text += "N/A"

		text += '\nVideo:  '
		if not self.onlineAliasData:
			try:
				text += 'AspectRatio: '
				text += _getItemsText(self.dvdCollection.VIDEOFORMAT_ASPECT)
			except: text += "N/A"

			try:
				text += 'Standard: '
				text += _getItemsText(self.dvdCollection.VIDEOFORMAT_STD)
			except: text += "N/A"

			try:
				text += 'Standard: '
				text += _getItemsText(self.dvdCollection.VIDEOFORMAT_STD)
			except: text += "N/A"

			try:
				text += ' 16x9: '
				value = _getItemsText(self.dvdCollection.VIDEOFORMAT_IS16x9)
				if value.lower() == 'false':
					value = 'No'
				elif value.lower() == 'true':
					value = 'Yes'
				text += value
			except: text += "N/A"
		else:
			try:
				text += _getItemsText(self.dvdCollection.VIDEOFORMAT)
			except: text += "N/A"

		try:
			text += '\nAudio Language:  '
			text += _getItemsText(self.dvdCollection.AUDIOFORMAT)
		except: text += "N/A"

		try:
			text += '\nStudios:  '
			text += _getItemsText(self.dvdCollection.STUDIO)
		except: text += "N/A"

		try:
			text += '\nReviews (F/V/A/E):  '
			text += _getItemsText(self.dvdCollection.REVIEW)
		except: text += "N/A"

		try:
			text += '\nFeatures:  '
			text += _getItemsText(self.dvdCollection.FEATURES)
		except: text += "N/A"

		try:
			text += '\nEaster Eggs:  '
			text += _getItemsText(self.dvdCollection.EASTEREGGS)
		except: text += "N/A"

		try:
			text += '\nMedia Location:  '
			text += _getItemsText(self.dvdCollection.LOCATION)
		except: text += "N/A"

		self.overviewCTB.setText(text)
		debug('\n\n'+text)		

		# cover image
		id = self.dvdCollection.getDVDKey(int(collNum))[self.dvdCollection.KEYS_DATA_ID]
		fn = self.fetchCover(id)
		self.coverCI.setImage(fn)
		self.coverCI.setVisible(True)
		self.setFocus(self.titlesCL)
		xbmcgui.unlock()
		debug ("< showDVD() collNum: " + collNum)
		return True

	###################################################################################################
	# fetch cover from same site collection held on
	###################################################################################################
	def fetchCover(self, coverID):
		debug ("> fetchCover() coverID=" + coverID)

		coverFilename = coverID + 'f.jpg'
		localFile = os.path.join(DIR_IMG_CACHE, coverFilename)
		success = fileExist(localFile)
		if not success:
			if self.onlineAliasData:
				alias, aliasURL = self.onlineAliasData
				if aliasURL == BASE_URL_INTER:
					url = "%s/cgi-bin/data/myprofiler/images/%s" % (aliasURL, coverFilename)
				else:
					url = "%s/mpimages/%s/%s" % (aliasURL, coverFilename[:2],coverFilename)
				dialogProgress.create(__language__(216), coverFilename)
				if fetchCookieURL(url, localFile, isImage=True):
					success = True

				dialogProgress.close()
			elif self.settings[self.SETTING_SMB_USE]:
				smbPath = "%s/%s/%s/%s" % (self.settings[self.SETTING_SMB_PATH],
										   self.settings[self.SETTING_SMB_DVDPRO_SHARE],
										   self.settings[self.SETTING_SMB_IMAGES_DIR],
										   coverFilename)
				success = smbFetchFile(smbPath, localFile, self.remote, self.settings[self.SETTING_SMB_PC_IP])
			else:
				success = False

			if not success:
				localFile = NOIMAGE_FILENAME

		debug ("< fetchCover() success="+str(success))
		return localFile

	###################################################################################################
	def fetchAllImages(self):
		debug("> fetchAllImages()")

		dialogProgress.create(__language__(17))
		MAX = self.dvdCollection.getCollectionSize()
		count = float(1.0)
		for collNum, data in self.dvdCollection.keys.items():
			dvdKeys = self.dvdCollection.getDVDKey(int(collNum))
			id = dvdKeys[self.dvdCollection.KEYS_DATA_ID]
			title = dvdKeys[self.dvdCollection.KEYS_DATA_SORTTITLE]
			dialogProgress.update(int(int(100/MAX)*count), title)
			self.fetchCover(id)
			count += 1
			if dialogProgress.iscanceled(): break

		dialogProgress.close()
		debug("< fetchAllImages(")

	###################################################################################################
	def mainMenu(self):
		debug("> mainMenu()")

		# menu choices
		MENU_VIEW_IMDB = "View IMDb Of Current Title"
		MENU_VIEW_ONLINE = "View An Online Collection"
		MENU_VIEW_OWN = "View Own Collection"
		MENU_FILTERS = "Filters"
		MENU_FETCH_COLL = "Fetch Collection From SMB"
		MENU_CONFIG_MENU = "Config Menu"
		MENU_FETCH_ALL_IMAGES = "Fetch All Images"
		MENU_VIEW_README = "View Script Readme"
		MENU_VIEW_CHANGELOG = "View Script ChangeLog"

		menuOptions = [
			MENU_VIEW_IMDB,
			MENU_VIEW_ONLINE,
			MENU_VIEW_OWN,
			MENU_FILTERS,
			MENU_FETCH_COLL,
			MENU_FETCH_ALL_IMAGES,
			MENU_CONFIG_MENU,
			MENU_VIEW_README,
			MENU_VIEW_CHANGELOG
			]

		if self.isOnlineOnly or not self.onlineAliasData:
			menuOptions.remove(MENU_VIEW_OWN)
		if self.isOnlineOnly or not self.remote:
			menuOptions.remove(MENU_FETCH_COLL)
			menuOptions.remove(MENU_FETCH_ALL_IMAGES)
		if self.isOnlineOnly or self.onlineAliasData:
			menuOptions.remove(MENU_FILTERS)

		# show this dialog and wait until it's closed
		restart = False
		selectedPos = -1	# start on exit
		while not restart:
			selectDialog = DialogSelect()
			selectDialog.setup(__language__(600), width=310, rows=len(menuOptions))
			selectedPos, action = selectDialog.ask(menuOptions, selectedPos)
			if selectedPos < 0:				# exit selected
				break

			if menuOptions[selectedPos] == MENU_VIEW_IMDB:
				if not self.onlineAliasData:
					colNo = self.lastCollNo
				else:
					colNo = self.lastOnlineCollNo
				title = self.dvdCollection.getDVDKey(colNo)[self.dvdCollection.KEYS_DATA_SORTTITLE]
				win = IMDbWin().ask(title)
				del win
			elif menuOptions[selectedPos] == MENU_VIEW_ONLINE:
				aliasData = ManageOnlineCollection().ask()
				if aliasData:							# if text entered
					self.onlineAliasData = aliasData
					restart = True
			elif menuOptions[selectedPos] == MENU_VIEW_OWN:
				self.onlineAliasData = []
				restart = True
			elif menuOptions[selectedPos] == MENU_FETCH_COLL:
				restart = self.fetchCollectionSMB(True)		# force new fetch
			elif menuOptions[selectedPos] == MENU_FILTERS:
				self.doFilters()
				break
			elif menuOptions[selectedPos] == MENU_CONFIG_MENU:
				restart = self.configMenu()
			elif menuOptions[selectedPos] == MENU_FETCH_ALL_IMAGES:
				self.fetchAllImages()
			elif menuOptions[selectedPos] == MENU_VIEW_README:
				textBoxDialog = TextBoxDialog()
				textBoxDialog.ask(file=README_FILENAME, title="Readme")
			elif menuOptions[selectedPos] == MENU_VIEW_CHANGELOG:
				textBoxDialog = TextBoxDialog()
				textBoxDialog.ask(file=CHANGELOG_FILENAME, title="ChangeLog")
		debug ("< mainMenu() restart: " + str(restart))
		return restart


	###################################################################################################
	def configMenu(self):
		debug("> configMenu() init()")

		# menu choices
		OPT_CONFIG_SMB = __language__(603)
		OPT_UPDATE_SCRIPT = __language__(631)
		OPT_UPDATE_SCRIPT_CHECK_STARTUP = __language__(632)
		OPT_CLEAR_CACHE = __language__(633)
		OPT_START_MODE = __language__(634)

		def _makeMenu():
			menu = []
			menu.append(xbmcgui.ListItem(OPT_CONFIG_SMB))
			if self.settings[self.SETTING_CHECK_SCRIPT_UPDATE_STARTUP]:
				value = __language__(350)
			else:
				value = __language__(351)
			menu.append(xbmcgui.ListItem(OPT_UPDATE_SCRIPT_CHECK_STARTUP, value))
			menu.append(xbmcgui.ListItem(OPT_UPDATE_SCRIPT))
			menu.append(xbmcgui.ListItem(OPT_CLEAR_CACHE))
			menu.append(xbmcgui.ListItem(OPT_START_MODE, self.settings[self.SETTING_START_MODE]))
			return menu

		# show this dialog and wait until it's closed
		selectedPos = 0
		restart = False
		while True:
			menu = _makeMenu()
			selectDialog = DialogSelect()
			selectDialog.setup("Config Menu",width=350, rows=len(menu))
			selectedPos, action = selectDialog.ask(menu, selectedPos)
			if selectedPos < 0:				# exit selected
				break

			selectedOpt = menu[selectedPos].getLabel()
			if selectedOpt == OPT_CONFIG_SMB:
				self.configSMB()
			elif selectedOpt == OPT_UPDATE_SCRIPT_CHECK_STARTUP:
				self.settings[self.SETTING_CHECK_SCRIPT_UPDATE_STARTUP] = xbmcgui.Dialog().yesno( __language__(0), OPT_UPDATE_SCRIPT_CHECK_STARTUP )
				saveFileObj(self.SETTINGS_FILENAME, self.settings)
			elif selectedOpt == OPT_UPDATE_SCRIPT:
				if self._update_script(False):							# never silent from config menu
					dialogOK(__language__(0),__language__(1010))
					# restart script after update
					xbmc.executebuiltin('XBMC.RunScript(%s)'%(os.path.join(DIR_HOME, 'default.py')))
					sys.exit(0)	# end current instance
			elif selectedOpt == OPT_CLEAR_CACHE:
				restart = self.clearCache()
			elif selectedOpt == OPT_START_MODE:
				menu = [ self.START_MODE_MENU, self.START_MODE_SMB, self.START_MODE_LOCAL, self.START_MODE_ONLINE]
				selectDialogStartMode = DialogSelect()
				selectDialogStartMode.setup(__language__(601),width=350, rows=len(menu))
				selectedPos, action = selectDialogStartMode.ask(menu)
				if selectedPos >= 0:
					self.settings[self.SETTING_START_MODE] = menu[selectedPos]
					saveFileObj(self.SETTINGS_FILENAME, self.settings)

		debug ("< configMenu().ask() restart="+str(restart))
		return restart

	#################################################################################################################
	# MENU ITEM - config SMB PC connection
	#################################################################################################################
	def configSMB(self):
		debug("> configSMB()")

		MENU_OPT_SMB_USE = __language__(640)
		MENU_OPT_SMB_PATH = __language__(641)
		MENU_OPT_SMB_PC_IP = __language__(642)
		MENU_OPT_SMB_DVDPRO_SHARE = __language__(643)
		MENU_OPT_SMB_MOVIES_SHARE = __language__(644)
		MENU_OPT_SMB_FILENAME = __language__(645)
		MENU_OPT_SMB_COLLECTION_DIR = __language__(646)
		MENU_OPT_SMB_IMAGES_DIR = __language__(647)
		MENU_OPT_SMB_CONN_CHECK = __language__(648)

		def _makeMenu():
			debug("_makeMenu()")
			menu = []
			if self.settings[self.SETTING_SMB_USE]:
				menu.append(xbmcgui.ListItem(MENU_OPT_SMB_USE, __language__(350)))
			else:
				menu.append(xbmcgui.ListItem(MENU_OPT_SMB_USE, __language__(351)))
			menu.append(xbmcgui.ListItem(MENU_OPT_SMB_PATH, self.settings[self.SETTING_SMB_PATH]))
			menu.append(xbmcgui.ListItem(MENU_OPT_SMB_PC_IP, self.settings[self.SETTING_SMB_PC_IP]))
			menu.append(xbmcgui.ListItem(MENU_OPT_SMB_DVDPRO_SHARE, self.settings[self.SETTING_SMB_DVDPRO_SHARE]))
			menu.append(xbmcgui.ListItem(MENU_OPT_SMB_COLLECTION_DIR, self.settings[self.SETTING_SMB_COLLECTION_DIR]))
			menu.append(xbmcgui.ListItem(MENU_OPT_SMB_IMAGES_DIR, self.settings[self.SETTING_SMB_IMAGES_DIR]))
			menu.append(xbmcgui.ListItem(MENU_OPT_SMB_FILENAME, self.settings[self.SETTING_SMB_FILENAME]))
			menu.append(xbmcgui.ListItem(MENU_OPT_SMB_MOVIES_SHARE, self.settings[self.SETTING_SMB_MOVIES_SHARE]))
			menu.append(xbmcgui.ListItem(MENU_OPT_SMB_CONN_CHECK))
			return menu

		selectedPos = -1	# start on exit
		while True:
			changed = False
			menu = _makeMenu()
			selectDialog = DialogSelect()
			selectDialog.setup(__language__(603), width=620, rows=len(menu))
			selectedPos, action = selectDialog.ask(menu, selectedPos)
			if selectedPos < 0:
				break # exit selected

			# get menu selected value
			key = menu[selectedPos].getLabel()
			value = menu[selectedPos].getLabel2()
			if value == None:
				value = ''

			debug("selected key = " + key)
			debug("selected value = " + value)
			if key == MENU_OPT_SMB_PATH:
				# this is now just the SMB base path, no sharename on end
				smbPath = doKeyboard(value, MENU_OPT_SMB_PATH, KBTYPE_ALPHA)
				smbPath, ip = getSMBPathIP(smbPath, isSMBBasePathOnly=True)
				if smbPath:
					self.settings[self.SETTING_SMB_PATH] = smbPath
				if ip:
					self.settings[self.SETTING_SMB_PC_IP] = ip
				if smbPath or ip:
					changed = True

			elif key == MENU_OPT_SMB_PC_IP:
				ip = doKeyboard(value, __language__(218), KBTYPE_IP)	# IP dialog)
				if not isIP(ip):
					messageOK(__language__(108),__language__(219))
				else:
					self.settings[self.SETTING_SMB_PC_IP] = ip
					changed = True

			elif key == MENU_OPT_SMB_FILENAME:
				filename = doKeyboard(value,__language__(220),KBTYPE_ALPHA)
				if filename:
					self.settings[self.SETTING_SMB_FILENAME] = filename
					changed = True

			elif key == MENU_OPT_SMB_COLLECTION_DIR:
				value = doKeyboard(value,__language__(221),KBTYPE_ALPHA)
				if value.endswith('/'): value = value[:-1]
				value = value.replace('\\','/')
				self.settings[self.SETTING_SMB_COLLECTION_DIR] = value
				changed = True

			elif key == MENU_OPT_SMB_IMAGES_DIR:
				value = doKeyboard(value,__language__(222),KBTYPE_ALPHA)
				if value.endswith('/'): value = value[:-1]
				value = value.replace('\\','/')
				self.settings[self.SETTING_SMB_IMAGES_DIR] = value
				changed = True

			elif key == MENU_OPT_SMB_USE:
				self.settings[self.SETTING_SMB_USE] = xbmcgui.Dialog().yesno(__language__(603), MENU_OPT_SMB_USE)
				changed = True

			elif key == MENU_OPT_SMB_DVDPRO_SHARE:
				value = doKeyboard(value, MENU_OPT_SMB_DVDPRO_SHARE, KBTYPE_ALPHA)
				if value:
					if value.endswith('/'): value = value[:-1]
					value = value.replace('\\','/')
					self.settings[self.SETTING_SMB_DVDPRO_SHARE] = value
					changed = True

			elif key == MENU_OPT_SMB_MOVIES_SHARE:
				value = doKeyboard(value, MENU_OPT_SMB_MOVIES_SHARE, KBTYPE_ALPHA)
				if value:
					if value.endswith('/'): value = value[:-1]
					value = value.replace('\\','/')
					self.settings[self.SETTING_SMB_MOVIES_SHARE] = value
					changed = True

			elif key == MENU_OPT_SMB_CONN_CHECK:
				smbPath = "%s/%s" % (self.settings[self.SETTING_SMB_PATH], self.settings[self.SETTING_SMB_DVDPRO_SHARE])
				remote, remoteInfo = smbConnect(self.settings[self.SETTING_SMB_PC_IP],smbPath)
				if remote and remoteInfo:
					messageOK(__language__(648),__language__(201), smbPath)

			if changed:
				saveFileObj(self.SETTINGS_FILENAME, self.settings)

		debug ("< configSMB changed="+str(changed))
		return changed

	#################################################################################################################
	def clearCache(self):
		debug("> clearCache()")
		success = False
		try:
			title = __language__(631).replace('?','')
			if xbmcgui.Dialog().yesno(title, __language__(223)):
				debug("rmtree " + DIR_IMG_CACHE)
				rmtree( DIR_IMG_CACHE )
				time.sleep(1)
				debug("makeDir " + DIR_IMG_CACHE)
				makeDir( DIR_IMG_CACHE )

			if xbmcgui.Dialog().yesno(title, __language__(224)):
				debug("rmtree " + DIR_CACHE)
				rmtree( DIR_CACHE )
				time.sleep(1)
				debug("makeDir " + DIR_CACHE)
				makeDir( DIR_CACHE )
		except:
			handleException()
		else:
			success = True

		debug("< clearCache() success="+str(success))
		return success


###################################################################################################
class DVDCollectionXML:
	def __init__(self, filename):
		debug("DVDCollectionXML().__init__")
		self.localCollectionFilename = filename

		# keys dict - [collNum] = [title, id, ...]
		DVDCollectionXML.KEYS_DATA_SORTTITLE = 0
		DVDCollectionXML.KEYS_DATA_ID = 1
		DVDCollectionXML.KEYS_DATA_GENRES = 2
		DVDCollectionXML.KEYS_DATA_TAGS = 3

		# DICT KEYS
		DVDCollectionXML.COLLNUM = 'collnum'
		DVDCollectionXML.ID = 'id'
		DVDCollectionXML.TITLE = 'title'
		DVDCollectionXML.SORTTITLE = 'sorttitle'
		DVDCollectionXML.GENRE = 'Genre'
		DVDCollectionXML.TAG = 'Tag'
		DVDCollectionXML.OVERVIEW = 'Overview'
		DVDCollectionXML.EASTEREGGS = 'EasterEggs'
		DVDCollectionXML.RATING = 'Rating'
		DVDCollectionXML.PRODYEAR = 'ProductionYear'
		DVDCollectionXML.RELEASED = 'Released'
		DVDCollectionXML.RUNNINGTIME = 'RunningTime'
		DVDCollectionXML.VIDEOFORMAT_ASPECT = 'VideoFormatAspect'
		DVDCollectionXML.VIDEOFORMAT_STD = 'VideoFormatStd'
		DVDCollectionXML.VIDEOFORMAT_IS16x9 = 'VideoFormatIs16x9'
		DVDCollectionXML.AUDIOFORMAT = 'AudioFormat'
		DVDCollectionXML.STUDIO = 'Studio'
		DVDCollectionXML.ACTORS = 'Actors'
		DVDCollectionXML.CREDITS = 'Credits'
		DVDCollectionXML.REGION = 'Region'
		DVDCollectionXML.REVIEW = 'Review'
		DVDCollectionXML.LOCATION = 'Location'

		DVDCollectionXML.GENRE_NONE = 'Unspecified genre'
		self.dvdDict = {}
		self.keys = {}
		self.filterGenres = []
		self.filterTags = []


		if fileExist(COLLECTION_FLAT_FILE) and fileExist(KEYS_FILE):
			dialogProgress.create(__language__(225),__language__(226))
			self.loadKeys()
		elif fileExist(self.localCollectionFilename):
			dialogProgress.create(__language__(225),__language__(227))
			self.saveFlatFile()
			dialogProgress.update(50,__language__(228))
			self.saveKeys()
			dialogProgress.update(50,__language__(228))

		if self.keys:
			dialogProgress.update(100,__language__(203))	# success
		else:
			dialogProgress.update(100,__language__(202))	# failed

		if Emulating:
			print "filterGenres=", self.filterGenres
			print "filterTags=", self.filterTags

		dialogProgress.close()


	##############################################################################################
	def saveFlatFile(self):
		debug("> saveFlatFile()")

		try:
			self.regexDict = {
						self.ID : '<ID>(.*?)</',
						self.TITLE : '<Title>(.*?)</',
						self.SORTTITLE : '<SortTitle>(.*?)</',
						self.GENRE : '<Genres>(.*?)</Genres>',
						self.OVERVIEW : '<Overview>(.*?)</Overview>',
						self.EASTEREGGS : '<EasterEggs>(.*?)</EasterEggs>',
						self.RATING : '<Rating>(.*?)</Rating>',
						self.PRODYEAR : '<ProductionYear>(.*?)</ProductionYear>',
						self.RELEASED : '<Released>(.*?)</Released>',
						self.RUNNINGTIME : '<RunningTime>(.*?)</RunningTime>',
						self.VIDEOFORMAT_ASPECT : '<FormatAspectRatio>(.*?)<',
						self.VIDEOFORMAT_STD : '<FormatVideoStandard>(.*?)<',
						self.VIDEOFORMAT_IS16x9 : '<Format16X9>(.*?)<',
						self.AUDIOFORMAT : '<AudioFormat>(.*?)</AudioFormat>',
						self.STUDIO : '<Studios>(.*?)</Studios>',
						self.REGION : '<Region>(.*?)</Region>',
						self.REVIEW : '<Review>(.*?)</Review>',
						self.LOCATION : '<Location>(.*?)</Location>'
						}

			# different re for each version
			if self.isV2XML():
				self.regexDict[self.ACTORS] = '<Actor>.*?<FirstName>(.*?)</.*?<LastName>(.*?)</.*?(?:<Role>(.*?)|)</'
				self.regexDict[self.CREDITS] =  '<Credit>.*?<FirstName>(.*?)<.*?<LastName>(.*?)<.*?<CreditSubtype>(.*?)<'
				self.regexDict[self.TAG] =  '<FullyQualifiedName>(.*?)<'
			else:
				self.regexDict[self.ACTORS] = '<Actor FirstName="(.*?)".*?LastName="(.*?)".*?Role="(.*?)"'
				self.regexDict[self.CREDITS] =  '<Credit FirstName="(.*?)".*?LastName="(.*?)".*?CreditSubtype="(.*?)"'
				self.regexDict[self.TAG] =  '<Tag Name.*?FullName="(.*?)"'

			fpDict = {}
			f = open(COLLECTION_FLAT_FILE,'w')

			self.keys = {}
			self.filterTags = []
			self.filterGenres = []
			section = []
			found = False
			replaceRE = re.compile('(<Locks>.*?</Locks>)', re.DOTALL + re.IGNORECASE + re.MULTILINE)
			collnumRE = re.compile('<CollectionNumber>(.*?)</', re.DOTALL + re.IGNORECASE + re.MULTILINE)

			for line in open(self.localCollectionFilename,'r'):
				if not found:
					if line.strip() == '<DVD>':
						found = True
						section = []
					continue
				elif line.strip() != '</DVD>':
					section.append(line)				# store line
					continue

				# process DVD XML section
				if found and section:
					data = '\n'.join(section)
					found = False
					dvdDict = {}

					# make sure this is owned
					matches = collnumRE.findall(data)
					if not matches:
						continue
					else:
						collnum = matches[0]

					dvdDict[self.COLLNUM] = [collnum]

					# remove LOCKS section
					data = replaceRE.sub('', data)

					# load dict with a list for each key
					for key, regex in self.regexDict.items():
						findRe = re.compile(regex, re.DOTALL + re.IGNORECASE + re.MULTILINE)
						matches = findRe.findall(data)
						matchList = []
						for match in matches:
							if not isinstance(match,str):
								matchList.append(match)		# saved as a list
							else:
								# split on newline, may give several <name>data</name>, then clean
								items = match.split('\n')
								cleanItemsList = []
								for item in items:
									cleanItem = cleanHTML(item)
									if cleanItem:
										cleanItemsList.append(cleanItem)

								matchList.extend(cleanItemsList)

						if matchList:
							dvdDict[key] = matchList

					if dvdDict:
						# save to file
#						print "save dvd to flat file"
						rec = self.COLLNUM+'|'+collnum
						for key,value in dvdDict.items():
							if not isinstance(value,str):					# is a list
								if isinstance(value[0],str):				# list of strs
									rec += '~'+key+'|'+'^'.join(value)
								else:										# list of lists
									for subValue in value:					# save each sublist with key name
										rec += '~'+key+'|'+'^'.join(subValue)
							else:
								rec += '~'+key+'|'+value

						f.write(decodeEntities(rec).replace('\n',' ').strip()+'\n')

						# save genre, further split to individual unique genre list
						if dvdDict.has_key(self.GENRE):
#							print "save genres"
							keyData = dvdDict[self.GENRE]
							for value in keyData:
								genreList = value.split(',')
								for split in genreList:
									try:
										self.filterGenres.index(split)
									except:
										self.filterGenres.append(split)

						# save tags
						if dvdDict.has_key(self.TAG):
#							print "save tags"
							keyData = dvdDict[self.TAG]
							for value in keyData:
								try:
									self.filterTags.index(value)
								except:
									self.filterTags.append(value)

						# save keys
						rec = [dvdDict[self.SORTTITLE][0],dvdDict[self.ID][0]]
						try:
							rec.append(dvdDict[self.GENRE])
						except:
							rec.append([])

						try:
							rec.append(dvdDict[self.TAG])
						except:
							rec.append([])
						self.keys[int(collnum)] = rec

			f.close()
		except:
			handleException("saveFlatFile()")

		debug("< saveFlatFile()")

	##############################################################################################
	def saveKeys(self):
		debug("> saveKeys()")
		try:
			f = open(KEYS_FILE,'w')
			if self.filterGenres:
				f.write('genres|'+(','.join(self.filterGenres))+'\n')
			if self.filterTags:
				f.write('tags|'+(','.join(self.filterTags))+'\n')
			if self.keys:
				for key,value in self.keys.items():
					if isinstance(value, str):
						f.write('keys|'+str(key)+','+value+'\n')
					else:
						rec = 'keys|'+str(key)
						for item in value:
							if isinstance(item, str):
								rec += ','+item
							else:
								rec += ','+('^'.join(item))

						f.write(rec+'\n')
			f.close()
		except:
			handleException("saveKeys()")
		debug("< saveKeys()")

	##############################################################################################
	def loadKeys(self):
		debug("> loadKeys()")

		try:
			for line in open(KEYS_FILE,'r'):
				rec = line.strip().split('|')
				if rec[0] == 'genres':
					self.filterGenres = rec[1].split(',')
				elif rec[0] == 'tags':
					self.filterTags = rec[1].split(',')
				elif rec[0] == 'keys':
					# dict key is collnum. each rec pos +1 as prefixed by collnum
					splits = rec[1].split(',')
					collnum = int(splits[0])
					keysList = [splits[self.KEYS_DATA_SORTTITLE+1],
								splits[self.KEYS_DATA_ID+1]]
					if splits[self.KEYS_DATA_GENRES+1]:
						keysList.append(splits[self.KEYS_DATA_GENRES+1].split('^'))
					else:
						keysList.append([])
					
					if splits[self.KEYS_DATA_TAGS+1]:
						keysList.append(splits[self.KEYS_DATA_TAGS+1].split('^'))
					else:
						keysList.append([])

					self.keys[collnum] = keysList
		except:
			handleException("loadKeys()")

		debug("< loadKeys()")


	##############################################################################################
	def getFileSize(self):
		try:
			return (os.stat(self.localCollectionFilename).st_size / 1024) / 1024	# into kb
		except:
			return 0


	##############################################################################################
	# sets a dict of selected DVD from stored collection
	##############################################################################################
	def parseDVD(self, collNum):
		debug("> parseDVD() collNum="+str(collNum))

		success = False
		self.dvdDict = {}
		regex = re.compile('(.*?)\|(.*?)(?:~|$)')
		for line in open(COLLECTION_FLAT_FILE,'r'):
			if line.startswith(self.COLLNUM+'|'+ collNum):
				matches = regex.findall(line)
				for key,value in matches:
					keyCount = line.count(key+'|')		# how many of this key stored ?
					subSplits = value.split('^')
					if not self.dvdDict.has_key(key):
						if keyCount == 1:
							self.dvdDict[key] = subSplits
						else:
							self.dvdDict[key] = [subSplits]
					else:
						try:
							self.dvdDict[key].append(subSplits)
						except: pass
#							print "ignored 2nd subSplits=", subSplits

				break


		if self.dvdDict:
			self.dvdDict[self.COLLNUM] = [collNum]
			success = True

		debug("< parseDVD() success="+str(success))
		return success


	##############################################################################################
	def getCollectionSize(self):
		sz = len(self.keys)
		debug("getCollectionSize() sz=" + str(sz))
		return sz

	##############################################################################################
	def getDVDData(self, dataKey):
		return self.dvdDict[dataKey]

	##############################################################################################
	def getDVDKey(self, collnum):
		try:
			return self.keys[int(collnum)]
		except:
			return None

	##############################################################################################
	# True = v2
	# False = v3+
	##############################################################################################
	def isV2XML(self):
		isV2 = False
		if fileExist(self.localCollectionFilename):
			lineCount = 0
			for line in open(self.localCollectionFilename,'r'):
				if find(line,'Version 2') >= 0:
					isV2 = True
					break
				elif lineCount >= 3:
					break
				else:
					lineCount += 1

		debug("isV2XML() "+str(isV2))
		return isV2

###################################################################################################
class DVDCollectionOnline:
	def __init__(self, aliasData):
		debug("DVDCollectionOnline().__init__")
		self.alias,aliasURL = aliasData

		# keys dict - [collNum] = [title, id]
		DVDCollectionOnline.KEYS_DATA_SORTTITLE = 0
		DVDCollectionOnline.KEYS_DATA_ID = 1

		# DICT KEYS
		DVDCollectionOnline.ID = 'id'
		DVDCollectionOnline.TITLE = 'title'
		DVDCollectionOnline.GENRE = 'Genre'
		DVDCollectionOnline.OVERVIEW = 'Overview'
		DVDCollectionOnline.RATING = 'Rating'
		DVDCollectionOnline.PRODYEAR = 'ProductionYear'
		DVDCollectionOnline.RELEASED = 'Released'
		DVDCollectionOnline.RUNNINGTIME = 'RunningTime'
		DVDCollectionOnline.VIDEOFORMAT = 'VideoFormat'
		DVDCollectionOnline.AUDIOFORMAT = 'AudioFormat'
		DVDCollectionOnline.STUDIO = 'Studio'
		DVDCollectionOnline.ACTORS = 'Actors'
		DVDCollectionOnline.CREDITS = 'Credits'
		DVDCollectionOnline.FEATURES = 'Features'
		DVDCollectionOnline.REGION = 'Region'

		self.regexDict = {
					self.GENRE : '>Genres<.+?f2">(.*?)</SPAN',
					self.OVERVIEW : '>SRP:<.+?<TD class="stylearea" colSpan="2">.+?f2">(.*?)<',
					self.RATING : 'Rating:<.+?f2">(.*?)</SPAN',
					self.PRODYEAR : 'Year:<.+?f2">(.*?)</SPAN',
					self.RELEASED : 'Release:<.+?f2">(.*?)</SPAN',
					self.RUNNINGTIME : 'Time:<.+?f2">(.*?)</SPAN',
					self.REGION : 'Coding:<.+?f2">(.*?)</SPAN',
					self.VIDEOFORMAT : 'Video.*?Formats:<.+?f2">(.*?)</SPAN',
					self.AUDIOFORMAT : 'Audio.*?Tracks<.+?f2">(.*?)</SPAN',
					self.STUDIO : '>Studios<.+?f2">(.*?)</SPAN',
					self.ACTORS : 'Actors<.+?f2">(.*?)</SPAN',
					self.CREDITS : 'Credits:<.+?f2">(.*?)</SPAN',
					self.FEATURES : '>Features<.+?f2">(.*?)</SPAN'
					}

		self.URL = aliasURL + "/DVDCollection.aspx/"
		self.URL_TITLES = aliasURL + "/onlinecollections/dvd/PlumPeachy/List.aspx?type=a&Sort=ta"
		self.URL_DVD = aliasURL + "/onlinecollections/dvd/PlumPeachy/DVD.aspx?U="
		self.FILENAME_ONLINE_COLLECTION = os.path.join(DIR_CACHE, 'online_titles.html')
		self.FILENAME_DVD = os.path.join(DIR_CACHE , 'online_dvd.html')

		self.dvdDict = {}
		self.keys = {}
		self.filterGenres = []
		self.filterTags = []

		self.fetchCollection()
		self.extractKeys()

	###################################################################################################
	def fetchCollection(self):
		debug ("> fetchCollectionOnline()")
		success = False
		html = ''

		deleteFile(self.FILENAME_ONLINE_COLLECTION)
		deleteFile(self.FILENAME_DVD)
		dialogProgress.create(__language__(229),__language__(230) + self.alias)

		html = fetchCookieURL(self.URL + self.alias)
		if html:
			# check if known alias
			if find(html,'Unknown Alias') >= 0:
				dialogOK(__language__(229), __language__(109) + self.alias)
			elif find(html,'Empty Online') >= 0:
				dialogOK(__language__(229), __language__(110) +  self.alias)
			else:
				debug("fetching data page")
				dialogProgress.update(50, __language__(231) + self.alias)

				if fetchCookieURL(self.URL_TITLES, self.FILENAME_ONLINE_COLLECTION,newRequest=False):
					success = True

				dialogProgress.update(100, __language__(203))
		dialogProgress.close()

		debug ("< fetchCollectionOnline() success="+str(success))
		return success

	###################################################################################################
	def fetchDVD(self, collNum):
		debug ("> fetchDVD() collNum="+str(collNum))

		deleteFile(self.FILENAME_DVD)
		title = self.getDVDKey(int(collNum))[self.KEYS_DATA_SORTTITLE]
		id = self.getDVDKey(int(collNum))[self.KEYS_DATA_ID]

		dialogProgress.create(__language__(229), self.alias, title)
		if fetchCookieURL(self.URL_DVD + id, self.FILENAME_DVD):
			success = True
		else:
			success = False

		dialogProgress.close()

		debug ("< fetchDVD() success="+str(success))
		return success

	##############################################################################################
	# parse DVD info
	def parseDVD(self, collNum):
		debug("> parseDVD() collNum="+str(collNum))

		self.dvdDict = {}
		if not self.fetchDVD(collNum):
			debug ("< parseDVD() failed")
			return None

		# using regex create a dict of lists
		try:
			title = self.keys[int(collNum)][self.KEYS_DATA_SORTTITLE]
			id = self.keys[int(collNum)][self.KEYS_DATA_ID]
			self.dvdDict[self.TITLE] = [title]
			self.dvdDict[self.ID] = [id]
			html = file(self.FILENAME_DVD).read()
			if html:
				# load dict with a list for each key
				for key, regex in self.regexDict.items():
					findRe = re.compile(regex, re.DOTALL + re.IGNORECASE + re.MULTILINE)
					findList = findRe.findall(html)
					matchList = []
					for matches in findList:
						matches = matches.replace('<br>','<BR>')
						replaceRE = re.compile('(<b>.*?</b>)', re.DOTALL + re.IGNORECASE + re.MULTILINE)
						groups = replaceRE.sub('', matches).split('<BR>')

						for group in groups:
							# DVD Profiler does not use HTML entities in its pages, we have to use translate manually
							cleanItem = cleanHTML(unicodeToAscii(group))
							if cleanItem:
								matchList.append([cleanItem])

					if matchList:
						self.dvdDict[key] = matchList
		except:
			handleException()
			self.dvdDict = {}

		debug("< parseDVD()")
		return self.dvdDict

	##############################################################################################
	def extractKeys(self):
		debug("> extractKeys()")
		self.keys = {}
		doc = readFile(self.FILENAME_ONLINE_COLLECTION)
		if doc:
			regex = "<A HREF=\"DVD.aspx\?U=(.*?)\" .+?entry\">(.*?)<.+?NOBR>(.*?)<.+?right\">(\d+)<"
			findRe = re.compile(regex, re.DOTALL + re.MULTILINE + re.IGNORECASE)
			matches = findRe.findall(doc)
			for match in matches:
				id = match[0]
#				DVD Profiler does not use HTML entities in its pages, we have to translate manually
				title = unicodeToAscii(match[1])
				date = match[2]
				collNum = int(match[3])
				self.keys[collNum] = [title, id, title]

		sz = len(self.keys)
		debug("< extractKeys() num keys="+str(sz))
		return sz

	##############################################################################################
	def getCollectionSize(self):
		sz = len(self.keys)
		debug("getCollectionSize() sz=" + str(sz))
		return sz

	##############################################################################################
	def getDVDData(self, dataKey):
		return self.dvdDict[dataKey]

	##############################################################################################
	def getDVDKey(self, collnum):
		try:
			return self.keys[int(collnum)]
		except:
			return None

#######################################################################################################################    
# Select/Add/Delete from list of online collections
#######################################################################################################################    
class ManageOnlineCollection:
	def __init__(self):
		debug("> ManageOnlineCollection() init()")

		self.ONLINE_FILENAME = os.path.join( DIR_USERDATA, 'online_users.dat' )
		self.TITLE = __language__(240)

		debug("< ManageOnlineCollection() init()")

	def load(self):
		debug("> load()")
		users = []
		if fileExist(self.ONLINE_FILENAME):
			for line in file(self.ONLINE_FILENAME).readlines():
				rec = line.strip().split('~')
				if len(rec) == 1:
					rec = [rec[0],BASE_URL_INTER]
				users.append(rec)
		else:
			debug("file missing: " + self.ONLINE_FILENAME)

		debug("< load() sz: " + str(len(users)))
		return users

	def save(self, users):
		debug("> save()")
		if not users:
			deleteFile(self.ONLINE_FILENAME)
		else:
			f = file(self.ONLINE_FILENAME,'w')
			for user, host in users:
				f.write(user + '~' + host+'\n')
			f.close()
		debug("< save()")

	def ask(self):
		debug("> ManageOnlineCollection().ask()")

		selectedPos = -1	# start on exit
		users = self.load()
		isDelete = False
		while True:
			aliasData = []
			selectDialog = DialogSelect()
			if isDelete:
				title = "%s (%s)" % (self.TITLE,  __language__(694))
			else:
				title = "%s - (A = %s, Y = %s, X = %s)" % (self.TITLE,__language__(696),__language__(691),__language__(694))
			selectDialog.setup(title=title, width=450, rows=len(users), \
								isDelete=isDelete, useX=True, useY=True)
			users.sort()

			selectedPos, action = (selectDialog.ask(users, selectedPos))
			if action == ACTION_PREVIOUS_MENU or action == ACTION_PARENT_DIR:
				break
			elif action == ACTION_Y_BUTTON: 	# add new
				debug("add user")
				# ALIAS
				user = doKeyboard("",__language__(241))

				# HOST URL
				if user:
					if xbmcgui.Dialog().yesno(__language__(242), \
									__language__(350) + " = " + BASE_URL_INTER, \
									__language__(351) + " = " + BASE_URL_INVOS):
						host = BASE_URL_INTER
					else:
						host = BASE_URL_INVOS

					# HOST URL
					try:
						aliasData = [user, host]
						users.index(aliasData)
						messageOK(__language__(240), __language__(111), user, host)
					except:
						users.append(aliasData)
						self.save(users)

			elif action == ACTION_X_BUTTON: 	# delete
				if len(users):
					isDelete = not isDelete
			elif selectedPos >= 0:				# select
				user, host = users[selectedPos]
				if isDelete:					# in delete mode
					if xbmcgui.Dialog().yesno(__language__(204), user, host):
						users.pop(selectedPos)
						self.save(users)
					isDelete = False
				else:
					aliasData = [user, host]
					break
			elif selectedPos < 0:				# exit
				break

			del selectDialog

		debug("< ManageOnlineCollection().ask()")
		return aliasData

#######################################################################################################################    
#
#######################################################################################################################    
class Filters(xbmcgui.WindowDialog):
	def __init__(self):
		if Emulating: xbmcgui.WindowDialog.__init__(self)
		debug("> Filters.init()")

		setResolution(self)

		# center on screen
		excess = 17
		panelW = 550
		panelH = 450
		panelX = int((REZ_W /2) - (panelW /2))
		panelY = int((REZ_H /2) - (panelH /2)) + excess

		xbmcgui.lock()

		# BACKG
		try:
			self.addControl(xbmcgui.ControlImage(panelX, panelY, panelW, panelH, PANEL_FILENAME))
		except: pass
		# shrink panel sz to allow for transparency on left/bottom that makes it bigger than it actually is
		panelW -= excess
		panelX += excess
		panelY += 8

		# TITLES/HEADINGS
		titleH = 28
		headingH = 20 

		# list dims
		listW = int(panelW/2)
		listH = int(panelH-titleH-headingH)-excess
		itemH = 20

		# TITLE
		xpos = panelX +10
		ypos = panelY
		self.addControl(xbmcgui.ControlLabel(xpos, ypos, 0, titleH,
										__language__(243), FONT14, '0xFFFFFF00'))

		# GENRES
		ypos += titleH
		self.genresHeading = xbmcgui.ControlLabel(xpos, ypos, 0, headingH,'', FONT12, '0xFFFFFF99')
		self.addControl(self.genresHeading)

		# GENRE LIST
		ypos += headingH
		self.genresCL = xbmcgui.ControlList(panelX, ypos, listW, listH, itemHeight=itemH)
		self.addControl(self.genresCL)
		try:
			self.genresCL.setPageControlVisible(False)
		except: pass

		# TAGS
		ypos = panelY + titleH
		xpos = panelX + listW - 5
		self.tagsHeading = xbmcgui.ControlLabel(xpos +10, ypos, 0, headingH,'', FONT12, '0xFFFFFF99')
		self.addControl(self.tagsHeading)

		# TAGS LIST
		ypos += headingH
		self.tagsCL = xbmcgui.ControlList(xpos, ypos, listW, listH, itemHeight=itemH)
		self.addControl(self.tagsCL)
		try:
			self.tagsCL.setPageControlVisible(False)
		except: pass

		# LISTS - control navigation
		self.genresCL.controlLeft(self.tagsCL)
		self.genresCL.controlRight(self.tagsCL)
		self.tagsCL.controlLeft(self.genresCL)
		self.tagsCL.controlRight(self.genresCL)
		self.setFocus(self.genresCL)

		xbmcgui.unlock()

		debug("< Filters.init()")

	##############################################################################################
	def onAction(self, action):
		if action == ACTION_PREVIOUS_MENU or action == ACTION_PARENT_DIR:
			self.close()

	##############################################################################################
	def onControl(self, control):
		if isinstance(control, xbmcgui.ControlList):
			lbl1 = control.getSelectedItem().getLabel()
			pos = control.getSelectedPosition()

		exit = False
		if control == self.genresCL:					# genre CL
			if pos == 0:								# exit
				exit = True
			elif pos == 1:								# select ALL
				self.setListState(self.genresDict, True)
			elif pos == 2:								# select NONE
				self.setListState(self.genresDict, False)
			elif pos == 3:								# select NONE for both filters
				self.setListState(self.tagsDict, False)
				self.setupList(self.tagsCL, self.tagsDict)
				self.setListState(self.genresDict, False)
			else:										# indivudual
				isSelected = self.genresDict[lbl1]
				isSelected = not isSelected
				self.genresDict[lbl1] = isSelected
			if not exit:
				self.setupList(self.genresCL, self.genresDict)
		elif control == self.tagsCL:					# tags CL
			if pos == 0:								# exit
				exit = True
			elif pos == 1:								# select ALL
				self.setListState(self.tagsDict, True)
			elif pos == 2:								# select NONE
				self.setListState(self.tagsDict, False)
			elif pos == 3:								# select NONE for both filters
				self.setListState(self.genresDict, False)
				self.setupList(self.genresCL, self.genresDict)
				self.setListState(self.tagsDict, False)
			else:										# indivudual
				isSelected = self.tagsDict[lbl1]
				isSelected = not isSelected
				self.tagsDict[lbl1] = isSelected
			if not exit:
				self.setupList(self.tagsCL, self.tagsDict)

		if exit:
			self.close()
		else:
			try:
				if isinstance(control, xbmcgui.ControlList):
					self.setFocus(control)
					control.selectItem(pos)
			except: pass

	##############################################################################################
	def setListState(self, dataDict, newState):
		debug("setListState() newState=" +str(newState))
		for key in dataDict.keys():
			dataDict[key] = newState

	##############################################################################################
	def updateTagsHeading(self):
		enabledCount = self.tagsDict.values().count(True)			# count enabled
		self.tagsHeading.setLabel(__language__(244) + str(enabledCount) + '\\' + str(len(self.tagsDict)))

	##############################################################################################
	def updateGenresHeading(self):
		enabledCount = self.genresDict.values().count(True)			# count enabled
		self.genresHeading.setLabel(__language__(245) + str(enabledCount) + '\\' + str(len(self.genresDict)))

	##############################################################################################
	def setupList(self, controlList, dataDict):
		debug("setupList()")
		def sortItemsAsc(x, y):
			return cmp(x[1],y[1])

		controlList.reset()

		sortList = dataDict.keys()
		sortList.sort()
		controlList.addItem(xbmcgui.ListItem(__language__(690)))
		controlList.addItem(xbmcgui.ListItem(__language__(246)))
		controlList.addItem(xbmcgui.ListItem(__language__(247)))
		controlList.addItem(xbmcgui.ListItem(__language__(248)))  # cancels in both filters

		for key in sortList:
			if dataDict[key]:
				if not Emulating:
					controlList.addItem(xbmcgui.ListItem(key, thumbnailImage=TICK_FILENAME))
				else:
					controlList.addItem(xbmcgui.ListItem(key, 'X'))
			else:
				controlList.addItem(xbmcgui.ListItem(key))

		self.updateTagsHeading()
		self.updateGenresHeading()

	##############################################################################################
	def ask(self, genres, tags):
		debug ("> ask()")
		self.genresDict = genres
		self.tagsDict = tags

		self.setupList(self.genresCL, self.genresDict)
		self.setupList(self.tagsCL, self.tagsDict)
		self.doModal()

		# just return selected list from each filter dict
		selectedGenres = []
		for genre, state in self.genresDict.items():
			if state:
				selectedGenres.append(genre)

		selectedTags = []
		for tag, state in self.tagsDict.items():
			if state:
				selectedTags.append(tag)

		debug ("< ask()")
		return selectedGenres, selectedTags

######################################################################################
def update_script(quite=False, notifyNotFound=False):
	xbmc.output( "> update_script() quite=%s" %quite)

	updated = False
	up = update.Update(__language__, __scriptname__)
	version = up.getLatestVersion(quite)
	xbmc.output("Current Version: " + __version__ + " Tag Version: " + version)
	if version != "-1":
		if __version__ < version:
			if xbmcgui.Dialog().yesno( __language__(0), \
								"%s %s %s." % ( __language__(1006), version, __language__(1002) ), \
								__language__(1003 )):
				updated = True
				up.makeBackup()
				up.issueUpdate(version)
		elif notifyNotFound:
			dialogOK(__language__(0), __language__(1000))
#	elif not quite:
#		dialogOK(__language__(0), __language__(1030))				# no tagged ver found

	del up
	xbmc.output( "< _update_script() updated=%s" % updated)
	return updated

#############################################################################################
# BEGIN !
#############################################################################################
dvdpro = DVDProfiler()
if dvdpro.isReady():
	dvdpro.doModal()
del dvdpro

moduleList = ['dvdproLib', 'bbbLib', 'smbLib', 'IMDbWin', 'IMDbLib']
for m in moduleList:
	try:
		del sys.modules[m]
		debug("del sys.module: " + m)
	except: pass

# remove other globals
try:
	del dialogProgress
except: pass
try:
	del __language__
except: pass

# goto xbmc home window
#try:
#	xbmc.executebuiltin('XBMC.ReplaceWindow(0)')
#except: pass
