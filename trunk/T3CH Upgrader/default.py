# T3CH Upgrader - Update your current T3CH Build to latest release.
#
# Process:
# Find & DL & unrar new build (keeping T3CH build name)
# Copies your UserData, preserving keymap.xml (if reqd).
# Create a dash boot shortcut cfg that points to new build path.
# Copies your scripts (preserving new build scripts).
# Reboots (if reqd).
#
# Included is an autoexec.py
# When installed to Q:\scripts it will run this script in 'SILENT' or 'NOTIFY' mode
#
# Many Thanks to Team AMT for code used.
#
import sys
import os
import xbmc
import xbmcgui
import urllib
from sgmllib import SGMLParser
import socket
import traceback
from string import lower, capwords
from shutil import copytree, rmtree, copy
import filecmp
import time
import re

# Script constants
__scriptname__ = "T3CH Upgrader"
__author__ = 'BigBellyBilly [BigBellyBilly@gmail.com]'
__url__ = "http://code.google.com/p/xbmc-scripting/"
__svn_url__ = "http://xbmc-scripting.googlecode.com/svn/trunk/T3CH%20Upgrader"
__date__ = '24-01-2008'
__version__ = "1.3.1"
xbmc.output( __scriptname__ + " Version: " + __version__  + " Date: " + __date__)

# Shared resources
DIR_HOME = os.path.join( os.getcwd().replace( ";", "" ) )
DIR_RESOURCES = os.path.join( DIR_HOME, "resources")
DIR_LIB = os.path.join( DIR_RESOURCES, "lib")
sys.path.append( DIR_RESOURCES )
sys.path.append( DIR_LIB )

import language
mylanguage = language.Language()
__language__ = mylanguage.localized
import update

socket.setdefaulttimeout( 15 )
dialogProgress = xbmcgui.DialogProgress()

EXIT_SCRIPT = ( 9, 10, 247, 275, 61467, )
CANCEL_DIALOG = EXIT_SCRIPT + ( 216, 257, 61448, )
TEXTBOX_XML_FILENAME = "script-T3CH_Upgrader-textbox.xml"

class Parser( SGMLParser ):
	def reset( self ):
		self.url = None
		SGMLParser.reset( self )

	def start_a( self, attrs ):
		for key, value in attrs:
			if ( key == "href" and value.find( "/STABLE/" ) == -1 and value.find( "ARCHIVE/" ) == -1 
				and value.find( "/t3ch/XBMC-SVN" ) != -1 and value.find( ".rar" ) != -1 ):
				self.url = value

#############################################################################################################
class Main:
	def __init__( self, runMode ):

		self.runMode = runMode
		xbmc.output("runMode=" + str(runMode))
		self.isSilent = (runMode != RUNMODE_NORMAL)
		xbmc.output("isSilent=" + str(self.isSilent))

		self.BASE_URL_LIST = ("http://217.118.215.116/", "http://t3ch.yi.se/")
		self.SCRIPT_DATA_DIR = os.path.join( "T:\\script_data", __scriptname__ )

		# init settings folder
		makeDir("T:\\script_data")
		makeDir(self.SCRIPT_DATA_DIR)

		# SETTINGS
		self.SETTINGS_FILENAME = os.path.join( self.SCRIPT_DATA_DIR, "settings.txt" )
		self.SETTING_SHORTCUT_DRIVE = "shortcut_drive"
		self.SETTING_SHORTCUT_NAME = "dash_shortcut_name"
		self.SETTING_UNRAR_PATH = "unrar_path"
		self.SETTING_NOTIFY_NOT_NEW = "notify_when_not_new"
		self.SETTING_CHECK_SCRIPT_UPDATE_STARTUP = "check_script_update_startup"
		self.SETTING_XFER_USERDATA = "transfer_userdata"
		self.SETTING_PROMPT_DEL_RAR = "prompt_del_rar"

		# COPY INCLUDES
		self.INCLUDES_FILENAME = os.path.join( self.SCRIPT_DATA_DIR, "includes.txt" )
		self.EXCLUDES_FILENAME = os.path.join( self.SCRIPT_DATA_DIR, "excludes.txt" )

		self._init_includes_excludes()
		self.settings = self._load_file_obj( self.SETTINGS_FILENAME, {} )

		self._check_settings()
		scriptUpdated = False
		if self.settings[self.SETTING_CHECK_SCRIPT_UPDATE_STARTUP] == __language__(402):	# check for update ?
			scriptUpdated = self._update_script(True) # silent

		if not scriptUpdated:
			url = self._get_latest_version()										# discover latest build
	#		url = "http://somehost/XBMC-SVN_2007-12-23_rev11071-T3CH.rar"			# DEV ONLY!!, saves DL it
			
			if url:
				remote_rar_name, remote_short_build_name = self._check_build_date( url )
			else:
				remote_rar_name = ""
				remote_short_build_name = ""

			# empty short_build_name indicates No New Build found.
			if self.runMode == RUNMODE_NORMAL or (remote_short_build_name and self.runMode == RUNMODE_SILENT):
				self._menu( url, remote_rar_name, remote_short_build_name )

		xbmc.output("__init__() done")


	######################################################################################
	def _check_settings( self, forceSetup=False ):
		xbmc.output( "_check_settings()" )
		while forceSetup or not self._set_default_settings(False):
			self.isSilent = False							# come out of silent inorder to setup
			self._settings_menu()							# enter settings
			forceSetup = False								# cancel force entry, can now exit when ok

	######################################################################################
	def _set_default_settings( self, forceReset=False ):
		""" set settings to default values if not exist """
		xbmc.output( "_set_default_settings() forceReset="+str(forceReset) )
		success = True

		items = {
			self.SETTING_SHORTCUT_DRIVE : "C:\\",
			self.SETTING_SHORTCUT_NAME : "xbmc",
			self.SETTING_UNRAR_PATH : "E:\\apps",
			self.SETTING_NOTIFY_NOT_NEW :  __language__(402), # yes
			self.SETTING_CHECK_SCRIPT_UPDATE_STARTUP : __language__(403),	# No
			self.SETTING_XFER_USERDATA : __language__(402),	# yes
			self.SETTING_PROMPT_DEL_RAR : __language__(402)	# yes
			}

		for key, defaultValue in items.items():
			if forceReset or not self.settings.has_key( key ) or not self.settings[key]:
				self.settings[key] = defaultValue
				if not forceReset:
					xbmc.output( "bad setting: " + key )
					success = False

		xbmc.output( "_set_default_settings() success=" +str(success))
		return success
		
	######################################################################################
	def _load_file_obj( self, filename, dataType ):
		xbmc.output( "_load_file_obj() " + filename)
		try:
			file_handle = open( filename, "r" )
			load_obj = eval( file_handle.read() )
			file_handle.close()
		except:
			if isinstance(dataType, dict):
				load_obj = {}
			elif isinstance(dataType, list):
				load_obj = []
			else:
				load_obj = None
		return load_obj

	######################################################################################
	def _save_file_obj( self, filename, save_obj ):
		xbmc.output( "_save_file_obj() " + filename)
		try:
			file_handle = open( filename, "w" )
			file_handle.write( repr( save_obj ) )
			file_handle.close()
		except:
			handleException( "_save_file_obj()" )


	######################################################################################
	def _browse_for_path( self, heading, default_path='', dialog_type=3):
		xbmc.output( "_browse_for_path() default_path=" + default_path + " dialog_type="+str(dialog_type) )
		dialog = xbmcgui.Dialog()
		skinName = xbmc.getSkinDir()
		if skinName.find("Project Mayhem") == -1:		# not PMIII, show dialog
			dialogOK( __language__( 0 ), heading )
		return dialog.browse( dialog_type, heading, "files", '', False, False, default_path)

	######################################################################################
	def _pick_shortcut_drive( self):
		xbmc.output( "_pick_shortcut_drive()" )
		options = [__language__(650), "C:\\", "E:\\", "F:\\"]
		selectDialog = xbmcgui.Dialog()
		selected = selectDialog.select( __language__( 202 ), options )
		if selected >= 1:
			return options[selected]
		else:
			return None

	######################################################################################
	def _browse_dashname(self, dash_name=''):
		xbmc.output( "_browse_dashname() curr dash_name="+dash_name)
		try:
			xbeFiles = [__language__(650), __language__(652)]

			# include current dash name into list after Exit and Manual
			xbeFiles.append(dash_name)

			# get shortcut drive to check for existing dash names
			try:
				drive = self.settings["shortcut_drive"]
			except:
				drive = "C:\\"
			xbmc.output( "checking for names on drive=" + drive)
			# find all existing dash name
			allFiles = os.listdir( drive )
			for f in allFiles:
				fn, ext = os.path.splitext(f)
				if fn != 'msdash' and (ext in ['.xbe','.cfg']):
					try:
						xbeFiles.index(fn)
					except:
						xbeFiles.append(fn)

			# select from list or use keyboard
			selectDialog = xbmcgui.Dialog()
			while True:
				selected = selectDialog.select( __language__( 201 ), xbeFiles )
				if selected <= 0:						# quit
					break
				elif selected == 1:
					dash_name = getKeyboard(dash_name, __language__( 201 ))
					if dash_name[-1] in ['\\','/']:
						dash_name = dash_name[:-1]
				else:
					# select dash name form list
					dash_name = xbeFiles[selected]

				if dash_name:
					break
				else:
					dialogOK(  __language__( 0 ), __language__( 309 ) )

		except:
			handleException("_browse_dashname()")
		xbmc.output( "_browse_dashname() final dash_name="+dash_name)
		return dash_name


	######################################################################################
	def _check_build_date( self, url ):
		xbmc.output( "> _check_build_date() " + url )

		rar_name = ''
		short_build_name = ''
		try:
			# get system build date and convert into YYYY-MM-DD
			curr_build_date_secs, curr_build_date = self._get_current_build_info()

			# extract new build date from name
			rar_name, found_build_date, found_build_date_secs, short_build_name = self._parse_rar_filename(url)

			if curr_build_date_secs >= found_build_date_secs:							# No new build
				short_build_name = ''
				rar_name = ''
				if self.settings[self.SETTING_NOTIFY_NOT_NEW] == __language__(402):		# YES, show notification
					dialogOK( __language__( 0 ), __language__( 517 ), isSilent=True )	# always use xbmc.notification
			elif self.runMode != RUNMODE_NORMAL:										# new build
				dialogOK( __language__( 0 ), __language__( 518 ), short_build_name, isSilent=True )		# always use xbmc.notification
		except:
			traceback.print_exc()

		xbmc.output("< _check_build_date() new available = " +str(short_build_name != ""))
		return (rar_name, short_build_name)

	######################################################################################
	# parse local file or url to get build info
	def _parse_rar_filename(self, filename):
		xbmc.output( "_parse_rar_filename()" )
		filenameInfo = ()
		try:
			rar_name = os.path.splitext( os.path.basename( filename ) )[0]       # removes ext
			found_build_date = searchRegEx(rar_name, '(\d+-\d+-\d+)') 
			found_build_date_secs = time.mktime( time.strptime(found_build_date,"%Y-%m-%d") )
			short_build_name = "T3CH_%s" % (found_build_date)
			xbmc.output( "rar_name= " + rar_name)
			xbmc.output( "found_build_date= " + found_build_date)
			xbmc.output( "found_build_date_secs= " + str(found_build_date_secs ))
			xbmc.output( "short_build_name= " + short_build_name)
			filenameInfo = (rar_name, found_build_date, found_build_date_secs, short_build_name)
		except:
			xbmc.output("exception parsing filename")
			traceback.print_exc()

		if not filenameInfo:
			dialogOK(__language__(0), "Unable to parse filename.", \
					 "EG.: XBMC-SVN_2007-12-23_rev11071-T3CH.rar", rar_name)

		return filenameInfo

	######################################################################################
	def _menu( self, url, remote_rar_name="", remote_short_build_name="" ):
		xbmc.output( "_menu() url=" + url )

		selectDialog = xbmcgui.Dialog()
		heading = "%s v%s (XBMC: %s %s): %s" % (__language__( 0 ), __version__, \
												xbmc.getInfoLabel('System.BuildVersion'), \
												xbmc.getInfoLabel('System.BuildDate'), \
												__language__( 600 ))

		while True:
			# build menu
			if remote_rar_name:
				dlOpt = "%s  %s"  % (__language__(612), remote_rar_name)			# download w/ rar name
			else:
				dlOpt = "%s  %s"  % (__language__(612),__language__(517))			# no new build
			options = [ __language__(650), __language__( 611 ), dlOpt,__language__( 615 ), \
						__language__( 618 ),__language__(616), __language__(617), \
						__language__(619), __language__(610) ]

			# if we have a local T3CH rar, add option to install from it
			local_rar_name = ''
			local_short_build_name = ''
			menuOptOffset = 0
			local_rar_file = self._get_local_rar_filename()
			if local_rar_file:
				try:
					local_rar_name, found_build_date, found_build_date_secs, local_short_build_name = self._parse_rar_filename(local_rar_file)
					options.insert(3, "%s  %s" % (__language__(620), local_rar_name))
					menuOptOffset += 1
				except:
					local_rar_name = '' # failed parsing local rar, don't add to menu


			if not self.isSilent:
				selected = selectDialog.select( heading, options )
			else:
				selected = 2										# do process
			xbmc.output("menu selected="+ str(selected))

			if selected <= 0:										# quit
				break

			if selected == 1:										# view logs (XBMC or T3CH)
				if dialogYesNo( __language__( 0 ), __language__( 611 ), \
								yesButton=__language__( 411 ), noButton=__language__( 410 )):
					self._view_t3ch_changelog()
				else:
					self._view_xbmc_changelog()
			elif (selected == 2 and remote_rar_name) or (selected == 3 and local_rar_name):	# install
				if selected == 2:														# local rar install
					self.rar_name = remote_rar_name
					self.short_build_name = remote_short_build_name
				else:
					self.rar_name = local_rar_name
					self.short_build_name = local_short_build_name
					url = ''

				if self._process(url):
					if dialogYesNo( __language__( 0 ), __language__( 512 )):			# reboot ?
						xbmc.executebuiltin( "XBMC.Reboot" )
					break											# stop
			elif selected == (3 + menuOptOffset):										# copy includes
				self._maintain_includes()
			elif selected == (4 + menuOptOffset):										# delete excludes
				self._maintain_excludes()
			elif selected == (5 + menuOptOffset):										# change to another t3ch
				if self._downgrade():
					break
			elif selected == (6 + menuOptOffset):										# delete old t3ch
				self._delete_old_t3ch()
			elif selected == (7 + menuOptOffset):										# update script
				if self._update_script(False):						# never silent from config menu
					xbmc.output("script updating ... closing current instance")
					break									# stop script if updated
			elif selected == (8  + menuOptOffset):										# settings
				self._check_settings(forceSetup=True)


	def _get_local_rar_filename(self):
		""" return latest T3CH rar found in install dir """

		rar_file = ""
		flist = []
		files = os.listdir( self.settings[ self.SETTING_UNRAR_PATH ] )
		for f in files:
			if searchRegEx(f, '(XBMC-SVN_\d+-\d+-\d+.*?.rar)'):
				flist.append(f)

		if flist:
			flist.sort()
			flist.reverse()
			rar_file = flist[0]
		xbmc.output("_get_local_rar_filename() " + rar_file)
		return rar_file

	######################################################################################
	# if given local unrar_file, no DL needed
	######################################################################################
	def _process( self, url='' ):
		xbmc.output( "_process() url=" + url)

		success = False
		try:
			# create work paths
			unrar_path = os.path.join( self.settings[ self.SETTING_UNRAR_PATH ], self.short_build_name)
			xbmc.output( "unrar_path= " + unrar_path )
			unrar_file = os.path.join( self.settings[ self.SETTING_UNRAR_PATH ], self.rar_name + '.rar' )
			xbmc.output( "unrar_file= " + unrar_file )

			if url:
				have_file = self._fetch_current_build( url, unrar_file )
			else:
				have_file = fileExist(unrar_file)

			if have_file:
				if self._extract_rar( unrar_file, unrar_path ):

					if self.isSilent or dialogYesNo( __language__( 0 ), __language__( 507 ), __language__( 508 ), "" ):		# switch to new build ?

						if not self.isSilent:
							dialogProgress.create( __language__( 0 ) )

						if self.settings[self.SETTING_XFER_USERDATA] == __language__(402):
							self._copy_user_data(unrar_path)

						# do Custom Copies
						self._copy_includes()

						# do Custom Deletes
						self._delete_excludes()

						success = self._update_shortcut(unrar_path)		# create shortcut

					if not self.isSilent:
						dialogProgress.close()

					# del rar according to del setting
					if self.settings[self.SETTING_PROMPT_DEL_RAR] == __language__(403) or \
						dialogYesNo( __language__( 0 ), __language__( 528 ), yesButton=__language__( 412 ), noButton=__language__( 413 )):
						deleteFile(unrar_file)									# remove RAR
		except:
			handleException("process()")
		return success

	######################################################################################
	def _init_includes_excludes(self, forceReset=False):
		xbmc.output("_init_includes_excludes()")

		if forceReset:
			deleteFile( self.INCLUDES_FILENAME )
			deleteFile( self.EXCLUDES_FILENAME )

		# if not exist we can setup using default includes & excludes files/folders
		setupIncludes = not fileExist(self.INCLUDES_FILENAME)
		setupExcludes = not fileExist(self.EXCLUDES_FILENAME)
		
		self.includes = self._load_file_obj( self.INCLUDES_FILENAME, [] )
		self.excludes = self._load_file_obj( self.EXCLUDES_FILENAME, [] )

		# setup additional Custom Copies/Delete if files dont exist
		if setupIncludes:
			self._hardcoded_includes()
			self._save_file_obj(self.INCLUDES_FILENAME, self.includes)
		if setupExcludes:
			self._hardcoded_excludes()
			self._save_file_obj(self.EXCLUDES_FILENAME, self.excludes)

	######################################################################################
	def _hardcoded_includes(self):
		""" Additional files/folders for post installation copying. All relative to Q:\ """
		xbmc.output("_hardcoded_includes()")
		# add if not already included
		srcList = [ "skin\\", "screensavers\\", "scripts\\", "plugins\\", "system\\profiles.xml" ]
		for src in srcList:
			if src not in self.includes:
				self.includes.append(src)

	######################################################################################
	def _hardcoded_excludes(self):
		""" Additional files/folders for post installation deleting. All relative to unrar_path\\XBMC """
		xbmc.output("_hardcoded_excludes()")
		srcList = [ "..\\_tools", "..\\win32", "..\\Changelog.txt", "..\\copying.txt", "..\\keymapping.txt" ]
		for src in srcList:
			if src not in self.excludes:
				self.excludes.append(src)

	######################################################################################
	def _get_latest_version( self ):
		xbmc.output( "_get_latest_version" )

		url = ""
		for baseUrl in self.BASE_URL_LIST:
			doc = readURL( baseUrl, __language__( 502 ), self.isSilent )
			if doc:
				url = self._parse_html_source( doc )
				break

		if not url:
			dialogOK( __language__( 0 ), __language__( 301 ), isSilent=self.isSilent)
		return url


	######################################################################################
	def _parse_html_source( self, htmlsource ):
		xbmc.output( "_parse_html_source()" )
		try:
			parser = Parser()
			parser.feed( htmlsource )
			parser.close()
			return parser.url
		except:
			handleException("_parse_html_source()", __language__( 305 ))
			return None

	######################################################################################
	def _fetch_current_build( self, url, file_name ):
		xbmc.output( "_fetch_current_build() " + url +" " + file_name )
		success = False
		try:
			self.reporthook_msg1 = __language__( 503 )
			self.reporthook_msg2 = file_name
			if not self.isSilent:
				dialogProgress.create( __language__( 0 ), self.reporthook_msg1, self.reporthook_msg2 )
			else:
				showNotification(__language__(0), "%s %s" % (__language__( 503 ), file_name), 240)

			urllib.urlretrieve( url , file_name, self._report_hook )

			if not self.isSilent:
				dialogProgress.close()
			success = True
		except:
			if not self.isSilent:
				dialogProgress.close()
			dialogOK( __language__( 0 ), __language__( 303 ), isSilent=self.isSilent )

		if not success:
			deleteFile(file_name)			# remove RAR, might be a partial DL
#		success = True						# DEV ONLY !!
		xbmc.output( "_fetch_current_build() success=" + str(success) )
		return success

	######################################################################################
	def _report_hook( self, count, blocksize, totalsize ):
		if not self.isSilent:
			# just update every x%
			percent = int( float( count * blocksize * 100) / totalsize )
			if percent % 5 == 0:
				dialogProgress.update( percent, self.reporthook_msg1, self.reporthook_msg2 )
			if ( dialogProgress.iscanceled() ): raise

	######################################################################################
	def _extract_rar( self, file_name, unrar_path ):
		xbmc.output( "_extract_rar() file_name=" + file_name + " unrar_path=" + unrar_path )
		success = False
		try:
			# check extract destination folder doesnt exist
			if os.path.exists(unrar_path):
				# ask to overwrite 
				if not dialogYesNo(__language__( 0 ), __language__( 314 ), unrar_path, \
								yesButton=__language__( 411 ), noButton=__language__( 410 )):
					return False

			# use a new dialog cos an update shows an empty bar that ppl expect to move
			if not self.isSilent:
				dialogProgress.create( __language__( 0 ), __language__( 504 ), unrar_path )
			else:
				showNotification(__language__( 0 ), "%s %s" % (__language__( 504 ), unrar_path), 60 )

			time.sleep(2)
			result = xbmc.executebuiltin( "XBMC.extract(%s,%s)" % ( file_name, unrar_path, ), )

			# inform user of os path checking
			if not self.isSilent:
				self._dialog_update( __language__(0), __language__( 522 ))

			# loop to check if unrar path appears
			userdata_path = os.path.join(unrar_path, 'XBMC','UserData' )
			newXBE = os.path.join(unrar_path, 'XBMC','default.xbe' )
			time.sleep(2)
			MAX = 35
			for count in range(MAX):
				isNewXBE = fileExist(newXBE)
				isUserDataPath = os.path.isdir( userdata_path )
				xbmc.output("checkCount=" + str(count) + " isUserDataPath="+str(isUserDataPath) + " isNewXBE="+str(isNewXBE))

				if not isNewXBE or not isUserDataPath:
					if count < MAX-1:
						if not self.isSilent:
							percent = int( count * 100.0 / MAX )
							msg1 = "%s (%d/%d)" % (__language__( 522 ), count, MAX)
							msg2 = "%s  %s" % (__language__(526), str(isUserDataPath))
							msg3 = "%s  %s" % (__language__(527), str(isNewXBE))
							dialogProgress.update( percent, msg1, msg2, msg3)
							if ( dialogProgress.iscanceled() ): break
						time.sleep(2)
					else:
						xbmc.output("check max reached")
				else:
					xbmc.output("checks successful")
					success = True
					break

			if not self.isSilent:
				dialogProgress.close()
		except:
			if not self.isSilent:
				dialogProgress.close()
			handleException( "_extract_rar()" )

		# unrar path not found
		if not success:
			xbmc.output("extract failed, clean up")
#			deleteFile(file_name)			# remove RAR, might be a partial DL
			try:
				rmtree( unrar_path, ignore_errors=True )	# remove partial extract
				xbmc.output("extract failed, extract path rmtree done")
			except: pass
			dialogOK( __language__( 0 ), __language__( 312 ), unrar_path )

		xbmc.output( "_extract_rar() success=" + str(success) )
		return success

	######################################################################################
	def _view_t3ch_changelog( self, ):
		xbmc.output( "_view_t3ch_changelog()" )
		doc = ""
		url = 'http://ftp1.srv.endpoint.nu/pub/repository/t3ch/T3CH-README_1ST.txt'
		doc = readURL( url, __language__( 502 ), self.isSilent )
		if doc:
			title = "T3CH Changelog"
			tbd = TextBoxDialogXML(TEXTBOX_XML_FILENAME, DIR_RESOURCES, "Default")
			tbd.ask(title, doc)
			del tbd
		else:
			dialogOK( __language__( 0 ), __language__( 310 ))

	######################################################################################
	def _view_xbmc_changelog( self, ):
		xbmc.output( "_view_xbmc_changelog()" )
		doc = ""
		# read from several home urls until get connection and doc
		for url in self.BASE_URL_LIST:
			doc = readURL( os.path.join( url, "latest.txt" ), __language__( 502 ), self.isSilent )
			if doc: break

		if doc:
			title = "XBMC Changelog"
			tbd = TextBoxDialogXML(TEXTBOX_XML_FILENAME, DIR_RESOURCES, "Default")
			tbd.ask(title, doc )
			del tbd
		else:
			dialogOK( __language__( 0 ), __language__( 310 ))

	######################################################################################
	def _view_script_doc( self, readmeORchangelog):
		xbmc.output( "_view_script_doc() readmeORchangelog=" +str(readmeORchangelog))
		if readmeORchangelog:		# readme
			title = "%s: %s" % (__language__(0), __language__(414))

			# determine language path
			base_path = mylanguage.get_base_path()
			language = xbmc.getLanguage().lower()
			fn = os.path.join( base_path, language, "readme.txt" )
			if ( not fileExist( fn ) ):
				fn = os.path.join( base_path, "english", "readme.txt" )
		else:
			title = "%s: %s" % (__language__(0), __language__(415))
			fn = os.path.join(DIR_RESOURCES, "changelog.txt")

		xbmc.output("fn=" + fn)
		# read and display
		if not fileExist(fn):
			doc = "File is missing!"
		else:
			doc = file(fn).read()

		tbd = TextBoxDialogXML(TEXTBOX_XML_FILENAME, DIR_RESOURCES, "Default")
		tbd.ask(title, doc)
		del tbd

	######################################################################################
	def _copy_user_data(self, unrar_path):
		xbmc.output( "_copy_user_data() " + unrar_path )

		try:
			# compare keymapping.xml, always copy, but make backups
			keymapFilename = "keymap.xml"
			curr_build_userdata_path = "T:\\"
			curr_build_userdata_file = os.path.join( "T:\\", keymapFilename)
			xbmc.output( "curr_build_userdata_file= " + curr_build_userdata_file )

			new_build_userdata_path = os.path.join( unrar_path, "XBMC", "UserData")
			new_build_userdata_file = os.path.join( new_build_userdata_path, keymapFilename)
			xbmc.output( "new_build_userdata_file= " + new_build_userdata_file )

			# backup new keymap as _new
			copy(new_build_userdata_file, curr_build_userdata_file+"_new")

			# backup curr keymap as _old
			copy(curr_build_userdata_file, curr_build_userdata_file+"_old")
			xbmc.output("backup made of keymap _new and _old")

			# if kemap.xml has changed, ask before copying
			try:
				if not filecmp.cmp( curr_build_userdata_file, new_build_userdata_file ):
					if self.isSilent or not dialogYesNo( __language__( 0 ), __language__( 509 ) ):
						# NO, keep new
						# copy new Keymap to current, so it will be included in copytree
						copy(new_build_userdata_file, curr_build_userdata_file)
						xbmc.output("new keymap kept")
			except:
				xbmc.output( "keymap missing=" + new_build_userdata_file )

			# remove new build UserData
			for checkCount in range(5):
				xbmc.output("rmtree UserData checkCount="+str(checkCount))
				self._dialog_update( __language__(0), __language__( 510 ), time=2)
				rmtree( new_build_userdata_path, ignore_errors=True )
				time.sleep(2)	# give os chance to complete rmdir
				if not os.path.isdir(new_build_userdata_path):
					break

			# copy current build to new build
			xbmc.output("copytree UserData")
			self._dialog_update( __language__(0), __language__( 511 ), time=2) 
			copytree( curr_build_userdata_path, new_build_userdata_path )
			xbmc.output("copytree UserData done")

			return True
		except:
			handleException("_copy_user_data()", __language__( 306 ))
		return False


	######################################################################################
	def _update_shortcut(self, unrar_path):
		xbmc.output( "_update_shortcut() " +unrar_path )

		success = False
		# get users prefered booting dash name eg. XBMC.xbe
		# if required, copy SHORTCUT by TEAM XBMC to root\<dash_name>
		dash_name = self.settings[self.SETTING_SHORTCUT_NAME]
		shortcut_drive = self.settings[self.SETTING_SHORTCUT_DRIVE]
		shortcut_xbe_file = os.path.join( shortcut_drive, dash_name + ".xbe" )
		xbmc.output( "shortcut_xbe_file= " + shortcut_xbe_file )
		shortcut_cfg_file = os.path.join( shortcut_drive, dash_name + ".cfg" )
		xbmc.output( "shortcut_cfg_file= " + shortcut_cfg_file )

		# backup CFG shortcut
		if fileExist( shortcut_cfg_file ):
			copy( shortcut_cfg_file, shortcut_cfg_file + "_old" )
			xbmc.output( "shortcut_cfg _old made" )

		# if shortcutname has dir prefix, ensure it exists
		prefix_dir = os.path.dirname(shortcut_xbe_file)
		xbmc.output("prefix_dir="+prefix_dir)
		if prefix_dir and not os.path.isdir(prefix_dir):
			makeDir(prefix_dir)

		# copy TEAM XBMC dash XBE shortcut to root - only if diff and backup first
		try:
			do_copy = False
			src_xbe_file = os.path.join( DIR_RESOURCES, "SHORTCUT by TEAM XBMC.xbe" )
			if fileExist( shortcut_xbe_file ):
				# DOES EXIST, check if diff
				if not filecmp.cmp( src_xbe_file, shortcut_xbe_file ):
					copy( shortcut_xbe_file, shortcut_xbe_file + "_old" )
					do_copy = True
					xbmc.output( "xbe diff to TEAM XBMC, shortcut_xbe _old made" )
			else:
				do_copy = True
			if do_copy:
				copy(src_xbe_file, shortcut_xbe_file)
				xbmc.output( "TEAM XBMC xbe copied" )
		except:
			handleException("_update_shortcut()", "error copying 'SHORTCUT by TEAM XBMC' to " + shortcut_drive)

		try:
			# create shortcut cfg - this points to the new T3CH XBMC build
			boot_path = os.path.join( unrar_path, "XBMC", "default.xbe" )
			xbmc.output( "boot_path= " + boot_path )
			# write new cfg to CFG_NEW
			shortcut_cfg_file_new = shortcut_cfg_file + "_new" 
			file(shortcut_cfg_file_new,'w').write(boot_path)

			# switch to new cfg now ?
			if self.isSilent or dialogYesNo( __language__( 0 ), __language__( 519 ), __language__( 520 ),__language__( 521  ),yesButton=__language__( 404 ), noButton=__language__(405) ):
				copy(shortcut_cfg_file_new, shortcut_cfg_file)
				time.sleep(1)
				success = True
		except:
			handleException("_update_shortcut()", __language__( 307 ))

		xbmc.output( "_update_shortcut() success=" + str(success) )
		return success

	######################################################################################
	def _copy_folder(self, src_path, dest_path):
		xbmc.output( "_copy_folder() src_path=" + src_path + " dest_path=" + dest_path)

		try:
			# check source folder exists!
			if not os.path.exists( src_path ):
				xbmc.output( "source folder doesnt exist! abort copy" )
				return

			# start copy of source tree
			self._dialog_update( __language__(0), __language__( 515 ), src_path) 
			# make dest root folder otherwise copytree will fail
			makeDir( dest_path )

			files = os.listdir(src_path)
			TOTAL = len(files)
			count = 0
			for f in files:
				# ignore parent dirs
				if f in ['.','..']: continue

				src_file = os.path.join( src_path, f )
				dest_file = os.path.join( dest_path, f )

				if not fileExist( dest_file ):
					if not self.isSilent:
						dialogProgress.update( int(100 / TOTAL) * count, __language__( 515 ), src_file)
						if dialogProgress.iscanceled(): break
					if os.path.isdir( src_file ):
						# copy directory
						copytree( src_file, dest_file )
						xbmc.output("copied tree OK " + src_file)
					else:
						# copy file
						copy( src_file, dest_file )
						xbmc.output("copied file OK " + src_file)
				else:
					xbmc.output( "ignored as exists in T3CH: " + dest_file)
				count += 1
		except:
			handleException("_copy_folder()", __language__( 308 ))

	######################################################################################
	def _copy_includes(self):
		xbmc.output( "_copy_includes() ")

		TOTAL = len(self.includes)
		count = 0
		unrar_path = self.settings[self.SETTING_UNRAR_PATH]
		for path in self.includes:
			try:
				if not path.startswith("Q:\\"): 
					src_path = os.path.join("Q:\\", path)
				else:
					src_path = path
				dest_path = os.path.join( unrar_path, self.short_build_name, "XBMC", path )
				if not self.isSilent:
					percent = int( count * 100.0 / TOTAL )
					self._dialog_update( __language__(0), __language__( 515 ), src_path, pct=percent )
					if dialogProgress.iscanceled(): break
				localCopy(src_path, dest_path, self.isSilent)
				count += 1
			except:
				handleException("_copy_includes() path="+path)


	######################################################################################
	def _delete_excludes(self):
		xbmc.output( "_delete_excludes() ")

		TOTAL = len(self.excludes)
		count = 0
		unrar_path = self.settings[self.SETTING_UNRAR_PATH]
		for path in self.excludes:
			try:
				if path.startswith(".."):
					path = path.replace("..\\","").replace("../","")
					dest_path = os.path.join( unrar_path, self.short_build_name, path )
				else:
					dest_path = os.path.join( unrar_path, self.short_build_name, "XBMC", path )

				if not self.isSilent:
					percent = int( count * 100.0 / TOTAL )
					self._dialog_update( __language__(0), __language__( 516 ), dest_path, pct=percent )
				if path[-1] in ["\\","/"] or os.path.isdir(dest_path):
					xbmc.output( "rmtree " + dest_path )
					rmtree(dest_path, ignore_errors=True)
				else:
					deleteFile(dest_path)
				count += 1
			except:
				handleException("_delete_excludes() path="+path)

	######################################################################################
	def _maintain_includes(self):
		xbmc.output( "_maintain_includes() ")

		try:
			selectDialog = xbmcgui.Dialog()
			while True:
				# make menu
				self.includes.sort()
				options = [__language__(650), __language__(651)]
				options.extend(self.includes)

				# show menu
				selected = selectDialog.select( __language__( 615 ), options )
				if selected <= 0:						# quit
					break

				path = ""
				deleteOption = False
				addOption = False
				if selected == 1:						# add new
					addOption = True
					path, type = self._select_file_folder(path)
					if path and \
						((type in [0,3] and self._isRestrictedFolder(path)) or \
						(type == 1 and self._isRestrictedFile(path))):
						path = ''
				else:									# remove or edit
					deleteOption = True
					path = options[selected]
					# ask what action to take (remove, edit)
					if not dialogYesNo( __language__( 0 ), path, yesButton=__language__(406), noButton=__language__(407)):
						path, type = self._select_file_folder(path)		# edit
						addOption = True

				if path:
					if deleteOption:
						del self.includes[selected-2]									# del

					if addOption:
						# add if not a duplicat
						try:
							self.includes.index(path)
						except:
							self.includes.append(path)

			# save options to file
			self._save_file_obj(self.INCLUDES_FILENAME, self.includes)
		except:
			handleException("_maintain_includes()")



	######################################################################################
	def _maintain_excludes(self):
		xbmc.output( "_maintain_excludes() ")
		try:
			def _pick_file(path=''):
				FILE = 1
				FOLDER = 0
				if not path:
					# add new
					if dialogYesNo(__language__(0), __language__(525), yesButton=__language__(408), noButton=__language__(409)):
						type = FOLDER
					else:
						type = FILE
				else:
					# editing existing
					path = os.path.join("Q:\\", path)
					path,filename = os.path.split(path)
					if not filename:
						type = FOLDER
					else:
						type = FILE

				try:
					if not path:
						path = "Q:\\"

					# always pick folder first
					path = self._browse_for_path(__language__(204), path, FOLDER)
					if not path or path[0] != "Q":
						raise

					if path[-1] not in ["\\","/"]:
						path += "\\"

					# enter filename using keyboard
					if type == FILE:
						path = getKeyboard(path, __language__(207))
						# ensure filename entered
						basename = os.path.basename(path)
						if not basename:
							raise

					bare_dest_path = str(os.path.splitdrive( path )[1])	# get path+filename, no drive
					if bare_dest_path and bare_dest_path[0] in ["/", "\\"]:
						bare_dest_path = bare_dest_path[1:]
					path = bare_dest_path.replace('/','\\')
				except:
					path = ''

				xbmc.output("_pick_file() final path=" + path + " type="+str(type))
				return path, type
			
			selectDialog = xbmcgui.Dialog()
			while True:
				# make menu
				self.excludes.sort()
				options = [__language__(650), __language__(651)]
				options.extend(self.excludes)

				# show menu
				selected = selectDialog.select( __language__( 618 ), options )
				if selected <= 0:						# quit
					break

				path = ""
				deleteOption = False
				addOption = False
				if selected == 1:						# add new
					addOption = True
					path, type = _pick_file()
					if path and \
						((type in [0,3] and self._isRestrictedFolder(path)) or \
						(type == 1 and self._isRestrictedFile(path))):
						path = ''

				else:									# remove or edit
					deleteOption = True
					path = options[selected]
					# ask what action to take (remove, edit)
					if not dialogYesNo( __language__( 0 ), path, yesButton=__language__(406), noButton=__language__(407)):
						path, type = _pick_file(path)					# edit
						addOption = True

				if path:
					if deleteOption:
						del self.excludes[selected-2]									# del

					if addOption:
						# add if not a duplicat
						try:
							self.excludes.index(path)
						except:
							self.excludes.append(path)

			# save options to file
			self._save_file_obj(self.EXCLUDES_FILENAME, self.excludes)
		except:
			handleException("_maintain_excludes()")

	#####################################################################################
	def _isRestrictedFolder(self, path):
		if (os.path.dirname(path).lower() in ["q:\\","credits","language","media","screensavers","scripts","skin","sounds","system","credits","visualisations"]):
			dialogOK(__language__(0), __language__(313))
			restricted = True
		else:
			restricted = False
		xbmc.output("_isRestrictedFolder() " + str(restricted))
		return restricted

	#####################################################################################
	def _isRestrictedFile(self, path):
		if (os.path.basename(path).lower() in ["default.xbe"]):
			dialogOK(__language__(0), __language__(313))
			restricted = True
		else:
			restricted = False
		xbmc.output("_isRestrictedFile() " + str(restricted))
		return restricted

	#####################################################################################
	def _select_file_folder(self, path=""):
		xbmc.output( "_select_file_folder() path="+path)
		FILE = 1
		FOLDER = 0
		if not path:
			# add new
			if dialogYesNo(__language__(0), __language__(525), yesButton=__language__(408), noButton=__language__(409)):
				type = FOLDER
			else:
				type = FILE
		else:
			# editing existing
			path = os.path.join("Q:\\", path)
			if path[-1] in ["\\","/"]:
				type = FOLDER
			else:
				type = FILE

		try:
			if not path:
				path = "Q:\\"

			if type == FILE:
				msg = __language__(203)
			else:
				msg = __language__(204)
			path = self._browse_for_path(msg, path, type)
			if not path or path[0] != "Q":
				raise

			bare_dest_path = str(os.path.splitdrive( path )[1])	# get path+filename, no drive
			if bare_dest_path and bare_dest_path[0] in ["/", "\\"]:
				bare_dest_path = bare_dest_path[1:]
			path = bare_dest_path.replace('/','\\')
		except:
			path = ''

		xbmc.output("_select_file_folder() final path=" + path + " type=" +str(type))
		return path, type

	#####################################################################################
	def _dialog_update(self, title="", line1="", line2="", line3="", pct=0, time=4):
		if not self.isSilent:
			dialogProgress.update( pct, line1, line2,line3 )
		else:
			msg = ("%s %s %s" % (line1, line2, line3)).strip()
			showNotification(title, msg, time)

	#####################################################################################
	def _downgrade(self):
		xbmc.output( "_downgrade() ")

		reboot = False
		# find all t3ch builds
		oldBuilds = self._find_t3ch_dirs()
		oldBuilds.insert(0, __language__( 650 ))

		# select
		selectDialog = xbmcgui.Dialog()
		selected = selectDialog.select( __language__( 205 ), oldBuilds )
		if selected > 0:						# quit
			selectedBuildName = oldBuilds[selected]

			# do downgrade by writing old path into Shortcut
			path = os.path.join( self.settings[ self.SETTING_UNRAR_PATH ], selectedBuildName)
			if self._update_shortcut(path):
				if dialogYesNo( __language__( 0 ), __language__( 512 )):				# reboot ?
					reboot = True
					xbmc.executebuiltin( "XBMC.Reboot" )

		return reboot


	#####################################################################################
	def _delete_old_t3ch(self):
		xbmc.output( "_delete_old_t3ch() ")

		# find all t3ch builds
		oldBuilds = self._find_t3ch_dirs()
		oldBuilds.insert(0, __language__( 650 ))

		# select
		selectDialog = xbmcgui.Dialog()
		while True:
			selected = selectDialog.select( __language__( 206 ), oldBuilds )
			if selected <= 0:						# quit
				break

			selectedBuildName = oldBuilds[selected]

			# delete path
			path = os.path.join( self.settings[ self.SETTING_UNRAR_PATH ], selectedBuildName)
			if dialogYesNo(__language__( 0 ), __language__( 523 ), selectedBuildName ):
				try:
					dialogProgress.create(__language__( 0 ), __language__( 524 ))
					rmtree(path, ignore_errors=True)
					del oldBuilds[selected]
					dialogProgress.close()
				except:
					handleException("_delete_old_t3ch()")

	#####################################################################################
	def _find_t3ch_dirs(self):
		xbmc.output( "_find_t3ch_dirs() ")
		dirList = []

		# get curr build name
		curr_build_date_secs, curr_build_date = self._get_current_build_info()
		# make list of folders, excluding curr build folder
		files = os.listdir(self.settings[ self.SETTING_UNRAR_PATH ] )
		for f in files:
			buildName = searchRegEx(f, "(T3CH_\d+-\d+-\d+)")
			if buildName and buildName != curr_build_date:
				dirList.append(buildName)

		return dirList

	#####################################################################################
	def _get_current_build_info(self):
		xbmc.output( "_get_current_build_info() ")
		buildDate = xbmc.getInfoLabel( "System.BuildDate" )
		curr_build_date_fmt = time.strptime(buildDate,"%b %d %Y")
		curr_build_date_secs = time.mktime(curr_build_date_fmt)
		curr_build_date = time.strftime("T3CH_%Y-%m-%d", curr_build_date_fmt)
		xbmc.output( "curr_build_date="+curr_build_date + " curr_build_date_secs= " + str(curr_build_date_secs ))
		return (curr_build_date_secs, curr_build_date)

	######################################################################################
	def _update_script( self, isSilent=False):
		xbmc.output( "> _update_script() isSilent="+str(isSilent))

		updated = False
		up = update.Update(__language__, __scriptname__)
		version = up.getLatestVersion()
		xbmc.output("Current Version: " + __version__ + " Tag Version: " + version)
		if version != "-1":
			if __version__ < version:
				if ( dialogYesNo( __language__(0), \
					  "%s %s %s." % ( __language__( 1006 ), version, __language__( 1002 ), ), __language__( 1003 ),\
					  "", noButton=__language__( 403 ), \
					  yesButton=__language__( 402 ) ) ):
					updated = True
					up.makeBackup()
					up.issueUpdate(version)
			elif not isSilent:
				dialogOK(__language__(0), __language__(1000))
		elif not isSilent:
			dialogOK(__language__(0), __language__(1030))

#		del up
		xbmc.output( "< _update_script() updated="+str(updated))
		return updated

	#####################################################################################
	def _settings_menu(self):
		xbmc.output( "_settings_menu() ")

		def _set_yes_no(key, prompt):
			if dialogYesNo( __language__( 0 ), prompt ):
				self.settings[key] = __language__( 402 )	# YES
			else:
				self.settings[key] = __language__( 403 )	# NO


		def _make_menu(settings):
			options = [__language__(639),
						__language__(650),
						"%s -> %s" %(__language__(630),self.settings[self.SETTING_SHORTCUT_DRIVE]),
						"%s -> %s" %(__language__(631),self.settings[self.SETTING_SHORTCUT_NAME]),
						"%s -> %s" %(__language__(632),self.settings[self.SETTING_UNRAR_PATH]),
						"%s -> %s" %(__language__(633),self.settings[self.SETTING_NOTIFY_NOT_NEW]),
						"%s -> %s" %(__language__(634),self.settings[self.SETTING_CHECK_SCRIPT_UPDATE_STARTUP]),
						"%s -> %s" %(__language__(635),self.settings[self.SETTING_XFER_USERDATA]),
						"%s -> %s" %(__language__(638),self.settings[self.SETTING_PROMPT_DEL_RAR]),
						__language__(636),
						__language__(637)
						]
			return options

		selectDialog = xbmcgui.Dialog()
		heading = "%s: %s" % (__language__( 0 ), __language__( 601 ) )
		while True:
			options = _make_menu(self.settings)
			selected = selectDialog.select( heading, options )
			if selected <= 0:						# quit
				break

			# match option name to settings key
			if selected == 1:														# readme/changelog
				if dialogYesNo(__language__( 0 ), __language__( 639 ), \
								yesButton=__language__( 414 ), noButton=__language__( 415 )):
					self._view_script_doc(True)			# readme
				else:
					self._view_script_doc(False)		# changelog
			if selected == 2:															# shortcut drive
				value = self._pick_shortcut_drive()
				if value:
					self.settings[self.SETTING_SHORTCUT_DRIVE] = value

			elif selected == 3:															# shortcut name
				value = self._browse_dashname(self.settings[self.SETTING_SHORTCUT_NAME])
				if value:
					self.settings[self.SETTING_SHORTCUT_NAME] = value

			elif selected == 4:															# unrar path
				value = self._browse_for_path( __language__( 200 ), self.settings[self.SETTING_UNRAR_PATH] )
				if value and value[0] != "Q":
					self.settings[self.SETTING_UNRAR_PATH] = value

			elif selected == 5:															# notify when not new
				_set_yes_no(self.SETTING_NOTIFY_NOT_NEW, __language__( 633 ))

			elif selected == 6:															# check for update
				_set_yes_no(self.SETTING_CHECK_SCRIPT_UPDATE_STARTUP, __language__( 634 ))

			elif selected == 7:															# xfer userdata
				_set_yes_no(self.SETTING_XFER_USERDATA, __language__( 635 ))

			elif selected == 8:															# prompt del rar
				_set_yes_no(self.SETTING_PROMPT_DEL_RAR, __language__( 638 ))

			elif selected == 9:															# reset settings
				if dialogYesNo(__language__(0), __language__( 636 ) + " ?"):
					self._set_default_settings(forceReset=True)

			elif selected == 10:														# reset incl & excl
				if dialogYesNo(__language__(0), __language__( 637 ) + " ?"):
					self._init_includes_excludes(forceReset=True)

		self._save_file_obj( self.SETTINGS_FILENAME, self.settings )


######################################################################################
# GLOBAL FUNCS
######################################################################################


######################################################################################
def localCopy(src_path, dest_path, isSilent=False, overwrite=False):
	xbmc.output( "localCopy() " + src_path)

	try:	
		if not os.path.exists(src_path):
			if not isSilent:
				dialogOK(__language__( 0 ), __language__( 311 ), src_path)
			return False

		# make dest root folder otherwise copytree will fail
		makeDir( os.path.dirname(dest_path) )

		if os.path.isfile(src_path):
			copy( src_path, dest_path )
		else:
			# dir
			files = os.listdir(src_path)
			TOTAL = len(files)
			xbmc.output("isdir; file count= " +str(TOTAL))
			count = 0
			for f in files:
				count += 1
				src_file = os.path.join( src_path, f )
				dest_file = os.path.join( dest_path, f )

				if overwrite or not fileExist( dest_file ):
					if os.path.isdir( src_file ):
						# copy directory
						xbmc.output( "copytree dir: " + src_file)
						copytree( src_file, dest_file )
					else:
						# copy file
						xbmc.output( "copy file: " + src_file)
						copy( src_file, dest_file )
				else:
					xbmc.output( "exists, ignored: " + src_file)
	except:
		handleException("copyFolder()", src_path, dest_path )


#################################################################################################################
def getKeyboard(default, heading, hidden=False):
	keyboard = xbmc.Keyboard( default, heading )
	keyboard.doModal()
	if ( keyboard.isConfirmed() ):
		default = keyboard.getText().strip()
	return default

#################################################################################################################
def dialogOK(title, line1='', line2='',line3='', isSilent=False, time=3):
	if isSilent:
		msg = ("%s %s %s" % (line1, line2, line3)).strip()
		showNotification(title, msg, time)
	else:
		xbmcgui.Dialog().ok(title ,line1,line2,line3)

#################################################################################################################
def showNotification(title, msg, time=4):
	time *= 1000		# make into milliseconds
	cmdArg = '"%s","%s",%d' % (title, msg, time)
	xbmc.executebuiltin( "XBMC.Notification(" + cmdArg +")" )

#################################################################################################################
def dialogYesNo(title="", line1="", line2="",line3="", yesButton="", noButton=""):
	if not title:
		title = __language__( 0 )
	if not yesButton:
		yesButton= __language__( 402 )
	if not noButton:
		noButton= __language__( 403 )
	return xbmcgui.Dialog().yesno(title, line1, line2, line3, noButton, yesButton)

#################################################################################################################
def handleException(title="", msg="", msg2=""):
	xbmc.output( "handleException()" )
	try:
		dialogProgress.close()
		title += " EXCEPTION!"
		msg3 = str( sys.exc_info()[ 1 ] )
		traceback.print_exc()
	except: pass
	dialogOK(title, msg, msg2, msg3)

#################################################################################################################
def makeDir( dir ):
	try:
		os.mkdir( dir )
		xbmc.output( "made dir: " + dir)
	except: pass

#################################################################################################################
def deleteFile( file_name ):
	try:
		os.remove( file_name )
		xbmc.output( "file deleted: " + file_name )
	except: pass

#################################################################################################################
def searchRegEx(data, regex, flags=re.IGNORECASE):
	try:
		value = re.search(regex, data, flags).group(1)
	except:
		value = ""
	xbmc.output("searchRegEx() value: " + value)
	return value

######################################################################################
def readURL( url, msg='', isSilent=False):
	xbmc.output( "readURL() " + url )

	if not isSilent:
		dialogProgress.create( __language__(0), msg, url )

	doc = None
	try:
		sock = urllib.urlopen( url )
		doc = sock.read()
		sock.close()
	except:
		print sys.exc_info()[ 1 ]

	if not isSilent:
		dialogProgress.close()
	return doc

#################################################################################################################
def fileExist(filename):
	return os.path.exists(filename)

#################################################################################################################
class TextBoxDialogXML( xbmcgui.WindowXML ):
	""" Create a skinned textbox window """
	def __init__( self, *args, **kwargs):
		pass
		
	def onInit( self ):
		xbmc.output( "TextBoxDialogXML.onInit()" )
		self.getControl( 3 ).setLabel( self.title )
		self.getControl( 5 ).setText( self.text )

	def onClick( self, controlId ):
		pass

	def onFocus( self, controlId ):
		pass

	def onAction( self, action ):
#		print( "onAction(): actionID=%i buttonCode=%i " % ( action.getId(), action.getButtonCode()) )
		if ( action.getButtonCode() in CANCEL_DIALOG or action.getId() in CANCEL_DIALOG):
			self.close()

	def ask(self, title, text ):
		xbmc.output("TextBoxDialogXML().ask()")
		self.title = title
		self.text = text

		self.doModal()		# causes window to be drawn


#################################################################################################################
 # Script starts here
#################################################################################################################
RUNMODE_NORMAL = "NORMAL"
RUNMODE_NOTIFY = "NOTIFY"
RUNMODE_SILENT = "SILENT"
try:
	# get runMode as arg
	runMode = sys.argv[1].strip()
	if not runMode in [RUNMODE_NORMAL, RUNMODE_NOTIFY, RUNMODE_SILENT]:
		print "unknown runmode"
		raise
except:
	runMode = RUNMODE_NORMAL

Main(runMode)

xbmc.output("script exit and housekeeping")
# remove globals
try:
	del dialogProgress
except: pass
