"""
Catchall module for shared functions and constants

Nuka1195
"""

import sys
import os

_ = sys.modules[ "__main__" ].__language__
__scriptname__ = sys.modules[ "__main__" ].__scriptname__
__version__ = sys.modules[ "__main__" ].__version__

# comapatble versions
SETTINGS_VERSIONS = ( "1.4.2", )
# base paths
BASE_DATA_PATH = os.path.join( "T:\\script_data", __scriptname__ )
BASE_SETTINGS_PATH = os.path.join( "P:\\script_data", __scriptname__ )
BASE_RESOURCE_PATH = sys.modules[ "__main__" ].BASE_RESOURCE_PATH
# special action codes
EXIT_SCRIPT = ( 247, 275, 61467, )
CANCEL_DIALOG = EXIT_SCRIPT + ( 216, 257, 61448, )
GET_EXCEPTION = ( 216, 260, 61448, )
SETTINGS_MENU = ( 229, 259, 261, 61533, )
MOVEMENT_UP = ( 166, 270, 61478, )
MOVEMENT_DOWN = ( 167, 271, 61480, )


def _create_base_paths():
    """ creates the base folders """
    if ( not os.path.isdir( BASE_DATA_PATH ) ):
        os.makedirs( BASE_DATA_PATH )
    if ( not os.path.isdir( BASE_SETTINGS_PATH ) ):
        os.makedirs( BASE_SETTINGS_PATH )
_create_base_paths()

def buttoncode_dict():
    """ depreciated: not used """
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
        settings = {
            "version": __version__,
            "scraper": "lyricwiki",
            "save_lyrics": True,
            "lyrics_path": os.path.join( BASE_DATA_PATH, "lyrics" ),
            "smooth_scrolling": False,
            "show_viz": True
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
            return False
