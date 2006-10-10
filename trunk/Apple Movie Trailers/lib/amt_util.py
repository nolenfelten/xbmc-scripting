from PIL import Image, ImageEnhance
import os

def makeThumbnails( poster ):
    try:
        size = ( 26, 38 )
        thumbnail = '%s.png' % ( os.path.splitext( poster )[0], )
        watched_thumbnail = '%s-w.png' % ( os.path.splitext( poster )[0], )
        im = Image.open( poster )
        im.thumbnail(size, Image.ANTIALIAS)
        im = im.convert('RGBA')
        im.save(thumbnail, 'PNG')
        alpha = im.split()[3]
        alpha = ImageEnhance.Brightness(alpha).enhance(0.2)
        im.putalpha(alpha)
        im.save(watched_thumbnail, 'PNG')
        return thumbnail, watched_thumbnail
    except:
        return None, None

def setThumbnailDisplay( _ ):
    return [_(310), _(311), _(312)]

def setStartupCategory( _ ):
    return [_(200), _(201), _(202)]

def setStartupCategoryActual():
    return ['Newest', 'Exclusives', 'Genre']

def setQuality( _ ):
    return [_(320), _(321), _(322)]

def setMode( _ ):
    return [_(330), _(331), _(332)]

def setControllerAction():
    return {
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
    def __init__( self ):
        self.getSettings()
        
    def getSettings( self ):
        try:
            settings = {}
            f = open( os.path.join( os.getcwd(), 'data', 'settings.txt' ).replace( ';', '' ), 'r' )
            s = f.read().split('|')
            f.close()
            self.trailer_quality = int( s[0] )
            self.mode = int( s[1] )
            self.skin = s[2]
            self.save_folder = s[3]
            self.startup_category = int( s[4] )
            self.startup_category_id = int( s[5] )
            self.thumbnail_display = int( s[6] )
        except:
            self.setDefaults()

    def setDefaults( self ):
        self.trailer_quality = 2
        self.mode = 0
        self.skin = 'Default'
        self.save_folder = 'f:\\'
        self.startup_category = 0
        self.startup_category_id = 1
        self.thumbnail_display = 1

    def saveSettings( self ):
        try:
            strSettings = '%d|%d|%s|%s|%d|%d|%d' % ( 
                self.trailer_quality,
                self.mode, self.skin,
                self.save_folder,
                self.startup_category,
                self.startup_category_id,
                self.thumbnail_display, )
            f = open( os.path.join( os.getcwd(), 'data', 'settings.txt' ).replace( ';', '' ), 'w' )
            f.write(strSettings)
            f.close()
            return True
        except:
            return False
