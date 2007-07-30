"""
Update module

Nuka1195
"""

import sys, os, xbmcgui, urllib, socket, traceback
from sgmllib import SGMLParser
import XinBox_Util

socket.setdefaulttimeout( 20 )

__scriptname__ = XinBox_Util.__scriptname__
__version__ = XinBox_Util.__version__
__udata__ = XinBox_Util.__settingdir__


class Parser( SGMLParser ):
    """ Parser Class: grabs all tag versions and urls """
    def reset( self ):
        self.tags = []
        self.url = None
        self.tag_found = None
        self.url_found = True
        SGMLParser.reset( self )

    def start_a( self, attrs ):
        for key, value in attrs:
            if ( key == "href" ): self.tag_found = value
    
    def handle_data( self, text ):
        if ( self.tag_found == text.replace( " ", "%20" ) ):
            self.tags.append( self.tag_found )
            self.tag_found = False
        if ( self.url_found ):
            self.url = text.replace( " ", "%20" )
            self.url_found = False
            
    def unknown_starttag( self, tag, attrs ):
        if ( tag == "h2" ):
            self.url_found = True


class Update:
    """ Update Class: used to update scripts from http://code.google.com/p/xbmc-scripting/ """
    def __init__( self ,  lang=False):
        self.returnval = 0
        self.language = lang
        self.base_url = XinBox_Util.__BaseURL__
        self.dialog = xbmcgui.DialogProgress()
        new = self._check_for_new_version()
        if ( new ): self._update_script()
        else: xbmcgui.Dialog().ok( __scriptname__ + " V." + __version__, self.language(390))
            
    def _check_for_new_version( self ):
        """ checks for a newer version """
        self.dialog.create( __scriptname__ + " V." + __version__, self.language(391) )
        # get version tags
        new = None
        htmlsource = self._get_html_source( "%s/tags/%s" % ( self.base_url, __scriptname__.replace( " ", "%20" ), ) )
        if ( htmlsource ):
            self.versions, url = self._parse_html_source( htmlsource )
            self.url = url[ url.find( ":%20" ) + 4 : ]
            if ( self.versions ):
                new = ( __version__ < self.versions[ -1 ][ : -1 ] or ( __version__.startswith( "pre-" ) and __version__.replace( "pre-", "" ) <= self.versions[ -1 ][ : -1 ] ) )
        self.dialog.close()
        return new
                
    def _update_script( self ):
        """ main update function """
        try:
            if ( xbmcgui.Dialog().yesno( __scriptname__ + " V." + __version__, "%s %s %s." % ( self.language(396), self.versions[ -1 ][ : -1 ], self.language(392)),self.language(393))):
                self.dialog.create( __scriptname__ + " V." + __version__, self.language(394), self.language(395))
                script_files = []
                folders = ["%s/%s" % ( self.url, self.versions[-1], )]
                while folders:
                    try:
                        htmlsource = self._get_html_source( "%s%s" % ( self.base_url, folders[0] ) )
                        if ( htmlsource ):
                            items, url = self._parse_html_source( htmlsource )
                            files, dirs = self._parse_items( items )
                            url = url[ url.find( ":%20" ) + 4 : ]
                            for file in files:
                                script_files.append( "%s/%s" % ( url, file, ) )
                            for folder in dirs:
                                folders.append( "%s/%s" % ( folders[ 0 ], folder, ) )
                        else: 
                            raise
                        folders = folders[ 1 : ]
                    except:
                        folders = None
                self._get_files( script_files, self.versions[ -1 ][ : -1 ] )
        except:
            self.dialog.close()
            xbmcgui.Dialog().ok( __scriptname__ + "V." + __version__, self.language(402))
        
    def _get_files( self, script_files, version ):
        """ fetch the files """
        try:
            for cnt, url in enumerate( script_files ):
                items = os.path.split( url )
                path = items[ 0 ].replace( "/tags/%s/" % ( __scriptname__.replace( " ", "%20" ), ), "Q:\\scripts\\%s_v" % ( __scriptname__, ) ).replace( "/", "\\" ).replace( "%20", " " )
                file = items[ 1 ].replace( "%20", " " )
                pct = int( ( float( cnt ) / len( script_files ) ) * 100 )
                self.dialog.update( pct, "%s %s" % ( self.language(397), url, ), "%s %s" % ( self.language(398), path, ), "%s %s" % ( self.language(399), file, ) )
                if ( self.dialog.iscanceled() ): raise
                if ( not os.path.isdir( path ) ): os.makedirs( path )
                urllib.urlretrieve( "%s%s" % ( self.base_url, url, ), "%s\\%s" % ( path, file, ) )
        except:
            raise
        else:
            self.dialog.close()
            if xbmcgui.Dialog().yesno( __scriptname__ + " V." + __version__, self.language(400), "Q:\\scripts\\%s_v%s\\" % ( __scriptname__, version, ),self.language(403)):
                self.createpy(version)

    def createpy(self, version):
        mylines = []
        f = open(sys.path[0] + "\\src\\lib\\XinBox_UpdateTemplate.txt", "r")
        for line in f.readlines():
            if "origpath =" in line:mylines.append("origpath = " + '"' + sys.path[0].replace("\\","\\\\") + '"' + "\n")
            elif "newpath =" in line:mylines.append("newpath = " + '"' + "Q:\\\\scripts\\\\%s_v%s" % ( __scriptname__, version, ) + '"' + "\n")
            else:mylines.append(line)
        f.close
        f = open(__udata__ + "XinBox_Update.py", "w")
        f.writelines(mylines)
        f.close()
        self.returnval = 1
            
    def _get_html_source( self, url ):
        """ fetch the SVN html source """
        try:
            sock = urllib.urlopen( url )
            htmlsource = sock.read()
            sock.close()
            return htmlsource
        except: return None

    def _parse_html_source( self, htmlsource ):
        """ parse html source for tagged version and url """
        try:
            parser = Parser()
            parser.feed( htmlsource )
            parser.close()
            return parser.tags, parser.url
        except: return None, None
            
    def _parse_items( self, items ):
        """ separates files and folders """
        folders = []
        files = []
        for item in items:
            if ( item.endswith( "/" ) ):
                folders.append( item )
            else:
                files.append( item )
        return files, folders
