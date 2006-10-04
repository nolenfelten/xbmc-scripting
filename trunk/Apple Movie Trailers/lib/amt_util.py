import os

def getSettings():
    try:
        settings = {}
        f = open( os.path.join( os.getcwd(), 'data', 'settings.txt' ).replace( ';', '' ), 'r' )
        s = f.read().split('|')
        f.close()
        settings['trailer quality'] = int( s[0] )
        settings['mode'] = int( s[1] )
        settings['skin'] = s[2]
        settings['save folder'] = s[3]
        settings['startup category'] = int( s[4] )
        settings['startup category id'] = int( s[5] )
        settings['thumbnail display'] = int( s[6] )
    except:
        settings = {'trailer quality' : 2, 'mode' : 0, 'skin' : 'Default', 'save folder' : 'f:\\', 'startup category' : 0, 'startup category id' : 1, 'thumbnail display' : 1}
    return settings

def saveSettings( settings ):
    try:
        f = open( os.path.join( os.getcwd(), 'data', 'settings.txt' ).replace( ';', '' ), 'w' )
        strSettings = '%d|%d|%s|%s|%d|%d|%d' % ( settings['trailer quality'], settings['mode'], settings['skin'], settings['save folder'], settings['startup category'], settings['startup category id'], settings['thumbnail display'],)
        f.write(strSettings)
        f.close()
        return True
    except:
        return False

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
