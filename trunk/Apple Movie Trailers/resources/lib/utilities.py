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

# comapatble versions
DATABASE_VERSIONS = ( "pre-0.98", "0.98", )
SETTINGS_VERSIONS = DATABASE_VERSIONS
# special categories
GENRES = -1
STUDIOS = -2
ACTORS = -3
FAVORITES = -6
DOWNLOADED = -7
# base paths
BASE_DATA_PATH = os.path.join( "T:\\script_data", __scriptname__ )
BASE_SETTINGS_PATH = os.path.join( "P:\\script_data", __scriptname__ )
BASE_RESOURCE_PATH = sys.modules[ "__main__" ].BASE_RESOURCE_PATH
# special action codes
SELECT_ITEM = ( 11, 256, 61453, )
EXIT_SCRIPT = ( 247, 275, 61467, )
CANCEL_DIALOG = EXIT_SCRIPT + ( 216, 257, 61448, )
TOGGLE_DISPLAY = ( 216, 257, 61448, )
CONTEXT_MENU = ( 229, 261, 61533, )
MOVEMENT_UP = ( 166, 270, 61478, )
MOVEMENT_DOWN = ( 167, 271, 61480, )
MOVEMENT = ( 166, 167, 168, 169, 270, 271, 272, 273, 61477, 61478, 61479, 61480 )
# Log status codes
LOG_INFO, LOG_ERROR, LOG_NOTICE, LOG_DEBUG = range( 1, 5 )

def _create_base_paths():
    """ creates the base folders """
    if ( not os.path.isdir( BASE_DATA_PATH ) ):
        os.makedirs( BASE_DATA_PATH )
    if ( not os.path.isdir( BASE_SETTINGS_PATH ) ):
        os.makedirs( BASE_SETTINGS_PATH )
_create_base_paths()

def get_keyboard( default="", heading="", hidden=False ):
    """ shows a keyboard and returns a value """
    keyboard = xbmc.Keyboard( default, heading, hidden )
    keyboard.doModal()
    if ( keyboard.isConfirmed() ):
        return keyboard.getText()
    return default

def get_numeric( default="", heading="", type=3 ):
    """ shows a numeric dialog and returns a value
        - 0 : ShowAndGetNumber		(default format: #)
        - 1 : ShowAndGetDate			(default format: DD/MM/YYYY)
        - 2 : ShowAndGetTime			(default format: HH:MM)
        - 3 : ShowAndGetIPAddress	(default format: #.#.#.#)
    """
    dialog = xbmcgui.Dialog()
    value = dialog.numeric( type, heading, default )
    return value

def get_browse_dialog( default="", heading="", type=1, shares="files", mask="", use_thumbs=False, treat_as_folder=False ):
    """ shows a browse dialog and returns a value
        - 0 : ShowAndGetDirectory
        - 1 : ShowAndGetFile
        - 2 : ShowAndGetImage
        - 3 : ShowAndGetWriteableDirectory
    """
    dialog = xbmcgui.Dialog()
    value = dialog.browse( type, heading, shares, mask, use_thumbs, treat_as_folder, default )
    return value

def LOG( status, format, *args ):
    if ( DEBUG_MODE >= status ):
        xbmc.output( "%s: %s\n" % ( ( "INFO", "ERROR", "NOTICE", "DEBUG", )[ status - 1 ], format % args, ) )

def buttoncode_dict():
    """ depreciated: button codes dictionary """
    return {
                61478 : "Keyboard Up Arrow",
                61480 : "Keyboard Down Arrow",
                61448 : "Keyboard Backspace Button",
                61533 : "Keyboard Menu Button",
                61467 : "Keyboard ESC Button",
                    216 : "Remote Back Button",
                    247 : "Remote Menu Button",
                    229 : "Remote Title Button",
                    207 : "Remote 0",
                    166 : "Remote Up",
                    167 : "Remote Down",
                    256 : "A Button",
                    257 : "B Button",
                    258 : "X Button",
                    259 : "Y Button",
                    260 : "Black Button",
                    261 : "White Button",
                    274 : "Start Button",
                    275 : "Back Button",
                    270 : "DPad Up",
                    271 : "DPad Down",
                    272 : "DPad Left",
                    273 : "DPad Right"
                }

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
            "thumbnail_display": 1,
            "startup_category_id": 10,
            "shortcut1": 10,
            "shortcut2": 4,
            "shortcut3": FAVORITES,
            "refresh_newest": False,
            "videoplayer_displayresolution": 10
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
            LOG( LOG_ERROR, "%s (ver: %s) Settings::save_settings [%s]", __scriptname__, __version__, sys.exc_info()[ 1 ], )
            return False
