import sys,os
import xbmc, xbmcgui
import urllib
from sgmllib import SGMLParser
import socket
import traceback

sys.path.append( os.path.join( os.getcwd().replace( ';', '' ), 'resources', 'lib' ) )
import language
_ = language.Language().string

socket.setdefaulttimeout( 10 )

__scriptname__ = 'T3CH Downloader'

class Parser( SGMLParser ):
    def reset( self ):
        self.url = None
        SGMLParser.reset( self )

    def start_a( self, attrs ):
        for key, value in attrs:
            if ( key == 'href' and value.find( '/STABLE/' ) == -1 and value.find( 'ARCHIVE/' ) == -1 
                and value.find( '/t3ch/XBMC-SVN' ) != -1 and value.find( '.rar' ) != -1 ):
                self.url = value
    
class Main:
    def __init__( self ):
        self.base_url = 'http://t3ch.xil.us/'
        self._get_settings()
        self._download_build()
        
    def _get_settings( self ):
        try:
            settings_file = open( os.path.join( 'T:\\script_data', __scriptname__, 'settings.txt' ), 'r' )
            settings = settings_file.read().split( '|' )
            settings_file.close()
            self.download_path = settings[ 0 ]
            self.unrar_path = settings[ 1 ]
            self.xbmc_folder = settings[ 2 ]
        except:
            self._set_default_settings()
           
    def _set_default_settings( self ):
        self.download_path = self._browse_for_path( _( 200 ) )
        self.unrar_path = self._browse_for_path( _( 201 ) )
        self.xbmc_folder = 'XBMC'#self._browse_for_path( _( 202 ) )
        self._save_settings()

    def _save_settings( self ):
        try:
            settings = '%s|%s|%s' % (
            self.download_path,
            self.unrar_path,
            self.xbmc_folder,
            )
            if ( not os.path.isdir( os.path.join( 'T:\\script_data', __scriptname__ ) ) ):
                os.makedirs( os.path.join( 'T:\\script_data', __scriptname__ ) )
            settings_file = open( os.path.join( 'T:\\script_data', __scriptname__, 'settings.txt' ), 'w' )
            settings_file.write( settings )
            settings_file.close()
        except:
            traceback.print_exc()
            ok = xbmcgui.Dialog().ok( _( 0 ), _( 300 ) )

    def _browse_for_path( self, heading ):
        dialog = xbmcgui.Dialog()
        path = dialog.browse( 3, heading, 'files')
        return path

    def _download_build( self ):
        try:
            url = self._get_latest_version()
            if ( url ):
                file_path = os.path.join( self.download_path, os.path.split( url )[ 1 ], )
                ok = xbmcgui.Dialog().yesno( _( 0 ), _( 500 ), os.path.split( url )[ 1 ], _( 501 ), _( 401 ), _( 400 ) )
                if ( ok ):
                    self._fetch_current_build( url, file_path )
            else: 
                ok = xbmcgui.Dialog().ok( _( 0 ), _( 301 ) )
        except:
            ok = xbmcgui.Dialog().ok( _( 0 ), _( 302 ) )
            
    def _get_latest_version( self ):
        try:
            dialog = xbmcgui.DialogProgress()
            dialog.create( _( 0 ), _( 502 ) )
            url = False
            htmlsource = self._get_html_source( self.base_url )
            if ( htmlsource ):
                url = self._parse_html_source( htmlsource )
        except:
            traceback.print_exc()
        dialog.close()
        return url
                
    def _fetch_current_build( self, url, file_path ):
        try:
            self.dialog = xbmcgui.DialogProgress()
            self.dialog.create( _( 0 ), _( 503 ), file_path )
            urllib.urlretrieve( url , file_path, self._report_hook )
            self.dialog.close()
            self._extract_rar( file_path )
        except:
            traceback.print_exc()
            self.dialog.close()
            ok = xbmcgui.Dialog().ok( _( 0 ), _( 303 ) )

    def _report_hook( self, count, blocksize, totalsize ):
        percent = int( float( count * blocksize * 100) / totalsize )
        self.dialog.update( percent )
        if ( self.dialog.iscanceled() ): raise
        
    def _extract_rar( self, file_path ):
        try:
            dialog = xbmcgui.DialogProgress()
            dialog.create( _( 0 ), _( 504 ), '%s' % ( os.path.join( self.unrar_path, os.path.splitext( os.path.split( file_path )[ 1 ] )[ 0 ] ), ) )
            xbmc.executebuiltin( 'XBMC.extract(%s,%s\\%s)' % ( file_path, self.unrar_path, os.path.splitext( os.path.split( file_path )[ 1 ] )[ 0 ], ) )
            dialog.close()
            ok = xbmcgui.Dialog().ok( _( 0 ), _( 505 ), '%s' % ( os.path.join( self.unrar_path, os.path.splitext( os.path.split( file_path )[ 1 ] )[ 0 ] ), ) )
        except: 
            dialog.close()
            traceback.print_exc()
            ok = xbmcgui.Dialog().ok( _( 0 ), _( 303 ) )
    
    def _get_html_source( self, url ):
        try:
            sock = urllib.urlopen( url )
            htmlsource = sock.read()
            sock.close()
            return htmlsource
        except: return None

    def _parse_html_source( self, htmlsource ):
        try:
            parser = Parser()
            parser.feed( htmlsource )
            parser.close()
            return parser.url
        except: return None
            
if ( __name__ == '__main__' ):
    Main()
    