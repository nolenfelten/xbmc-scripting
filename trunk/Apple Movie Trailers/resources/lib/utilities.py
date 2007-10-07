"""
Catchall module for shared functions and constants

Nuka1195
"""

import sys
import os
import xbmc
import xbmcgui

DEBUG_MODE = 0

_ = sys.modules[ "__main__" ].__language__
__scriptname__ = sys.modules[ "__main__" ].__scriptname__
__version__ = sys.modules[ "__main__" ].__version__
__svn_revision__ = sys.modules[ "__main__" ].__svn_revision__

# comapatble versions
DATABASE_VERSIONS = ( "pre-0.99", "0.99", "pre-0.99.1", "0.99.1", )
SETTINGS_VERSIONS =  ( "pre-0.99.1", "0.99.1", )
# special categories
GENRES = -1
STUDIOS = -2
ACTORS = -3
FAVORITES = -6
DOWNLOADED = -7
HD_TRAILERS = -8
NO_TRAILER_URLS = -9
WATCHED = -10
CUSTOM_SEARCH = -99
# base paths
BASE_DATA_PATH = xbmc.translatePath( os.path.join( "T:\\script_data", __scriptname__ ) )
BASE_SETTINGS_PATH = xbmc.translatePath( os.path.join( "P:\\script_data", __scriptname__ ) )
BASE_DATABASE_PATH = BASE_SETTINGS_PATH
BASE_RESOURCE_PATH = sys.modules[ "__main__" ].BASE_RESOURCE_PATH
# special action codes
SELECT_ITEM = ( 11, 256, 61453, )
EXIT_SCRIPT = ( 247, 275, 61467, )
CANCEL_DIALOG = EXIT_SCRIPT + ( 216, 257, 61448, )
TOGGLE_DISPLAY = ( 216, 257, 61448, )
CONTEXT_MENU = ( 229, 261, 61533, )
MOVEMENT_UP = ( 166, 270, 61478, )
MOVEMENT_DOWN = ( 167, 271, 61480, )
MOVEMENT = ( 166, 167, 168, 169, 270, 271, 272, 273, 61477, 61478, 61479, 61480, )
# Log status codes
LOG_ERROR, LOG_INFO, LOG_NOTICE, LOG_DEBUG = range( 1, 5 )

def _create_base_paths():
    """ creates the base folders """
    new = False
    if ( not os.path.isdir( BASE_DATA_PATH ) ):
        os.makedirs( BASE_DATA_PATH )
        new = True
    if ( not os.path.isdir( BASE_SETTINGS_PATH ) ):
        os.makedirs( BASE_SETTINGS_PATH )
    return new
INSTALL_PLUGIN = _create_base_paths()

def install_plugin():
    plugin_path1 = xbmc.translatePath( os.path.join( "Q:\\", "plugins", "video", __scriptname__ + " Plugin" ) )
    if ( xbmcgui.Dialog().yesno( _( 700 ), _( 701 ), _( 702 ), _( 703 ) ) ):
        try:
            from shutil import copytree, rmtree
            if ( os.path.isdir( plugin_path1 ) ):
                rmtree( plugin_path1 )
            plugin_path2 = xbmc.translatePath( os.path.join( "Q:\\", "plugins", "video", __scriptname__ + " Plugin", "pysqlite2" ) )
            copy_path1 = xbmc.translatePath( os.path.join( BASE_RESOURCE_PATH, __scriptname__ + " Plugin" ) )
            copy_path2 = xbmc.translatePath( os.path.join( BASE_RESOURCE_PATH, "lib", "pysqlite2" ) )
            copytree( copy_path1, plugin_path1 )
            copytree( copy_path2, plugin_path2 )
            ok = xbmcgui.Dialog().ok( _( 700 ), _( 704 ), _( 705 ) )
        except:
            ok = xbmcgui.Dialog().ok( _( 700 ), _( 730 ) )

def get_keyboard( default="", heading="", hidden=False ):
    """ shows a keyboard and returns a value """
    keyboard = xbmc.Keyboard( default, heading, hidden )
    keyboard.doModal()
    if ( keyboard.isConfirmed() ):
        return keyboard.getText()
    return default

def get_numeric_dialog( default="", heading="", dlg_type=3 ):
    """ shows a numeric dialog and returns a value
        - 0 : ShowAndGetNumber		(default format: #)
        - 1 : ShowAndGetDate			(default format: DD/MM/YYYY)
        - 2 : ShowAndGetTime			(default format: HH:MM)
        - 3 : ShowAndGetIPAddress	(default format: #.#.#.#)
    """
    dialog = xbmcgui.Dialog()
    value = dialog.numeric( dlg_type, heading, default )
    return value

def get_browse_dialog( default="", heading="", dlg_type=1, shares="files", mask="", use_thumbs=False, treat_as_folder=False ):
    """ shows a browse dialog and returns a value
        - 0 : ShowAndGetDirectory
        - 1 : ShowAndGetFile
        - 2 : ShowAndGetImage
        - 3 : ShowAndGetWriteableDirectory
    """
    dialog = xbmcgui.Dialog()
    value = dialog.browse( dlg_type, heading, shares, mask, use_thumbs, treat_as_folder, default )
    return value

def LOG( status, format, *args ):
    if ( DEBUG_MODE >= status ):
        xbmc.output( "%s: %s\n" % ( ( "ERROR", "INFO", "NOTICE", "DEBUG", )[ status - 1 ], format % args, ) )

def get_custom_sql():
    try:
        query = ""
        file_object = open( os.path.join( BASE_DATA_PATH, "custom.sql" ), "r" )
        query = file_object.read()
        file_object.close()
    except: pass
    return query

def save_custom_sql( query ):
    try:
        file_object = open( os.path.join( BASE_DATA_PATH, "custom.sql" ), "w" )
        file_object.write( query )
        file_object.close()
        return True
    except:
        return False

def make_legal_filepath( path, compatible=False, extension=True ):
    environment = os.environ.get( "OS", "xbox" )
    path = path.replace( "\\", "/" )
    drive = os.path.splitdrive( path )[ 0 ]
    parts = os.path.splitdrive( path )[ 1 ].split( "/" )
    if ( not drive and parts[ 0 ].endswith( ":" ) and len( parts[ 0 ] ) == 2 and compatible ):
        drive = parts[ 0 ]
        parts[ 0 ] = ""
    if ( environment == "xbox" or environment == "win32" or compatible ):
        illegal_characters = """,*=|<>?;:"+"""
        for count, part in enumerate( parts ):
            tmp_name = ""
            for char in part:
                # if char's ord() value is > 127 or an illegal character remove it
                if ( char in illegal_characters or ord( char ) > 127 ): char = ""
                tmp_name += char
            if ( environment == "xbox" or compatible ):
                if ( len( tmp_name ) > 42 ):
                    if ( count == len( parts ) - 1 and extension == True ):
                        ext = os.path.splitext( tmp_name )[ 1 ]
                        tmp_name = "%s%s" % ( os.path.splitext( tmp_name )[ 0 ][ : 42 - len( ext ) ].strip(), ext, )
                    else:
                        tmp_name = tmp_name[ : 42 ].strip()
            parts[ count ] = tmp_name
    filepath = drive + "/".join( parts )
    if ( environment == "win32" ):
        return filepath.encode( "utf-8" )
    else:
        return filepath


class Settings:
    """ Settings class """
    def get_settings( self ):
        """ read settings from a settings.txt file in BASE_SETTINGS_PATH """
        try:
            settings_file = open( os.path.join( BASE_SETTINGS_PATH, "settings.txt" ), "r" )
            settings = eval( settings_file.read() )
            settings_file.close()
            if ( settings[ "version" ] not in SETTINGS_VERSIONS ):
                raise
        except:
            settings = self._use_defaults()
        return settings

    def _use_defaults( self, show_dialog=False ):
        """ setup default values if none obtained """
        LOG( LOG_NOTICE, "%s (ver: %s) used default settings", __scriptname__, __version__ )
        settings = {  
            "version": __version__,
            "skin": "Default",
            "trailer_quality": 2,
            "mode": 0,
            "save_folder": "f:\\",
            "thumbnail_display": 0,
            "fade_thumb": True,
            "startup_category_id": 10,
            "shortcut1": 10,
            "shortcut2": 4,
            "shortcut3": FAVORITES,
            "refresh_newest": False,
            "videoplayer_displayresolution": 10,
            "use_simple_search": False,
            "match_whole_words": False,
            "showtimes_local": "33102",
            "showtimes_scraper": "Google",
            }
        ok = self.save_settings( settings )
        return settings

    def save_settings( self, settings ):
        """ save settings to a settings.txt file in BASE_SETTINGS_PATH """
        try:
            settings_file = open( os.path.join( BASE_SETTINGS_PATH, "settings.txt" ), "w" )
            settings_file.write( repr( settings ) )
            settings_file.close()
            return True
        except:
            LOG( LOG_ERROR, "%s (rev: %s) Settings::save_settings [%s]", __scriptname__, __svn_revision__, sys.exc_info()[ 1 ], )
            return False
