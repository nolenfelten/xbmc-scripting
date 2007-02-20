'''###XBMC Lyrics script by SveinT###
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
'''

########## IMPORTS ###############
import xbmc, xbmcgui
import os, sys
import threading
import traceback

ExtrasPath = os.path.join( sys.path[0], 'extras' )
sys.path.append( os.path.join( ExtrasPath, 'lib' ) )
import language, lyricsutil#, settings
import guibuilder
_ = language.Language().string


class Overlay( xbmcgui.WindowDialog ):
    def __init__( self ):
        try:
            self.Timer = None
            self.setupGUI()
            if ( not self.SUCCEEDED ): self.exitScript()
            else:
                self.getSettings()
                self.setupVariables()
                sys.path.append( os.path.join( ExtrasPath, 'scrapers', self.settings.SCRAPER ) )
                import lyricsScraper
                self.artist = None
                self.song = None
                self.dummy()
                self.LyricsScraper = lyricsScraper.LyricsFetcher()
                self.MyPlayer = MyPlayer( xbmc.PLAYER_CORE_PAPLAYER, function = self.myPlayerChanged )
                self.myPlayerChanged( 2 )
        except: 
            traceback.print_exc()
            self.exitScript()
            
    def setupGUI( self ):
        cwd = sys.path[ 0 ]
        current_skin = xbmc.getSkinDir()
        if ( not os.path.exists( os.path.join( cwd, 'extras', 'skins', current_skin ))): current_skin = 'default'
        skin_path = os.path.join( cwd, 'extras', 'skins', current_skin )
        image_path = os.path.join( skin_path, 'gfx' )
        if ( self.getResolution() == 0 or self.getResolution() % 2 ): xml_file = 'skin_16x9.xml'
        else: xml_file = 'skin.xml'
        if ( not os.path.isfile( os.path.join( skin_path, xml_file ))): xml_file = 'skin.xml'
        guibuilder.GUIBuilder( self, os.path.join( skin_path, xml_file ), image_path, fastMethod=True )

    def getSettings( self ):
        self.settings = lyricsutil.Settings()

    def setupVariables( self ):
        self.controller_action = lyricsutil.setControllerAction()
        try: self.controls[ 8 ][ 'control' ].setLabel( self.settings.SCRAPER )
        except: pass

    def exitScript(self):
        if ( self.Timer ): self.Timer.cancel()
        self.close()

    def show_control( self, control ):
        self.controls[ 4 ][ 'control' ].setVisible( control == 4 )
        self.controls[ 5 ][ 'control' ].setVisible( control == 5 )
        try:
            self.controls[ 7 ][ 'control' ].setVisible( control == 5 or ( control == 4 and str( self.controls[4]['control'] ).find( 'ControlTextBox' ) == -1 ) )
        except: pass
        self.setFocus( self.controls[ control ][ 'control' ] )
        self.update_label()
        
    def get_lyrics(self, artist, song):
        try:
            self.controls[4]['control'].reset()
            self.controls[5]['control'].reset()
            self.menu_items = []
            self.artist_filename = self.make_fatx_compatible( artist, False )
            self.song_filename = self.make_fatx_compatible( song + '.txt', True )
            lyrics = self.get_lyrics_from_file()
            if ( lyrics ):
                self.show_lyrics( lyrics )
            else:
                test = self.LyricsScraper.get_lyrics( artist, song )#self.main.lyrc_search( artist, song )
                if ( type( test ) == str or type( test ) == unicode ):
                    self.show_lyrics( test )
                elif ( type( test ) == list and test ):
                    self.show_choices( test )
                else:
                    self.show_lyrics( _( 2 ) )
        except: pass
        
    def get_lyrics_from_list( self, item ):
        try:
            lyrics = self.LyricsScraper.get_lyrics_from_list( self.menu_items[ item ] )
            self.show_lyrics( lyrics )
        except: traceback.print_exc()

    def get_lyrics_from_file( self ):
        try:
            song_path = os.path.join( self.settings.LYRICS_PATH, self.artist_filename, self.song_filename )
            lyrics_file = open( song_path, 'r' )
            lyrics = lyrics_file.read()
            lyrics_file.close()
            return lyrics
        except: return None

    def save_lyrics_to_file( self, lyrics ):
        try:
            song_path = os.path.join( self.settings.LYRICS_PATH, self.artist_filename, self.song_filename )
            if ( not os.path.isdir( os.path.join( self.settings.LYRICS_PATH, self.artist_filename ) ) ):
                os.makedirs( os.path.join( self.settings.LYRICS_PATH, self.artist_filename ) )
            lyrics_file = open( song_path, 'w' )
            lyrics_file.write( lyrics )
            lyrics_file.close()
            return True
        except: return False
        
    def make_fatx_compatible( self, name, extension ):
        #name = name.decode( 'utf-8', 'replace' ).encode( 'ascii', 'replace' )
        if len( name ) > 42:
            if ( extension ): name = '%s_%s' % ( name[ : 37 ], name[ -4 : ], )
            else: name = name[ : 42 ]
        name = name.replace( ',', '_' ).replace( '*', '_' ).replace( '=', '_' ).replace( '\\', '_' ).replace( '|', '_' )
        name = name.replace( '<', '_' ).replace( '>', '_' ).replace( '?', '_' ).replace( ';', '_' ).replace( ':', '_' )
        name = name.replace( '"', '_' ).replace( '+', '_' ).replace( '/', '_' )
        return name
        
    def show_lyrics( self, lyrics ):
        xbmcgui.lock()
        self.controls[4]['control'].reset()
        self.controls[5]['control'].reset()
        control_is_TextBox = str( self.controls[4]['control'] ).find( 'ControlTextBox' ) != -1
        #Checking whether some idiot has submitted empty lyrics or not:
        if ( len( lyrics ) < 2 ):
            if ( control_is_TextBox ):
                self.controls[ 4 ][ 'control' ].setText( _( 3 ) )
            else:
                self.controls[ 4 ][ 'control' ].addItem( _( 3 ) )
        #If not, we show whatever results we got:
        else:
            if ( control_is_TextBox ):
                self.controls[ 4 ][ 'control' ].setText( lyrics )
            else:
                for x in lyrics.split( '\n' ):
                    self.controls[ 4 ][ 'control' ].addItem( x )
            if ( self.settings.SAVE_LYRICS ): success = self.save_lyrics_to_file( lyrics )
        self.show_control( 4 )
        xbmcgui.unlock()
        
    def show_choices( self, choices ):
        xbmcgui.lock()
        self.controls[ 4 ][ 'control' ].reset()
        self.controls[ 5 ][ 'control' ].reset()
        for song in choices:
            self.controls[ 5 ][ 'control' ].addItem( song[ 0 ] )
        self.menu_items = choices
        self.show_control( 5 )
        xbmcgui.unlock()
    
    def update_label( self ):
        xbmcgui.lock()
        try:
            current_control = self.getFocus()
            item_height = current_control.getItemHeight() + current_control.getSpace()
            total_height = current_control.getHeight() - item_height
            items_per_page = int( float( total_height ) / float( item_height ) )
            item = current_control.getSelectedPosition()
            total_pages = int( float( current_control.size() ) / items_per_page + 0.99 )
            current_page = int( float( item ) / items_per_page + 1 )
            self.controls[ 7 ][ 'control' ].setLabel( '%d/%d' % ( current_page, total_pages, ) )
        except: pass
        xbmcgui.unlock()

    def changeSettings( self ):
        try:
            import settings
            settings = settings.GUI( language=_ )
            settings.doModal()
            del settings
            self.getSettings()
        except: traceback.print_exc()
            
    def onAction(self, action):
        button_key = self.controller_action.get( action.getButtonCode(), 'n/a' )
        if ( button_key == 'Keyboard ESC Button' or button_key == 'Back Button' or button_key == 'Remote Menu Button' ):
            self.exitScript()
        elif ( button_key == 'Keyboard Menu Button' or button_key == 'Y Button' or button_key == 'Remote Title Button' or button_key == 'White Button' ):
            self.changeSettings()
        else: self.update_label()
    
    def onControl(self, control):
        if control == self.controls[ 5 ][ 'control' ]:
            self.get_lyrics_from_list( self.controls[ 5 ][ 'control' ].getSelectedPosition() )
            
    # dummy() and self.Timer are currently used for the Player() subclass so when an onPlayback* event occurs, 
    # it calls myPlayerChanged() immediately.
    def dummy( self ):
        self.Timer = threading.Timer( 60*60*60, self.dummy,() )
        self.Timer.start()
    
    def myPlayerChanged( self, event ):
        #print [ 'stopped', 'ended', 'started'][ event ]
        if ( event < 2 ): 
            self.exitScript()
        else:
            song = self.song
            for cnt in range( 5 ):
                if ( xbmc.getInfoLabel( 'MusicPlayer.Title' ) != self.song ): break
                xbmc.sleep( 50 )
            self.song = xbmc.getInfoLabel( 'MusicPlayer.Title' )
            self.artist = xbmc.getInfoLabel( 'MusicPlayer.Artist' )
            self.controls[ 6 ][ 'control' ].setImage( xbmc.getInfoImage( 'MusicPlayer.Cover' ) )
            self.get_lyrics( self.artist, self.song )
            
## Thanks Thor918 for this class ##
class MyPlayer( xbmc.Player ):
    def  __init__( self, *args, **kwargs ):
        if ( kwargs.has_key( 'function' ) ): 
            self.function = kwargs[ 'function' ]
            xbmc.Player.__init__( self )

    def onPlayBackStopped( self ):
        self.function( 0 )
    
    def onPlayBackEnded( self ):
        self.function( 1 )
    
    def onPlayBackStarted( self ):
        self.function( 2 )

    
if ( __name__ == '__main__' ):
    if ( xbmc.Player().isPlayingAudio() ):
        xbmc.executebuiltin( 'XBMC.ActivateWindow(2006)' )
        w = Overlay()
        if ( w.SUCCEEDED ): w.doModal()
        del w
    else:
        xbmcgui.Dialog().ok( _( 0 ), _( 10 ), _( 11 ) )
