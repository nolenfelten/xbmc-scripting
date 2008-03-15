"""
    A script to display a wealth of UK Football related information. Powered by BBC Sport.

	Written By BigBellyBilly
	bigbellybilly AT gmail DOT com	- bugs, comments, ideas, help ...

	THANKS:
	To everyone who's ever helped in anyway, or if I've used code from your own scripts, MUCH APPRECIATED!

	CHANGELOG: see changelog.txt or view throu Settings Menu
	README: see ..\resources\language\<language>\readme.txt or view throu Settings Menu

    Additional support may be found on xboxmediacenter forum.	
"""

import xbmc, xbmcgui
import sys, os.path
import re, os, time, datetime, traceback
from string import rjust,replace,split, upper, lower, capwords,find
from datetime import date
from threading import Thread

# Script doc constants
__scriptname__ = "Football"
__version__ = '1.4'
__author__ = 'BigBellyBilly [BigBellyBilly@gmail.com]'
__date__ = '13-03-2008'
xbmc.output(__scriptname__ + " Version: " + __version__ + " Date: " + __date__)

# Shared resources
DIR_HOME = os.getcwd().replace( ";", "" )
DIR_RESOURCES = os.path.join( DIR_HOME , "resources" )
DIR_RESOURCES_LIB = os.path.join( DIR_RESOURCES , "lib" )
DIR_USERDATA = os.path.join( "T:\\script_data", __scriptname__ )
DIR_GFX = os.path.join(DIR_RESOURCES,'gfx')
DIR_TEAM_GFX = os.path.join(DIR_RESOURCES,'team_gfx')
sys.path.insert(0, DIR_RESOURCES_LIB)

# Custom libs
import language
mylanguage = language.Language()
__language__ = mylanguage.localized

import update                                       # script update module
from bbbLib import *								# requires __language__ to be defined
from bbbGUILib import *

# dialog object for the whole app
dialogProgress = xbmcgui.DialogProgress()
INIT_NONE = 0
INIT_DISPLAY = 1
INIT_PART = 2
INIT_FULL = 3

BUTTON_FOCUS_LONG=os.path.join(DIR_GFX, 'button-focus-long.jpg')
BUTTON_FOCUS=os.path.join(DIR_GFX,'button-focus.jpg')

global timerthread
timerthread = None

try: Emulating = xbmcgui.Emulating
except: Emulating = False

#################################################################################################################
# MAIN
#################################################################################################################
class Football(xbmcgui.Window):
	def __init__(self):
		if Emulating: xbmcgui.Window.__init__(self)
		debug("> Football()")

		setResolution(self)

		self.SETTINGS_FILENAME = os.path.join( DIR_USERDATA, "settings.txt" )
		# settings keys
		self.SETTING_START_MODE = "start_mode"
		self.SETTING_CHECK_SCRIPT_UPDATE_STARTUP = "check_script_update_startup"
		# setting default values
		self.SETTING_VALUE_START_MODE_MENU = "MENU"
		# settings defaults
		self.SETTINGS_DEFAULTS = {
			self.SETTING_CHECK_SCRIPT_UPDATE_STARTUP : False,	# No
			self.SETTING_START_MODE : self.SETTING_VALUE_START_MODE_MENU,
			}

		self.settings = {}
		self._initSettings(forceReset=False)

		self.SETTINGS_LEAGUES_FILENAME = os.path.join( DIR_USERDATA, "league_%s.txt" )

		# check for script update
		scriptUpdated = False
		if self.settings[self.SETTING_CHECK_SCRIPT_UPDATE_STARTUP]:	# check for update ?
			scriptUpdated = update_script(False, False)

		if scriptUpdated:
			self.close()
			return

		self.DATASOURCE_BBC = __language__(330)
		self.DATASOURCE_SOCSTND = __language__(331)

		# used to calc string width based on each char width
		self.font = FontAttr()
		self.liveTextUpdateURL = ''		# saved (fully formed) url for livetext updates

		# EXTRA URL INFOS
		self.BBC_MMS_URL_PREFIX = 'mms://wm.bbc.net.uk/$SUBAREA'	# replace subarea, eg 'news'
		self.BBC_NEWS_URL_PREFIX = 'http://news.bbc.co.uk'				# news site prefix
		self.BBC_URL_PREFIX = 'http://bbc.co.uk'

		# vars for nav list / content
		self.contentControls = [] 			# central content controls
		self.contentFocusIdx = 0			# which control to focus on when switching to content
		self.contentData = []				# extra data store for content use
		self.focusNavLists = True
		self.loadLeagueTeamsConfig()		# load known team in leagues

		self.CONTENT_REC_CONTROL = 0		# rec of contentControls [ctrl, data]
		self.CONTENT_REC_DATA = 1

		self.NAV_LISTS_DATA_REC_X = 0
		self.NAV_LISTS_DATA_REC_Y = 1
		self.NAV_LISTS_DATA_REC_W = 2
		self.NAV_LISTS_DATA_REC_H = 3
		self.NAV_LISTS_DATA_REC_SELECTED = 4
		self.NAV_LIST_ATTRIBS = 'ATTRIBS'
		self.NAV_LIST_MENU = 'MENU'
		self.NAV_LISTS_ITEM_REC_NAME = 0	# all navlists data store have name in this pos

		# KEYS TO NAV LISTS DICT
		self.LEAGUES_KEY = 'Leagues'
		self.LEAGUE_VIEW_KEY = 'League Views'
		self.TEAMS_KEY = 'Teams'
		self.TEAM_VIEW_KEY = 'Team Views'

		self.LEAGUE_ITEM_REC_LEAGUE_ID = 0
		self.LEAGUE_ITEM_REC_TABLE_PATH = 1
		self.LEAGUE_ITEM_REC_FIX_PATH = 2
		self.LEAGUE_ITEM_REC_RES_PATH = 3
		self.LEAGUE_ITEM_REC_SCORERS_PATH = 4
		self.LEAGUE_ITEM_REC_HAS_LIVESCORE = 5
		self.LEAGUE_ITEM_REC_HAS_NEWS = 6

		# common LEAGUE MENU ITEMS
		self.LEAGUE_VIDEPRINTER = __language__(530)
		self.LEAGUE_INTL = __language__(531)
		self.LEAGUE_UEFA_CUP = __language__(532)

		# common LEAGUE VIEWS MENU ITEMS
		self.LEAGUE_VIEW_TEAMS = __language__(533)
		self.LEAGUE_VIEW_TABLE = __language__(534)
		self.LEAGUE_VIEW_NEWS = __language__(535)
		self.LEAGUE_VIEW_FIX = __language__(536)
		self.LEAGUE_VIEW_RES = __language__(537)
		self.LEAGUE_VIEW_LIVE_SCORES = __language__(538)
		self.LEAGUE_VIEW_TOP_SCORERS = __language__(539)

		# common TEAM VIEWS MENU ITEMS
		self.TEAM_VIEW_NEWS = __language__(540)
		self.TEAM_VIEW_FIX = __language__(541)
		self.TEAM_VIEW_RES = __language__(542)
		self.TEAM_VIEW_LIVE_TEXT = __language__(543)
		self.TEAM_VIEW_SQUAD = __language__(544)

		# MAIN MENU
		self.MAINMENU_SELECTED = ''
		self.MAINMENU_REC_TITLE = 0
		self.MAINMENU_REC_URL = 1
		self.MAINMENU_OPT_PHOTO_GALLERY = __language__(545)
		self.MAINMENU_OPT_FFOCUS = __language__(546)
		self.MAINMENU_OPT_INTERVIEWS = __language__(547)
		self.MAINMENU_OPT_MOTD_INTERVIEWS = __language__(548)
		self.MAINMENU_OPT_SCORE_INTERVIEWS = __language__(549)
		self.MAINMENU_OPT_GRANDSTAND_INTERVIEWS = __language__(550)
		self.MAINMENU_OPT_5LIVE = __language__(551)
		self.MAINMENU_OPT_5LIVEX = __language__(552)
		self.MAINMENU_OPT_606 = __language__(553)
		self.MAINMENU_OPT_LSONTV = __language__(554)
		self.MAINMENU_OPT_606_THREAD = __language__(555)
		self.MAINMENU_OPT_GOSSIP =  __language__(556)
		self.MAINMENU_OPT_CONFIG_MENU = __language__(505)
		self.MAINMENU_URL = {
			self.MAINMENU_OPT_PHOTO_GALLERY:'http://newsrss.bbc.co.uk/rss/sportonline_uk_edition/photo_galleries/rss.xml',
#			self.MAINMENU_OPT_FFOCUS:'http://news.bbc.co.uk/sport1/hi/football/football_focus/default.stm',
			self.MAINMENU_OPT_FFOCUS:'http://newsrss.bbc.co.uk/rss/sportplayer_uk_edition/football_focus/rss.xml',
			self.MAINMENU_OPT_INTERVIEWS:'http://news.bbc.co.uk/sol/ukfs_sport/hi/av/football/bb_wm_default.stm',
			self.MAINMENU_OPT_MOTD_INTERVIEWS:'http://news.bbc.co.uk/sol/ukfs_sport/hi/av/match_of_the_day/bb_wm_default.stm',
			self.MAINMENU_OPT_SCORE_INTERVIEWS:'http://news.bbc.co.uk/sol/ukfs_sport/hi/av/score_interactive/bb_wm_default.stm',
			self.MAINMENU_OPT_GRANDSTAND_INTERVIEWS:'http://news.bbc.co.uk/sol/ukfs_sport/hi/av/grandstand/bb_wm_default.stm',
			self.MAINMENU_OPT_5LIVE:'mms://wmlive.bbc.net.uk/wms/radio5/5Live_int_s1',
			self.MAINMENU_OPT_5LIVEX:'mms://wmlive.bbc.net.uk/wms/radio5/sportsextra/5SportX_int_s1',
			self.MAINMENU_OPT_606:'http://news.bbc.co.uk/sport1/hi/football/606/default.stm',
			self.MAINMENU_OPT_LSONTV:'http://www.livesportontv.com/printsport.php?id=1',
			self.MAINMENU_OPT_GOSSIP:'http://newsrss.bbc.co.uk/rss/sportonline_uk_edition/football/gossip_and_transfers/rss.xml',
			self.MAINMENU_OPT_CONFIG_MENU:None
			}
		self.MAINMENU = [__language__(500), 	# exit
						self.MAINMENU_OPT_PHOTO_GALLERY,
						 self.MAINMENU_OPT_FFOCUS,
						 self.MAINMENU_OPT_INTERVIEWS,
						 self.MAINMENU_OPT_MOTD_INTERVIEWS,
						 self.MAINMENU_OPT_SCORE_INTERVIEWS,
						 self.MAINMENU_OPT_GRANDSTAND_INTERVIEWS,
						 self.MAINMENU_OPT_5LIVE,
						 self.MAINMENU_OPT_5LIVEX,
						 self.MAINMENU_OPT_606,
						 self.MAINMENU_OPT_LSONTV,
						 self.MAINMENU_OPT_GOSSIP,
						 self.MAINMENU_OPT_CONFIG_MENU
						]

		# some predetermined regex strings
		self.STR_SECTION_START = '<!-- S BO -->'
		self.STR_SECTION_END = '<!-- E BO -->'
		self.STR_SUB_SECTION_START = '<!-- S IINC -->'
		self.STR_SUB_SECTION_END = '<!-- E IINC -->'
		self.RE_SECTION = "%s(.*?)%s" % (self.STR_SECTION_START, self.STR_SECTION_END)
		self.RE_SUB_SECTION = "%s(.*?)%s" % (self.STR_SUB_SECTION_START, self.STR_SUB_SECTION_END)

		self.teams606 = {}
		self.URL_606 = 'http://www.bbc.co.uk/dna/606/ArticleSearchPhrase?phrase=$PHRASE&contenttype=-1&articlesortby=DateUploaded&show=50'

		# SETTINGS
		self.dataSource = self.startupMenu()
		if self.dataSource:
			self.ready = True
			# setup data and draw screen accordingly
			self.reset()

			# clock thread
			global timerthread
			timerthread=Timer(self)
			if not Emulating and timerthread:
				timerthread.start()
		else:
			self.ready = False

		debug("< Football()")

	##############################################################################################
	def isReady(self):
		return self.ready

	########################################################################################################################
	def setupDisplay(self):
		debug("> setupDisplay()")
		self.screenH = REZ_H
		self.screenW = REZ_W

		mc360 = isMC360()
		if mc360:
			self.headerH = 70
			self.footerH = 80
		else:
			self.headerH = 70
			self.footerH = 100
		self.footerY = REZ_H -self.footerH

		# DRAW AREA DIMS
		self.contentX = 0
		self.contentY = self.headerH + 1
		self.contentH = REZ_H - (self.contentY + self.footerH)
		self.contentW = REZ_W
		debug("self.contentX: " + str(self.contentX) + "  self.contentY: " + str(self.contentY) \
			+ "  self.contentH: " + str(self.contentH) + "  self.contentW: " + str(self.contentW))
		debug("self.headerH="+str(self.headerH) + " self.footerH="+str(self.footerH))

		self.navListsH = self.footerH
		self.navListsY = self.footerY + 1
		debug("navListsY: " + str(self.navListsY) + " navListsH: "+ str(self.navListsH))

		self.contentCenterX = int(self.contentW/2)
		self.contentCenterY = self.headerH + int(self.contentH/2)
		debug("contentCenterX: " + str(self.contentCenterX) + " contentCenterY: " + str(self.contentCenterY))

		xbmcgui.lock()

		if mc360:
			# gfx files come with actual MC360 installation
			try:
				debug("drawing mc360 specific gfx")
				self.addControl(xbmcgui.ControlImage(0,0, REZ_W, REZ_H, 'background-blue.png'))
				self.addControl(xbmcgui.ControlImage(70,0, 16,54, 'bkgd-whitewash-glass-top-left.png'))
				self.addControl(xbmcgui.ControlImage(86,0, 667,54, 'bkgd-whitewash-glass-top-middle.png'))
				self.addControl(xbmcgui.ControlImage(753,0, 16,54, 'bkgd-whitewash-glass-top-right.png'))
				self.addControl(xbmcgui.ControlImage(70, 427, 16,54, 'bkgd-whitewash-glass-bottom-left.png'))
				self.addControl(xbmcgui.ControlImage(86, 427, 667,54, 'bkgd-whitewash-glass-bottom-middle.png'))
				self.addControl(xbmcgui.ControlImage(753, 427, 667,54, 'bkgd-whitewash-glass-bottom-right.png'))
				self.addControl(xbmcgui.ControlImage(60,0, 32, REZ_H, 'background-overlay-whitewash-left.png'))
				self.addControl(xbmcgui.ControlImage(92,0, 628, REZ_H, 'background-overlay-whitewash-centertile.png'))
				self.addControl(xbmcgui.ControlImage(-61,0, 128, REZ_H, 'blades-runner-left.png'))
				self.addControl(xbmcgui.ControlImage(18,0, 80, REZ_H, 'blades-size4-header.png'))
				self.addControl(xbmcgui.ControlLabel(75,200,0, 0, __language(0),
													font=FONT18,textColor='0xFF000000',angle=270))
			except:
				xbmcgui.unlock()
				messageOK("MC360 Skin Error","Failed loading graphic files.","Ensure XBMC is using MC360 skin.")
		else:
			# NON MC360
			# HEADER
			try:
				self.removeControl(self.backgroundCI)
			except: pass
			try:
				self.backgroundCI = xbmcgui.ControlImage(0,0, REZ_W, REZ_H, BACKGROUND_FILENAME)
				self.addControl(self.backgroundCI)
			except: pass

			# HEADER
			try:
				self.removeControl(self.headerCI)
			except: pass
			try:
				self.headerCI = xbmcgui.ControlImage(0, 0, REZ_W, self.headerH, HEADER_FILENAME)
				self.addControl(self.headerCI)
			except: pass

			# FOOTER
			try:
				self.removeControl(self.footerCI)
			except: pass
			try:
				self.footerCI = xbmcgui.ControlImage(0, self.footerY, self.contentW, self.footerH, FOOTER_FILENAME)
				self.addControl(self.footerCI)
			except: pass

		# remove content controls & other stuff
		self.clearContentControls()

		# CLOCK
		try:
			self.removeControl(self.clockLbl)
		except: pass
		xpos = REZ_W
		ypos = 0
		self.clockLbl = xbmcgui.ControlLabel(xpos, ypos, 0, 0, \
							time.strftime("%H:%M:%S",time.localtime()), \
							FONT12, "0xFFFFFFCC",alignment=XBFONT_RIGHT)
		self.addControl(self.clockLbl)

		# VERSION
		try:
			self.removeControl(self.versionLbl)
		except: pass
		ypos += 20
		self.versionLbl = xbmcgui.ControlLabel(xpos, ypos, 0, 0, "v"+__version__, \
							FONT10, "0xFFFFFFCC",alignment=XBFONT_RIGHT)
		self.addControl(self.versionLbl)


		# DATASOURCE
		try:
			self.removeControl(self.datasourceLbl)
		except: pass
		ypos += 20
		self.datasourceLbl = xbmcgui.ControlLabel(xpos, ypos, 0, 0, self.dataSource, \
							FONT12, "0xFFFFFFCC",alignment=XBFONT_RIGHT)
		self.addControl(self.datasourceLbl)


		# LIVE TEXT LIST - created seperatly so the update thread can add data to it.
		# seperate class timer can create controls and add them to self.
		try:
			self.removeControl(self.liveTextCL)
		except: pass
		self.liveTextCL = xbmcgui.ControlList(self.contentX, self.contentY, self.contentW, self.contentH, \
							font=FONT12, itemHeight=28, \
							buttonFocusTexture=BUTTON_FOCUS_LONG, alignmentY=XBFONT_CENTER_Y)
		self.addControl(self.liveTextCL)
		self.liveTextCL.setVisible(False)
		try:
			self.liveTextCL.setPageControlVisible(False)
		except: pass

		# remove all nav lists
		for navListData in self.navLists.itervalues():
			try:
				self.removeControl(navListData[self.NAV_LISTS_VALUE_CONTROL])
			except: pass

		# change xpos,ypos held for nav lists
		# LEAGUES
		xpos = 0
		self.setNavListAttrib(self.LEAGUES_KEY, self.NAV_LISTS_DATA_REC_X, xpos)
		self.setNavListAttrib(self.LEAGUES_KEY, self.NAV_LISTS_DATA_REC_Y, self.navListsY+2)

		# LEAGUE VIEWS
		xpos += self.getNavListAttrib(self.LEAGUES_KEY, self.NAV_LISTS_DATA_REC_W)
		self.setNavListAttrib(self.LEAGUE_VIEW_KEY, self.NAV_LISTS_DATA_REC_X, xpos)
		self.setNavListAttrib(self.LEAGUE_VIEW_KEY, self.NAV_LISTS_DATA_REC_Y, self.navListsY+2)

		# TEAMS
		xpos += self.getNavListAttrib(self.LEAGUE_VIEW_KEY, self.NAV_LISTS_DATA_REC_W)
		self.setNavListAttrib(self.TEAMS_KEY, self.NAV_LISTS_DATA_REC_X, xpos)
		self.setNavListAttrib(self.TEAMS_KEY, self.NAV_LISTS_DATA_REC_Y, self.navListsY+2)

		# TEAM VIEWS
		xpos += self.getNavListAttrib(self.TEAMS_KEY, self.NAV_LISTS_DATA_REC_W)
		self.setNavListAttrib(self.TEAM_VIEW_KEY, self.NAV_LISTS_DATA_REC_X, xpos)
		self.setNavListAttrib(self.TEAM_VIEW_KEY, self.NAV_LISTS_DATA_REC_Y, self.navListsY+2)

		# setup home screen
		self.selectedNavListKey = self.LEAGUES_KEY
		self.createNavList(self.LEAGUES_KEY)
		self.loadNavList(self.LEAGUES_KEY)
		self.createNavList(self.LEAGUE_VIEW_KEY)
		self.loadNavList(self.LEAGUE_VIEW_KEY)
		self.createNavList(self.TEAMS_KEY)
		self.loadNavList(self.TEAMS_KEY)
		self.createNavList(self.TEAM_VIEW_KEY)
		self.loadNavList(self.TEAM_VIEW_KEY)
		self.setupNavListsNav()
		self.getNavListDictValue(self.LEAGUES_KEY, self.NAV_LISTS_VALUE_CONTROL).setVisible(True)
		self.getNavListDictValue(self.LEAGUE_VIEW_KEY, self.NAV_LISTS_VALUE_CONTROL).setVisible(True)
		self.setLeagueLogo()
		self.toggleNavListFocus(True)		# switch to nav lists

		xbmcgui.unlock()
		debug("< setupDisplay()")

########################################################################################################################
	def exit(self):
		debug ("exit()")
		global timerthread
		if not Emulating and timerthread:
			timerthread.stop()
		self.close()

########################################################################################################################
	def onAction(self, action):
		debug ("onAction() action=%s" % action)
		if not action:
			return

		if action == ACTION_BACK:		# exit directly
			debug("ACTION_BACK")
			self.exit()
		elif action == ACTION_B:		# GO BACK
			debug("ACTION_B")
			if self.MAINMENU_SELECTED:
				debug("MAINMENU_SELECTED")
				# MAINMENU active
				if self.MAINMENU_SELECTED == self.MAINMENU_OPT_GOSSIP:
					debug("onAction MAINMENU_OPT_GOSSIP")
					self.getGossipTransferDates()
				elif self.MAINMENU_SELECTED == self.MAINMENU_OPT_606_THREAD:
					debug("onAction MAINMENU_OPT_606_THREAD")
					if self.setup606():
						self.MAINMENU_SELECTED = self.MAINMENU_OPT_606
				elif self.MAINMENU_SELECTED == self.MAINMENU_OPT_PHOTO_GALLERY:
					debug("onAction MAINMENU_OPT_PHOTO_GALLERY")
					self.getPhotoGalley()
			else:
				# NOT MAINMENU
				debug("not MAINMENU_SELECTED")
				if not self.focusNavLists:
					if (self.selectedNavListKey == self.TEAM_VIEW_KEY and \
						self.getNavListAttrib(self.TEAM_VIEW_KEY, self.NAV_LISTS_DATA_REC_SELECTED) == self.TEAM_VIEW_SQUAD):
						debug("go back to navlist")
						self.toggleNavListFocus(True)		# switch to nav lists
						self.navListSelected()				# causes refetch
						self.toggleNavListFocus(False)		# switch back to content
		elif action == ACTION_X:
			debug("ACTION_X")
			self.toggleNavListFocus(isLiveText=timerthread.isCountDownRunning())
		elif action in CONTEXT_MENU:
			debug("CONTEXT_MENU")
			self.MAINMENU_SELECTED, reInitLevel = self.mainMenu()
			if reInitLevel == INIT_FULL:
				self.reset()
			elif reInitLevel == INIT_DISPLAY:
				self.setupDisplay()

########################################################################################################################
	def onControl(self, control):
		debug("onControl()")

		# is it a NAV LISTS
		if self.focusNavLists:
			debug("NAV LIST CONTROL")
			for key, data in self.navLists.items():
				if control == data[self.NAV_LISTS_VALUE_CONTROL]:
					self.MAINMENU_SELECTED = ''		# reset
					self.selectedNavListKey = key
					selectedItem = control.getSelectedItem().getLabel()
					self.setNavListAttrib(key, self.NAV_LISTS_DATA_REC_SELECTED, selectedItem)
					self.navListSelected()
					self.setLeagueLogo()
					# set focus to newly selected navlist
					self.setFocus(self.getNavListDictValue(self.selectedNavListKey, self.NAV_LISTS_VALUE_CONTROL))
					break
		else:
			debug("CONTENT CONTROL")
			self.contentSelected()

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
				debug( "setting reset: key=%s = %s " % (key, defaultValue))

		if changed or not fileExist(self.SETTINGS_FILENAME):
			saveFileObj(self.SETTINGS_FILENAME, self.settings)

		debug( "< _initSettings() changed="+str(changed))
		return changed

	##############################################################################################
	def reset(self):
		debug("> reset()")

		# start according to startupMode
		if self.dataSource == self.DATASOURCE_BBC:								# BBC
			self.sourceBBC()
		elif self.dataSource == self.DATASOURCE_SOCSTND:						# SOCER
			self.sourceSoccerStand()

		# dict of nav lists - which can only be done after datasource selected
		self.setupNavListDict()
		self.setupDisplay()

		debug("< reset()")

	##############################################################################################
	def startupMenu(self):
		debug("> startupMenu()")
		menu = [ __language__(500), self.DATASOURCE_BBC, self.DATASOURCE_SOCSTND]
		selectedPos = 0
		dataSource = self.settings[self.SETTING_START_MODE]
		if dataSource == self.SETTING_VALUE_START_MODE_MENU:
			selectDialog = DialogSelect()
			selectDialog.setup("Select Data Source:", width=300, rows=len(menu),banner=LOGO_FILENAME)
			selectedPos, action = selectDialog.ask(menu, selectedPos)
			if selectedPos == 0:
				dataSource = None
			else:
				dataSource = menu[selectedPos]

		debug("< startupMenu() dataSource=%s" % dataSource)
		return dataSource


	########################################################################################################################
	def sourceBBC(self):
		debug("> sourceBBC()")
		self.dataSource = self.DATASOURCE_BBC

		# LEAGUES
		LEAGUE_PREM = __language__(557)
		LEAGUE_CHAMP= __language__(558)
		LEAGUE_1 = __language__(559)
		LEAGUE_2 = __language__(560)
		LEAGUE_CONF = __language__(561)
		LEAGUE_SPL = __language__(562)
		LEAGUE_SDIV1 = __language__(563)
		LEAGUE_SDIV2 = __language__(564)
		LEAGUE_SDIV3 = __language__(565)
		LEAGUE_SHIGHL = __language__(566)
		LEAGUE_WELSH = __language__(567)
		LEAGUE_IRISH = __language__(568)
		LEAGUE_SCOT_CUP = __language__(569)
		LEAGUE_SCOT_LEAGUE_CUP = __language__(570)
		LEAGUE_CHAMPIONSL = __language__(571)
		LEAGUE_WOMEN = __language__(572)
		LEAGUE_AUSTRIA = __language__(573)
		LEAGUE_BELGIUM = __language__(574)
		LEAGUE_DENMARK = __language__(575)
		LEAGUE_FINLAND = __language__(576)
		LEAGUE_FRANCE = __language__(577)
		LEAGUE_GERMANY = __language__(578)
		LEAGUE_GREECE = __language__(579)
		LEAGUE_HOLLAND = __language__(580)
		LEAGUE_ITALY = __language__(581)
		LEAGUE_NORWAY = __language__(582)
		LEAGUE_PORTUGAL = __language__(583)
		LEAGUE_SPAIN = __language__(584)
		LEAGUE_SWEDEN = __language__(585)
		LEAGUE_SWISS = __language__(586)
		LEAGUE_TURKEY = __language__(587)
		LEAGUE_AFRICAN = __language__(588)

		# this is the order that the menu items will appear in
		LEAGUES_MENU = [LEAGUE_PREM,LEAGUE_CHAMP,LEAGUE_1,LEAGUE_2,
			LEAGUE_CONF,LEAGUE_SPL,LEAGUE_SDIV1,LEAGUE_SDIV2,LEAGUE_SDIV3,
			LEAGUE_SHIGHL,LEAGUE_WELSH,LEAGUE_IRISH,LEAGUE_SCOT_CUP,
			LEAGUE_SCOT_LEAGUE_CUP,self.LEAGUE_INTL,LEAGUE_CHAMPIONSL,self.LEAGUE_UEFA_CUP,
			LEAGUE_WOMEN,self.LEAGUE_VIDEPRINTER,
			LEAGUE_AFRICAN,LEAGUE_AUSTRIA,LEAGUE_BELGIUM,
			LEAGUE_DENMARK,LEAGUE_FINLAND,
			LEAGUE_FRANCE ,LEAGUE_GERMANY,LEAGUE_GREECE,LEAGUE_ITALY,
			LEAGUE_NORWAY,LEAGUE_PORTUGAL,LEAGUE_SPAIN,LEAGUE_SWEDEN,
			LEAGUE_SWISS,LEAGUE_TURKEY
			]

		# LEAGUES data store
		self.LEAGUES_DATA = {
			self.NAV_LIST_ATTRIBS : [0, 0, 160, 120, LEAGUE_PREM], # name,x,y,w,h,selectedItem
			self.NAV_LIST_MENU : LEAGUES_MENU,
			LEAGUE_PREM : ['eng_prem','table','fixtures','results','top_scorers',True,True],
			LEAGUE_CHAMP : ['eng_div_1','table','fixtures','results','top_scorers',True,True],
			LEAGUE_1 : ['eng_div_2','table','fixtures','results','top_scorers',True,True],
			LEAGUE_2 : ['eng_div_3','table','fixtures','results','top_scorers',True,True],
			LEAGUE_CONF : ['eng_conf','conference_table','conf_fixtures','conf_results','conf_scorers',True,True],
			LEAGUE_SPL : ['scot_prem','table','fixtures','results','top_scorers',True,True],
			LEAGUE_SDIV1 : ['scot_div_1','div_1_table','div_1_fixtures','div_1_results','div_1_scorers',True,True],
			LEAGUE_SDIV2 : ['scot_div_1','div_2_table','div_2_fixtures','div_2_results','div_2_scorers',False,True],
			LEAGUE_SDIV3 : ['scot_div_1','div_3_table','div_3_fixtures','div_3_results','div_3_scorers',False,True],
			LEAGUE_SHIGHL : ['scot_div_1','highland_lge_tab','highland_lge_fix','highland_lge_res',None,False,True],
			LEAGUE_WELSH : ['league_of_wales','table','fixtures','results',None,False,True],
			LEAGUE_IRISH : ['irish','irish_prem_tables','irish_prem_fix','irish_prem_res',None,False,True],
			LEAGUE_SCOT_CUP : ['scot_cups',None,'scottish_cup_fix','scottish_cup_res',None,True,True],
			LEAGUE_SCOT_LEAGUE_CUP : ['scot_cups',None,'league_cup_fix','league_cup_res',None,True,True],
			self.LEAGUE_INTL : ['internationals','tables','fixtures','results',None,True,True],
			LEAGUE_CHAMPIONSL : ['europe','champions_league_tables','champions_league_fixtures','champions_league_results',None,True,True],
			self.LEAGUE_UEFA_CUP : ['europe','uefa_cup_tables','uefa_cup_fixtures','uefa_cup_results',None,True,True],
			LEAGUE_WOMEN : ['women','table','fixtures','results',None,False,True],
			self.LEAGUE_VIDEPRINTER : ['http://news.bbc.co.uk/sport1/hi/football/live_videprinter/default.stm'],
			LEAGUE_AFRICAN : ['africa','','','',None, False, True],
			LEAGUE_AUSTRIA : ['europe/austria_results','tables','fixtures','/',None, False, False],
			LEAGUE_BELGIUM : ['europe/belgium_results','tables','fixtures','/',None, False, False],
			LEAGUE_DENMARK : ['europe/denmark_results','tables','fixtures','/',None, False, False],
			LEAGUE_FINLAND : ['europe/finland_results','tables','fixtures','/',None, False, False],
			LEAGUE_FRANCE : ['europe/france_results','tables','fixtures','/',None, False, False],
			LEAGUE_GERMANY : ['europe/germany_results','tables','fixtures','/',None, False, False],
			LEAGUE_GREECE : ['europe/greece_results','tables','fixtures','/',None, False, False],
			LEAGUE_ITALY : ['europe/italy_results','tables','fixtures','/',None, False, False],
			LEAGUE_NORWAY : ['europe/norway_results','tables','fixtures','/',None, False, False],
			LEAGUE_PORTUGAL : ['europe/portugal_results','tables','fixtures','/',None, False, False],
			LEAGUE_SPAIN : ['europe/spain_results','tables','fixtures','/',None, False, False],
			LEAGUE_SWEDEN : ['europe/sweden_results','tables','fixtures','/',None, False, False],
			LEAGUE_SWISS : ['europe/swiss_results','tables','fixtures','/',None, False, False],
			LEAGUE_TURKEY : ['europe/turkey_results','tables','fixtures','/',None, False, False]
			}
			
		# this is the order that the menu items will appear in
		self.LEAGUE_VIEW_MENU = [self.LEAGUE_VIEW_TABLE, self.LEAGUE_VIEW_TEAMS, self.LEAGUE_VIEW_NEWS,
							self.LEAGUE_VIEW_FIX, self.LEAGUE_VIEW_RES, self.LEAGUE_VIEW_LIVE_SCORES,
							self.LEAGUE_VIEW_TOP_SCORERS]
		self.LEAGUE_VIEW_DATA = {
			self.NAV_LIST_ATTRIBS : [0, 0, 150, 120, ''],	# name,x,y,w,h,selectedItem
			self.NAV_LIST_MENU : [],						# created according to league selected
			self.LEAGUE_VIEW_TABLE : 'http://news.bbc.co.uk/sport1/hi/football/$LEAGUE/$TABLE/default.stm',
			self.LEAGUE_VIEW_TEAMS : 'http://news.bbc.co.uk/sport1/hi/football/$LEAGUE/$TABLE/default.stm',
			self.LEAGUE_VIEW_NEWS : 'http://newsrss.bbc.co.uk/rss/sportonline_uk_edition/football/$LEAGUE/rss.xml',
			self.LEAGUE_VIEW_FIX : 'http://news.bbc.co.uk/sport1/hi/football/$LEAGUE/$FIX/default.stm',
			self.LEAGUE_VIEW_RES : 'http://news.bbc.co.uk/sport1/hi/football/$LEAGUE/$RES/default.stm',
			self.LEAGUE_VIEW_LIVE_SCORES : 'http://news.bbc.co.uk/sport1/hi/football/$LEAGUE/live_scores/default.stm',
			self.LEAGUE_VIEW_TOP_SCORERS : 'http://news.bbc.co.uk/sport1/hi/football/$LEAGUE/$SCORERS/default.stm'
			}

		# TEAMS
		self.TEAMS_DATA = {
					self.NAV_LIST_ATTRIBS : [0, 0, 125, 120,''] #name,x,y,w,h,selectedItem
					}

		TEAM_VIEWS_MENU = [self.TEAM_VIEW_NEWS,self.TEAM_VIEW_FIX,self.TEAM_VIEW_RES,
						   self.TEAM_VIEW_LIVE_TEXT,self.TEAM_VIEW_SQUAD]
		self.TEAM_VIEW_DATA = {
			self.NAV_LIST_ATTRIBS : [0, 0, 125, 120,self.TEAM_VIEW_NEWS], #name,x,y,w,h,selectedItem
			self.NAV_LIST_MENU : TEAM_VIEWS_MENU,
			self.TEAM_VIEW_NEWS : 'http://newsrss.bbc.co.uk/rss/sportonline_uk_edition/football/teams/$AZ/$TEAM/rss.xml',
			self.TEAM_VIEW_FIX : 'http://news.bbc.co.uk/sport1/hi/football/teams/$AZ/$TEAM/fixtures/default.stm',
			self.TEAM_VIEW_RES : 'http://news.bbc.co.uk/sport1/hi/football/teams/$AZ/$TEAM/results/default.stm',
			self.TEAM_VIEW_LIVE_TEXT : 'http://news.bbc.co.uk/sport1/hi/football/teams/$AZ/$TEAM/live_text/default.stm',
			self.TEAM_VIEW_SQUAD : 'http://news.bbc.co.uk/sport1/hi/football/teams/$AZ/$TEAM/squad_profiles/default.stm'
			}

		debug("< sourceBBC()")

	########################################################################################################################
	# This site offers just a list of results - but more Intl than BBC
	########################################################################################################################
	def sourceSoccerStand(self):
		debug("> sourceSoccerStand()")
		self.dataSource = self.DATASOURCE_SOCSTND

		# LEAGUES with different page names to display name
		CZECH = 'Czech Republic'
		SERB = 'Serbia'
		TOTOCUP = 'Intertoto Cup'
		EUROCUP = 'Euro Cup'
		WORLDCUP = 'World Cup'
		AFRICANCUP = 'African Cup'
		CHAMPCUP = 'Champions League'
		UEFACUP = 'UEFA Cup'
		ASIANCUP = 'Asian Cup'
		COPACUP = 'Copa Libertadores'

		# this is the order that the menu items will appear in
		LEAGUES_MENU = ['Argentina','Austria','Belgium','Belarus','Brazil','Croatia',CZECH,'Denmark','England',
			'Finland','France' ,'Germany','Greece','Holland','Iceland','Ireland','Italy','Japan','Mexico','Norway',
			'Portugal','Poland','Romania','Russia','Scotland',SERB,'Slovakia','Slovenia','Spain','Sweden',
			'Switzerland','Turkey','Ukraine','USA',
			EUROCUP, TOTOCUP, WORLDCUP, AFRICANCUP,CHAMPCUP,UEFACUP,ASIANCUP,COPACUP
			]

		# LEAGUES data store
		self.LEAGUES_DATA = {
			self.NAV_LIST_ATTRIBS : [0, 0, 160, 120, 'Argentina'], # name,x,y,w,h,selectedItem
			self.NAV_LIST_MENU : LEAGUES_MENU
			}

		for team in LEAGUES_MENU:
			self.LEAGUES_DATA[team] = [team, '', '', '///', '', False, False]

		# alter leagueID for a few whos webpage isnt same
		self.LEAGUES_DATA[CZECH] = ['czech', '', '', '///', '', False, False]
		self.LEAGUES_DATA[SERB] = ['yug', '', '', '///', '', False, False]
		self.LEAGUES_DATA[EUROCUP] = ['euro', '', '', '///', '', False, False]
		self.LEAGUES_DATA[TOTOCUP] = ['intertoto', '', '', '///', '', False, False]
		self.LEAGUES_DATA[WORLDCUP] = ['wc', '', '', '///', '', False, False]
		self.LEAGUES_DATA[AFRICANCUP] = ['nationcup', '', '', '///', '', False, False]
		self.LEAGUES_DATA[CHAMPCUP] = ['liga', '', '', '///', '', False, False]
		self.LEAGUES_DATA[UEFACUP] = ['uefa', '', '', '///', '', False, False]
		self.LEAGUES_DATA[ASIANCUP] = ['cup', '', '', '///', '', False, False]
		self.LEAGUES_DATA[COPACUP] = ['libertadores', '', '', '///', '', False, False]
			
		# this is the order that the menu items will appear in
		self.LEAGUE_VIEW_MENU = [self.LEAGUE_VIEW_RES]
		self.LEAGUE_VIEW_DATA = {
			self.NAV_LIST_ATTRIBS : [0, 0, 150, 120, ''],	# name,x,y,w,h,selectedItem
			self.NAV_LIST_MENU : [],						# created according to league selected
			self.LEAGUE_VIEW_RES :  'http://www4.soccerstand.com/$LEAGUE.php'
			}

		# TEAMS
		self.TEAMS_DATA = {
					self.NAV_LIST_ATTRIBS : [0, 0, 125, 120,''] #name,x,y,w,h,selectedItem
					}

		self.TEAM_VIEW_DATA = {
			self.NAV_LIST_ATTRIBS : [0, 0, 125, 120,self.TEAM_VIEW_NEWS], #name,x,y,w,h,selectedItem
			self.NAV_LIST_MENU : []
			}

		debug("< sourceSoccerStand()")

########################################################################################################################
	def contentSelected(self):
		debug("> contentSelected()")
		debug("contentFocusIdx=%s MAINMENU_SELECTED=%s" % (self.contentFocusIdx, self.MAINMENU_SELECTED))

		# get content control
		ctrl = self.contentControls[self.contentFocusIdx][self.CONTENT_REC_CONTROL]
		# if a list, get selected POS and ITEM
		if isinstance(ctrl, xbmcgui.ControlList):
			debug("content control is a list")
			contentSelectedPos = ctrl.getSelectedPosition()
			contentSelectedItem = ctrl.getSelectedItem().getLabel()
			debug("contentSelectedPos=%s contentSelectedItem=%s" % (contentSelectedPos,contentSelectedItem))

		# MENU
		if self.MAINMENU_SELECTED:
			debug("content was created from MainMenu")
			self.logoViewCLbl.setLabel(self.MAINMENU_SELECTED)
			contentDataRec = self.contentData[contentSelectedPos]
			try:
				title = contentDataRec[0]
				lbl2 = contentDataRec[1]
				url = contentDataRec[2]
				desc = contentDataRec[3]
				guid = contentDataRec[4]
			except:
				debug("contentDataRec not fully unpacked")

			if self.MAINMENU_SELECTED == self.MAINMENU_OPT_PHOTO_GALLERY:
				debug("self.MAINMENU_OPT_PHOTO_GALLERY")
				# determine if this is a selection from a list of galleries or a list of images
				if lower(url).endswith('.jpg'):						# IMAGE, display it
					self.logoViewCLbl.setLabel(desc)
					self.displayGalleryPhoto(url)
				elif self.getGalleryPhotoLinks(guid):			# list of photos
					self.clearContentControls()
					self.drawContentList(__language__(358), width=300, font=FONT13, x=0)
					# force selection of 1st photo
					self.contentSelected()
				try:
					self.setFocus(self.contentControls[self.contentFocusIdx][self.CONTENT_REC_CONTROL])
				except: pass
			elif self.MAINMENU_SELECTED in [self.MAINMENU_OPT_INTERVIEWS, \
											self.MAINMENU_OPT_MOTD_INTERVIEWS, \
											self.MAINMENU_OPT_SCORE_INTERVIEWS, \
											self.MAINMENU_OPT_GRANDSTAND_INTERVIEWS]:
				debug("MAINMENU - INTERVIEWS")
				# extract data associated with this selected item
				self.getInterviewMediaLink(url)
				self.toggleNavListFocus(False)		# switch back to content

			elif self.MAINMENU_SELECTED == self.MAINMENU_OPT_606:			
				debug("MAINMENU - MAINMENU_OPT_606")
				# NB. url holds 'search phrase' 
				# pop keyboard to refine search terms
				phrase = doKeyboard(url, "Refine Search Phrase")
				if phrase:
					url = self.URL_606.replace('$PHRASE',phrase)
					title = '606 Search: ' + phrase
					if self.get606Debate(url, title):
						title = self.contentData[contentSelectedPos][0]
						url = self.contentData[contentSelectedPos][2]
						self.clearContentControls()
						self.logoViewCLbl.setLabel(title)
						self.drawContentList(__language__(359),width=680,font=FONT10)
						self.MAINMENU_SELECTED = self.MAINMENU_OPT_606_THREAD
					self.toggleNavListFocus(False)		# focus content

			elif self.MAINMENU_SELECTED == self.MAINMENU_OPT_606_THREAD:			
				debug("MAINMENU - MAINMENU_OPT_606_THREAD")
				if self.show606Debate(url, title):
					self.toggleNavListFocus(False)		# switch back to content

			elif self.MAINMENU_SELECTED == self.MAINMENU_OPT_GOSSIP:			
				debug("MAINMENU - MAINMENU_OPT_GOSSIP")
				# extract data associated with this selected item
				if find(title, 'gossip') != -1:
					if self.getGossip(guid, title):
						self.clearContentControls()
						self.drawContentList(title)
				elif find(title, 'Transfers') != -1:
					if self.getTransfers(guid, title):
						self.clearContentControls()
						self.drawContentList(title)
				else:
					debug("no further data")
				self.toggleNavListFocus(False)	# content

			elif self.MAINMENU_SELECTED == self.MAINMENU_OPT_FFOCUS:			
				debug("MAINMENU - MAINMENU_OPT_FFOCUS")
				self.showFFocusItem(guid, title)

		else:
			# content NOT created from MainMenu
			navListSelectedItem = self.getNavListAttrib(self.selectedNavListKey, self.NAV_LISTS_DATA_REC_SELECTED)
			debug("selectedNavListKey=" + self.selectedNavListKey + "  navListSelectedItem=" + navListSelectedItem)

			# nav list LEAGUES
			if self.selectedNavListKey == self.LEAGUES_KEY:
				debug("LEAGUES_KEY")

			# nav list LEAGUE_VIEWS
			elif self.selectedNavListKey == self.LEAGUE_VIEW_KEY:
				debug("LEAGUE_VIEWS_KEY")
				if navListSelectedItem == self.LEAGUE_VIEW_TABLE:
					debug("LEAGUE_VIEWS_KEY - LEAGUE_VIEW_TABLE")
					# extract data associated with this selected item
					contentControlData = self.contentControls[self.contentFocusIdx][self.CONTENT_REC_DATA]
					dataItem = contentControlData[contentSelectedPos]
					self.clearContentControls()
					if isinstance(dataItem, bool):								# last item is view table half boolean
						debug("REDRAW TABLE OTHER HALF")
						self.showTable(not dataItem)							# redraw table, but toggle table view
					else:
						debug("SELECTED A TEAM")
						# setup TEAMS
						# set item in TEAMS to that selected from TABLE
						ctrl = self.getNavListDictValue(self.TEAMS_KEY, self.NAV_LISTS_VALUE_CONTROL)
						found = False
						idx = 0
						for idx in range(len(self.contentData)):
							ctrl.selectItem(idx)							# select this idx
							teamName = ctrl.getSelectedItem().getLabel()	# get item at selected
							if contentSelectedItem == teamName:
								found = True
								break
							idx += 1

						if found:
							debug("calling TEAMS")
							self.selectedNavListKey = self.TEAMS_KEY
							self.setNavListAttrib(self.LEAGUE_VIEW_KEY, self.NAV_LISTS_DATA_REC_SELECTED, self.LEAGUE_VIEW_TEAMS)
							self.setNavListAttrib(self.TEAMS_KEY, self.NAV_LISTS_DATA_REC_SELECTED, teamName)
							ctrl.setVisible(True)
							self.navListSelected()
							self.setLeagueLogo()
							self.toggleNavListFocus(True)	# navlists

				elif navListSelectedItem == self.LEAGUE_VIEW_NEWS:
					debug("LEAGUE_VIEW_NEWS")
					# extract data associated with this selected item
					title = self.contentData[contentSelectedPos][0]
					link = self.contentData[contentSelectedPos][2]
					self.showNewsItem(link, title)

			# nav list TEAM_VIEWS
			elif self.selectedNavListKey == self.TEAM_VIEW_KEY:
				debug("TEAM_VIEWS_KEY")
				if navListSelectedItem == self.TEAM_VIEW_NEWS:
					debug("TEAM_VIEW_NEWS")
					# extract data associated with this selected item
					title = self.contentData[contentSelectedPos][0]
					link = self.contentData[contentSelectedPos][2]
					self.showNewsItem(link, title)

				elif navListSelectedItem == self.TEAM_VIEW_SQUAD:
					debug("TEAM_VIEW_SQUAD")
					# extract data associated with this selected item
					title = self.contentData[contentSelectedPos][1]
					url = self.contentData[contentSelectedPos][2]
					if not url:
						messageOK(navListSelectedItem, __language__(353), title)
					elif self.getPlayerProfile(url, title):
						self.clearContentControls()
						self.drawContentList(__language__(360),__language__(361))
					# set focus to list
					try:
						self.setFocus(self.contentControls[self.contentFocusIdx][self.CONTENT_REC_CONTROL])
					except: pass


		debug("< contentSelected()")


########################################################################################################################
	def navListSelected(self):
		debug("> **** navListSelected()")

		debug("selected NAV LIST KEY = " + self.selectedNavListKey)
		# get selected item from selected list
		navListSelectedItem = self.getNavListAttrib(self.selectedNavListKey, self.NAV_LISTS_DATA_REC_SELECTED)

		self.clearContentControls()

		# cancel liveText timer thread if running
		if timerthread.isCountDownRunning():
			timerthread.disableCountDown()
			self.liveTextCL.setVisible(False)

		dataMissing = False
		xbmcgui.lock()

		# LEAGUE or LEAGUE_VIEWS
		if self.selectedNavListKey in [self.LEAGUES_KEY,self.LEAGUE_VIEW_KEY]:
			debug("LEAGUES_KEY or LEAGUE_VIEWS_KEY - remove other lists etc")
			self.resetLeagueTeams(False)	# dont clear stored league/Team data, just lists

			# only reset LEAGUES_VIEW if LEAGUES was selected.
			if self.selectedNavListKey == self.LEAGUES_KEY:
				self.updateNavListLeagueViews(navListSelectedItem)			# rebuild leagueView menu

		# GET NAV LIST SELECTED ITEMS
		leagueSelectedItem = self.getNavListAttrib(self.LEAGUES_KEY, self.NAV_LISTS_DATA_REC_SELECTED)				
		leagueViewSelectedItem = self.getNavListAttrib(self.LEAGUE_VIEW_KEY, self.NAV_LISTS_DATA_REC_SELECTED)				
		teamsSelectedItem = self.getNavListAttrib(self.TEAMS_KEY, self.NAV_LISTS_DATA_REC_SELECTED)				
		teamsViewSelectedItem = self.getNavListAttrib(self.TEAM_VIEW_KEY, self.NAV_LISTS_DATA_REC_SELECTED)

		# data item LEAGUE NAME
		leagueID = self.getNavListItem(self.LEAGUES_KEY, self.LEAGUE_ITEM_REC_LEAGUE_ID, leagueSelectedItem)

		# data item LEAGUE TABLE
		leagueTableID = self.getNavListItem(self.LEAGUES_KEY, self.LEAGUE_ITEM_REC_TABLE_PATH, leagueSelectedItem)
		leagueDictKey = (leagueID+'_'+leagueTableID).replace('/','_')
		debug("leagueDictKey=%s" % leagueDictKey)

		# TEAM ID
		try:
			teamID = self.leagueTeams[leagueDictKey][teamsSelectedItem]
		except:
			teamID = ''

		# LEAGUES
		if self.selectedNavListKey == self.LEAGUES_KEY:
			debug("LEAGUES_KEY")
			if navListSelectedItem == self.LEAGUE_VIDEPRINTER:
				debug("LEAGUES_KEY - LEAGUE_VIDEPRINTER")
				# league ID in this case holds the url
				url = self.getNavListItem(self.LEAGUES_KEY, self.LEAGUE_ITEM_REC_LEAGUE_ID, leagueSelectedItem)
				# start the countdown timer, does an update at startup
				self.liveTextUpdateURL = url
				if Emulating:
					self.updateLiveText()
				else:
					timerthread.enableCountDown()
			else:
				debug("LEAGUES_KEY - OTHER")
				# all other options from LEAGUES need focus to move to LEAGUE_VIEWS
				self.selectedNavListKey = self.LEAGUE_VIEW_KEY

		# LEAGUE VIEWS
		if self.selectedNavListKey == self.LEAGUE_VIEW_KEY:
			debug("LEAGUE_VIEWS_KEY")
			# get URL from selected LEAGUE_VIEWS
			url = self.getNavListItem(self.LEAGUE_VIEW_KEY, itemName=leagueViewSelectedItem)
			url =  url.replace('$LEAGUE',leagueID)

			# setup teams list if chosen
			if leagueViewSelectedItem == self.LEAGUE_VIEW_TEAMS:
				debug("LEAGUE_VIEWS_KEY - LEAGUE_VIEW_TEAMS")
				if leagueTableID:
					url = url.replace('$TABLE',leagueTableID)
					# get league from preloaded league/teams dict
					success = self.loadNavListTeams(leagueDictKey)
					if not success and self.getTable(url):
						self.storeLeagueTeams(leagueDictKey)				# save to mem
						if leagueSelectedItem != self.LEAGUE_INTL:	# dont save from intl table
							self.writeLeagueTeamsConfig(leagueDictKey)	# write to config
						success = self.loadNavListTeams(leagueDictKey)	# load navlist TEAMS

					if success:
						self.selectedNavListKey = self.TEAMS_KEY			# set to next navlist
				else:
					url = None

			elif leagueViewSelectedItem == self.LEAGUE_VIEW_TABLE:
				debug("LEAGUE_VIEWS_KEY - LEAGUE_VIEW_TABLE")
				if leagueTableID:
					url = url.replace('$TABLE',leagueTableID)
					# change table location according to league
					if self.getTable(url):
						isLeagueIntl = (leagueSelectedItem == self.LEAGUE_INTL)
						if isLeagueIntl:									# clear intl saved teams
							try:
								del self.leagueTeams[leagueDictKey]
							except: pass
							success = False									# forces store
						else:
							success = self.loadNavListTeams(leagueDictKey)
						if not success:
							self.storeLeagueTeams(leagueDictKey)				# store in mem
							if not isLeagueIntl:						# dont save from intl table
								self.writeLeagueTeamsConfig(leagueDictKey)	# write to config
							self.loadNavListTeams(leagueDictKey)				# load TEAMS navlist
						else:
							debug("team already in mem")

						self.showTable()
				else:
					url = None

			elif leagueViewSelectedItem == self.LEAGUE_VIEW_NEWS:
				debug("LEAGUE_VIEWS_KEY - LEAGUE_VIEW_NEWS")
				if self.getRSS(url, leagueViewSelectedItem):
					self.drawContentList(__language__(356))

			elif leagueViewSelectedItem == self.LEAGUE_VIEW_FIX:
				debug("LEAGUE_VIEWS_KEY - LEAGUE_VIEW_FIX")
				replaceStr = self.getNavListItem(self.LEAGUES_KEY, self.LEAGUE_ITEM_REC_FIX_PATH, leagueSelectedItem)
				if replaceStr:
					# could be empty, so remove '//'
					url = url.replace('$FIX',replaceStr).replace('///','/')
					if self.getLeagueFixtures(url, leagueViewSelectedItem):
						self.drawContentList()
					else:
						dataMissing = True
				else:
					url = None

			elif leagueViewSelectedItem == self.LEAGUE_VIEW_RES:
				debug("LEAGUE_VIEWS_KEY - LEAGUE_VIEW_RES")
				replaceStr = self.getNavListItem(self.LEAGUES_KEY, self.LEAGUE_ITEM_REC_RES_PATH, leagueSelectedItem)
				if replaceStr:
					# could be empty, so remove '//'
					url = url.replace('$RES',replaceStr).replace('///','/')
					if self.dataSource == self.DATASOURCE_BBC and self.getLeagueResults(url, leagueViewSelectedItem):
						self.drawContentList()
					elif self.dataSource == self.DATASOURCE_SOCSTND and self.getLeagueResultsSOCSTND(url, leagueViewSelectedItem):
						self.drawContentList()
					else:
						dataMissing = True
				else:
					url = None

			elif leagueViewSelectedItem == self.LEAGUE_VIEW_LIVE_SCORES:
				debug("LEAGUE_VIEWS_KEY - LEAGUE_VIEW_LIVE_SCORES")
				# UEFA CUP is the only league with  a different livescores url
				if leagueSelectedItem == self.LEAGUE_UEFA_CUP:
					self.liveTextUpdateURL = url.replace('live_scores','live_uefa_cup')
				else:
					self.liveTextUpdateURL = url
				# start the countdown timer, does an update at startup
				if Emulating:
					self.updateLiveText()
				else:
					timerthread.enableCountDown()

			elif leagueViewSelectedItem == self.LEAGUE_VIEW_TOP_SCORERS:
				debug("LEAGUE_VIEWS_KEY - LEAGUE_VIEW_TOP_SCORERS")
				replaceStr = self.getNavListItem(self.LEAGUES_KEY, self.LEAGUE_ITEM_REC_SCORERS_PATH, leagueSelectedItem)
				if not replaceStr:
					url = None
				else:
					if self.getLeagueTopScorers(url.replace('$SCORERS',replaceStr)):
						self.drawContentList(__language__(362),__language__(363),400)
					else:
						dataMissing = True

		# TEAMS
		if self.selectedNavListKey == self.TEAMS_KEY:
			debug("TEAMS_KEY teamID="+teamID)
			if teamsSelectedItem:
				# prevent TEAM_VIEWS if no teamID, means theres no urls
				ctrl = self.getNavListDictValue(self.TEAM_VIEW_KEY, self.NAV_LISTS_VALUE_CONTROL)
				if teamID:
					ctrl.setVisible(True)
					ctrl.setEnabled(True)
					self.setFocus(ctrl)
					self.selectedNavListKey = self.TEAM_VIEW_KEY
				else:
					debug("no teamViews information")
					ctrl.setVisible(False)
					ctrl.setEnabled(False)
					self.selectedNavListKey = self.TEAMS_KEY
					self.setFocus(self.getNavListDictValue(self.TEAMS_KEY, self.NAV_LISTS_VALUE_CONTROL))

		# TEAM VIEWS
		if self.selectedNavListKey == self.TEAM_VIEW_KEY:
			debug("TEAM_VIEWS_KEY teamsViewSelectedItem="+teamsViewSelectedItem)
			# get URL from selected LEAGUE_VIEWS
			url = self.getNavListItem(self.TEAM_VIEW_KEY, itemName=teamsViewSelectedItem)
			url = url.replace('$AZ',teamsSelectedItem[0]).replace('$TEAM',teamID)
			if teamsViewSelectedItem == self.TEAM_VIEW_NEWS:
				debug("TEAM_VIEWS_KEY - TEAM_VIEW_NEWS")
				if self.getRSS(url, teamsViewSelectedItem):
					self.drawContentList(__language__(356))
			elif teamsViewSelectedItem == self.TEAM_VIEW_FIX:
				debug("TEAM_VIEWS_KEY - TEAM_VIEW_FIX")
				if self.getLeagueFixtures(url, teamsViewSelectedItem):
					self.drawContentList()
				else:
					dataMissing = True
			elif teamsViewSelectedItem == self.TEAM_VIEW_RES:
				debug("TEAM_VIEWS_KEY - TEAM_VIEW_RES")
				if self.getLeagueResults(url, teamsViewSelectedItem):
					self.drawContentList()
				else:
					dataMissing = True
			elif teamsViewSelectedItem == self.TEAM_VIEW_LIVE_TEXT:
				debug("TEAM_VIEWS_KEY - TEAM_VIEW_LIVE_TEXT")
				try:
					hasLiveScore = self.getNavListItem(self.LEAGUES_KEY, self.LEAGUE_ITEM_REC_HAS_LIVESCORE)
				except:
					hasLiveScore = False
				if hasLiveScore:
					# start the countdown timer, does an update at startup
					self.liveTextUpdateURL = url
					if Emulating:
						self.updateLiveText()
					else:
						timerthread.enableCountDown()
				else:
					messageOK(__language_(351),__language__(101))
					self.liveTextUpdateURL = ''
			elif teamsViewSelectedItem == self.TEAM_VIEW_SQUAD:
				debug("TEAM_VIEWS_KEY - TEAM_VIEW_SQUAD")
				if not self.getTeamSquad(url):
					dataMissing = True
				else:
					self.drawContentList(__language__(364),width=300)

		xbmcgui.unlock()
		if dataMissing:
			messageNoInfo()

		debug("< **** navListSelected()")


########################################################################################################################
	def createNavList(self, navListKey):
		debug("> createNavList() navListKey: " + navListKey)

		data = self.getNavListDictValue(navListKey, self.NAV_LISTS_VALUE_DATA)
		attribs = data[self.NAV_LIST_ATTRIBS]

		# get list dims
		xpos = attribs[self.NAV_LISTS_DATA_REC_X]
		ypos = attribs[self.NAV_LISTS_DATA_REC_Y]
		width = attribs[self.NAV_LISTS_DATA_REC_W]
		height = attribs[self.NAV_LISTS_DATA_REC_H]

		# create list with items
		control = xbmcgui.ControlList(xpos, ypos, width, height, itemTextXOffset=0, \
							itemHeight=24,selectedColor='0xFFFFFF99', \
							buttonFocusTexture=BUTTON_FOCUS, alignmentY=XBFONT_CENTER_Y)
		self.addControl(control)
		try:
			control.setPageControlVisible(False)
		except: pass
		control.setVisible(False)

		# save controllist to nav list dict
		self.setNavListDictValue(navListKey, self.NAV_LISTS_VALUE_CONTROL, control)
		debug("< createNavList()")


	########################################################################################################################
	def loadNavList(self, navListKey):
		debug("> loadNavList() navListKey: " + navListKey)

		# add menu items
		try:
			data = self.getNavListDictValue(navListKey, self.NAV_LISTS_VALUE_DATA)
			controlList = self.getNavListDictValue(navListKey, self.NAV_LISTS_VALUE_CONTROL)

			for item in data[self.NAV_LIST_MENU]:
				controlList.addItem(unicodeToAscii(item))
		except:
			debug("no such navListKey=%s" % navListKey)

		debug("< loadNavList()")

	########################################################################################################################
	def updateNavListLeagueViews(self, leagueSelectedItem):
		debug("> updateNavListLeagueViews()")

		leagueViewCL = self.getNavListDictValue(self.LEAGUE_VIEW_KEY, self.NAV_LISTS_VALUE_CONTROL)
		leagueViewCL.reset()
		if leagueSelectedItem != self.LEAGUE_VIDEPRINTER:
			leagueData = self.getNavListDictValue(self.LEAGUES_KEY, self.NAV_LISTS_VALUE_DATA)[leagueSelectedItem]
			leagueViewMenu = self.LEAGUE_VIEW_MENU[:]

			# remove menu item from leagueViews if no league option
			try:
				if not leagueData[self.LEAGUE_ITEM_REC_TABLE_PATH]:
					leagueViewMenu.remove(self.LEAGUE_VIEW_TABLE)
					leagueViewMenu.remove(self.LEAGUE_VIEW_TEAMS)
			except: pass

			try:
				if not leagueData[self.LEAGUE_ITEM_REC_FIX_PATH]:
					leagueViewMenu.remove(self.LEAGUE_VIEW_FIX)
			except: pass

			try:
				if not leagueData[self.LEAGUE_ITEM_REC_RES_PATH]:
					leagueViewMenu.remove(self.LEAGUE_VIEW_RES)
			except: pass

			try:
				if not leagueData[self.LEAGUE_ITEM_REC_SCORERS_PATH]:
					leagueViewMenu.remove(self.LEAGUE_VIEW_TOP_SCORERS)
			except: pass

			try:
				hasItem = leagueData[self.LEAGUE_ITEM_REC_HAS_LIVESCORE]
				if not hasItem:
					leagueViewMenu.remove(self.LEAGUE_VIEW_LIVE_SCORES)
			except: pass

			try:
				hasItem = leagueData[self.LEAGUE_ITEM_REC_HAS_NEWS]
				if not hasItem:
					leagueViewMenu.remove(self.LEAGUE_VIEW_NEWS)
			except: pass

			for item in leagueViewMenu:
				leagueViewCL.addItem(unicodeToAscii(item))

			leagueViewCL.selectItem(0)
			self.setNavListAttrib(self.LEAGUE_VIEW_KEY, self.NAV_LISTS_DATA_REC_SELECTED, '')
			isVisible = True
		else:
			isVisible = False

		# turn LEAGUE_VIEWS invisible if not a league
		leagueViewCL.setVisible(isVisible)
		leagueViewCL.setEnabled(isVisible)

		debug("< updateNavListLeagueViews()")

	########################################################################################################################
	def setupNavListDict(self):
		debug("> setupNavListDict()")
		self.NAV_LISTS_VALUE_DATA = 0
		self.NAV_LISTS_VALUE_CONTROL = 1
		self.navLists = {
			self.LEAGUES_KEY : [self.LEAGUES_DATA, None],
			self.LEAGUE_VIEW_KEY : [self.LEAGUE_VIEW_DATA, None],
			self.TEAMS_KEY : [self.TEAMS_DATA, None],
			self.TEAM_VIEW_KEY : [self.TEAM_VIEW_DATA, None]
			}
		debug("< setupNavListDict()")

	########################################################################################################################
	def setupNavListsNav(self):
		debug("> setupNavListsNav()")

		# RIGHT
		self.navLists[self.LEAGUES_KEY][self.NAV_LISTS_VALUE_CONTROL] \
			.controlRight(self.getNavListDictValue(self.LEAGUE_VIEW_KEY, self.NAV_LISTS_VALUE_CONTROL))

		self.navLists[self.LEAGUE_VIEW_KEY][self.NAV_LISTS_VALUE_CONTROL] \
			.controlRight(self.getNavListDictValue(self.TEAMS_KEY, self.NAV_LISTS_VALUE_CONTROL))

		self.navLists[self.TEAMS_KEY][self.NAV_LISTS_VALUE_CONTROL] \
			.controlRight(self.getNavListDictValue(self.TEAM_VIEW_KEY, self.NAV_LISTS_VALUE_CONTROL))

		self.navLists[self.TEAM_VIEW_KEY][self.NAV_LISTS_VALUE_CONTROL] \
			.controlRight(self.getNavListDictValue(self.LEAGUES_KEY, self.NAV_LISTS_VALUE_CONTROL))

		# LEFT
		self.navLists[self.LEAGUES_KEY][self.NAV_LISTS_VALUE_CONTROL] \
			.controlLeft(self.getNavListDictValue(self.TEAM_VIEW_KEY, self.NAV_LISTS_VALUE_CONTROL))

		self.navLists[self.LEAGUE_VIEW_KEY][self.NAV_LISTS_VALUE_CONTROL] \
			.controlLeft(self.getNavListDictValue(self.LEAGUES_KEY, self.NAV_LISTS_VALUE_CONTROL))

		self.navLists[self.TEAMS_KEY][self.NAV_LISTS_VALUE_CONTROL] \
			.controlLeft(self.getNavListDictValue(self.LEAGUE_VIEW_KEY, self.NAV_LISTS_VALUE_CONTROL))

		self.navLists[self.TEAM_VIEW_KEY][self.NAV_LISTS_VALUE_CONTROL] \
			.controlLeft(self.getNavListDictValue(self.TEAMS_KEY, self.NAV_LISTS_VALUE_CONTROL))

		debug("< setupNavListsNav()")

########################################################################################################################
	def setLeagueLogo(self):
		debug("> setLeagueLogo()")

		# league logo
		try:
			self.removeControl(self.logoLeagueCI)
		except: pass

		# team logo
		try:
			self.removeControl(self.logoTeamCI)
		except: pass

		# league name
		try:
			self.removeControl(self.logoLeagueCLbl)
		except: pass

		# league view name
		try:
			self.removeControl(self.logoViewCLbl)
		except: pass

		# get league logo filename
		if self.dataSource == self.DATASOURCE_SOCSTND:
			imgW = 115		# country flags
		else:
			imgW = 160		# league logos
		leagueName = self.getNavListAttrib(self.LEAGUES_KEY, self.NAV_LISTS_DATA_REC_SELECTED)
		filenameLeague = os.path.join(DIR_TEAM_GFX,leagueName+'.jpg')
		if not fileExist(filenameLeague):
			filenameLeague = LOGO_FILENAME
		debug("LEAGUES filename: " + filenameLeague)

		# set league logo
		try:
			xpos = 0
			ypos = 0
			imgH = self.headerH-2
			self.logoLeagueCI = xbmcgui.ControlImage(xpos, ypos, imgW, imgH, \
													filenameLeague) # , aspectRatio=2
			self.addControl(self.logoLeagueCI)
			xpos += imgW + 10
		except: pass

		# get team logo filename
		teamName = self.getNavListAttrib(self.TEAMS_KEY, self.NAV_LISTS_DATA_REC_SELECTED)
		debug("teamName=" + teamName)
		if teamName:
			fname = os.path.join(DIR_TEAM_GFX, teamName.replace(' ','_').replace('&','and') + '.jpg')
			if not fileExist(fname):
				fname = os.path.join(DIR_TEAM_GFX, 'Unknown_team.png')
			debug("TEAMS fname: " + fname)

			# set team logo
			try:
				# use headerH for w & h  to give a square area - aspectRatio sorts it out
				imgW = 60
				self.logoTeamCI = xbmcgui.ControlImage(xpos, ypos, imgW, imgH,
													fname, aspectRatio=2)
				self.addControl(self.logoTeamCI)
				xpos += imgW + 5
			except: pass

		# append TEAM_VIEW to label
		leagueViewSelectedItem = self.getNavListAttrib(self.LEAGUE_VIEW_KEY, self.NAV_LISTS_DATA_REC_SELECTED)
		if leagueViewSelectedItem:
			leagueName += '; ' + leagueViewSelectedItem

		# append team name to league label
		labelH = 30
		if teamName:
			leagueName += '; ' + teamName
		self.logoLeagueCLbl = xbmcgui.ControlLabel(xpos, ypos, 0, labelH, leagueName, \
												FONT14, "0xFFFFFF00")
		self.addControl(self.logoLeagueCLbl)

		# set view label.
		# if team selected, display team view, otherwise display league view
		if teamName:
			teamsViewText = self.getNavListAttrib(self.TEAM_VIEW_KEY, self.NAV_LISTS_DATA_REC_SELECTED)
		else:
			teamsViewText = ''

		self.logoViewCLbl = xbmcgui.ControlLabel(xpos, ypos+labelH+5, self.contentW, 20, \
												teamsViewText, FONT12, "0xFFFFFF00")
		self.addControl(self.logoViewCLbl)

		debug("< setLeagueLogo()")

########################################################################################################################
	def getNavListItem(self, navList, field=0, itemName=''):
		if not itemName:
			# use currently selected list item if itemName not provided
			itemName = self.getNavListAttrib(navList, self.NAV_LISTS_DATA_REC_SELECTED)

		try:
			data = (self.navLists[navList])[self.NAV_LISTS_VALUE_DATA][itemName]
			if isinstance(data, list):
				value = data[field]		# stored is key : [value1, value2, ...]
			else:
				value = data			# stored is key : value
		except:
			debug("getNavListItem() itemName not stored")
			value = ''

		msg = "getNavListItem() navList: %s field: %s itemName: %s value = %s" % (navList, str(field), itemName, str(value))
		debug(msg)
		return value

########################################################################################################################
	def getNavListAttrib(self, navList, field):
		value = (self.navLists[navList])[self.NAV_LISTS_VALUE_DATA][self.NAV_LIST_ATTRIBS][field]
		msg = "getNavListAttrib() navList: %s field: %s value = %s" % (navList, str(field), str(value))
		debug(msg)
		return value

########################################################################################################################
	def setNavListAttrib(self, navList, field, value):
		(self.navLists[navList])[self.NAV_LISTS_VALUE_DATA][self.NAV_LIST_ATTRIBS][field] = value
		msg = "setNavListAttrib() navList: %s field: %s value = %s" % (navList, str(field), str(value))
		debug(msg)

########################################################################################################################
	def getNavListDictValue(self, navList, key):
		return (self.navLists[navList])[key]

########################################################################################################################
	def setNavListDictValue(self, navList, dictKey, value):
		(self.navLists[navList])[dictKey] = value
		msg = "setNavListDictValue() navList: %s dictKey: %s value = %s" % (navList, dictKey, str(value))
		debug(msg)

########################################################################################################################
	def clearContentControls(self):
		debug("> clearContentControls()")
		if self.contentControls:
			xbmcgui.lock()
			for ctrl,data in self.contentControls:
				try:
					self.removeControl(ctrl)
				except: pass
			self.contentControls = []

			try:
				self.liveTextCL.reset()
				self.liveTextCL.setVisible(False)
			except: pass
			xbmcgui.unlock()
		debug("< clearContentControls()")

#######################################################################################################################    
	def toggleNavListFocus(self, switchToNavLists=None, isLiveText=False):
		debug("> toggleNavListFocus() switchToNavLists=" + str(switchToNavLists) + " isLiveText="+str(isLiveText))

		if switchToNavLists == None:
			# toggle
			self.focusNavLists = not self.focusNavLists
		else:
			# force state
			self.focusNavLists = switchToNavLists

		if self.focusNavLists:
			debug("set focus to NAV LISTS")
			self.setFocus(self.getNavListDictValue(self.selectedNavListKey, self.NAV_LISTS_VALUE_CONTROL))
		else:
			if isLiveText:
				debug("set focus to CONTENT - LIVE TEXT")
				self.setFocus(self.liveTextCL)
			else:
				debug("set focus to CONTENT")
				if self.contentControls:
					debug("self.contentFocusIdx = " + str(self.contentFocusIdx))
					self.setFocus(self.contentControls[self.contentFocusIdx][self.CONTENT_REC_CONTROL])		# [ctrl,data]
				else:
					# no content, go back to nav lists
					self.focusNavLists = True
		debug("< toggleNavListFocus() new state: " + str(self.focusNavLists))


########################################################################################################################
	def loadLeagueTeamsConfig(self):
		debug("> loadLeagueTeamsConfig()")

		self.leagueTeams = {}
		files = listDir(DIR_USERDATA, ".txt", fnRE='league_(.*?)$', getFullFilename=True )

		for fn in files:
			# extract league from filename
			leagueName = searchRegEx(fn, 'league_(.*?).txt')
			debug('loading fn=%s leagueName=%s' % (fn, leagueName))
			self.leagueTeams[leagueName] = loadFileObj(os.path.join(DIR_USERDATA, fn))

		debug("< loadLeagueTeamsConfig() leagues count=%s" % len(self.leagueTeams))

########################################################################################################################
	def writeLeagueTeamsConfig(self, leagueName):
		debug("> writeLeagueTeamsConfig() leagueName=%s" % leagueName)

		leagueName = leagueName.replace('/','_')
		teamsDict = self.leagueTeams[leagueName]
		fn = os.path.join(DIR_USERDATA, self.SETTINGS_LEAGUES_FILENAME % leagueName)
		saveFileObj(fn, teamsDict)

		debug("< writeLeagueTeamsConfig()")

########################################################################################################################
	def storeLeagueTeams(self, leagueKey):
		debug("> storeLeagueTeams() leagueKey=%s" % leagueKey)

		teamsDict = {}
		# take each team rec from contentData, as loaded by getTable, save name,id to a dict
		# skip table details rec at IDX 0
		for teamIDX in range(1, len(self.contentData)):
			team = self.contentData[teamIDX]
			teamURL = team[0]
			teamName = capwords(decodeEntities(team[1]))		# [url, display name, ....]

			# not all teams have a url, which means we cant do any further team based actions
			if teamURL:
				teamID = searchRegEx(teamURL, 'teams/./(.*?)/')
			else:
				teamID = ''

			teamsDict[teamName] = teamID
			debug("teamName=%s teamID=%s" % (teamName, teamID))

		self.leagueTeams[leagueKey] = teamsDict
		debug("< storeLeagueTeams()")

########################################################################################################################
	def getTable(self, url):
		debug("> getTable()")

		# FETCH HTML
		title = self.getNavListAttrib(self.LEAGUES_KEY, self.NAV_LISTS_DATA_REC_SELECTED)				
		title2 = self.getNavListAttrib(self.LEAGUE_VIEW_KEY, self.NAV_LISTS_DATA_REC_SELECTED)				
		dialogProgress.create(__language__(302), title, title2)
		html = fetchURL(url)
		dialogProgress.close()
		if not validWebPage(html):
			debug("< getTable() no data")
			return False

		self.contentData = []
		tablesDict = {}
		sections = parseDocList(html, self.RE_SUB_SECTION)
		debug("html sections=%s " % len(sections))

		reTableDets = 'fulltableHeader"><b>(.*?)<.*?br>(.*?)<'	# 13/03/08
		reShortTable = '()c1">\d+<.*?c2">(.*?)</td.*?c3">(.*?)</td.*?c4">(.*?)</td.*?c5">(.*?)</td.*?c6">(.*?)</td.*?c7">(.*?)</td.*?c8">(.*?)</td.*?c9">(.*?)</td.*?c10">(.*?)</td'
		reFullTable = '()c1">\d+<.*?c2">(.*?)</td.*?c3">(.*?)</td.*?c4">(.*?)</td.*?c5">(.*?)</td.*?c6">(.*?)</td.*?c7">(.*?)</td.*?c8">(.*?)</td.*?c9">(.*?)</td.*?c10">(.*?)</td.*?c11">(.*?)</td.*?c12">(.*?)</td.*?c13">(.*?)</td.*?c14">(.*?)</td.*?c15">(.*?)</td'
		for section in sections:
			tableData = []
			tableName = ''
			tableDate = ''
			# GET TABLE NAME & DATE
			matches = re.search(reTableDets, section, re.DOTALL+re.MULTILINE+re.IGNORECASE)
			if matches:
				tableName = capwords(matches.group(1).replace('\n','').strip())
				tableDate = matches.group(2).replace('\n','').strip()

			# TABLE SIZE, determines team row regex
			isFullTable = (find(section, 'fulltable') != -1)
			if isFullTable:
				reRow = reFullTable
			else:
				reRow = reShortTable

			# save table Details
			tableData.append([tableName, tableDate, isFullTable])

			# GET TEAM ROW - start re matching after first table row
			matches = parseDocList(section, reRow, '</tr','</table')
			for match in matches:
				rowData = list(match)	# make a list from a tuple
				# row c2 may have a url, extract and store as seperate teamURL, teamName
				rowData[0], rowData[1] = extractURLName(match[1])
				tableData.append(rowData)

			# store table data for later selection
			tablesDict[tableName] = tableData	

		# if more than 1 table, user selects, then save into contentData
		if len(tablesDict) > 1:
			menu = tablesDict.keys()
			menu.sort()
			selectDialog = DialogSelect()
			selectDialog.setup("Select Table To View", rows=len(menu), width=400)
			selectedPos, action = selectDialog.ask(menu)
			if selectedPos >= 0:				# exit selected
				self.contentData = tablesDict[menu[selectedPos]]
		elif len(tablesDict) == 1:
			self.contentData = tablesDict[tableName]

		print self.contentData
		sz = len(self.contentData)
		if not sz:
			messageNoInfo()
		debug("< getTable() teamCount=%s " % sz)
		return sz

########################################################################################################################
	def showTable(self, drawTop=True):
		debug("> showTable() drawTop: " + str(drawTop))

		# DRAW TABLE
		# contentData holds previously fetched table data in the form of a list (see getTable())
		if self.contentData:
			xbmcgui.lock()
			colW = 30
			gapW = 5
			gapH = 0
			imgTableOdd = os.path.join(DIR_GFX, 'table_odd.jpg')
			imgTableEven = os.path.join(DIR_GFX, 'table_even.jpg')

			# SHOW TABLE DETAILS
			try:
				tableName, tableDate, isFulltable = self.contentData[0]
				self.logoViewCLbl.setLabel(tableName + '; ' + tableDate)
			except: pass
			
			if isFulltable:
				colHeaders = ['Team','P','W','D','L','F','A','W','D','L','F','A','GD','PTS']
				colWidths = [180,							# name
							colW + (gapW*2),				# Played
							colW + gapW,					# home W
							colW + gapW,					# home D
							colW + gapW,					# home L
							colW + gapW,					# home F
							colW + (gapW*2),				# home A
							colW + gapW,					# away W
							colW + gapW,					# away D
							colW + gapW,					# away L
							colW + gapW,					# away F
							colW + gapW,					# away A
							colW + (gapW*2),				# GD
							colW + gapW]					# PTS
			else:
				colHeaders = ['Team','P','W','D','L','F','A','GD','PTS']
				colWidths = [180,							# name
							colW + (gapW*2),				# Played
							colW + gapW,					# home W
							colW + gapW,					# home D
							colW + gapW,					# home L
							colW + gapW,					# home F
							colW + gapW,					# home A
							colW + (gapW*2),				# GD
							colW + gapW]					# PTS

			# calc overhall width
			w = 0
			for width in colWidths:
				w += width
			x = self.contentCenterX - (w/2)
			y = self.contentY

			# DRAW TABLE DETAILS
			h = 18
			lbl = xbmcgui.ControlLabel(x, y, 0, h, tableName+'; '+tableDate, FONT12, "0xFFFFFF99")
			self.contentControls.append([lbl,None])
			self.addControl(lbl)
			y += h

			# determine which is start row from table. Exclude tableDetails row
			maxContentData = len(self.contentData)-1
			debug("maxContentData="+str(maxContentData))

			# split table in half if cant all be fitted on scr
			maxRows = 12
			if maxContentData > maxRows:
				halfRows = int(maxContentData/2)
			else:
				halfRows = maxContentData

			if drawTop:
				startTableIdx = 1
				endTableIdx = halfRows
			else:
				startTableIdx = halfRows+1
				endTableIdx = maxContentData
			debug("halfRows=" + str(halfRows) + " startTableIdx=" + str(startTableIdx) + " endTableIdx=" + str(endTableIdx))

			# determine table row height according to how many rows needed per table half
			if halfRows <= 7:
				rowH = 35
			elif halfRows <= 10:
				rowH = 30
			else:
				rowH = 25
			debug("rowH=" + str(rowH))

			# draw header row
			headerX = x
			headerH = 18
			for idx in range(len(colHeaders)):
				colHeader = colHeaders[idx]
				colW = colWidths[idx]
				lbl = xbmcgui.ControlLabel(headerX, y, colW, headerH, colHeader, "font13", "0xFFFFFF99")
				self.contentControls.append([lbl,None])
				self.addControl(lbl)
				headerX += colWidths[idx]
			y += headerH

			# draw rows
#			rowY = y + headerH +5
			startTableY = y
			isOddRow = True
			for row in range(startTableIdx, endTableIdx+1):
				rowX = x + colWidths[0]					# reset to row beginning after team list
				if isOddRow:
					img = imgTableOdd
				else:
					img = imgTableEven
				isOddRow = not isOddRow					# reverse state

				# draw row background image
				try:
					rowCI = xbmcgui.ControlImage(rowX, y, w-colWidths[0], rowH, img)
					self.contentControls.append([rowCI,None])
					self.addControl(rowCI)
				except: pass

				# place stats
				for col in range(1, len(colHeaders)):
					text = self.contentData[row][col+1]	# col; allow for url stored at idx 0
					colW = colWidths[col]
					ctrl = xbmcgui.ControlLabel(rowX, y, colW, rowH, text, 'font14', \
												textColor='0xFF000000',alignment=XBFONT_CENTER_Y)
					self.contentControls.append([ctrl,None])
					self.addControl(ctrl)
					rowX += colW

				y += rowH + gapH

			# TEAMS CONTROL LIST
#			listY = y + headerH + 5
			teamCL = xbmcgui.ControlList(x, startTableY, colWidths[0], self.contentH, \
							itemTextXOffset=0, itemHeight=rowH, space=0, \
							buttonFocusTexture=BUTTON_FOCUS)
			self.addControl(teamCL)
			try:
				teamCL.setPageControlVisible(False)
			except: pass

			# add team name to list.
			# Also, create associated data list, each element corresponds to each list item
			teamCLData = []
			for idx in range(startTableIdx, endTableIdx+1):
				teamCL.addItem(capwords(decodeEntities(self.contentData[idx][1])))	# team name
				teamCLData.append(self.contentData[idx][0])							# team url

			# if more than 1 page of rows , add show top/bottom nav button
			if maxContentData > halfRows:
				if drawTop:
					teamCL.addItem(unicodeToAscii(__language__(354)))
				else:
					teamCL.addItem(unicodeToAscii(__language__(355)))
				# store table view state (top == true, bottom == false)
				teamCLData.append(drawTop)

			self.contentControls.append([teamCL, teamCLData])
			self.contentFocusIdx = len(self.contentControls)-1			# set focus to VIEW item
			# set focus to list
			self.setFocus(self.contentControls[self.contentFocusIdx][self.CONTENT_REC_CONTROL])
#			self.toggleNavListFocus(False)		# switch to content
			self.setFocus(teamCL)

			xbmcgui.unlock()
		debug("< showTable()")


########################################################################################################################
	def getLeagueFixtures(self, url, title):
		debug("> getLeagueFixtures()")

		success = False
		leagueSelectedItem = self.getNavListAttrib(self.LEAGUES_KEY, self.NAV_LISTS_DATA_REC_SELECTED)				
		leagueViewSelectedItem = self.getNavListAttrib(self.LEAGUE_VIEW_KEY, self.NAV_LISTS_DATA_REC_SELECTED)				
		dialogProgress.create(__language__(302), leagueSelectedItem, leagueViewSelectedItem, title)
		html = fetchURL(url)
		dialogProgress.close()
		if not validWebPage(html):
			debug("< getLeagueFixtures() no data")
			return False

		# DATA SECTION
		subSection = searchRegEx(html, self.RE_SUB_SECTION, re.MULTILINE+re.IGNORECASE+re.DOTALL)

		# split in dates
		splits = subSection.split('class="greyline" noshade>')
		if splits:
			self.contentData = []
			# get fixtures within each date
			regexDate = 'mvb\"><b>(.*?)</b>'
			regexFixtures = 'mvb">(.*?)</div'
			for split in splits:
				matches = parseDocList(split, regexFixtures)
				if matches:
					self.contentData.append([cleanHTML(matches[0]),''])
					for match in matches[1:]:
						text = decodeEntities(cleanHTML(match)).strip()
						if text:	# ignore empty matches
							self.contentData.append(['',text])	# home v Away, KO (all in one group)

			success = (len(self.contentData) > 0)

		debug("< getLeagueFixtures() success: " + str(success))
		return success

########################################################################################################################
	def getGossip(self, url, title):
		debug("> getGossip()")

		success = False
		dialogProgress.create(__language__(302), self.MAINMENU_OPT_GOSSIP, title)
		html = fetchURL(url)
		dialogProgress.close()
		if not validWebPage(html):
			debug("< getGossip() no data")
			return False

		# DATA SECTION
		# header, data
		reData = 'ch1"><B>(.*?)</B>(.*?)<!-- S ILIN -->'
		matches = parseDocList(html, reData, self.STR_SECTION_START, self.STR_SECTION_END)
		if matches:
			self.contentData = []
			for match in matches:
				header = cleanHTML(match[0])
				self.contentData.append([header,''])
				rumours = parseDocList(match[1], '>(.*?)<')
				for rumour in rumours:
					rumour = decodeEntities(cleanHTML(rumour)).strip()
					if rumour:
						self.contentData.append([rumour,''])

		success = (len(self.contentData) > 0)
		debug("< getGossip() success: " + str(success))
		return success

########################################################################################################################
	def getTransfers(self, url, title):
		debug("> getTransfers()")

		success = False
		dialogProgress.create(__language__(302), self.MAINMENU_OPT_GOSSIP, title)
		html = fetchURL(url)
		dialogProgress.close()
		if not validWebPage(html):
			debug("< getTransfers() no data")
			return False

		section = searchRegEx(html, self.RE_SECTION, re.MULTILINE+re.IGNORECASE+re.DOTALL)
#		match = searchRegEx(section, self.RE_SECTION, re.MULTILINE+re.IGNORECASE+re.DOTALL)
		matches = parseDocList(section, '>(.*?)<')
		if matches:
			self.contentData = []
			for match in matches:
				text = decodeEntities(cleanHTML(match)).strip()
				if text:	# ignore empty matches
					self.contentData.append([text, ''])

		success = (len(self.contentData) > 0)
		debug("< getTransfers() success: " + str(success))
		return success

########################################################################################################################
	def getLeagueResults(self, url, title):
		debug("> getLeagueResults()")

		success = False
		leagueSelectedItem = self.getNavListAttrib(self.LEAGUES_KEY, self.NAV_LISTS_DATA_REC_SELECTED)				
		leagueViewSelectedItem = self.getNavListAttrib(self.LEAGUE_VIEW_KEY, self.NAV_LISTS_DATA_REC_SELECTED)				
		dialogProgress.create(__language__(302), leagueSelectedItem, leagueViewSelectedItem, title)
		html = fetchURL(url)
		dialogProgress.close()
		if not validWebPage(html):
			debug("< getLeagueResults() no data")
			return False

		subSection = searchRegEx(html, self.RE_SUB_SECTION, re.MULTILINE+re.IGNORECASE+re.DOTALL)
		# split into sections
		splits = subSection.split('</table>')
		if splits:
			self.contentData = []
			totalSplits = len(splits)
			dialogProgress.create(__language__(304),__language__(300))	# parsing
			# get fixtures within each date
			regexDate = '<b>(.*?)</b>.*?<hr'
			regexResults = 'c1\">(.*?)</td.*?c2\">(.*?)</td.*?c3"\>(.*?)</td'
			for splitIDX in range(totalSplits):
				split = splits[splitIDX]
				# DATE
				matches = parseDocList(split, regexDate, 'noshade','noshade')
				if matches:
					resultDate = cleanHTML(matches[0])
					self.contentData.append([resultDate,''])

				# RESULT DETAILS
				matches = parseDocList(split, regexResults)
				for match in matches:
					text = ("%s %s") % (cleanHTML(match[0]),cleanHTML(match[1]))
					self.contentData.append([text,cleanHTML(match[2])])

				if splitIDX < totalSplits-1:
					self.contentData.append(['',''])

				pct=int(splitIDX*100.0/totalSplits)
				# just update every x%
				if pct and (pct % 10 == 0):
					dialogProgress.update(pct, resultDate)

			dialogProgress.close()

		success = (len(self.contentData) > 0)
		if not success:
			messageNoInfo()

		debug("< getLeagueResults() success: " + str(success))
		return success

########################################################################################################################
	def getLeagueResultsSOCSTND(self, url, title):
		debug("> getLeagueResultsSOCSTND()")

		success = False
		leagueSelectedItem = self.getNavListAttrib(self.LEAGUES_KEY, self.NAV_LISTS_DATA_REC_SELECTED)				
		leagueViewSelectedItem = self.getNavListAttrib(self.LEAGUE_VIEW_KEY, self.NAV_LISTS_DATA_REC_SELECTED)				
		dialogProgress.create(__language__(302), leagueSelectedItem, leagueViewSelectedItem, title)
		html = fetchURL(url)
		dialogProgress.close()
		if not validWebPage(html):
			debug("< getLeagueResults() no data")
			return False

		# split into sections
		splits = html.split('</table>')
		if splits:
			self.contentData = []
			totalSplits = len(splits)
			dialogProgress.create(__language__(302), __language__(300))
			# get fixtures within each date
			regexDate = 'class=date>(.*?)<'
			regexLeague = '<td>.*?<b>(.*?)</B>(.*?)</td>'
			regexResults = '<tr.*?<td.*?>(.*?)</td.*?<td.*?>(.*?)</td.*?<td.*?>(.*?)</td.*?<td.*?>(.*?)</td.*?<td.*?>(.*?)</td'
			for splitIDX in range(totalSplits):
				
				split = splits[splitIDX]
				# LEAGUE
				matches = parseDocList(split, regexLeague)
				if matches:
					try:
						resultLeague = "%s %s" % (cleanHTML(matches[0][0]), cleanHTML(matches[0][1]))
						self.contentData.append([decodeEntities(resultLeague),''])
						continue
					except: pass

				# DATE
				resultDate = cleanHTML(searchRegEx(split, regexDate, re.MULTILINE+re.IGNORECASE+re.DOTALL))
				if resultDate:
					self.contentData.append(['',resultDate])
					continue

				# RESULT DETAILS
				found = False
				matches = parseDocList(split, regexResults)
				for match in matches:
					try:
						if match[0] and match[1] and match[2] and match[3]:
							text = "%s %s %s %s %s" % (cleanHTML(match[0]),cleanHTML(match[1]),cleanHTML(match[2]),cleanHTML(match[3]),cleanHTML(match[4]))
							self.contentData.append([decodeEntities(text),''])
							found = True
					except: pass

				if found and splitIDX < totalSplits-1:
					self.contentData.append(['',''])

				pct=int(splitIDX*100.0/totalSplits)
				# just update every x%
				if pct and (pct % 10 == 0):
					dialogProgress.update(pct, resultDate)

			dialogProgress.close()

		success = (len(self.contentData) > 0)
		if not success:
			messageNoInfo()

		debug("< getLeagueResultsSOCSTND() success: " + str(success))
		return success

########################################################################################################################
	def getLeagueTopScorers(self, url):
		debug("> getLeagueTopScorers()")

		success = False
		leagueSelectedItem = self.getNavListAttrib(self.LEAGUES_KEY, self.NAV_LISTS_DATA_REC_SELECTED)				
		title2 = self.getNavListAttrib(self.LEAGUE_VIEW_KEY, self.NAV_LISTS_DATA_REC_SELECTED)				
		dialogProgress.create(__language__(302), leagueSelectedItem, title2)
		html = fetchURL(url)
		dialogProgress.close()
		if not validWebPage(html):
			debug("< getLeagueTopScorers() no data")
			return False

		# get fixtures within each date
		regexLink = 'c2\">(.*?)</td.*?stats\">(.*?)<.*?c4\">(.*?)</td'
		matches = parseDocList(html, regexLink, '>TOT<','</table>')
		if matches:
			self.contentData = []
			for match in matches:
				text0 = decodeEntities(match[0]).strip()
				text1 = decodeEntities(match[1]).strip()
				text2 = decodeEntities(match[2]).strip()
				if not text0 or not text1 or not text2:	# ignore empty matches
					continue
				self.contentData.append([text0 + ' (' + text1 + ') ',text2])	# name, team, goals

			success = (len(self.contentData) > 0)

		debug("< getLeagueTopScorers() success: " + str(success))
		return success

########################################################################################################################
	def getTeamLiveText(self, url):
		debug("> getTeamLiveText()")

		success = False
		title = self.getNavListAttrib(self.TEAMS_KEY, self.NAV_LISTS_DATA_REC_SELECTED)				
		title2 = self.getNavListAttrib(self.TEAM_VIEW_KEY, self.NAV_LISTS_DATA_REC_SELECTED)				
		dialogProgress.create(__language__(302), title, title2)
		html = fetchURL(url)
		dialogProgress.close()
		if not validWebPage(html):
			debug("< no data")
			return False

		self.contentData = []
		self.contentData.append([__language__(351),__language__(352)])

		# current score
		score = searchRegEx(html, 'class="sh">(.*?)</d', re.DOTALL+re.MULTILINE+re.IGNORECASE)
		if score:
			self.contentData.append([__language__(350),cleanHTML(score)])

		# split into sections
		debug("LIVE TEXT - get section")
		splits = parseDocList(html, '<b>(\d+:\d+.*?br /><br />)', 'noshade', '</td>')

		# regexTimeEventText, regexTimeText
		reList = ('(\d+:\d+.*?)(?:<b>|</b>)(.*?)<br /><br />', '(\d+:\d+.*?)(?:<b>|</b>)(.*?)<')
		for split in splits:
			for regex in reList:
				matches = re.search(regex, split, re.DOTALL+re.MULTILINE+re.IGNORECASE)
				if matches:
					time = matches.group(1)
					text = cleanHTML(decodeEntities(matches.group(2)))
					self.contentData.append([text, time])
					break

		if len(self.contentData) <= 1:
			self.contentData.append([__language__(353),''])

		debug("< getTeamLiveText() success=%s" % success)
		return True



########################################################################################################################
	def getLeagueLiveScores(self, url):
		debug("> getLeagueLiveScores()")

		success = False
		title = self.getNavListAttrib(self.LEAGUES_KEY, self.NAV_LISTS_DATA_REC_SELECTED)				
		title2 = self.getNavListAttrib(self.LEAGUE_VIEW_KEY, self.NAV_LISTS_DATA_REC_SELECTED)				
		dialogProgress.create(__language__(302), title, title2)
		html = fetchURL(url)
		dialogProgress.close()
		if not validWebPage(html):
			debug("< getLeagueLiveScores() no data")
			return False

		self.contentData = []
		self.contentData.append([__language__(351),__language__(352)])

		# page has 2 subSections. 1) refresh statement 2) livescores - split into tables per match
		subSections = parseDocList(html, self.RE_SUB_SECTION)
		if len(subSections) > 1:
			# DATE 
			regex = 'noshade />.*?<b>(.*?)</b>'
			theDate = cleanHTML(searchRegEx(subSections[1], regex, re.MULTILINE+re.IGNORECASE+re.DOTALL))
			if theDate:
				self.contentData.append([theDate,__language__(352)])

			# TABLES (EACH ONE A MATCH)
			tables = parseDocList(subSections[1], '<table(.*?)</table>')
			for table in tables:
				# ROWS WITHIN TABLE
				tableRows = parseDocList(table, '<tr(.*?)</tr')

				# SCORE
				self.contentData.append(['',''])
				matches = parseDocList(tableRows[0], '>(.*?)<')
				score = ' '
				for match in matches:
					score += decodeEntities(cleanHTML(match)) + ' '
				self.contentData.append([score.strip(),''])	# score

				# SCORERS + BOOKINGS
				regex = 'c1">(.*?)</td.*?c3">(.*?)</td'
				try:
					for tableRow in tableRows[1:]:
						matches = parseDocList(tableRow, regex)
						homeList = matches[0][0].split('<br />')
						awayList = matches[0][1].split('<br />')
						# use highest count
						homeMAX = len(homeList)
						awayMAX = len(awayList)
						if homeMAX > awayMAX:
							max = homeMAX
						else:
							max = awayMAX

						self.contentData.append(['',''])
						for idx in range(max):
							try:
								home = decodeEntities(cleanHTML(homeList[idx]))
							except:
								home = ''

							try:
								away = decodeEntities(cleanHTML(awayList[idx]))
							except:
								away = ''
							if home or away:
								self.contentData.append([home,away])
				except: pass

		if len(self.contentData) <= 1:
			self.contentData.append([__language__(353),""])
			success = True

		debug("< getLeagueLiveScores() success=%s" % success)
		return True


########################################################################################################################
	def getVideprinter(self, url):
		debug("> getVideprinter()")

		success = False
		title = self.getNavListAttrib(self.LEAGUES_KEY, self.NAV_LISTS_DATA_REC_SELECTED)				
		title2 = self.getNavListAttrib(self.LEAGUE_VIEW_KEY, self.NAV_LISTS_DATA_REC_SELECTED)				
		dialogProgress.create(__language__(302), title, title2)
		html = fetchURL(url)
		dialogProgress.close()
		if not validWebPage(html):
			debug("< getVideprinter() no data")
			return False

		self.contentData = []
		# DATE
		regex = 'day and the date.*?<B>(.*?)<'
		theDate = searchRegEx(html, regex, re.MULTILINE+re.IGNORECASE+re.DOTALL)
		if theDate:
			self.contentData.append([theDate,'Updated Every 2 mins'])	# date

		# find start of relvant section - all matches
		regex = '<!--Start of stat table-->(.*?)<!--End of stat table-->'
		section = searchRegEx(html, regex, re.MULTILINE+re.IGNORECASE+re.DOTALL)

		# split into table sections - 1 per match
		splits = section.split('<p>')
		for split in splits:
			text = decodeEntities(cleanHTML(split)).strip()
			if text:
				self.contentData.append([text,''])

		success = (len(self.contentData) > 0)
		if not success:
			self.contentData.append(["No data to display.","Updated Every 2 mins"])
			success = True

		debug("< getVideprinter() success=" + str(success))
		return success


########################################################################################################################
	def getPlayerProfile(self, url, playerName):
		debug("> getPlayerProfile()")

		success=False
		title = self.getNavListAttrib(self.TEAMS_KEY, self.NAV_LISTS_DATA_REC_SELECTED)				
		title2 = self.getNavListAttrib(self.TEAM_VIEW_KEY, self.NAV_LISTS_DATA_REC_SELECTED)				

		dialogProgress.create(__language__(302), title, title2, playerName)
		html = fetchURL(url)
		dialogProgress.close()
		if not validWebPage(html):
			debug("< getPlayerProfile() no data")
			return False

		# find start of relvant section - all matches
		regex = "%s(.*?)%s" % ("<!--content start-->", "<!--content end-->")
		section = searchRegEx(html, regex, re.MULTILINE+re.IGNORECASE+re.DOTALL)

		# split into table sections - 1 per match
		tableSplits = section.split('</table')
		if tableSplits:
			self.contentData = []
			# name etc
			regex = 'c1\">(.*?)<.*?c2\"><b>(.*?)<'
			matches = parseDocList(tableSplits[0], regex)
			for match in matches:
				text = decodeEntities(cleanHTML(match[0])).strip()
				text2 = decodeEntities(cleanHTML(match[1])).strip()
				if text and text2:
					self.contentData.append([text,text2])

			# split down into stat groups
			regexStats='c1\">(.*?)<.*?c2\">(.*?)<.*?c3\">(.*?)<.*?c4\">(.*?)<.*?c5\">(.*?)<.*?c6\">(.*?)<'
			regexGroupName = 'mvb\"><b>(.*?)<'
			for idx in range(1, len(tableSplits)):
				# get group name
				groupName = searchRegEx(tableSplits[idx], regexGroupName, re.DOTALL+re.MULTILINE+re.IGNORECASE)
				if groupName:
					self.contentData.append(['',''])	# blank row
					self.contentData.append([groupName,''])

				# group stat
				matches = parseDocList(tableSplits[idx], regexStats, '"r2"')	# skip over 1st header line
				for match in matches:
					rowname = decodeEntities(cleanHTML(match[0])).strip()
					apps = decodeEntities(cleanHTML(match[1])).strip()
					assub = decodeEntities(cleanHTML(match[2])).strip()
					goals = decodeEntities(cleanHTML(match[3])).strip()
					yellow = decodeEntities(cleanHTML(match[4])).strip()
					red = decodeEntities(cleanHTML(match[5])).strip()
					lbl2 = apps + ' ' + assub + ' ' + goals + ' ' + yellow + ' ' + red
					self.contentData.append([rowname,lbl2])

			success = (len(self.contentData) > 0)
			if not success:
				self.contentData.append(["No data to display.","Updated Every 2 mins."])

		debug("< getPlayerProfile() success=" + str(success))
		return success



########################################################################################################################
	def getRSS(self, url, title=""):
		debug("> getRSS()")

		success = False
		self.rssparser = RSSParser2()
		ELEMENT_TITLE = 'title'
		ELEMENT_LINK = 'link'
		ELEMENT_DESC = 'description'
		ELEMENT_QUID = 'guid'
		tags = {ELEMENT_TITLE:[], ELEMENT_LINK:[],ELEMENT_DESC:[],ELEMENT_QUID:[]}

		dialogProgress.create(__language__(302), __language__(305), title)
		if self.rssparser.feed(url):
			feeds = self.rssparser.parse("item", tags)
			if feeds:
				self.contentData = []
				for feed in feeds:
					# store title, '', link, guid
					title = feed.getElement(ELEMENT_TITLE)
					link = feed.getElement(ELEMENT_LINK)
					desc = feed.getElement(ELEMENT_DESC)
					guid = feed.getElement(ELEMENT_QUID)
					if title and link:
						self.contentData.append([title,'',link, desc, guid])

				success = (len(self.contentData) > 0)

		dialogProgress.close()
		if not success:
			messageNoInfo()

		debug("< getRSS() success: " + str(success))
		return success


#######################################################################################################################    
	def showNewsItem(self, url, title, desc=''):
		debug("> showNewsItem()")

		success = False
		if url:
			dialogProgress.create(__language__(302), title)
			html = fetchURL(url)
			dialogProgress.close()
			if not validWebPage(html):
				debug("< no data")
				return False

			regex = "%s(.*?)%s" % ("<!-- S SF -->", self.STR_SECTION_END)
			section = searchRegEx(html, regex, re.MULTILINE+re.IGNORECASE+re.DOTALL)
			if not section:
				regex = "%s(.*?)%s" % ("<!-- E IBOX -->", self.STR_SECTION_END)
				section = searchRegEx(html, regex,re.MULTILINE+re.IGNORECASE+re.DOTALL)

			if section:
				desc = cleanHTML(decodeEntities(section).replace('<P>','\n'))		# leave single newlines

		if desc:
			textDialog = TextBoxDialog()
			textDialog.ask(title=title, text=desc)
			del textDialog
			success = True
		else:
			messageOK("RSS Item","No data to display for this item.")

		debug("< showNewsItem() success: " +str(success))
		return success

#######################################################################################################################    
	def getInterviewLinks(self, url, title):
		debug("> getInterviewLinks()")

		success = False
		dialogProgress.create(__language__(302), title)
		html = fetchURL(url)
		dialogProgress.close()
		if not validWebPage(html):
			debug("< Failed no data")
			return False

		try:
			# split into sections
			matches = parseDocList(html,'"story" href="(.*?)">(.*?)<.*?time">(.*?)<')
			if matches:
				self.contentData = []
				for match in matches:
					# [link, title, time]
					link = match[0].strip()
					title = decodeEntities(cleanHTML(match[1])).strip()
					time = decodeEntities(match[2]).strip()
					if link and title and time:
						self.contentData.append([title, time, self.BBC_NEWS_URL_PREFIX + link,'',''])

				success = (len(self.contentData) > 0)
		except:
			handleException()

		if not success:
			messageNoInfo()
			self.toggleNavListFocus(True)		# switch to navlists
		else:
			self.drawContentList(__language__(356),__language__(357),width=580)
			self.toggleNavListFocus(False)		# switch to content

		debug("< getInterviewLinks() success=%s" % success)
		return success

	######################################################################################################################
	def setup606(self):
		debug("> setup606()")
		success = False

		if not self.teams606:
			# download 606 section & store
			self.get606(self.MAINMENU_URL[self.MAINMENU_OPT_606])

		if self.teams606:
			self.contentData = []
			self.clearContentControls()
			self.logoViewCLbl.setLabel('606 Debates')
			items = self.teams606.items()
			items.sort()
			for team, phrase in items:
				self.contentData.append([team, '', phrase, '', ''])

			self.drawContentList(__language__(365), width=300, itemHeight=22, font=FONT12)
			self.toggleNavListFocus(False)					# set focus to content

			success = (len(self.contentData) > 0)
		debug("< setup606() success: " +str(success))
		return success

	######################################################################################################################
	def get606(self, url):
		debug("> get606()")

		success = False
		dialogProgress.create(__language__(302), self.MAINMENU_OPT_606)
		html = fetchURL(url)
		dialogProgress.close()
		if not validWebPage(html):
			debug("< Failed")
			return False

		regex = '<!-- S ICOL -->(.*?)<!-- E ICOL -->'
		section = searchRegEx(html, regex, re.MULTILINE+re.IGNORECASE+re.DOTALL)
		if section:
			matches = parseDocList(section, '<!-- S ILIN -->.*?phrase=(.*?)&.*?>(.*?)<')
			if matches:
				self.teams606 = {}
				for phrase, team in matches:
					self.teams606[team] = phrase

				success = (len(self.teams606) > 0)

		if not success:
			messageNoInfo()
		debug("< get606() success: " + str(success))
		return success


	######################################################################################################################
	def get606Debate(self, url, title):
		debug("> get606Debate()")

		success = False
		dialogProgress.create(__language__(302), title)
		html = fetchURL(url)
		dialogProgress.close()
		if not validWebPage(html):
			debug("< Failed")
			return False

		regex = 'articletitle"><a href="(/dna/606/[A-Z]\d+)">(.*?)<.*?articletext">(.*?)<'
		matches = parseDocList(html, regex)
		if matches:
			self.contentData = []
			for link, title, text in matches:
				self.contentData.append([title,text,self.BBC_URL_PREFIX+link,'',''])

			success = (len(self.contentData) > 0)

		if not success:
			messageNoInfo()
		debug("< get606Debate() success: " + str(success))
		return success

#######################################################################################################################    
	def show606Debate(self, url, title):
		debug("> show606Debate()")

		success = False
		dialogProgress.create(__language__(302), title)
		html = fetchURL(url)
		dialogProgress.close()
		if not validWebPage(html):
			debug("< Failed")
			return False

		desc = cleanHTML(searchRegEx(html, 'bodytext">.*?<p>(.*?)</p>', re.MULTILINE+re.IGNORECASE+re.DOTALL))
		if desc:
			# now find replies
			regex = 'comment by.*?>(.*?)<.*?posted">(.*?)<.*?<p>(.*?)</p>'
			replies = parseDocList(html, regex, 'h3>Latest','>Comment on this article<')
			for userID, posted, comment in replies:
				desc += '\n' + userID + ': ' + posted + '\n' + cleanHTML(comment) +'\n'

			textDialog = TextBoxDialog()
			textDialog.ask(title=title, text=desc)
			del textDialog
			success = True
		else:
			messageNoInfo()

		debug("< show606Debate() success: " +str(success))
		return success


	#######################################################################################################################    
	def showFFocusItem(self, url, title):
		debug("> showFFocusItem()")
		success = False

		self.logoViewCLbl.setLabel(title)
		# find post parms
		regex = '(newsid_.*?)\?.*?(redirect=\d+)'
		matches = re.search(regex, url, re.DOTALL+re.MULTILINE+re.IGNORECASE)
		try:
			post = "ms_bandwidth=bb&ms_player=rp&ms_path=/player/sol/%s&lang=en&nbram=1" \
				   "&%s.stm&news=1&nbwm=1&bbwm=1&bbram=1&bbcws=1&ms_multicast=false&ms_javascript=true" \
				   "&ms_whitelist=0&ms_warning=0&throughput=" % (matches.group(1), matches.group(2))
		except:
			post = ''

		if post:
			# fetch mediaplayer url
			dialogProgress.create(__language__(302), title)
			html = fetchURL(url, params=post,encodeURL=False)		# prevents removal of ?
			dialogProgress.close()
			if validWebPage(html):
				# extract media stream doc link
				regex = 'mediaPlayerObject.*?"src".*?value="(.*?)"'
				partURL = searchRegEx(html, regex, re.MULTILINE+re.IGNORECASE+re.DOTALL)
				if partURL:
					# fetch media stream doc
					rtspDoc = fetchURL(self.BBC_NEWS_URL_PREFIX + '/' + partURL)
					# find rtsp link
					mediaURL = searchRegEx(rtspDoc, '(rtsp.*?)\?')
					if mediaURL:
						success = playMedia(mediaURL)

		if not success:
			messageNoInfo()

		debug("< showFFocusItem() success=%s" % success)
		return success


#######################################################################################################################    
# passed url need preficing with BBC
########################################################################################################################
	def getFFocusVideo(self):
		debug("> getFFocusVideo()")

		self.clearContentControls()
		success = self.getRSS(self.MAINMENU_URL[self.MAINMENU_OPT_FFOCUS], self.MAINMENU_OPT_FFOCUS)
		if success:
			self.drawContentList(__language__(366), width=450)
			self.toggleNavListFocus(False)		# switch to content
		else:
			self.toggleNavListFocus(True)		# switch to navlists

		debug("< getFFocusVideo() success: " + str(success))
		return success


#######################################################################################################################    
# passed url need prefixing with BBC
########################################################################################################################
	def getInterviewMediaLink(self, url):
		debug("> getInterviewMediaLink()")

# ASX	http://news.bbc.co.uk/media/avdb/sport_web/video/9012da68002d768/bb/09012da68002d9cc_16x9_bb.asx
# translates to -
# VIDEO	mms://wm.bbc.net.uk/news/media/avdb/sport_web/video/9012da68002d768/bb/09012da68002d9cc_16x9_bb.wmv
# AUDIO mms://wm.bbc.net.uk/news/media/avdb/sport_web/audio/9012da68002e708/bb/09012da68002e90f_16x9_bb.wma

		success = False
		dialog.create(__language__(302), __language__(306), url)
		html = fetchURL(url)
		dialog.close()
		if not validWebPage(html):
			debug("< Failed")
			return False

		asxLink = searchRegEx(html, 'clipurl = "(.*?)"', re.MULTILINE+re.IGNORECASE+re.DOTALL)
		if asxLink:
			debug("regex media url from within ASX")
			asxDoc = fetchURL(asxLink)
			mediaLink = searchRegEx(asxDoc, 'href="(mms.*?)"', re.MULTILINE+re.IGNORECASE+re.DOTALL)
			debug("mediaLink="+mediaLink)
			if mediaLink:
				success = playMedia(mediaLink)

		if not success:
			messageNoInfo()

		debug("< getInterviewMediaLink() success: " + str(success))
		return success

########################################################################################################################
	def getGalleryPhotoLinks(self, url):
		debug("> getGalleryPhotoLinks()")

		success = False
		dialogProgress.create(__language__(302), __language__(307))
		html = fetchURL(url)
		dialogProgress.close()
		if not validWebPage(html):
			debug("< getGalleryPhotoLinks()")
			return False

		regex = 'galImg"><img src="(.*?)".*?alt="(.*?)".*?picGalCaption">(.*?)<'
		matches = parseDocList(html, regex)
		if matches:
			self.contentData = []
			for match in matches:
				try:
					link = match[0]
					title = decodeEntities(match[1]).strip()
					desc = decodeEntities(match[2]).strip()
					self.contentData.append([title,'',link, desc,link])
				except: pass

			success = (len(self.contentData) > 0)

		debug("< getGalleryPhotoLinks() success: " + str(success))
		return success

########################################################################################################################
	def displayGalleryPhoto(self, url):
		debug("> displayGalleryPhoto()")

		dialogProgress.create(__language__(302), os.path.basename(url))
		filename = os.path.join(DIR_TEAM_GFX, 'gallery_photo.jpg')
		deleteFile(filename)
		fetchURL(url, filename)
		dialogProgress.close()
		if fileExist(filename):
			# remove last photo from contentControl
			# contentCOntrol at this stahe will be TITLE, photos list - and maybe photo image
			# remove image if exists
			ctrl = self.contentControls[-1][self.CONTENT_REC_CONTROL] # get last ctrl on list
			if isinstance(ctrl, xbmcgui.ControlImage):
				debug("removing old image control")
				self.removeControl(ctrl)
				self.contentControls.pop()	# remove last element of list, which is our control image
			w = 416
			h = 300
			x = self.contentX + 300
			y = self.contentCenterY - (h/2)
			ctrl = xbmcgui.ControlImage(x, y, w, h, filename)
			self.addControl(ctrl)
			self.contentControls.append([ctrl,None])
		else:
			messageOK("Photo","Photo file missing",url)

		debug("< displayGalleryPhoto()")

########################################################################################################################
	def loadNavListTeams(self, leagueKey, visible=True):
		debug("> loadNavListTeams() leagueKey=%s" % leagueKey)

		try:
			teamsDict = self.leagueTeams[leagueKey]
		except:
			debug("leagueKey not found")
			success = False
		else:
			print teamsDict
			ctrl = self.getNavListDictValue(self.TEAMS_KEY, self.NAV_LISTS_VALUE_CONTROL)
			ctrl.reset()
			teamNameList = teamsDict.keys()
			teamNameList.sort()				# sort internally, returns None
			for teamName in teamNameList:
				ctrl.addItem(capwords(teamName))

			# only make visible if requested
			if visible:
				ctrl.setVisible(True)
				self.setFocus(ctrl)
			success = True

		debug("< loadNavListTeams() success=%s" % success)
		return success


#######################################################################################################################    
	def getTeamSquad(self, url):
		debug("> getTeamSquad()")

		success = False
		title = self.getNavListAttrib(self.TEAMS_KEY, self.NAV_LISTS_DATA_REC_SELECTED)				
		title2 = self.getNavListAttrib(self.TEAM_VIEW_KEY, self.NAV_LISTS_DATA_REC_SELECTED)				
		dialogProgress.create(__language__(302), title, title2)
		html = fetchURL(url)
		dialogProgress.close()
		if not validWebPage(html):
			debug("< getTeamSquad() no data")
			return False

		self.contentData = []
		if find(html, "Team Lineup") == -1:
			self.contentData.append([__language__(353),'',''])
			debug("< getTeamSquad() no team found")
			return True

		# DATA SECTION
		regex = 'Team Lineup(.*?)</table'
		section = searchRegEx(html, regex, re.MULTILINE+re.IGNORECASE+re.DOTALL)
		if section:
			# [squad number, link, name]
			reList = ('c1\".*?>(.+?)<.*?c2\">.*?href=\"(.*?)\".*?>(.*?)</a', 'c1\".*?>(.+?)<.*?c2\">(.*?)<')
			for regex in reList:
				matches = parseDocList(section, regex)
				if matches:
					for match in matches:
						print match
						if len(match) == 2:
							squadno = decodeEntities(match[0]).strip()
							name = decodeEntities(match[1]).strip()
							link = ''
						else:
							squadno = decodeEntities(match[0]).strip()
							link = match[1]
							name = decodeEntities(match[2]).strip() + " " + __language__(368)

						if not name:
							continue
						if not squadno:
							squadno = '?'

						self.contentData.append([squadno + '. ' + name,'',link])

				self.contentData.sort()
				success = len(self.contentData) > 0

		if not success:
			messageNoInfo()
		debug("< getTeamSquad() success: " + str(success))
		return success

########################################################################################################################
	def resetLeagueTeams(self, clear=False):
		debug("> resetLeagueTeams() clear="+str(clear))
		success = False

		try:
			debug("reset/remove TEAMS_KEY")
			self.setNavListAttrib(self.TEAMS_KEY, self.NAV_LISTS_DATA_REC_SELECTED, '')
			ctrl = self.getNavListDictValue(self.TEAMS_KEY, self.NAV_LISTS_VALUE_CONTROL)
			ctrl.reset()
			ctrl.setVisible(False)
			success = True
		except: pass
		try:
			debug("reset/remove TEAM_VIEWS_KEY")
			self.setNavListAttrib(self.TEAM_VIEW_KEY, self.NAV_LISTS_DATA_REC_SELECTED, '')
			ctrl = self.getNavListDictValue(self.TEAM_VIEW_KEY, self.NAV_LISTS_VALUE_CONTROL)
			ctrl.setVisible(False)
			ctrl.selectItem(0)
			success = True
		except: pass

		if clear and xbmcgui.Dialog().yesno(__language__(520) + " ?",__language__(200)):
			debug("reset gui, clearing all data")
			try:
				# delete leagues settings files
				for leagueName in self.leagueTeams.keys():
					fn = os.path.join(DIR_USERDATA, self.SETTINGS_LEAGUES_FILENAME % leagueName)
					deleteFile(fn)

				self.leagueTeams = {}
				self.toggleNavListFocus(switchToNavLists=True)			# force back to navlists
				self.selectedNavListKey == self.LEAGUES_KEY				# force to LEAGUES navlist
				self.setFocus(self.getNavListDictValue(self.LEAGUES_KEY, self.NAV_LISTS_VALUE_CONTROL))
				self.clearContentControls()								# wipe content display control
				self.contentData = []									# wipe content extra data
			except:
				messageOK("ERROR","Failed to reset GUI and data.","Must now close to avoid a script hang.")
				self.exit()
			else:
				messageOK(__language__(520), __language__(301))
				success = True

		debug("< resetLeagueTeams() success=%s" % success)
		return success


########################################################################################################################
	def drawContentList(self, title1='', title2='',width=600, itemHeight=28, font='font14', x=-1):
		debug("> drawContentList()")

		try:
			if self.contentData:
				debug("content available, DRAWING")
				if width > self.contentW:
					width = self.contentW
				if x == -1:
					# centered
					x = self.contentCenterX - (width/2)
					if x < 0:
						x = 0
				else:
					# as specified
					x = self.contentX + x
				y = self.contentY
				labelH = 20
				listH = self.contentH
				if title1:
					ctrl = xbmcgui.ControlLabel(x+20, self.contentY, 0, labelH, title1, font, "0xFFFFFF99")
					self.addControl(ctrl)
					self.contentControls.append([ctrl,None])		# add to content control
				if title2:
#					title2W = self.font.getTextWidth(title2, font)
					xpos = (x + width)
					ctrl = xbmcgui.ControlFadeLabel(xpos, self.contentY, 0, labelH, font, "0xFFFFFF99",alignment=XBFONT_RIGHT)
					self.addControl(ctrl)
					ctrl.addLabel(title2)
					self.contentControls.append([ctrl,None])		# add to content control

				if title1 or title2:
					y += labelH + 5
					listH -= labelH 

				if width > 250:
					btnFocusFile = BUTTON_FOCUS_LONG
				else:
					btnFocusFile = BUTTON_FOCUS
				controlList = xbmcgui.ControlList(x, y, width, listH, font=font, \
									itemHeight=itemHeight, buttonFocusTexture=btnFocusFile, \
									alignmentY=XBFONT_CENTER_Y)
				self.addControl(controlList)
				self.contentControls.append([controlList,None])
				try:
					controlList.setPageControlVisible(False)
				except: pass

				debug("adding content items")
				for contentItem in self.contentData:
					lbl1 = decodeEntities(contentItem[0])
					lbl2 = decodeEntities(contentItem[1])
					# to get around abug in ListItem that offsets label2 Y if label1 is empty,
					# load labels with at least a space
					if lbl2 == '':
						lbl2 = ' '
					if lbl1 == '':
						lbl1 = ' '
					controlList.addItem(xbmcgui.ListItem(lbl1,label2=lbl2))

				self.contentFocusIdx = len(self.contentControls)-1	# list is last
		except:
			handleException("drawContentList()")
		debug("< drawContentList()")


#######################################################################################################################    
	def drawLiveText(self):
		debug("> drawLiveText()")
		if self.contentData:
			self.liveTextCL.reset()
			for contentItem in self.contentData:
				lbl1 = decodeEntities(contentItem[0])
				lbl2 = decodeEntities(contentItem[1])
				# to get around abug in ListItem that offsets label2 Y if label1 is empty,
				# load labels with at least a space
				if not lbl2:
					lbl2 = ' '
				if not lbl1:
					lbl1 = ' '
				self.liveTextCL.addItem(xbmcgui.ListItem(lbl1,label2=lbl2))

			self.liveTextCL.setVisible(True)
		debug("< drawLiveText()")

#######################################################################################################################    
	def updateLiveText(self):
		debug("> updateLiveText()")

		success = False
		if self.liveTextUpdateURL:
			navListSelectedItem = self.getNavListAttrib(self.selectedNavListKey, self.NAV_LISTS_DATA_REC_SELECTED)
			debug("navListSelectedItem=" + navListSelectedItem)

			if navListSelectedItem == self.LEAGUE_VIEW_LIVE_SCORES:
				debug("LEAGUE_VIEW_LIVE_SCORES")
				success = self.getLeagueLiveScores(self.liveTextUpdateURL)

			elif navListSelectedItem == self.TEAM_VIEW_LIVE_TEXT:
				debug("TEAM_VIEW_LIVE_TEXT")
				success = self.getTeamLiveText(self.liveTextUpdateURL)

			elif navListSelectedItem == self.LEAGUE_VIDEPRINTER:
				debug("LEAGUE_VIDEPRINTER")
				success = self.getVideprinter(self.liveTextUpdateURL)

			if success:
				self.drawLiveText()

		if not success:
			messageNoInfo()
			timerthread.disableCountDown()
		debug("< updateLiveText()")

	#######################################################################################################################    
	def getGossipTransferDates(self):
		debug("> getGossipTransferDates()")
		self.clearContentControls()
		self.logoViewCLbl.setLabel(self.MAINMENU_OPT_GOSSIP)
		success = self.getRSS(self.MAINMENU_URL[self.MAINMENU_OPT_GOSSIP], self.MAINMENU_OPT_GOSSIP)
		if success:
			self.drawContentList(self.MAINMENU_OPT_GOSSIP,width=300)
			self.toggleNavListFocus(False)		# switch to content
		else:
			self.toggleNavListFocus(True)		# switch to navlists
		debug("< getGossipTransferDates() success="+str(success))
		return success


	#######################################################################################################################    
	def getPhotoGalley(self):
		debug("> getPhotoGalley()")
		self.clearContentControls()
		self.logoViewCLbl.setLabel(self.MAINMENU_OPT_PHOTO_GALLERY)
		success = self.getRSS(self.MAINMENU_URL[self.MAINMENU_OPT_PHOTO_GALLERY], self.MAINMENU_OPT_PHOTO_GALLERY)
		if success:
			self.drawContentList(__language__(367), width=400)
			self.toggleNavListFocus(False)		# switch to content
		else:
			self.toggleNavListFocus(True)		# switch to navlists
		debug("< getPhotoGalley() success="+str(success))
		return success

	#######################################################################################################################    
	# MAIN MENU
	#######################################################################################################################    
	def mainMenu(self):
		debug ("> mainMenu()")
		# show this dialog and wait until it's closed

		selectedItem = ''
		selectedPos = -1
		reInit = INIT_NONE
		while True:
			optReInit = INIT_NONE
			selectDialog = DialogSelect()
			selectDialog.setup(__language__(501), rows=len(self.MAINMENU), width=300)
			selectedPos, action = selectDialog.ask(self.MAINMENU, selectedPos)
			if selectedPos <= 0:				# exit selected
				break

			selectedItem = self.MAINMENU[selectedPos]
			url = self.MAINMENU_URL[selectedItem]
			self.clearContentControls()
			self.logoViewCLbl.setLabel(selectedItem)

			try:
				if selectedItem == self.MAINMENU_OPT_CONFIG_MENU:
					optReInit = self.configMenu()
				elif selectedItem in [self.MAINMENU_OPT_INTERVIEWS, \
									self.MAINMENU_OPT_MOTD_INTERVIEWS, \
									self.MAINMENU_OPT_SCORE_INTERVIEWS, \
									self.MAINMENU_OPT_GRANDSTAND_INTERVIEWS]:
					debug("self.MAINMENU - INTERVIEWS")
					if self.getInterviewLinks(url, selectedItem):
						break	# to view content
				elif selectedItem == self.MAINMENU_OPT_5LIVE:
					debug("self.MAINMENU_OPT_5LIVE")
					success = playMedia(mediaLink)
				elif selectedItem == self.MAINMENU_OPT_5LIVEX:
					debug("self.MAINMENU_OPT_5LIVEX")
					success = playMedia(mediaLink)
				elif selectedItem == self.MAINMENU_OPT_PHOTO_GALLERY:
					debug("self.MAINMENU_OPT_PHOTO_GALLERY")
					if self.getPhotoGalley():
						break	# to view content
				elif selectedItem == self.MAINMENU_OPT_LSONTV:
					debug("self.MAINMENU_OPT_LSONTV")
					lsontv = LiveSportOnTV().ask()
				elif selectedItem == self.MAINMENU_OPT_FFOCUS:
					debug("self.MAINMENU_OPT_FFOCUS")
					if self.getFFocusVideo():
						break	# to view content
				elif selectedItem == self.MAINMENU_OPT_606:
					debug("self.MAINMENU_OPT_606")
					if self.setup606():
						break	# to view content
				elif selectedItem == self.MAINMENU_OPT_GOSSIP:
					if self.getGossipTransferDates():
						break	# to view content
			except:
				messageOK("Unknown Option","Option not available for this datasource.",self.dataSource)
			else:
				if optReInit > reInit:
					reInit = optReInit	# save highest reinit level
				del selectDialog

		debug ("< mainMenu() selectedItem=%s reInit=%s" % (selectedItem, reInit))
		return selectedItem, reInit


	#############################################################################################
	# CONFIG MENU
	#############################################################################################
	def configMenu(self):
		debug("> configMenu()")

		# menu choices
		OPT_CLEAR_TEAMS = __language__(520)
		OPT_VIEW_README = __language__(521)
		OPT_VIEW_CHANGELOG = __language__(522)
		OPT_DATASOURCE = __language__(523)

		menu = [__language__(500),
				OPT_CLEAR_TEAMS,
				OPT_VIEW_README,
				OPT_VIEW_CHANGELOG,
				OPT_DATASOURCE]

		selectedPos = 0
		reInit = INIT_NONE
		while True:
			optReInit = INIT_NONE
			selectDialog = DialogSelect()
			selectDialog.setup(__language__(505), width=300, rows=len(menu))
			selectedPos, action = selectDialog.ask(menu, selectedPos)
			if selectedPos <= 0:				# exit selected
				break

			selectedItem = menu[selectedPos]

			if selectedItem == OPT_CLEAR_TEAMS:
				if self.resetLeagueTeams(True):
					optReInit = INIT_FULL
			elif selectedItem == OPT_VIEW_README:
				fn = getReadmeFilename(mylanguage)
				textBoxDialog = TextBoxDialog()
				textBoxDialog.ask(title=OPT_VIEW_README, file=fn, panel=DIALOG_PANEL)
			elif selectedItem == OPT_VIEW_CHANGELOG:
				fn = os.path.join(DIR_HOME, "Changelog.txt")
				textBoxDialog = TextBoxDialog()
				textBoxDialog.ask(title=OPT_VIEW_CHANGELOG, file=fn, panel=DIALOG_PANEL)
			elif selectedItem == OPT_DATASOURCE:
				if self.startupMenu():
					optReInit = INIT_FULL

			if optReInit > reInit:
				reInit = optReInit	# save highest reinit level

		debug ("< configMenu() reInit=%s" % reInit)
		return reInit


#######################################################################################################################    
# Realtime clock
#######################################################################################################################    
class Timer(Thread): 
	def __init__(self, motherclass, use24HourClock = True):
		debug ("> **** Timer() init")
		Thread.__init__(self)
		self.mother = motherclass #self.mother will be the same as 'self' in the main class
		self.running = False
		self.use24HourClock = use24HourClock
		self.secCounter = 0
		self.countDownRunning = False
		debug ("< **** Timer() init")

	def run(self):
		debug( "Timer().run() running: " + str(self.running) + " use24HourClock: " + str(self.use24HourClock))
		if self.running:
			return

		self.running=True
		while self.running:
			time.sleep(1)
			if self.use24HourClock:
				format = "%H:%M:%S"
			else:
				format = "%I:%M:%S %p"
			self.mother.clockLbl.setLabel(time.strftime(format,time.localtime()))

			# delay timer
			if self.countDownRunning:
				if self.secCounter >= self.delay:
					self.secCounter = 0
					self.mother.updateLiveText()
				else:
					self.secCounter += 1

		debug("Timer().run() finished")

	def setClock(self, use24HourClock):
		debug("setClock() use24HourClock: " + str(use24HourClock))
		self.use24HourClock = use24HourClock

	def stop(self):
		debug( "Timer().stop() self.running: " +str(self.running))
		self.disableCountDown()
		if self.running:
			self.running = 0
			self.join()

	def isRunning(self):
		return self.running

	def isCountDownRunning(self):
		return self.countDownRunning

	def enableCountDown(self, delay=120):
		debug("enableCountDown() delay="+str(delay))
		self.delay = delay
		self.secCounter = delay		# force an update now
		self.countDownRunning = True

	def disableCountDown(self):
		debug("disableCountDown()")
		self.countDownRunning = False


##################################################################################################################    
def validWebPage(html):
	if not html or html == -1:
		messageOK("Web page unavailable.","Please try later.")
		success = False
	else:
		success = True
	debug("validWebPage() %s" % success)
	return success

###################################################################################################################
# this version just for Football script as it doesnt use __language__
###################################################################################################################
class LiveSportOnTV:
	def __init__(self):
		debug("> LiveSportOnTV() init()")

		self.URL_BASE = 'http://www.livesportontv.com/'
		self.URL_FULLLISTING = self.URL_BASE + 'search3.php?id='
		self.URL_RSS = self.URL_BASE + 'rss.php?p=/search3.php&id='
		self.ICON_FN = os.path.join(DIR_GFX, "lsotv_$ID.png")

		self.MAIN_MENU_DATA = {
			'HDTV' : 'hdfull.php',
			'American Football' : 11,
			'Baseball' : 13,
			'Basketball' : 10,
			'Boxing' : 12,
			'Cricket' : 4,
			'Darts' : 2,
			'Football' : 1,
			'Golf' : 6,
			'Hockey' : 14,
			'Motor Sports' : 5,
			'Rugby League' : 8,
			'Rugby Union' : 7,
			'Snooker' : 3,
			'Tennis' : 9
			}
		debug("< LiveSportOnTV() init()")

	###################################################################################################################
	def onAction(self, action):
		if action in [ACTION_BACK, ACTION_B]:
			self.close()

	###################################################################################################################
	def onControl(self, control):
		pass

	###################################################################################################################
	def getSportDataRSS(self, html, ID):
		debug("> LiveSportOnTV.getSportDataRSS() ID="+str(ID))

		menu = []
		# split into rss items
		items = html.split("</item>")
		for item in items:
			matches = findAllRegEx(item, "<title>(.*?)</title")
			for match in matches:
				title = cleanHTML(decodeEntities(match))
				if title:
					menu.append(xbmcgui.ListItem(title))

		debug("< LiveSportOnTV.getSportDataRSS()")
		return menu, []

	###################################################################################################################
	def getSportData(self, html, ID):
		debug("> LiveSportOnTV.getSportData() ID=%s" % ID)

		menu = []
		menuIcons = []
		iconFN = self.ICON_FN.replace('$ID', str(ID))

		regex = 'dt">(.*?)<.*?fx">(.*?)<.*?tt">(.*?)<.*?ch">(.*?)<'
		matches = parseDocList(html, regex, '>FIXTURE DATE','</table>' )
		for match in matches:
			date = cleanHTML(decodeEntities(match[0]))
			fixture = cleanHTML(decodeEntities(match[1]))
			tourn = cleanHTML(decodeEntities(match[2]))
			channel = cleanHTML(decodeEntities(match[3]))
			menu.append(xbmcgui.ListItem(date+', '+fixture+', '+tourn ,channel))
			menuIcons.append(iconFN)

		debug("< LiveSportOnTV.getSportData()")
		return menu, menuIcons

	###################################################################################################################
	# ID is either a number (eg 1 = football) or partURL (eg hdindex.php)
	# get specific sport from the RSS version of web page (quicker)
	# or uses the web page, from which it can also get sport image icon.
	###################################################################################################################
	def displaySport(self, title, ID):
		debug("> LiveSportOnTV.displaySport title=%s ID=%s" % (title, ID))

		# ID string is a url otherwise a number
		if isinstance(ID, int):
			urlList = [self.URL_FULLLISTING + str(ID), self.URL_RSS + str(ID)]
		else:
			urlList = [self.URL_BASE + ID]

		listTitle = "LiveSportOnTV.com"
		menu = []
		menuIcons = []
		for url in urlList:
			dialogProgress.create(listTitle, "Downloading ...", title)
			html = fetchURL(url)
			dialogProgress.close()
			if html and html != -1:
				if find(url, 'rss') != -1:
					menu, menuIcons = self.getSportDataRSS(html, ID)
				else:
					menu, menuIcons = self.getSportData(html, ID)
				if menu:
					break

		selectDialog = DialogSelect()
		selectDialog.setup(listTitle, imageWidth=22,width=680, rows=len(menu), itemHeight=22, panel=DIALOG_PANEL)
		selectedPos,action = selectDialog.ask(menu, icons=menuIcons)
		debug("< LiveSportOnTV.displaySport")

	###################################################################################################################
	def ask(self):
		debug("> LiveSportOnTV.ask()")

		# make menu
		menu = self.MAIN_MENU_DATA.keys()
		menu.sort()
		menuIcons = []
		for title in menu:
			ID = str(self.MAIN_MENU_DATA[title])
			iconFN = self.ICON_FN.replace('$ID', ID)
			menuIcons.append(iconFN)

		selectedPos = 0
		while menu:
			try:
				selectDialog = DialogSelect()
				selectDialog.setup(imageWidth=25, width=300, rows=len(menu), itemHeight=25,
								   banner=os.path.join(DIR_GFX, 'livesportontv_logo.gif'), panel=DIALOG_PANEL)
				selectedPos,action = selectDialog.ask(menu, selectedPos,icons=menuIcons)
				if selectedPos < 0:				# exit selected
					break
			except:
				handleException()

			title = menu[selectedPos]
			id = self.MAIN_MENU_DATA[title]
			self.displaySport(title, id)

		debug("< LiveSportOnTV.ask()")

##############################################################################################################    
def playMedia(filename):
	success = True
	try:
		xbmc.Player().play(filename)
	except:
		debug('xbmc.Player().play() failed trying xbmc.PlayMedia() ')
		try:
			cmd = 'xbmc.PlayMedia(%s)' % filename
			xbmc.executebuiltin(cmd)
		except:
			handleException('xbmc.PlayMedia()')
			success = False
	return success

def messageNoInfo(msg=''):
	messageOK(__language__(100), __language__(102), msg)

#######################################################################################################################    
# BEGIN !
#######################################################################################################################
makeScriptDataDir() 
myscript = Football()
if myscript.isReady():
	myscript.doModal()
del myscript

xbmcgui.output("exiting script ...")
# housekeep on exit
deleteFile("temp.xml")
deleteFile("temp.html")

moduleList = ['bbbLib', 'bbbGUILib']
for m in moduleList:
	try:
		del sys.modules[m]
	except: pass

# remove other globals
try:
	del dialogProgress
except: pass

# goto xbmc home window
#try:
#	xbmc.executebuiltin('XBMC.ReplaceWindow(0)')
#except: pass

