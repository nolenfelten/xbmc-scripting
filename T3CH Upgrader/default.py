# T3CH Upgrader - An extention of official 'T3CH Loader' script.
#
# Heavily modified by BigBellyBilly to extend functionality to also copy UserData, Scripts,Plugins etc
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
__date__ = '25-11-2007'
__version__ = "1.0"
xbmc.output( __scriptname__ + " Version: " + __version__  + " Date: " + __date__)

# Shared resources
DIR_HOME = os.path.join( os.getcwd().replace( ";", "" ) )
DIR_RESOURCES = os.path.join( DIR_HOME, "resources")
DIR_LIB = os.path.join( DIR_RESOURCES, "lib")
sys.path.append( DIR_RESOURCES )
sys.path.append( DIR_LIB )

import language
__language__ = language.Language().localized

socket.setdefaulttimeout( 15 )
dialogProgress = xbmcgui.DialogProgress()

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

		# SETTINGS
		self.SETTINGS_FILENAME = os.path.join( self.SCRIPT_DATA_DIR, "settings.txt" )
		self.SETTING_SHORTCUT_DRIVE = "shortcut_drive"
		self.SETTING_SHORTCUT_NAME = "dash_shortcut_name"
		self.SETTING_UNRAR_PATH = "unrar_path"
		self.SETTING_NOTIFY_NOT_NEW = "notify_when_not_new"
		self.SETTING_CHECK_SCRIPT_UPDATE_STARTUP = "check_script_update_startup"
		self.SETTING_XFER_USERDATA = "transfer_userdata"

		# COPY INCLUDES
		self.INCLUDES_FILENAME = os.path.join( self.SCRIPT_DATA_DIR, "includes.txt" )
		self.EXCLUDES_FILENAME = os.path.join( self.SCRIPT_DATA_DIR, "excludes.txt" )

		# init
		makeDir(self.SCRIPT_DATA_DIR)
		self.settings = self._load_file_obj( self.SETTINGS_FILENAME, {} )
		self.includes = self._load_file_obj( self.INCLUDES_FILENAME, [] )
		self.excludes = self._load_file_obj( self.EXCLUDES_FILENAME, [] )

		self._check_settings()
		if self.settings[self.SETTING_CHECK_SCRIPT_UPDATE_STARTUP] == __language__(402):	# check for update ?
			self._update_script(True)														# silent

		url = self._get_latest_version()										# discover latest build
#		url = "http://somehost/XBMC-SVN_2007-11-17_rev10770-T3CH.rar"			# DEV ONLY!!, saves DL it
		if url:
			self.rar_name, self.short_build_name = self._check_build_date( url )
		else:
			self.short_build_name = ""

		# empty short_build_name indicates No New Build found.
		if self.runMode == RUNMODE_NORMAL or (self.short_build_name and self.runMode == RUNMODE_SILENT):
			self._menu( url )

		xbmc.output("__init__() done - exit script")


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
			self.SETTING_XFER_USERDATA : __language__(402)	# yes
			}

		for key, defaultValue in items.items():
			if forceReset or not self.settings.has_key( key ) or not self.settings[key]:
				self.settings[key] = defaultValue
				if not forceReset:
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
		xbmc.output( "_browse_dashname() ")
		try:
			xbeFiles = [__language__(650), __language__(652)]
			# get shortcut drive to check for existing dash names
			try:
				drive = self.settings["shortcut_drive"]
			except:
				drive = "C:\\"
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
				else:
					# select dash name form list
					dash_name = xbeFiles[selected]

				if dash_name:
					break
				else:
					dialogOK(  __language__( 0 ), __language__( 309 ) )

		except:
			handleException("_browse_dashname()")
		return dash_name


	######################################################################################
	def _check_build_date( self, url ):
		xbmc.output( "_check_build_date() " + url )

		rar_name = ''
		short_build_name = ''
		try:
			# get system build date and convert into YYYY-MM-DD
			curr_build_date_secs, curr_build_date = self._get_current_build_info()

			# extract new build date from name
			try:
				rar_name = os.path.splitext( os.path.basename( url ) )[0]       # removes ext
				found_build_date = searchRegEx(rar_name, '(\d+-\d+-\d+)') 
				found_build_date_secs = time.mktime( time.strptime(found_build_date,"%Y-%m-%d") )
				xbmc.output( "found_build_date= " + found_build_date)
				xbmc.output( "found_build_date_secs= " + str(found_build_date_secs ))
			except:
				xbmc.output("unable to parse 'found_build_date' - setting to None Found")
				found_build_date_secs = 0

			if curr_build_date_secs >= found_build_date_secs:							# No new build
				if self.settings[self.SETTING_NOTIFY_NOT_NEW] == __language__(402):		# YES, show notification
					dialogOK( __language__( 0 ), __language__( 517 ), isSilent=True )						# always use xbmc.notification
			else:
				# new build
				short_build_name = "T3CH_%s" % (found_build_date)
				if self.runMode != RUNMODE_NORMAL:
					dialogOK( __language__( 0 ), __language__( 518 ), short_build_name, isSilent=True )		# always use xbmc.notification
		except:
			handleException("_check_build_date()")

		xbmc.output("_check_build_date() new available = " +str(short_build_name != ""))
		return (rar_name, short_build_name)

	######################################################################################
	def _menu( self, url ):
		xbmc.output( "_menu() " + url )

		selectDialog = xbmcgui.Dialog()
		heading = "%s: %s" % (__language__( 0 ), __language__( 600 ))
		if self.short_build_name:
			dlOpt = "%s  %s"  % (__language__(612),self.rar_name)		# download
		else:
			dlOpt = "%s  %s"  % (__language__(612),__language__(517))			# no new build
		options = [ __language__(650), __language__( 611 ), dlOpt,__language__( 615 ),__language__( 618 ),__language__(616), __language__(617), __language__(619), __language__(610) ]
		while True:
			if not self.isSilent:
				selected = selectDialog.select( heading, options )
			else:
				selected = 2										# do process
			xbmc.output("menu selected="+ str(selected))

			if selected <= 0:						# quit
				break
			elif selected == 1:										# view log
				self._view_changelog()
			elif selected == 2 and self.short_build_name:			# if available, download & process
				if self._process(url):
					if dialogYesNo( __language__( 0 ), __language__( 512 )):				# reboot ?
						xbmc.executebuiltin( "XBMC.Reboot" )
				break											# stop
			elif selected == 3:										# copy includes
				self._maintain_includes()
			elif selected == 4:										# delete excludes
				self._maintain_excludes()
			elif selected == 5:										# downgrade to an old t3ch
				self._downgrade()
			elif selected == 6:										# delete old t3ch
				self._delete_old_t3ch()
			elif selected == 7:										# update script
				self._update_script(False)							# never silent from config menu
			elif selected == 8:										# settings
				self._check_settings(forceSetup=True)


	######################################################################################
	def _process( self, url):
		xbmc.output( "_process()" + url )

		success = False
		try:
			# create work paths
			unrar_path = os.path.join( self.settings[ self.SETTING_UNRAR_PATH ], self.short_build_name)
			xbmc.output( "unrar_path= " + unrar_path )
			unrar_file = os.path.join( self.settings[ self.SETTING_UNRAR_PATH ], self.rar_name + '.rar' )
			xbmc.output( "unrar_file= " + unrar_file )

			if self._fetch_current_build( url, unrar_file ):

				# try unrar twice
				if self._extract_rar( unrar_file, unrar_path ):

					if self.isSilent or dialogYesNo( __language__( 0 ), __language__( 507 ), __language__( 508 ), "" ):		# switch to new build ?

						if not self.isSilent:
							dialogProgress.create( __language__( 0 ) )

						if self.settings[self.SETTING_XFER_USERDATA] == __language__(402):
							self._copy_user_data(unrar_path)

						# copy additional folders
						src_path = os.path.join( "Q:\\", "skin" )
						dest_path = os.path.join( unrar_path, "XBMC", "skin" )
						self._copy_folder(src_path, dest_path)

						src_path = os.path.join( "Q:\\", "screensavers" )
						dest_path = os.path.join( unrar_path, "XBMC", "screensavers" )
						self._copy_folder(src_path, dest_path)

						src_path = os.path.join( "Q:\\", "scripts" )
						dest_path = os.path.join( unrar_path, "XBMC", "scripts" )
						self._copy_folder(src_path, dest_path)

						# for each subdir in plugins copy their subdirs
						src_path = os.path.join( "Q:\\", "plugins" )
						dirList = os.listdir(src_path)
						for dir in dirList:
							src_path = os.path.join( "Q:\\", "plugins", dir )
							dest_path = os.path.join( unrar_path, "XBMC", "plugins", dir )
							self._copy_folder(src_path, dest_path )

						# do INCLUDE and EXCLUDE file lists
						self._copy_includes()
						self._delete_excludes()

						success = self._update_shortcut(unrar_path)		# create shortcut

					# delete unwanted files/folders
					self._delete_excess(unrar_file)
					if not self.isSilent:
						dialogProgress.close()
		except:
			handleException("process()")
		return success

	######################################################################################
	def _delete_excess( self, unrar_file ):
		xbmc.output( "_delete_excess" )
		deleteFile(unrar_file)									# remove RAR
		removeList = [ os.path.join( self.settings[ self.SETTING_UNRAR_PATH ], self.short_build_name,"_tools"), \
					 os.path.join( self.settings[ self.SETTING_UNRAR_PATH ], self.short_build_name,"win32"), \
					 os.path.join( self.settings[ self.SETTING_UNRAR_PATH ], self.short_build_name,"Changelog.txt") ]

		for f in removeList:
			try:
				if os.path.exists(f):
					if os.path.isdir(f):
						rmtree(f, ignore_errors=True)
						xbmc.output( "rmtree: " + f)
					else:
						deleteFile(f)
			except:
				xbmc.output("delete failed: " + f)

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
			if not self.isSilent:
				dialogProgress.create( __language__( 0 ), __language__( 503 ), file_name )
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
		xbmc.output( "_fetch_current_build() success=" + str(success) )
		return success

	######################################################################################
	def _report_hook( self, count, blocksize, totalsize ):
		if not self.isSilent:
			# just update every x%
			percent = int( float( count * blocksize * 100) / totalsize )
			if (percent % 5) == 0:
				dialogProgress.update( percent )
			if ( dialogProgress.iscanceled() ): raise

	######################################################################################
	def _extract_rar( self, file_name, unrar_path ):
		xbmc.output( "_extract_rar() file_name=" + file_name + " unrar_path=" + unrar_path )
		success = False
		try:
			# use a new dialog cos an update shows an empty bar that ppl expect to move
			if not self.isSilent:
				dialogProgress.create( __language__( 0 ), __language__( 504 ), unrar_path )
			else:
				showNotification(__language__( 0 ), "%s %s" % (__language__( 504 ), unrar_path), 60 )
				
			result = xbmc.executebuiltin( "XBMC.extract(%s,%s)" % ( file_name, unrar_path, ), )

			# inform user of os path checking
			if not self.isSilent:
				self._dialog_update( __language__(0), __language__( 522 ))

			# loop to check if unrar path appears
			userdata_path = os.path.join(unrar_path, 'XBMC','UserData' )
			time.sleep(5)
			MAX = 20
			for count in range(MAX):
				if not os.path.exists( unrar_path ) or not os.path.exists( userdata_path ):
					if count < MAX-1:
						if not self.isSilent:
							dialogProgress.update( int(int(100 / MAX) * count) )
						time.sleep(2)
				else:
					success = True
					break

			if not self.isSilent:
				dialogProgress.close()
		except:
			if not self.isSilent:
				dialogProgress.close()
			handleException( "_extract_rar()", __language__( 304 ) )

		# unrar path not found
		if not success:
			dialogOK( __language__( 0 ), __language__( 312 ), unrar_path )
			deleteFile(os.path.join( unrar_path, file_name ))			# remove RAR, might be a partial DL

		xbmc.output( "_extract_rar() success=" + str(success) )
		return success

	######################################################################################
	def _view_changelog( self, ):
		xbmc.output( "_view_changelog()" )
		doc = ""
		for url in self.BASE_URL_LIST:
			doc = readURL( os.path.join( url, "latest.txt" ), __language__( 502 ), self.isSilent )
			if doc: break

		if doc:
			tbd = TextBoxDialog().ask("Changelog:", doc, panel=os.path.join( DIR_RESOURCES, 'dialog-panel.png'))
		else:
			dialogOK( __language__( 0 ), __language__( 310 ))

	######################################################################################
	def _copy_user_data(self, unrar_path):
		xbmc.output( "_copy_user_data() " + unrar_path )

		try:
			# compare keymapping.xml, always copy, but make backups
			keymapFilename = "keymap.xml"
			curr_build_userdata_path = "T:\\"
			xbmc.output( "curr_build_userdata_path= " + curr_build_userdata_path )

			curr_build_userdata_file = os.path.join( "T:\\", keymapFilename)
			xbmc.output( "curr_build_userdata_file= " + curr_build_userdata_file )

			new_build_userdata_path = os.path.join( unrar_path, "XBMC", "UserData")
			xbmc.output( "new_build_userdata_path= " + new_build_userdata_path )

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
		# if required, copy SHORTCUT by TEAM XBMCto root\<dash_name>
		dash_name = self.settings[self.SETTING_SHORTCUT_NAME]
		shortcut_drive = self.settings[self.SETTING_SHORTCUT_DRIVE]
		shortcut_xbe_file = os.path.join( shortcut_drive, dash_name + ".xbe" )
		shortcut_cfg_file = os.path.join( shortcut_drive, dash_name + ".cfg" )
		xbmc.output( "shortcut_xbe_file= " + shortcut_xbe_file )

		# backup CFG shortcut
		if os.path.exists( shortcut_cfg_file ):
			copy( shortcut_cfg_file, shortcut_cfg_file + "_old" )

		# copy TEAM XBMC dash XBE shortcut to root - backup first
		try:
			if os.path.exists( shortcut_xbe_file ):
				copy( shortcut_xbe_file, shortcut_xbe_file + "_old" )
			src_xbe_file = os.path.join( DIR_RESOURCES, "SHORTCUT by TEAM XBMC.xbe" )
			copy(src_xbe_file, shortcut_xbe_file)
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
				count += 1
				# ignore parent dirs
				if f in ['.','..']: continue

				src_file = os.path.join( src_path, f )
				xbmc.output( "src_file= " + src_file )
				dest_file = os.path.join( dest_path, f )
				xbmc.output( "dest_file= " + dest_file )

				if not os.path.exists( dest_file ):
					if not self.isSilent:
						dialogProgress.update( int(100 / TOTAL) * count, __language__( 515 ), src_file)
					if os.path.isdir( src_file ):
						# copy directory
						copytree( src_file, dest_file )
						xbmc.output("copied tree OK")
					else:
						# copy file
						copy( src_file, dest_file )
						xbmc.output("copied file OK")
				else:
					xbmc.output( "ignored as exists in T3CH" )
		except:
			handleException("_copy_folder()", __language__( 308 ))

	######################################################################################
	def _copy_includes(self):
		xbmc.output( "_copy_includes() ")

		TOTAL = len(self.includes)
		count = 0
		for path in self.includes:
			try:
				src_path = os.path.join("Q:\\", path)
				dest_path = os.path.join( self.settings[self.SETTING_UNRAR_PATH], self.short_build_name, "XBMC", path )
				if not self.isSilent:
					percent = int(int(100 / TOTAL) * count)
					self._dialog_update( __language__(0), __language__( 515 ), src_path, pct=percent ) 
				localCopy(src_path, dest_path, self.isSilent)
			except:
				handleException("_copy_includes() path="+path)


	######################################################################################
	def _delete_excludes(self):
		xbmc.output( "_delete_excludes() ")

		TOTAL = len(self.excludes)
		count = 0
		for path in self.excludes:
			try:
				dest_path = os.path.join( self.settings[self.SETTING_UNRAR_PATH], self.short_build_name, "XBMC", path )
				if not self.isSilent:
					percent = int(int(100 / TOTAL) * count)
					self._dialog_update( __language__(0), __language__( 516 ), dest_path, pct=percent )
				if path[-1] in ["\\","/"]:
					xbmc.output( "rmtree " + dest_path )
					rmtree(dest_path, ignore_errors=True)
				else:
					deleteFile(dest_path)
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
					xbmc.executebuiltin( "XBMC.Reboot" )


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
			else:
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
		xbmc.output( "_update_script() isSilent="+str(isSilent))
		import update
		updt = update.Update(isSilent)
		del updt
		xbmc.output( "_update_script() done")

	#####################################################################################
	def _settings_menu(self):
		xbmc.output( "_settings_menu() ")

		def _set_yes_no(key, prompt):
			if dialogYesNo( __language__( 0 ), prompt ):
				self.settings[key] = __language__( 402 )	# YES
			else:
				self.settings[key] = __language__( 403 )	# NO


		def _make_menu(settings):
			options = [ __language__(650),
						"%s -> %s" %(__language__(630),self.settings[self.SETTING_SHORTCUT_DRIVE]),
						"%s -> %s" %(__language__(631),self.settings[self.SETTING_SHORTCUT_NAME]),
						"%s -> %s" %(__language__(632),self.settings[self.SETTING_UNRAR_PATH]),
						"%s -> %s" %(__language__(633),self.settings[self.SETTING_NOTIFY_NOT_NEW]),
						"%s -> %s" %(__language__(634),self.settings[self.SETTING_CHECK_SCRIPT_UPDATE_STARTUP]),
						"%s -> %s" %(__language__(635),self.settings[self.SETTING_XFER_USERDATA]),
						"%s" % (__language__(636))
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
			if selected == 1:
				value = self._pick_shortcut_drive()
				if value:
					self.settings[self.SETTING_SHORTCUT_DRIVE] = value

			elif selected == 2:
				value = self._browse_dashname(self.settings[self.SETTING_SHORTCUT_NAME])
				if value:
					self.settings[self.SETTING_SHORTCUT_NAME] = value

			elif selected == 3:
				value = self._browse_for_path( __language__( 200 ), self.settings[self.SETTING_UNRAR_PATH] )
				if value and value[0] != "Q":
					self.settings[self.SETTING_UNRAR_PATH] = value

			elif selected == 4:
				_set_yes_no(self.SETTING_NOTIFY_NOT_NEW, __language__( 633 ))

			elif selected == 5:
				_set_yes_no(self.SETTING_CHECK_SCRIPT_UPDATE_STARTUP, __language__( 634 ))

			elif selected == 6:
				_set_yes_no(self.SETTING_XFER_USERDATA, __language__( 635 ))

			elif selected == 7:												# reset
				if dialogYesNo(__language__(0), __language__( 636 ) + " ?"):
					self._set_default_settings(forceReset=True)

			self._save_file_obj( self.SETTINGS_FILENAME, self.settings )


######################################################################################
# GLOBAL FUNCS
######################################################################################


######################################################################################
def localCopy(src_path, dest_path, isSilent=False):
	xbmc.output( "localCopy() ")
	print "src=" + src_path, "dest=" + dest_path

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
			xbmc.output("copy dir")
			files = os.listdir(src_path)
			TOTAL = len(files)
			count = 0
			for f in files:
				count += 1
				src_file = os.path.join( src_path, f )
				xbmc.output( "src_file= " + src_file )
				dest_file = os.path.join( dest_path, f )
				xbmc.output( "dest_file= " + dest_file )

				if os.path.isdir( src_file ):
					# copy directory
					if os.path.exists( dest_file ):
						os.remove(dest_file)
					copytree( src_file, dest_file )
				else:
					# copy file
					copy( src_file, dest_file )
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

	try:
		sock = urllib.urlopen( url )
		doc = sock.read()
		sock.close()
	except:
		print sys.exc_info()[ 1 ]
		doc = None

	if not isSilent:
		dialogProgress.close()
	return doc


#################################################################################################################
class TextBoxDialog(xbmcgui.WindowDialog):
	def __init__(self):
		self.setCoordinateResolution(6)	# PAL 4:3

	def _setupDisplay(self, width, height, panel='dialog-panel.png'):
		xbmc.output( "TextBoxDialog().ask()" )

		xpos = int((720 /2) - (width /2))
		ypos = int((576 /2) - (height /2))

		try:
			self.addControl(xbmcgui.ControlImage(xpos, ypos, width, height, panel))
		except: pass

		xpos += 25
		ypos += 10
		self.titleCL = xbmcgui.ControlLabel(xpos, ypos, width-35, 30, '','font14', "0xFFFFFF99", alignment=0x00000002)
		self.addControl(self.titleCL)
		ypos += 25
		self.descCTB = xbmcgui.ControlTextBox(xpos, ypos, width-44, height-85, 'font10', '0xFFFFFFEE')
		self.addControl(self.descCTB)

	def ask(self, title, text, width=685, height=560, panel=''):
		xbmc.output( "TextBoxDialog().ask()" )
		self._setupDisplay(width, height, panel)
		self.titleCL.setLabel(title)
		self.descCTB.setText(text)
		self.setFocus(self.descCTB)
		self.doModal()

	def onAction(self, action):
		if action in [9, 10]:
			self.close()

	def onControl(self, control):
		xbmc.output( "TextBoxDialog().onControl()" )

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

# remove globals
try:
	del dialogProgress
except: pass
