import urllib, os, sys, xbmc, xbmcgui, shutil, language, traceback
sys.path.append( os.path.join( os.path.dirname( __file__ ), '_xmlplus.zip' ) )
from sgmllib import SGMLParser

class Parser( SGMLParser ):
	def reset( self ):
		self.tags = []
		self.tag_found = None
		self.url_found = True
		SGMLParser.reset( self )

	def start_a( self, attrs ):
		for key, value in attrs:
			if key == 'href': self.tag_found = value
	
	def handle_data( self, text ):
		if ( self.tag_found == text ):
			self.tags.append( text )
			self.tag_found = False
		if ( self.url_found ):
			self.url = text
			self.url_found = False
			
	def unknown_starttag(self, tag, attrs):
		if (tag == 'h2'):
			self.url_found = True

class Update:
	def __init__( self, language, script = 'Tetris'):
		self._ = language
		self.dialog = xbmcgui.DialogProgress()
		#self.dialog.create( script, self._( 90 ) )
		self.local_dir = 'Q:\\scripts\\' + script
		self.script = script.replace( ' ', '%20' )
		self.base_url = 'http://xbmc-scripting.googlecode.com/svn'
		
	def downloadVersion(self,version):
		try:
			print 'here'
			self.dialog.create( self.script, self._( 93 ), self._( 94 ) ) #fetching
			print 'here2'
			folders = ['tags/%s/%s/' % ( self.script, version )]
			print 'here3', folders
			script_files = []
			while folders:
				print 'here4', folders
				try:
					htmlsource = self.getHTMLSource( '%s/%s' % ( self.base_url, folders[0] ) )
					print 'here4.5'
					if ( htmlsource ):
						items, url = self.parseHTMLSource( htmlsource )
						print 'here4.6', items, url
						files, dirs = self.parseItems( items )
						url = url[url.find( ': ' ) + 2:].replace( ' ', '%20' )
						print 'here4.7', items, url, files, dirs
						for file in files:
							script_files.append( '%s/%s' % ( url, file, ) )
						for folder in dirs:
							folders.append( '%s/%s' % ( folders[0], folder, ) )
					else: 
						raise
					folders = folders[1:]
				except:
					folders = None
			print 'here5', folders, script_files						
			self.getFiles( script_files, version )
			print 'here7', folders
		except:
			self.dialog.close()
			traceback.print_exc()
			xbmcgui.Dialog().ok( self.script, self._( 96 ) ) #error
	
	def getLatestVersion( self, quiet=True ):
		try:
			# get version tags
			if not quiet:
				self.dialog.create( self.script, self._( 90 ), self._( 94 )) #fetching tags
			htmlsource = self.getHTMLSource( '%s/tags/%s' % ( self.base_url, self.script, ) )
			if ( htmlsource ):
				self.versions, url = self.parseHTMLSource( htmlsource )
			else: raise
			self.dialog.close()
			return self.versions[-1][:-1]
		except:
			traceback.print_exc()
			return "-1"
				
	def makeBackup( self ):
		self.removeBackup()
		shutil.copytree(self.local_dir+'\\',self.local_dir+'_backup\\')
	
	def issueUpdate( self, version ):
		path = self.local_dir+'_backup\\resources\\lib\\update.py'
		command = 'XBMC.RunScript(%s,%s,%s)'%(path,self.script.replace('%20',' '), version)
		print "issueing command: ",command
		xbmc.executebuiltin(command)
		
	def removeBackup( self ):
		if self.backupExists():
			shutil.rmtree(self.local_dir+'_backup\\',ignore_errors=True)		
	
	def removeOriginal( self ):
		shutil.rmtree(self.local_dir+'\\',ignore_errors=True)		
		
	def backupExists( self ):
		return os.path.exists(self.local_dir+'_backup\\')
		
	
	def getFiles( self, script_files, version ):
		try:
			for cnt, url in enumerate( script_files ):
				items = os.path.split( url )
				print "getting -- ",items[0],items[1]
				path = items[0].replace( '/tags/%s/%s' % ( self.script, version), 'Q:\\scripts\\%s' % ( self.script) ).replace( '%20', ' ' ).replace( '/', '\\' )
				file = items[1].replace( '%20', ' ' )
				pct = int( ( float( cnt ) / len( script_files ) ) * 100 )
				self.dialog.update( pct, '%s %s' % ( self._( 101 ), url, ), '%s %s' % ( self._( 97 ), path, ), '%s %s' % ( self._( 98 ), file, ) )
				if ( self.dialog.iscanceled() ): raise
				if ( not os.path.isdir( path ) ): os.makedirs( path )
				urllib.urlretrieve( '%s%s' % ( self.base_url, url, ), '%s\\%s' % ( path, file, ) )
		except:
			raise
		else:
			self.dialog.close()
			
	def getHTMLSource( self, url ):
		try:
			sock = urllib.urlopen( url )
			htmlsource = sock.read()
			sock.close()
			return htmlsource
		except: return None

	def parseHTMLSource( self, htmlsource ):
		try:
			parser = Parser()
			parser.feed( htmlsource )
			parser.close()
			return parser.tags, parser.url
		except:
			return None
			
	def parseItems( self, items ):
		folders = []
		files = []
		for item in items:
			if ( item[-1] == '/' ):
				folders.append( item )
			else:
				files.append( item )
		return files, folders

if __name__ == "__main__":
	print 'we got here!',sys.argv
	if len(sys.argv) != 3:
		xbmcgui.Dialog().ok("Update error",  "Not enough arguments were passed for update")
		sys.exit(1)
	up = Update(language.Language().string,sys.argv[1])
	up.removeOriginal()
	up.downloadVersion(sys.argv[2])
	xbmc.executebuiltin('XBMC.RunScript(%s)'%(up.local_dir+'\\default.py'))