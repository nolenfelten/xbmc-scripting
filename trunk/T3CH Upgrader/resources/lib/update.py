"""
Update module

Nuka1195

07-11-2007 Modified by BBB 
 Use language _(0) in dialogs instead of __scriptname__
 Used regex to parse svn.
 Added a 'silent' mode.
 Changed to use YES/NO string ids.
"""

import sys
import os
import xbmcgui, xbmc
import urllib
import socket
import re

socket.setdefaulttimeout( 10 )

_ = sys.modules[ "__main__" ].__language__
__scriptname__ = sys.modules[ "__main__" ].__scriptname__
__version__ = sys.modules[ "__main__" ].__version__


class Update:
	""" Update Class: used to update scripts from http://code.google.com/p/xbmc-scripting/ """
	def __init__( self, isSilent=False ):
		xbmc.output( "Update().__init__() isSilent="+str(isSilent) )
		self.isSilent = isSilent
		self.base_url = "http://xbmc-scripting.googlecode.com/svn"
		self.tagsPath = "%s/tags/%s/" % ( self.base_url, __scriptname__)

		self.dialog = xbmcgui.DialogProgress()
		new = self._check_for_new_version() 
		if ( new ):
			self._update_script()
		elif not self.isSilent:
			xbmcgui.Dialog().ok( _(0), _( 1000 + ( 30 * ( new is None ) ) ) )
			
	def _check_for_new_version( self ):
		""" checks for a newer version """
		xbmc.output( "Update()._check_for_new_version()" )
		if not self.isSilent:
			self.dialog.create( _(0), _( 1001 ) )
		# get version tags
		new = None
		htmlsource = self._get_html_source( self.tagsPath )
		if ( htmlsource ):
			tagList, url = self._parse_html_source( htmlsource )
			if ( tagList ):
				self.version = tagList[-1].replace("/","")  # remove trailing /
				new = ( __version__ < self.version or ( __version__.startswith( "pre-" ) and __version__.replace( "pre-", "" ) <= self.version ) )
		if not self.isSilent:
			self.dialog.close()
		xbmc.output( "Update()._check_for_new_version() new="+str(new) )

				
	def _update_script( self ):
		""" main update function """
		xbmc.output( "Update()._update_script()" )
		try:
			if ( xbmcgui.Dialog().yesno( _(0), "%s %s %s." % ( _( 1006 ), self.version, _( 1002 ), ), _( 1003 ), "", _( 403 ), _( 402 ) ) ):
				self.dialog.create( _(0), _( 1004 ), _( 1005 ) )
				script_files = []
				folders = [self.version]
				# recusivly look for folders and files
				while folders:
					htmlsource = self._get_html_source( os.path.join(self.tagsPath, folders[0]) )
					if ( htmlsource ):
						# extract folder/files sored in path
						itemList, url = self._parse_html_source( htmlsource )

						# append folders to those we're looping throu and store file
						for item in itemList:
							if item[-1] == "/":
								folders.append( os.path.join(folders[ 0 ], item) )
							else:
								script_files.append( os.path.join(folders[ 0 ], file) )

						folders = folders[ 1 : ]
					else:
						raise

				if not script_files:
					raise
				self._get_files( script_files )
				self.dialog.close()
				xbmcgui.Dialog().ok( _(0), _( 1010 ), "Q:\\scripts\\%s_v%s\\" % ( __scriptname__, self.version, ), _(1011) )
		except:
			self.dialog.close()
			xbmcgui.Dialog().ok( _(0), _( 1031 ) )
		
	def _get_files( self, script_files ):
		""" fetch the files """
		xbmc.output( "Update()._get_files()" )
		try:
			totalFiles = len(script_files)
			for cnt, url in enumerate( script_files ):
				url = url.replace( "//", "\\" ).replace( "/", "\\" )
				items = os.path.split( url.replace( "%20", " " ) )
				path = "Q:\\scripts\\%s_v%s" % ( __scriptname__, items[0])
				file = items[ 1 ]

				pct = int( ( float( cnt ) / totalFiles ) * 100 )
				self.dialog.update( pct, "%s %s" % ( _( 1007 ), url, ), "%s %s" % ( _( 1008 ), path, ), "%s %s" % ( _( 1009 ), file, ) )
				if ( self.dialog.iscanceled() ): raise
				if ( not os.path.isdir( path ) ): os.makedirs( path )
				src = "%s\\%s" % (self.base_url, url)
				dest = "%s\\%s" % (path, file)
				urllib.urlretrieve( src,  dest)
		except:
			raise

	def _get_html_source( self, url ):
		""" read a doc from a url """
		safe_url = url.replace( " ", "%20" )
		xbmc.output( "Update()._get_html_source() " + safe_url)
		try:
			sock = urllib.urlopen( safe_url )
			doc = sock.read()
			sock.close()
			return doc
		except:
			print sys.exc_info()[ 1 ]
			return None

	def _parse_html_source( self, htmlsource ):
		""" parse html source for tagged version and url """
		xbmc.output( "Update()._parse_html_source()" )
		try:
			url = re.search('Revision \d+:(.*?)<', htmlsource, re.IGNORECASE).group(1).strip()
			tagList = re.compile('<li><a href="(.*?)"', re.MULTILINE+re.IGNORECASE+re.DOTALL).findall(htmlsource)
			if tagList[0] == "../":
				del tagList[0]
			return tagList, url
		except:
			return None, None

