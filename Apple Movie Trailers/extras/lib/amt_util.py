import xbmcgui, xbmc
import os, sys, default

COMPATIBLE_VERSIONS = [ 'pre-0.95', '0.95', 'pre-0.95.1', '0.95.1', 'pre-0.96', '0.96' , 'pre-0.97', '0.97' ]
GENRES				= -1
STUDIOS			= -2
ACTORS				= -3
FAVORITES			= -6
DOWNLOADED		= -7

def setThumbnailDisplay( _ ):
    return [_(310), _(311), _(312)]

def setQuality( _ ):
    return [_(320), _(321), _(322)]

def setMode( _ ):
    return [_(330), _(331), '%s (videos)' % _(332), '%s (files)' % _(332)]

def setControllerAction():
    return {
                61478 : 'Keyboard Up Arrow',
                61480 : 'Keyboard Down Arrow',
                61448 : 'Keyboard Backspace Button',
                61533 : 'Keyboard Menu Button',
                61467 : 'Keyboard ESC Button',
                    216 : 'Remote Back Button',
                    247 : 'Remote Menu Button',
                    229 : 'Remote Title',
                    207 : 'Remote 0',
                    166 : 'Remote Up',
                    167 : 'Remote Down',
                    256 : 'A Button',
                    257 : 'B Button',
                    258 : 'X Button',
                    259 : 'Y Button',
                    260 : 'Black Button',
                    261 : 'White Button',
                    274 : 'Start Button',
                    275 : 'Back Button',
                    270 : 'DPad Up',
                    271 : 'DPad Down',
                    272 : 'DPad Left',
                    273 : 'DPad Right'
                }

class Settings:
    def __init__( self, *args, **kwargs ):
        self.getSettings()

    def getSettings( self ):
        try:
            self.usedDefaults = False
            f = open( os.path.join( os.path.dirname( sys.modules['default'].__file__ ), 'extras', 'data', 'settings.txt' ), 'r' )
            s = f.read().split('|')
            f.close()
            version = s[0]
            self.trailer_quality = int( s[1] )
            self.mode = int( s[2] )
            self.skin = s[3]
            self.save_folder = s[4]
            self.startup_category_id = int( s[5] )
            self.thumbnail_display = int( s[6] )
            self.shortcut1 = int( s[7] )
            self.shortcut2 = int( s[8] )
            self.shortcut3 = int( s[9] )
            if ( version not in COMPATIBLE_VERSIONS ):
                self.setDefaults( True )
        except:
            print 'ERROR: getting settings'
            self.setDefaults()

    def setDefaults( self, show_dialog = False ):
        self.trailer_quality = 2
        self.mode = 0
        self.skin = 'Default'
        self.save_folder = 'f:\\'
        self.thumbnail_display = 1
        self.shortcut1 = 10
        self.shortcut2 = 4
        self.shortcut3 = -6
        self.startup_category_id = self.shortcut1
        success = self.saveSettings()
        self.usedDefaults = True
        #if ( success and show_dialog ):
        #    xbmcgui.Dialog().ok( 'Apple Movie Trailers', 'Settings incompatible, using default values.' )
        
    def saveSettings( self ):
        try:
            strSettings = '%s|%d|%d|%s|%s|%d|%d|%d|%d|%d' % ( 
                default.__version__,
                self.trailer_quality,
                self.mode, 
                self.skin,
                self.save_folder,
                self.startup_category_id,
                self.thumbnail_display,
                self.shortcut1,
                self.shortcut2,
                self.shortcut3, )
            f = open( os.path.join( os.path.dirname( sys.modules['default'].__file__ ), 'extras', 'data', 'settings.txt' ), 'w' )
            f.write(strSettings)
            f.close()
            return True
        except:
            return False
