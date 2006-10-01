"""
    xbmc.py - emulator for Xbox Media Center
"""
import platform, sys, os

sys.path += [ os.path.join( sys.prefix, 'Lib', 'site-packages', 'xbmc-emulator' ) ]
import emulator

__author__ = emulator.__author__
__credits__ = emulator.__credits__
__platform__ = emulator.__platform__
__date__ = ' '.join( '$Date: 2006-09-13 17:56:46 -0600 (Wed, 13 Sep 2006) $'.split()[1:4] )
__version__ = '%s R%s' % ( emulator.__version__, '$Rev: 21 $'.split()[1] )

# define playlist types
PLAYLIST_MUSIC      = 0
PLAYLIST_MUSIC_TEMP = 1
PLAYLIST_VIDEO      = 2
PLAYLIST_VIDEO_TEMP = 3

DRIVE_NOT_READY           = 1
TRAY_OPEN                 = 16
TRAY_CLOSED_NO_MEDIA      = 64
TRAY_CLOSED_MEDIA_PRESENT = 96

# xbmc classes

class InfoTagMusic:
    """
        http://home.no.net/thor918/xbmc/xbmc.html#InfoTagMusic
    """
    def getAlbum( self ):
        return 'Album'
    def getArtist( self ):
        return 'Artist'
    def getDuration( self ):
        return 0
    def getGenre( self ):
        return 'Genre'
    def getReleaseDate( self ):
        return '01 Jan 1901'
    def getTitle( self ):
        return 'Title'
    def getTrack( self ):
        return 0
    def getURL( self ):
        return 'http://foo.bar'

class InfoTagVideo:
    """
        http://home.no.net/thor918/xbmc/xbmc.html#InfoTagVideo
    """
    def getCast( self ):
        return 'Cast'
    def getDVDLabel( self ):
        return 'DVD Label'
    def getDirector( self ):
        return 'Director'
    def getFile( self ):
        return 'File'
    def getGenre( self ):
        return 'Genre'
    def getIMDBNumber( self ):
        return 'IMDB Number'
    def getPictureURL( self ):
        return 'http://foo.bar.img'
    def getPlot( self ):
        return 'Plot'
    def getPlotOutline( self ):
        return 'Plot Outline'
    def getRating( self ):
        return float( 0 )
    def getTagLine( self ):
        return 'Tagline'
    def getTitle( self ):
        return 'Title'
    def getVotes( self ):
        return 'Votes'
    def getWritingCredits( self ):
        return 'Writing Credits'
    def getYear( self ):
        return 2005

class Keyboard:
    """
        http://home.no.net/thor918/xbmc/xbmc.html#Keyboard
    """
    # should this be __init__(self, text=None): ?
    def __init__(self, text = '', heading = ''):
        import time
        time.sleep(1)
        self.confirmed = False
        self.root = Toplevel()
        box = Frame(self.root)
        box.pack(expand = YES, fill = BOTH)
        self.ent = Entry(box)
        self.ent.insert(0, text)
        self.ent.pack(side = TOP, fill = X)
        self.ent.focus()
        self.ent.bind("<Return>", self.__ok)
        Button(box, text = "Accept (Y-button)", command = self.__ok).pack(side = LEFT)
        Button(box, text = "Cancel (B-button)", command = self.__cancel).pack(side = RIGHT)
        self.root.focus_set()
        self.root.grab_set()
        self.root.wait_window()

    def __ok(self, event = None):
        """
            INTERNAL
        """
        self.confirmed = True
        self.text = self.ent.get()
        self.root.destroy()

    def __cancel(self):
        """
            INTERNAL
        """
        self.confirmed = False
        self.text = ""
        self.root.destroy()

    def doModal(self):
        pass

    def getText(self):
        return self.text

    def isConfirmed(self):
        return self.confirmed

    def setDefault(self, text):
        self.ent.insert(0, text)

    def setHeading(self, text):
        pass
        
class PlayList:
    """
        http://home.no.net/thor918/xbmc/xbmc.html#PlayList
    """
    def __init__(self,playlist):
        # playlist is "x" in doc strings
        self.x = []

    def __getitem__(self,y):
        return self.x[y]

    def __len__(self):
        return len(x)

    def add(self, filename, description="",duration=0):
        self.x.append(PlayListItem())
        i = len(self.x) -1
        self.x[i].__filename    = filename
        self.x[i].__description = description
        self.x[i].__duration    = duration

    def clear(self):
        for i in range(0,len(self.x)):
            del self.x[len(self.x)-1]

    def load(self,filename):
        pass

    def remove(self,filename):
        f = filename.upper()
        for i in range(0,len(self.x)-1):
            if self.x[i].__filename.upper() == f:
                del self.x[i]
                return

    def shuffle(self):
        pass

    def size( self ):
        return len( self )

class PlayListItem:
    """
        http://home.no.net/thor918/xbmc/xbmc.html#PlayListItem
    """
    def __init__(self):
        self.__filename     = ""
        self.__description  = ""
        self.__duration     = 0

    def getdescription(self):
        return self.__description

    def getduration(self):
        return  self.__duration

    def getfilename(self):
        return self.__filename

class Player:
    """
        http://home.no.net/thor918/xbmc/xbmc.html#Player
    """
    def __init__(self):
        # create default playlist
        pass

    def getMusicInfoTag( self ):
        return 'Music Info Tag'

    def getPlayingFile( self ):
        return 'File'

    def getTime( self ):
        return 0

    def getTotalTime( self ):
        return 0

    def getVideoInfoTag( self ):
        return 'Video Info Tag'

    def isPlaying( self ):
        return False

    def isPlayingAudio( self ):
        return False

    def isPlayingVideo( self ):
        return False

    def onPlayBackEnded( self ):
        pass

    def onPlayBackStarted( self ):
        pass

    def onPlayBackStopped( self ):
        pass

    def pause(self):
        pass

    def play(self,item=None):
        pass


    def playnext(self):
        pass

    def playprevious(self):
        pass

    def playselected( self ):
        pass

    def seekTime( self ):
        pass

    def stop(self):
        pass

# functions...

def dashboard():
    """
        http://home.no.net/thor918/xbmc/xbmc.html#-dashboard
    """
    raise KeyboardInterrupt

def executebuiltin( command ):
    """
        http://home.no.net/thor918/xbmc/xbmc.html#-executebuiltin
    """
    pass

def executehttpapi( command ):
    """
        http://home.no.net/thor918/xbmc/xbmc.html#-executehttpapi
    """
    pass

def executescript(script):
    """
        http://home.no.net/thor918/xbmc/xbmc.html#-executescript
    """
    execfile(script)

def getCpuTemp():
    """
        FIXME: possibly removed?
    """
    return 20
    
def getCondVisibility(condition):
    """
        http://home.no.net/thor918/xbmc/xbmc.html#-getCondVisibility
    """
    pass

def getDVDState():
    """
        http://home.no.net/thor918/xbmc/xbmc.html#-getDVDState
    """
    return DRIVE_NOT_READY

def getFreeMem():
    """
        http://home.no.net/thor918/xbmc/xbmc.html#-getFreeMem
    """
    return 99
    
def getGlobalIdleTime():
    """
        FIXME: possibly removed
    """
    pass

def getIPAddress():
    """
        http://home.no.net/thor918/xbmc/xbmc.html#-getIPAddress
    """
    return "127.0.0.1"

def getInfoImage(infotag):
    """
        http://home.no.net/thor918/xbmc/xbmc.html#-getInfoImage
    """
    return infotag
    
def getInfoLabel(infotag):
    """
        http://home.no.net/thor918/xbmc/xbmc.html#-getInfoLabel
    """
    return infotag
    
def getLanguage():
    """
        http://home.no.net/thor918/xbmc/xbmc.html#-getLanguage
    """
    return "English"

def getLocalizedString(id):
    """
        http://home.no.net/thor918/xbmc/xbmc.html#-getLocalizedString
    """
    return str(id)

def getSkinDir():
    """
        http://home.no.net/thor918/xbmc/xbmc.html#-getSkinDir
    """
    return "Project Mayhem III"

def log( text ):
    """
        http://home.no.net/thor918/xbmc/xbmc.html#-log
    """
    pass

def output(s):
    """
        http://home.no.net/thor918/xbmc/xbmc.html#-output
    """
    print s
    
def playSFX(filename):
    """
        http://home.no.net/thor918/xbmc/xbmc.html#-playSFX
    """
    pass

def restart():
    """
        http://home.no.net/thor918/xbmc/xbmc.html#-restart
    """
    import sys
    sys.exit()

def shutdown():
    """
        http://home.no.net/thor918/xbmc/xbmc.html#-shutdown
    """
    import sys
    sys.exit()

def sleep( msec ):
    """
        http://home.no.net/thor918/xbmc/xbmc.html#-sleep
    """
    if ( msec > 0):
        try:
            from time import sleep
            sleep(float(msec) / 1000)
        except: pass
            