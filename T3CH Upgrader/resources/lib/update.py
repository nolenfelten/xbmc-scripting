"""
Update module

Nuka1195

07-11-2007 Modified by BBB
 Changed to use language _(0) in dialogs instead of __scriptname__
 Added func call logging
 Added in some exception reporting
"""

import sys
import os
import xbmcgui, xbmc
import urllib
import socket
from sgmllib import SGMLParser

socket.setdefaulttimeout( 10 )

_ = sys.modules[ "__main__" ].__language__
__scriptname__ = sys.modules[ "__main__" ].__scriptname__
__version__ = sys.modules[ "__main__" ].__version__
__svn_revision__ = sys.modules[ "__main__" ].__svn_revision__


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
    def __init__( self ):
        xbmc.output( "Update().__init__()" )
        self.base_url = "http://xbmc-scripting.googlecode.com/svn"
        self.dialog = xbmcgui.DialogProgress()
        new = self._check_for_new_version()
        if ( new ): self._update_script()
        else: xbmcgui.Dialog().ok( _(0), _( 1000 + ( 30 * ( new is None ) ) ) )
            
    def _check_for_new_version( self ):
        """ checks for a newer version """
        xbmc.output( "Update()._check_for_new_version()" )
        self.dialog.create( _(0), _( 1001 ) )
        # get version tags
        new = None
        htmlsource = self._get_html_source( "%s/tags/%s" % ( self.base_url, __scriptname__.replace( " ", "%20" ), ) )
        if ( htmlsource ):
            self.versions, url = self._parse_html_source( htmlsource )
            print "self.versions=", self.versions, url
            self.url = url[url.find( ":%20" ) + 4:]
            print "self.url=", self.url
            if ( self.versions ):
                new = ( __version__ < self.versions[ -1 ][ : -1 ] or ( __version__.startswith( "pre-" ) and __version__.replace( "pre-", "" ) <= self.versions[ -1 ][ : -1 ] ) )
                print ("new="+str(new))
        self.dialog.close()
        return new
                
    def _update_script( self ):
        """ main update function """
        xbmc.output( "Update()._update_script()" )
        try:
            if ( xbmcgui.Dialog().yesno( _(0), "%s %s %s." % ( _( 1006 ), self.versions[ -1 ][ : -1 ], _( 1002 ), ), _( 1003 ), "", _( 251 ), _( 252 ) ) ):
                self.dialog.create( _(0), _( 1004 ), _( 1005 ) )
                script_files = []
                folders = ["%s/%s" % ( self.url, self.versions[-1], )]
                print "folders=", folders
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

                print "script_files=", script_files
                self._get_files( script_files, self.versions[ -1 ][ : -1 ] )
        except:
            self.dialog.close()
            xbmcgui.Dialog().ok( _(0), _( 1031 ) )
        
    def _get_files( self, script_files, version ):
        """ fetch the files """
        xbmc.output( "Update()._get_files()" )
        try:
            for cnt, url in enumerate( script_files ):
                print cnt, url
                items = os.path.split( url )
                path = items[ 0 ].replace( "/tags/%s/" % ( __scriptname__.replace( " ", "%20" ), ), "Q:\\scripts\\%s_v" % ( __scriptname__, ) ).replace( "/", "\\" ).replace( "%20", " " )
                file = items[ 1 ].replace( "%20", " " )
                print path, file
                pct = int( ( float( cnt ) / len( script_files ) ) * 100 )
                self.dialog.update( pct, "%s %s" % ( _( 1007 ), url, ), "%s %s" % ( _( 1008 ), path, ), "%s %s" % ( _( 1009 ), file, ) )
                if ( self.dialog.iscanceled() ): raise
                if ( not os.path.isdir( path ) ): os.makedirs( path )
                urllib.urlretrieve( "%s%s" % ( self.base_url, url, ), "%s\\%s" % ( path, file, ) )
        except:
            raise
        else:
            self.dialog.close()
            xbmcgui.Dialog().ok( _(0), _( 1010 ), "Q:\\scripts\\%s_v%s\\" % ( __scriptname__, version, ) )
            
    def _get_html_source( self, url ):
        """ fetch the SVN html source """
        xbmc.output( "Update()._get_html_source()" )
        try:
            sock = urllib.urlopen( url )
            htmlsource = sock.read()
            sock.close()
            print "htmlsource=",htmlsource
            return htmlsource
        except:
            print sys.exc_info()[ 1 ]
            return None

    def _parse_html_source( self, htmlsource ):
        """ parse html source for tagged version and url """
        xbmc.output( "Update()._parse_html_source()" )
        try:
            parser = Parser()
            parser.feed( htmlsource )
            parser.close()
            print parser.tags, parser.url
            return parser.tags, parser.url
        except:
            print sys.exc_info()[ 1 ]
            return None, None
            
    def _parse_items( self, items ):
        """ separates files and folders """
        xbmc.output( "Update()._parse_items()" )
        folders = []
        files = []
        for item in items:
            if ( item.endswith( "/" ) ):
                folders.append( item )
            else:
                files.append( item )
        print files, folders
        return files, folders

