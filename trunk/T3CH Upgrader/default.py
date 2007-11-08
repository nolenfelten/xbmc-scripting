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
__date__ = '07-11-2007'
__version__ = "v1.0 b23"
__svn_revision__ = "1653"
xbmc.output( __scriptname__ + " Version: " + __version__ + " SVN Revision: " + __svn_revision__ + " Date: " + __date__)

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

		# COPY INCLUDES
		self.INCLUDES_FILENAME = os.path.join( self.SCRIPT_DATA_DIR, "includes.txt" )
		self.EXCLUDES_FILENAME = os.path.join( self.SCRIPT_DATA_DIR, "excludes.txt" )

		if self._initialize():
			# check for script update ?
			if self.settings[self.SETTING_CHECK_SCRIPT_UPDATE_STARTUP] == __language__(402):
				self._update_script()

			url = self._get_latest_version()										# discover latest build
#			url = "http://somehost/XBMC-SVN_2007-11-04_rev10675-T3CH.rar"			# DEV ONLY!!, saves DL it
			if url:
				self.rar_name, self.short_build_name = self._check_build_date( url )
			else:
				self.short_build_name = ""

			# empty short_build_name indicates No New Build found, but we can still enter menu
			# if NOTIFY, no further processing
			if self.runMode in (RUNMODE_NORMAL, RUNMODE_SILENT):
				self._menu( url )

	######################################################################################
	def _initialize( self, forceSetup=False ):
		xbmc.output( "_initialize()" )
		success = False

		self._make_script_data_path()
		self.settings = self._load_file_obj( self.SETTINGS_FILENAME, {} )
		self.includes = self._load_file_obj( self.INCLUDES_FILENAME, [] )
		self.excludes = self._load_file_obj( self.EXCLUDES_FILENAME, [] )
		while not success:
			# if forcing setup, skip initial setting check
			if not forceSetup:
				success = self._check_default_settings()
			else:
				forceSetup = False								# will now check on next loop

			# enter and save settings
			if not success:
				self.isSilent = False							# come out of silent inorder to setup
				self._set_default_settings()
				self._settings_menu()

		xbmc.output( "_initialize() success= " + str(success) )
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
	def _set_default_settings( self ):
		xbmc.output( "_set_default_settings()" )
		key = self.SETTING_SHORTCUT_DRIVE
		if not self.settings.has_key( key ) or not self.settings[key]:
			self.settings[key] = "C:\\" 

		key = self.SETTING_SHORTCUT_NAME
		if not self.settings.has_key( key ) or not self.settings[key]:
			self.settings[ key ] = "xbmc"
			
		key = self.SETTING_UNRAR_PATH
		if not self.settings.has_key( key ) or not self.settings[key]:
			self.settings[ key ] = "E:\\apps"

		key = self.SETTING_NOTIFY_NOT_NEW
		if not self.settings.has_key( key ) or not self.settings[key]:
			self.settings[ self.SETTING_NOTIFY_NOT_NEW ] = __language__(402)	# yes
			
		key = self.SETTING_CHECK_SCRIPT_UPDATE_STARTUP
		if not self.settings.has_key( key ) or not self.settings[key]:
			self.settings[ key ] = __language__(403)	# No

	######################################################################################
	def _check_default_settings( self ):
		xbmc.output( "_check_default_settings()" )
		error = False
		try:
			if not self.settings:
				raise

			# check all keys exist
			keysList = [self.SETTING_SHORTCUT_DRIVE,
						self.SETTING_UNRAR_PATH,
						self.SETTING_SHORTCUT_NAME,
						self.SETTING_NOTIFY_NOT_NEW,
						self.SETTING_CHECK_SCRIPT_UPDATE_STARTUP]
			for key in keysList:
				if not self.settings.has_key( key ):
					xbmc.output( "setting missing, key= " + key )
					raise
				elif self.settings[ key ] in ["",None]:
					xbmc.output( "setting empty, key= " + key )
					raise
		except:
			error = True

		xbmc.output( "_check_default_settings() error = " + str(error) )
		return not error

	######################################################################################
	def _make_script_data_path( self ):
		xbmc.output( "_make_script_data_path() " + self.SCRIPT_DATA_DIR)
		try:
			os.makedirs( self.SCRIPT_DATA_DIR )
		except: pass

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
				new_build_date = searchRegEx(rar_name, '(\d+-\d+-\d+)') 
				new_build_date_secs = time.mktime( time.strptime(new_build_date,"%Y-%m-%d") )
				xbmc.output( "new_build_date= " + new_build_date)
				xbmc.output( "new_build_date_secs= " + str(new_build_date_secs ))
			except:
				new_build_date_secs = 0

			if curr_build_date_secs >= new_build_date_secs:							# No new build
				if self.settings[self.SETTING_NOTIFY_NOT_NEW] == __language__(402):	# YES, show notification
					dialogOK( __language__( 0 ), __language__( 517 ), isSilent=True )						# always use xbmc.notification
			else:
				# new build
				short_build_name = "T3CH_%s" % (new_build_date)
				if self.runMode != RUNMODE_NORMAL:
					dialogOK( __language__( 0 ), __language__( 518 ), short_build_name, isSilent=True )		# always use xbmc.notification
		except:
			handleException("_check_build_date")
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
				self._update_script()
			elif selected == 8:										# settings
				if not self._initialize(forceSetup=True):			# setup incomplete, quit
					break


	######################################################################################
	def _process( self, url):
		xbmc.output( "_process()" + url )

		success = False
		try:
			if not self.isSilent:
				dialogProgress.create( __language__( 0 ) )
			# create work paths
			unrar_path = os.path.join( self.settings[ self.SETTING_UNRAR_PATH ], self.short_build_name)
			xbmc.output( "unrar_path= " + unrar_path )
			unrar_file = os.path.join( self.settings[ self.SETTING_UNRAR_PATH ], self.rar_name + '.rar' )
			xbmc.output( "unrar_file= " + unrar_file )

			if self._fetch_current_build( url, unrar_file ):

				# try unrar twice
				if self._extract_rar( unrar_file, unrar_path ):

					if self.isSilent or dialogYesNo( __language__( 0 ), __language__( 507 ), __language__( 508 ), "" ):		# switch to new build ?

						if self._copy_user_data(unrar_path):								# copy userdata

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

							# copy then delete files listed in INCLUDE and EXCLUDE file lists
							self._copy_includes()											# copy custom files
							self._delete_excludes()											# delete custom files

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
						xbmc.output( "deleted: " + f)
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
			if not self.isSilent:
				self._dialog_update( __language__(0), __language__( 506 )) 
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
		try:
			if not os.path.exists( file_name ):
				self._dialog_update( __language__(0), __language__( 503 ), file_name, time=10) 
				urllib.urlretrieve( url , file_name, self._report_hook )
			else:
				xbmc.output( "rar already exists" )
			return True
		except IOError:
			handleException("_fetch_current_build()")
		except:
			dialogOK( __language__( 0 ), __language__( 303 ), isSilent=self.isSilent )
		return False

	######################################################################################
	def _report_hook( self, count, blocksize, totalsize ):
		if not self.isSilent:
			percent = int( float( count * blocksize * 100) / totalsize )
			# just update every x%
			if (percent % 5) == 0:
				dialogProgress.update( percent )
		if ( dialogProgress.iscanceled() ): raise

	######################################################################################
	def _extract_rar( self, file_name, unrar_path ):
		xbmc.output( "_extract_rar() file_name=" + file_name + " unrar_path=" + unrar_path )
		success = False
		try:
			self._dialog_update( __language__(0), __language__( 504 ), unrar_path, time=10)
			time.sleep(1)	# give dialogProgress a chance to appear
			result = xbmc.executebuiltin( "XBMC.extract(%s,%s)" % ( file_name, unrar_path, ), )

			self._dialog_update( __language__(0), __language__( 522 )) 
			time.sleep(5)

			# loop to check if unrar path appears
			userdata_path = os.path.join(unrar_path, 'XBMC','UserData' )

			MAX = 20
			for count in range(MAX):
				if not os.path.exists( unrar_path ) or not os.path.exists( userdata_path ):
					if count < MAX-1:
						if not self.isSilent:
							dialogProgress.update( int(int(100 / MAX) * count) )
						time.sleep(2)
					else:
						dialogOK( __language__( 0 ), __language__( 312 ), unrar_path )
				else:
					success = True
					break
		except:
			handleException( "_extract_rar()", __language__( 304 ) )
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
			# compare keymapping.xml, only copy if user happy
			filename = "keymap.xml"
			curr_build_userdata_path = "T:\\"
			xbmc.output( "curr_build_userdata_path= " + curr_build_userdata_path )

			curr_build_userdata_file = os.path.join( "T:\\", filename)
			xbmc.output( "curr_build_userdata_file= " + curr_build_userdata_file )

			new_build_userdata_path = os.path.join( unrar_path, "XBMC", "UserData")
			xbmc.output( "new_build_userdata_path= " + new_build_userdata_path )

			new_build_userdata_file = os.path.join( new_build_userdata_path, filename)
			xbmc.output( "new_build_userdata_file= " + new_build_userdata_file )

			# if kemap.xml has changed, ask before copying
			if os.path.exists( new_build_userdata_file ):
				if not filecmp.cmp( curr_build_userdata_file, new_build_userdata_file ):
					if self.isSilent or not dialogYesNo( __language__( 0 ), __language__( 509 ) ):
						# NO, keep new
						# copy new Keymap to current, so it will be included in copytree
						copy(new_build_userdata_file, curr_build_userdata_file)
						xbmc.output("keymap copied")
			else:
				xbmc.output( "keymap missing=" + new_build_userdata_file )

			# remove new build UserData
			xbmc.output("rmtree UserData")
			self._dialog_update( __language__(0), __language__( 510 ), time=2)
			rmtree( new_build_userdata_path, ignore_errors=True )
			time.sleep(1)	# give os chance to complete rmdir
			xbmc.output("rmtree UserData done")

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
		self._dialog_update( __language__(0), __language__( 514 )) 

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

		# copy TEAM XBMC dash XBE shortcut to root - only if diff and backup first
		try:
			do_copy = False
			src_xbe_file = os.path.join( DIR_RESOURCES, "SHORTCUT by TEAM XBMC.xbe" )
			if os.path.exists( shortcut_xbe_file ):
				# DOES EXIST, check is diff
				if not filecmp.cmp( src_xbe_file, shortcut_xbe_file ):
					# backup
					copy( shortcut_xbe_file, shortcut_xbe_file + "_old" )
					do_copy = True
			else:
				do_copy = True
			if do_copy:
				copy(src_xbe_file, shortcut_xbe_file)
		except:
			handleException("_update_shortcut()", "error copying 'SHORTCUT by TEAM XBMC' to root")

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
		try:
			for path in self.includes:
				src_path = os.path.join("Q:\\", path)
				dest_path = os.path.join( self.settings[self.SETTING_UNRAR_PATH], self.short_build_name, "XBMC", path )
				if not self.isSilent:
					self._dialog_update( __language__(0), __language__( 515 ), src_path ) 
				localCopy(src_path, dest_path, self.isSilent)
		except:
			handleException("_copy_includes()")


	######################################################################################
	def _delete_excludes(self):
		xbmc.output( "_delete_excludes() ")
		try:
			for path in self.excludes:
				full_path = os.path.join( self.settings[self.SETTING_UNRAR_PATH], self.short_build_name, "XBMC", path )
				if not self.isSilent:
					self._dialog_update( __language__(0), __language__( 516 ), full_path )
				deleteFile(full_path)
		except:
			handleException("_delete_excludes()")


	######################################################################################
	def _maintain_includes(self):
		xbmc.output( "_maintain_includes() ")
		try:

			def _pick_file(path=''):
				if not path:
					path = "Q:\\"
				else:
					path = os.path.join("Q:\\", path)
				try:
					path = self._browse_for_path(__language__(203), path, 1)		# file
					if not path or path[0] != "Q":
						raise

					# subs dest drive with new build path
					bare_dest_path = str(os.path.splitdrive( path )[1])	# get path+filename, no drive
					if bare_dest_path and (bare_dest_path[0] == '\\' or bare_dest_path[0] == '/'):
						bare_dest_path = bare_dest_path[1:]
					# create dest path into new build
					path = bare_dest_path.replace('/','\\')
				except:
					path = ''

				xbmc.output("_pick_file() final path=" + path)
				return path
			
			selectDialog = xbmcgui.Dialog()
			while True:
				# make menu
				self.includes.sort()
				options = [__language__(650), __language__(651)]
				options.extend(self.includes)

				# show menu
				selected = selectDialog.select( __language__( 605 ), options )
				if selected <= 0:						# quit
					break
				elif selected == 1:						# add new
					path = _pick_file()
					if path:
						# add if not a duplicat
						try:
							self.includes.index(path)
						except:
							self.includes.append(path)
				else:									# remove or edit
					path = options[selected]
					# ask what action to take (remove, edit)
					if dialogYesNo( __language__( 0 ), path, yesButton=__language__(406), noButton=__language__(407)):
						del self.includes[selected-2]								# del
					else:
						path = _pick_file(path)										# edit
						if path:
							# add if not a duplicat
							try:
								self.includes.index(path)
							except:
								del self.includes[selected-2]						# del orig entry
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
				if not path:
					path = "Q:\\"
				else:
					path = os.path.join("Q:\\", path)
				try:
					# pick folder first
					print os.path.dirname(path)
					path = self._browse_for_path(__language__(204), os.path.dirname(path), 3)		# dirs
					if not path or path[0] != "Q":
						raise
	
					# append filename using keyboard
					if path[-1] != '\\': path += '\\'
					path = getKeyboard(path, __language__(207))

					# ensure filename entered
					basename = os.path.basename(path)
					if not basename:
						raise

					# subs dest drive with new build path
					bare_dest_path = str(os.path.splitdrive( path )[1])	# get path+filename, no drive
					if bare_dest_path and (bare_dest_path[0] == '\\' or bare_dest_path[0] == '/'):
						bare_dest_path = bare_dest_path[1:]
					path = bare_dest_path.replace('/','\\')
				except:
					path = ''

				xbmc.output("_pick_file() final path=" + path)
				return path
			
			selectDialog = xbmcgui.Dialog()
			while True:
				# make menu
				self.excludes.sort()
				options = [__language__(650), __language__(651)]
				options.extend(self.excludes)

				# show menu
				selected = selectDialog.select( __language__( 608 ), options )
				if selected <= 0:						# quit
					break
				elif selected == 1:						# add new
					path = _pick_file()
					if path:
						# add if not a duplicat
						try:
							self.excludes.index(path)
						except:
							self.excludes.append(path)
				else:									# remove or edit
					path = options[selected]
					# ask what action to take (remove, edit)
					if dialogYesNo( __language__( 0 ), path, yesButton=__language__(406), noButton=__language__(407)):
						del self.excludes[selected-2]								# del
					else:
						path = _pick_file(path)										# edit
						if path:
							# add if not a duplicat
							try:
								self.excludes.index(path)
							except:
								del self.excludes[selected-2]						# del orig entry
								self.excludes.append(path)

			# save options to file
			self._save_file_obj(self.EXCLUDES_FILENAME, self.excludes)
		except:
			handleException("_maintain_excludes()")


	#####################################################################################
	def _dialog_update(self, title="", line1="", line2="", line3="", pct=0, time=4):
		if not self.isSilent:
			dialogProgress.update( pct, line1, line2,line3 )
		else:
			time *= 1000		# make into milliseconds
			msg = ("%s %s %s" % (line1, line2, line3)).strip()
			cmdArg = '"%s","%s",%d' % (title, msg, time)
			xbmc.executebuiltin( "XBMC.Notification(" + cmdArg +")" )

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
	def _update_script( self):
		xbmc.output( "_update_script() ")
		import update
		updt = update.Update()
		del updt

	#####################################################################################
	def _settings_menu(self):
		xbmc.output( "_settings_menu() ")

		def _make_menu(settings):
			options = [ __language__(650),
						"%s -> %s" %(__language__(630),self.settings[self.SETTING_SHORTCUT_DRIVE]),
						"%s -> %s" %(__language__(631),self.settings[self.SETTING_SHORTCUT_NAME]),
						"%s -> %s" %(__language__(632),self.settings[self.SETTING_UNRAR_PATH]),
						"%s -> %s" %(__language__(633),self.settings[self.SETTING_NOTIFY_NOT_NEW]),
						"%s -> %s" %(__language__(634),self.settings[self.SETTING_CHECK_SCRIPT_UPDATE_STARTUP])
						]
			return options

		selectDialog = xbmcgui.Dialog()
		heading = "%s: %s" % (__language__( 0 ), __language__( 601 ) )
		while True:
			options = _make_menu(self.settings)
			selected = selectDialog.select( heading, options )
			if selected <= 0:						# quit
				break

#			matches = re.search('(.*?)->(.*?)$', options[selected], re.IGNORECASE)
#			optionName = matches.group(1).strip()
#			optionValue = matches.group(2).strip()

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
				value = self._browse_for_path( __language__( 200 ) )
				if value and value[0] != "Q":
					self.settings[self.SETTING_UNRAR_PATH] = value

			elif selected == 4:
				if dialogYesNo( __language__( 0 ), __language__( 633 ) ):
					self.settings[self.SETTING_NOTIFY_NOT_NEW] = __language__( 402 )	# YES
				else:
					self.settings[self.SETTING_NOTIFY_NOT_NEW] = __language__( 403 )	# NO

			elif selected == 5:
				if dialogYesNo( __language__( 0 ), __language__( 634 ) ):
					self.settings[self.SETTING_CHECK_SCRIPT_UPDATE_STARTUP] = __language__( 402 )	# YES
				else:
					self.settings[self.SETTING_CHECK_SCRIPT_UPDATE_STARTUP] = __language__( 403 )	# NO

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
		time *= 1000		# make into milliseconds
		msg = ("%s %s %s" % (line1, line2, line3)).strip()
		cmdArg = '"%s","%s",%d' % (title, msg, time)
		xbmc.executebuiltin( "XBMC.Notification(" + cmdArg +")" )
	else:
		xbmcgui.Dialog().ok(title ,line1,line2,line3)


#################################################################################################################
def dialogYesNo(title='', line1='', line2='',line3='', yesButton="", noButton=""):
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
		ypos += 20
		self.titleCL = xbmcgui.ControlLabel(xpos, ypos, width-35, 30, '','font14', "0xFFFFFF99", alignment=0x00000002)
		self.addControl(self.titleCL)
		ypos += 30
		self.descCTB = xbmcgui.ControlTextBox(xpos, ypos, width-40, height-70, 'font10', '0xFFFFFFEE')
		self.addControl(self.descCTB)

	def ask(self, title, text, width=675, height=540, panel=''):
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
		raise
except:
	runMode = RUNMODE_NORMAL
Main(runMode)

# remove globals
try:
	del dialogProgress
except: pass
