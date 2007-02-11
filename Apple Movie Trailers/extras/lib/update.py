import urllib, os, sys, xbmcgui
sys.path.append( os.path.join( os.path.dirname( sys.modules['update'].__file__ ), '_xmlplus.zip' ) )
from sgmllib import SGMLParser
import socket

# timeout in seconds
timeout = 10
socket.setdefaulttimeout( timeout )

class Parser( SGMLParser ):
    def reset( self ):
        self.tags = []
        self.tag_found = None
        self.url_found = True
        SGMLParser.reset( self )

    def start_a( self, attrs ):
        for key, value in attrs:
            if ( key == 'href' ): self.tag_found = value
    
    def handle_data( self, text ):
        if ( self.tag_found == text.replace( ' ', '%20' ) ):
            self.tags.append( self.tag_found )
            self.tag_found = False
        if ( self.url_found ):
            self.url = text.replace( ' ', '%20' )
            self.url_found = False
            
    def unknown_starttag( self, tag, attrs ):
        if ( tag == 'h2' ):
            self.url_found = True

class Update:
    def __init__( self, language, script = 'Apple Movie Trailers', version = '0' ):
        self._ = language
        self.script = script
        self.version = version
        self.base_url = 'http://xbmc-scripting.googlecode.com/svn'
        self.dialog = xbmcgui.DialogProgress()
        new = self.checkForNewVersion()
        if ( new ): self.updateScript()
        else: xbmcgui.Dialog().ok( self.script, self._( 95 + ( new == None ) ) )
            
    def checkForNewVersion( self ):
        self.dialog.create( self.script, self._( 90 ) )
        # get version tags
        htmlsource = self.getHTMLSource( '%s/tags/%s' % ( self.base_url, self.script.replace( ' ', '%20' ), ) )
        if ( htmlsource ):
            self.versions, url = self.parseHTMLSource( htmlsource )
            self.url = url[url.find( ':%20' ) + 4:]
            new = ( self.version < self.versions[-1][:-1] or ( self.version[:4] == 'pre-' and self.version.replace( 'pre-', '' ) <= self.versions[-1][:-1] ) )
        else: new = None
        self.dialog.close()
        return new
                
    def updateScript( self ):
        try:
            if ( xbmcgui.Dialog().yesno( self.script, '%s %s %s.' % ( self._( 100 ), self.versions[-1][:-1], self._( 91 ), ), self._( 92 ), '', self._( 211 ), self._( 208 ) ) ):
                self.dialog.create( self.script, self._( 93 ), self._( 94 ) )
                script_files = []
                folders = ['%s/%s' % ( self.url, self.versions[-1], )]
                while folders:
                    try:
                        htmlsource = self.getHTMLSource( '%s%s' % ( self.base_url, folders[0] ) )
                        if ( htmlsource ):
                            items, url = self.parseHTMLSource( htmlsource )
                            files, dirs = self.parseItems( items )
                            url = url[url.find( ':%20' ) + 4:]
                            for file in files:
                                script_files.append( '%s/%s' % ( url, file, ) )
                            for folder in dirs:
                                folders.append( '%s/%s' % ( folders[0], folder, ) )
                        else: 
                            raise
                        folders = folders[1:]
                    except:
                        folders = None
                self.getFiles( script_files, self.versions[-1][:-1] )
        except:
            self.dialog.close()
            xbmcgui.Dialog().ok( self.script, self._( 96 ) )
        
    def getFiles( self, script_files, version ):
        try:
            for cnt, url in enumerate( script_files ):
                items = os.path.split( url )
                path = items[0].replace( '/tags/%s/' % ( self.script.replace( ' ', '%20' ), ), 'Q:\\scripts\\%s_v' % ( self.script, ) ).replace( '/', '\\' ).replace( '%20', ' ' )
                file = items[1].replace( '%20', ' ' )
                pct = int( ( float( cnt ) / len( script_files ) ) * 100 )
                self.dialog.update( pct, '%s %s' % ( self._( 68 ), url, ), '%s %s' % ( self._( 97 ), path, ), '%s %s' % ( self._( 98 ), file, ) )
                if ( self.dialog.iscanceled() ): raise
                if ( not os.path.isdir( path ) ): os.makedirs( path )
                urllib.urlretrieve( '%s%s' % ( self.base_url, url, ), '%s\\%s' % ( path, file, ) )
        except:
            raise
        else:
            self.dialog.close()
            xbmcgui.Dialog().ok( self.script, self._( 99 ), 'Q:\\scripts\\%s_v%s\\' % ( self.script, version, ) )
            
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
