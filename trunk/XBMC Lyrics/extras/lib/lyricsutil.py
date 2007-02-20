import os, sys

def setControllerAction():
    return {
                61478 : 'Keyboard Up Arrow',
                61480 : 'Keyboard Down Arrow',
                61448 : 'Keyboard Backspace Button',
                61533 : 'Keyboard Menu Button',
                61467 : 'Keyboard ESC Button',
                    216 : 'Remote Back Button',
                    247 : 'Remote Menu Button',
                    229 : 'Remote Title Button',
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
            f = open( os.path.join( sys.path[ 0 ], 'extras', 'data', 'settings.txt' ), 'r' )
            s = f.read().split('|')
            f.close()
            self.SAVE_LYRICS = ( s[ 0 ] == '1' )
            self.LYRICS_PATH = s[ 1 ]
            self.SCRAPER = s[ 2 ]
        except:
            print 'ERROR: getting settings'
            self.setDefaults()

    def setDefaults( self, show_dialog = False ):
        self.SAVE_LYRICS = True
        self.LYRICS_PATH = 'Q:\\UserData\\lyrics\\'
        self.SCRAPER = 'lyricwiki'#'lyrc.com.ar'
        success = self.saveSettings()
        
    def saveSettings( self ):
        try:
            if ( not os.path.isdir( os.path.join( sys.path[ 0 ], 'extras', 'data' ) ) ):
                os.makedirs( os.path.join( sys.path[ 0 ], 'extras', 'data' ) )
            strSettings = '%d|%s|%s' % ( 
                self.SAVE_LYRICS,
                self.LYRICS_PATH,
                self.SCRAPER, )
            f = open( os.path.join( sys.path[ 0 ], 'extras', 'data', 'settings.txt' ), 'w' )
            f.write( strSettings )
            f.close()
            return True
        except:
            return False
