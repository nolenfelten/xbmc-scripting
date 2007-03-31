import sys
import os
import default

DATABASE_VERSIONS = [ "pre-0.97.2", "0.97.2" ]
SETTINGS_VERSIONS = DATABASE_VERSIONS
GENRES = -1
STUDIOS = -2
ACTORS = -3
FAVORITES = -6
DOWNLOADED = -7
BASE_DATA_PATH = os.path.join( "T:\\script_data", default.__scriptname__ )
EXIT_SCRIPT = ( 247, 275, 61467, )
TOGGLE_DISPLAY = ( 216, 257, 61448, )
CONTEXT_MENU = ( 229, 261, 61533, )
MOVEMENT_UP = ( 166, 270, 61478, )
MOVEMENT_DOWN = ( 167, 271, 61480, )

def setControllerAction():
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
    def __init__( self, *args, **kwargs ):
        pass

    def get_settings( self ):
        try:
            settings_path = os.path.join( "P:\\script_data", sys.modules[ "__main__" ].__scriptname__ )
            settings_file = open( os.path.join( settings_path, "settings.txt" ), "r" )
            settings = eval( settings_file.read() )
            settings_file.close()
            if ( settings[ "version" ] not in SETTINGS_VERSIONS ):
                raise
        except:
            settings = self._use_defaults()
        return settings

    def _use_defaults( self, show_dialog=False ):
        settings = {  
            "version": sys.modules[ "__main__" ].__version__,
            "skin": "Default",
            "trailer_quality": 2,
            "mode": 0,
            "save_folder": "f:\\",
            "thumbnail_display": 1,
            "startup_category_id": 10,
            "shortcut1": 10,
            "shortcut2": 4,
            "shortcut3": FAVORITES,
            "refresh_newest": False
            }
        ok = self.save_settings( settings )
        return settings

    def save_settings( self, settings ):
        try:
            settings_path = os.path.join( "P:\\script_data", sys.modules[ "__main__" ].__scriptname__ )
            if ( not os.path.isdir( settings_path ) ):
                os.makedirs( settings_path )
            settings_file = open( os.path.join( settings_path, "settings.txt" ), "w" )
            settings_file.write( repr( settings ) )
            settings_file.close()
            return True
        except:
            return False
            
