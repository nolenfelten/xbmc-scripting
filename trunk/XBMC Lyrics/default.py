'''
	Credits:	
		EnderW:					Original Author
		Stanley87:				PM3 Integration and AD Removal
		solexalex:
		TomKun:
		Smuto:					Skinning Mod
		Rockstar & Donno:	Language Routine
		Spiff:						Unicode support
		Nuka1195:				lyricwiki Scraper and Modulization
				
Please report any bugs: http://www.xboxmediacenter.com/forum/showthread.php?t=10187
'''
__scriptname__ = 'XBMC Lyrics'
__author__ = 'XBMC Lyrics Team'
__url__ = 'http://code.google.com/p/xbmc-scripting/'
__credits__ = 'XBMC TEAM, freenode/#xbmc-scripting'
__version__ = '1.2.1'


import os, sys
import xbmc, xbmcgui
import threading

resourcesPath = os.path.join( os.getcwd().replace( ";", "" ), 'resources' )
sys.path.append( os.path.join( resourcesPath, 'lib' ) )
import language, lyricsutil
import guibuilder
_ = language.Language().string


class GUI( xbmcgui.WindowDialog ):
    def __init__( self ):
        try:
            self.Timer = None
            self.setupGUI()
            if ( not self.SUCCEEDED ): self.exitScript()
            else:
                self.getSettings()
                self.setupVariables()
                self.getScraper()
                self.getDummyTimer()
                self.getMyPlayer()
        except: 
            self.exitScript()
            
    def setupGUI( self ):
        cwd = os.getcwd().replace( ";", "" )
        current_skin = xbmc.getSkinDir()
        if ( not os.path.exists( os.path.join( cwd, 'resources', 'skins', current_skin ))): current_skin = 'default'
        skin_path = os.path.join( cwd, 'resources', 'skins', current_skin )
        image_path = os.path.join( skin_path, 'gfx' )
        if ( self.getResolution() == 0 or self.getResolution() % 2 ): xml_file = 'skin_16x9.xml'
        else: xml_file = 'skin.xml'
        if ( not os.path.isfile( os.path.join( skin_path, xml_file ))): xml_file = 'skin.xml'
        guibuilder.GUIBuilder( self, os.path.join( skin_path, xml_file ), image_path, fastMethod=True )

    def setupVariables( self ):
        self.artist = None
        self.song = None
        self.controller_action = lyricsutil.setControllerAction()
        try: self.controls[ 8 ][ 'control' ].setLabel( self.settings.SCRAPER )
        except: pass
    
    def getSettings( self ):
        self.settings = lyricsutil.Settings()

    def getScraper( self ):
        sys.path.append( os.path.join( resourcesPath, 'scrapers', self.settings.SCRAPER ) )
        import lyricsScraper
        self.LyricsScraper = lyricsScraper.LyricsFetcher()

    # getDummyTimer() and self.Timer are currently used for the Player() subclass so when an onPlayback* event occurs, 
    # it calls myPlayerChanged() immediately.
    def getDummyTimer( self ):
        self.Timer = threading.Timer( 60*60*60, self.getDummyTimer,() )
        self.Timer.start()
    
    def getMyPlayer( self ):
        self.MyPlayer = MyPlayer( xbmc.PLAYER_CORE_PAPLAYER, function = self.myPlayerChanged )
        self.myPlayerChanged( 2 )
    
    def show_control( self, controlId ):
        self.controls[ 3 ][ 'control' ].setVisible( controlId == 3 )
        self.controls[ 4 ][ 'control' ].setVisible( controlId == 4 )
        self.controls[ 5 ][ 'control' ].setVisible( controlId == 5 )
        try:
            self.controls[ 7 ][ 'control' ].setVisible( controlId == 4 or controlId == 5 )
        except: pass
        self.setFocus( self.controls[ controlId ][ 'control' ] )
        self.controlId = controlId
        self.update_label()
        
    def get_lyrics(self, artist, song):
        self.menu_items = []
        self.reset_controls()
        lyrics = self.get_lyrics_from_file( artist, song )
        if ( lyrics ):
            self.show_lyrics( lyrics )
        else:
            lyrics = self.LyricsScraper.get_lyrics( artist, song )
            if ( type( lyrics ) == str or type( lyrics ) == unicode ):
                self.show_lyrics( lyrics, True )
            elif ( type( lyrics ) == list and lyrics ):
                self.show_choices( lyrics )
            else:
                self.show_lyrics( _( 2 ) )
        
    def get_lyrics_from_list( self, item ):
        lyrics = self.LyricsScraper.get_lyrics_from_list( self.menu_items[ item ] )
        self.show_lyrics( lyrics, True )

    def get_lyrics_from_file( self, artist, song ):
        try:
            self.artist_filename = self.make_fatx_compatible( artist, False )
            self.song_filename = self.make_fatx_compatible( song + '.txt', True )
            song_path = os.path.join( self.settings.LYRICS_PATH, self.artist_filename, self.song_filename )
            lyrics_file = open( song_path, 'r' )
            lyrics = unicode( lyrics_file.read(), 'utf-8', 'ignore' )
            lyrics_file.close()
            return lyrics
        except: return None

    def save_lyrics_to_file( self, lyrics ):
        try:
            song_path = os.path.join( self.settings.LYRICS_PATH, self.artist_filename, self.song_filename )
            if ( not os.path.isdir( os.path.join( self.settings.LYRICS_PATH, self.artist_filename ) ) ):
                os.makedirs( os.path.join( self.settings.LYRICS_PATH, self.artist_filename ) )
            lyrics_file = open( song_path, 'w' )
            lyrics_file.write( lyrics.encode( 'utf-8', 'ignore' ) )
            lyrics_file.close()
            return True
        except: return False
        
    def make_fatx_compatible( self, name, extension ):
        if len( name ) > 42:
            if ( extension ): name = '%s_%s' % ( name[ : 37 ], name[ -4 : ], )
            else: name = name[ : 42 ]
        name = name.replace( ',', '_' ).replace( '*', '_' ).replace( '=', '_' ).replace( '\\', '_' ).replace( '|', '_' )
        name = name.replace( '<', '_' ).replace( '>', '_' ).replace( '?', '_' ).replace( ';', '_' ).replace( ':', '_' )
        name = name.replace( '"', '_' ).replace( '+', '_' ).replace( '/', '_' )
        return name
        
    def show_lyrics( self, lyrics, save=False ):
        xbmcgui.lock()
        #Checking whether some idiot has submitted empty lyrics or not:
        if ( len( lyrics ) < 2 ):
            self.controls[ 3 ][ 'control' ].setText( _( 3 ) )
            self.controls[ 4 ][ 'control' ].addItem( _( 3 ) )
        #If not, we show whatever results we got:
        else:
            self.controls[ 3 ][ 'control' ].setText( lyrics )
            for x in lyrics.split( '\n' ):
                self.controls[ 4 ][ 'control' ].addItem( x )
            if ( self.settings.SAVE_LYRICS and save ): success = self.save_lyrics_to_file( lyrics )
        self.show_control( 3 + self.settings.USE_LIST )
        xbmcgui.unlock()
        
    def show_choices( self, choices ):
        xbmcgui.lock()
        for song in choices:
            self.controls[ 5 ][ 'control' ].addItem( song[ 0 ] )
        self.menu_items = choices
        self.show_control( 5 )
        xbmcgui.unlock()
    
    def reset_controls( self ):
        self.controls[ 3 ][ 'control' ].reset()
        self.controls[ 4 ][ 'control' ].reset()
        self.controls[ 5 ][ 'control' ].reset()
        
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

    def change_settings( self ):
        try:
            import settings
            settings = settings.GUI( language=_, scriptname=__scriptname__, version=__version__ )
            settings.doModal()
            del settings
            self.getSettings()
            if ( self.controlId == 3 or self.controlId == 4 ): 
                self.show_control( 3 + self.settings.USE_LIST )
        except: pass
            
    def exitScript(self):
        if ( self.Timer ): self.Timer.cancel()
        self.close()

    def onAction(self, action):
        button_key = self.controller_action.get( action.getButtonCode(), 'n/a' )
        if ( button_key == 'Keyboard ESC Button' or button_key == 'Back Button' or button_key == 'Remote Menu Button' ):
            self.exitScript()
        elif ( button_key == 'Keyboard Menu Button' or button_key == 'Y Button' or button_key == 'Remote Title Button' or button_key == 'White Button' ):
            self.change_settings()
        else: self.update_label()
    
    def onControl(self, control):
        if control == self.controls[ 5 ][ 'control' ]:
            self.get_lyrics_from_list( self.controls[ 5 ][ 'control' ].getSelectedPosition() )
            
    def myPlayerChanged( self, event ):
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
        ui = GUI()
        if ( ui.SUCCEEDED ): ui.doModal()
        del ui
    else:
        xbmcgui.Dialog().ok( _( 0 ), _( 10 ), _( 11 ) )
