###XBMC Lyrics script by SveinT##########################################
#
# Be sure to play a mp3 before running this script, or else it won't work.
# Report any bugs to sveint@gmail.com
# 
# Thanks to solexalex and TomKun for bugfixes and additions
#
# Last updated: March 13th 2005
#
# Smuto mod: July 27th 2006
# Thanks to Nuka1195 and Rocko (Rockstar)

SAVE_LYRICS = True

########## IMPORTS ###############
import xbmc, xbmcgui
import os
import urllib
import re
import glob
import string
import threading

########## STANDARDS ###############

ExtrasPath =    sys.path[0] +  '\\extras\\'
sys.path.append(ExtrasPath + '\\lib')
import lang

LangPath = ExtrasPath + 'languages\\'
LyricsPath = 'Q:\\UserData\\lyrics\\'

######### KEY - FUNCTIONS ################

ACTION_MOVE_LEFT				= 1	
ACTION_MOVE_RIGHT			= 2
ACTION_MOVE_UP				= 3
ACTION_MOVE_DOWN			= 4
ACTION_PAGE_UP				= 5
ACTION_PAGE_DOWN			= 6
ACTION_SELECT_ITEM			= 7
ACTION_HIGHLIGHT_ITEM		= 8
ACTION_PARENT_DIR			= 9
ACTION_PREVIOUS_MENU		= 10
ACTION_SHOW_INFO			= 11

ACTION_PAUSE					= 12
ACTION_STOP						= 13
ACTION_NEXT_ITEM				= 14
ACTION_PREV_ITEM				= 15

########## Functions ##############

if ( not os.path.isdir( LyricsPath ) ): #if folder doesn't exist
    try:
        os.makedirs(LyricsPath)
    except Exception:
        pass
        

class Main:
    def lyrc_search(self, artist, song):
        params = urllib.urlencode({'artist': artist, 'songname': song, 'procesado2': '1', 'Submit': ' S E A R C H '})
        f = urllib.urlopen("http://lyrc.com.ar/en/tema1en.php", params)
        Page = f.read()
        if string.find(Page, "Nothing found :") != -1:
            print "Couldn't find artist/song"
        elif string.find(Page, "Suggestions :") != -1:
            links_query = re.compile('<br><a href=\"(.*?)\"><font color=\'white\'>(.*?)</font></a>', re.IGNORECASE)
            urls = re.findall(links_query, Page)
            links = []
            for x in urls:
                link = Links(x[0], x[1])
                links.append(link)
            return links
        else:
            return Page
    
    def lyrc_download(self, link):
        self.url = "http://lyrc.com.ar/en/" + link
        data = urllib.urlopen(self.url)
        Page = data.read()
        return Page
    
    def parse_lyrics(self, lyrics):
        try:
            query = re.compile('</script></td></tr></table>(.*)<p><hr size=1', re.IGNORECASE | re.DOTALL)
            full_lyrics = re.findall(query, lyrics)
            final = full_lyrics[0].replace("<br />\r\n","\n ")
        except:
            try:
                query = re.compile('</script></td></tr></table>(.*)<br><br><a href="#', re.IGNORECASE | re.DOTALL)
                full_lyrics = re.findall(query, lyrics)
                final = full_lyrics[0].replace("<br />\r\n","\n ")
            except:
                final = glob.language.string(1)
        return str(final)
         
class Links:
    def __init__(self, link, linkname):
        self.link = link
        self.linkname = linkname
                       
    def get_link(self):
        return self.link
        
    def get_linkname(self):
        return self.linkname

####GUI START####

class Overlay(xbmcgui.WindowDialog):
    def __init__(self):
        self.song = None
        self.artist = None
        self.setupGUI()
        if (not self.SUCCEEDED): self.exitScript()
        else:
            self.dummy()
            self.load_language()
            self.main = Main()
            self.MyPlayer = MyPlayer( xbmc.PLAYER_CORE_PAPLAYER, function = self.myPlayerChanged )
            self.myPlayerChanged( 2 )
        
    def setupGUI( self ):
        import  guibuilder
        cwd = sys.path[ 0 ]
        current_skin = xbmc.getSkinDir()
        if ( not os.path.exists( os.path.join( cwd, 'extras', 'skins', current_skin ))): current_skin = 'default'
        skin_path = os.path.join( cwd, 'extras', 'skins', current_skin )
        image_path = os.path.join( skin_path, 'gfx' )
        if ( self.getResolution() == 0 or self.getResolution() % 2 ): xml_file = 'skin_16x9.xml'
        else: xml_file = 'skin.xml'
        if ( not os.path.isfile( os.path.join( skin_path, xml_file ))): xml_file = 'skin.xml'
        guibuilder.GUIBuilder( self, os.path.join( skin_path, xml_file ), image_path, fastMethod=True )

    def exitScript(self):
        if ( self.Timer ): self.Timer.cancel()
        self.close()

    def load_language(self):
        glob.language = lang.Language()
        glob.language.load(LangPath)

    # dummy() and self.Timer are currently used for the Player() subclass so when an onPlayback* event occurs, 
    # it calls myPlayerChanged() immediately.
    def dummy( self ):
        #self.debugWrite('dummy', 2)
        self.Timer = threading.Timer( 60*60*60, self.dummy,() )
        self.Timer.start()
    
    def myPlayerChanged( self, event ):
        if ( event < 2 ): 
            self.exitScript()
        else:
            try:
                xbmc.sleep( 50 )
                print '----------------------'
                print self.artist, self.song
                artist = xbmc.getInfoLabel( 'MusicPlayer.Artist' )
                song = xbmc.getInfoLabel( 'MusicPlayer.Title' )
                print artist, song
                print '----------------------'
                self.artist = artist
                self.song = song
                
                self.controls[ 6 ][ 'control' ].setImage( xbmc.getInfoImage( 'MusicPlayer.Cover' ) )
                self.lyrics( artist, song )
            except: pass
            
    def show_text(self):
        self.controls[5]['control'].setVisible(False)
        self.controls[4]['control'].setVisible(True)
        self.setFocus(self.controls[4]['control'])
    
    def show_list(self):
        self.controls[4]['control'].setVisible(False)
        self.controls[5]['control'].setVisible(True)
        self.setFocus(self.controls[5]['control'])
        
    def getLyrics( self ):
        try:
            song_path = os.path.join( LyricsPath, self.artist_filename, self.song_filename )
            lyrics_file = open( song_path, 'r' )
            lyrics = lyrics_file.read()
            lyrics_file.close()
            return lyrics
        except: return None

    def saveLyrics( self, lyrics ):
        try:
            song_path = os.path.join( LyricsPath, self.artist_filename, self.song_filename )
            if ( not os.path.isdir( os.path.join( LyricsPath, self.artist_filename ) ) ):
                os.makedirs( os.path.join( LyricsPath, self.artist_filename ) )
            #print song_path
            lyrics_file = open( song_path, 'w' )
            lyrics_file.write( lyrics )
            lyrics_file.close()
            return True
        except: return False
        
    def lyrics(self, artist, song):
        try:
            self.artist_filename = self.makeFatXCompatible( artist, False )
            self.song_filename = self.makeFatXCompatible( song + '.txt', True )
            lyrics = self.getLyrics()
            if ( lyrics ):
                self.controls[4]['control'].setText( lyrics )
                self.show_text()
            else:
                test = self.main.lyrc_search( artist, song )
                self.controls[4]['control'].reset()
                self.controls[5]['control'].reset()
                if type(test) == str:
                    self.show_lyrics( test )
                elif type(test) == list:
                    for x in test:
                       try:
                           self.controls[5]['control'].addItem(x.get_linkname())
                       except:
                           self.controls[5]['control'].addItem(glob.language.string(2))
                    self.menu_items = test
                    self.show_list()
                elif test == None:
                    self.controls[4]['control'].setText(glob.language.string(3))
                    self.show_text()
        except: pass
            
    def makeFatXCompatible( self, name, extension ):
        if len( name ) > 42:
            if ( extension ): name = '%s_%s' % ( name[ : 37 ], name[ -4 : ], )
            else: name = name[ : 42 ]
        name = name.replace( ',', '_' ).replace( '*', '_' ).replace( '=', '_' ).replace( '\\', '_' ).replace( '|', '_' )
        name = name.replace( '<', '_' ).replace( '>', '_' ).replace( '?', '_' ).replace( ';', '_' ).replace( ':', '_' )
        name = name.replace( '"', '_' ).replace( '+', '_' ).replace( '/', '_' )
        return name
        
    def show_lyrics( self, lyrics ):
        final_lyrics = self.main.parse_lyrics( lyrics )
        #Checking whether some idiot has submitted empty lyrics or not:
        if ( len( final_lyrics ) < 2 ):
            self.controls[4]['control'].setText(glob.language.string(4))
        #If not, we show whatever results we got:
        else:
            self.controls[4]['control'].setText(' ' + final_lyrics)
            if ( SAVE_LYRICS ): success = self.saveLyrics( final_lyrics )
        self.show_text()
       
    def onAction(self, action):
        if action == ACTION_PREVIOUS_MENU:
            self.exitScript()
    
    def onControl(self, control):
        if control == self.controls[5]['control']:
            templyrc = self.main.lyrc_download(self.menu_items[self.controls[5]['control'].getSelectedPosition()].get_link())
            self.show_lyrics(templyrc)
            
## Thanks Thor918 for this class ##
class MyPlayer( xbmc.Player ):
    def  __init__( self, *args, **kwargs ):
        if ( kwargs.has_key( 'function' ) ): 
            self.function = kwargs[ 'function' ]
            xbmc.Player.__init__( self )
        if ( self.isPlayingAudio() ):
            xbmc.executebuiltin( 'XBMC.ActivateWindow(2006)' )

    def onPlayBackStopped( self ):
        self.function( 0 )
    
    def onPlayBackEnded( self ):
        self.function( 1 )
    
    def onPlayBackStarted( self ):
        self.function( 2 )
    
            
w = Overlay()
if ( w.SUCCEEDED ): w.doModal()
del w