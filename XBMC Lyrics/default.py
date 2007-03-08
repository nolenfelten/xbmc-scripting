"""
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
"""
__scriptname__ = "XBMC Lyrics"
__author__ = "XBMC Lyrics Team"
__url__ = "http://code.google.com/p/xbmc-scripting/"
__credits__ = "XBMC TEAM, freenode/#xbmc-scripting"
__version__ = "1.2.3"


import os, sys
import xbmc, xbmcgui
import threading

resourcesPath = os.path.join( os.getcwd().replace( ";", "" ), "resources" )
sys.path.append( os.path.join( resourcesPath, "lib" ) )
import language, utilities
import guibuilder
_ = language.Language().string


class GUI( xbmcgui.WindowDialog ):
    def __init__( self ):
        try:
            self.Timer = None
            self.gui_loaded = self.setupGUI()
            if ( not self.gui_loaded ): self.exit_script()
            else:
                self.setup_all()
        except: 
            self.exit_script()
            
    def setup_all( self ):
        self.get_settings()
        self.show_viz_window()
        self.setup_variables()
        self.get_scraper()
        self.getDummyTimer()
        self.getMyPlayer()

    def setupGUI( self ):
        gb = guibuilder.GUIBuilder()
        ok = gb.create_gui( self, fastMethod=True, language=_ )
        return ok

    def setup_variables( self ):
        self.artist = None
        self.song = None
        self.controller_action = utilities.setControllerAction()
        try: self.controls[ 8 ][ "control" ].setLabel( self.settings[ "scraper" ] )
        except: pass
    
    def get_settings( self ):
        self.settings = utilities.Settings().get_settings()
        
    def show_viz_window( self, startup=True ):
        if ( self.settings[ "show_viz" ] ):
            xbmc.executebuiltin( "XBMC.ActivateWindow(2006)" )
        elif ( not startup ):
            xbmc.executebuiltin( "XBMC.ActivateWindow(%s)" % ( current_wid, ) )

    def get_scraper( self ):
        sys.path.append( os.path.join( resourcesPath, "scrapers", self.settings[ "scraper" ] ) )
        import lyricsScraper
        self.LyricsScraper = lyricsScraper.LyricsFetcher()

    def show_control( self, controlId ):
        self.controls[ 3 ][ "control" ].setVisible( controlId == 3 )
        self.controls[ 4 ][ "control" ].setVisible( controlId == 4 )
        self.controls[ 5 ][ "control" ].setVisible( controlId == 5 )
        try:
            self.controls[ 7 ][ "control" ].setVisible( controlId == 4 or controlId == 5 )
        except: pass
        self.setFocus( self.controls[ controlId ][ "control" ] )
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
                self.show_lyrics( _( 631 ) )
        
    def get_lyrics_from_list( self, item ):
        lyrics = self.LyricsScraper.get_lyrics_from_list( self.menu_items[ item ] )
        self.show_lyrics( lyrics, True )

    def get_lyrics_from_file( self, artist, song ):
        try:
            self.artist_filename = self.make_fatx_compatible( artist, False )
            self.song_filename = self.make_fatx_compatible( song + ".txt", True )
            song_path = os.path.join( self.settings[ "lyrics_path" ], self.artist_filename, self.song_filename )
            lyrics_file = open( song_path, "r" )
            lyrics = unicode( lyrics_file.read(), "utf-8", "ignore" )
            lyrics_file.close()
            return lyrics
        except: return None

    def save_lyrics_to_file( self, lyrics ):
        try:
            song_path = os.path.join( self.settings[ "lyrics_path" ], self.artist_filename, self.song_filename )
            if ( not os.path.isdir( os.path.join( self.settings[ "lyrics_path" ], self.artist_filename ) ) ):
                os.makedirs( os.path.join( self.settings[ "lyrics_path" ], self.artist_filename ) )
            lyrics_file = open( song_path, "w" )
            lyrics_file.write( lyrics.encode( "utf-8", "ignore" ) )
            lyrics_file.close()
            return True
        except: return False
        
    def make_fatx_compatible( self, name, extension ):
        if len( name ) > 42:
            if ( extension ): name = "%s_%s" % ( name[ : 37 ], name[ -4 : ], )
            else: name = name[ : 42 ]
        name = name.replace( ",", "_" ).replace( "*", "_" ).replace( "=", "_" ).replace( "\\", "_" ).replace( "|", "_" )
        name = name.replace( "<", "_" ).replace( ">", "_" ).replace( "?", "_" ).replace( ";", "_" ).replace( ":", "_" )
        name = name.replace( '"', "_" ).replace( "+", "_" ).replace( "/", "_" )
        return name
        
    def show_lyrics( self, lyrics, save=False ):
        xbmcgui.lock()
        #Checking whether some idiot has submitted empty lyrics or not:
        if ( len( lyrics ) < 2 ):
            self.controls[ 3 ][ "control" ].setText( _( 632 ) )
            self.controls[ 4 ][ "control" ].addItem( _( 632 ) )
        #If not, we show whatever results we got:
        else:
            self.controls[ 3 ][ "control" ].setText( lyrics )
            for x in lyrics.split( "\n" ):
                self.controls[ 4 ][ "control" ].addItem( x )
            #################################################
            self.controls[ 4 ][ "control" ].selectItem( 0 )
            if ( self.settings[ "save_lyrics" ] and save ): success = self.save_lyrics_to_file( lyrics )
        self.show_control( 3 + self.settings[ "smooth_scrolling" ] )
        xbmcgui.unlock()
        
    def show_choices( self, choices ):
        xbmcgui.lock()
        for song in choices:
            self.controls[ 5 ][ "control" ].addItem( song[ 0 ] )
        #################################################
        self.controls[ 5 ][ "control" ].selectItem( 0 )
        self.menu_items = choices
        self.show_control( 5 )
        xbmcgui.unlock()
    
    def reset_controls( self ):
        self.controls[ 3 ][ "control" ].reset()
        self.controls[ 4 ][ "control" ].reset()
        self.controls[ 5 ][ "control" ].reset()
        
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
            self.controls[ 7 ][ "control" ].setLabel( "%d/%d" % ( current_page, total_pages, ) )
        except: pass
        xbmcgui.unlock()

    def change_settings( self ):
        try:
            import settings
            settings = settings.GUI( language=_ )
            if ( settings.gui_loaded ):
                settings.doModal()
                ok = False
                if ( settings.changed ):
                    self.get_settings()
                    if ( settings.restart ):
                        ok = xbmcgui.Dialog().yesno( __scriptname__, _( 240 ), "", _( 241 ) % ( __scriptname__, ), _( 256 ), _( 255 ) )
                del settings
                if ( not ok ):
                    if ( self.controlId == 3 or self.controlId == 4 ): 
                        self.show_control( 3 + self.settings[ "smooth_scrolling" ] )
                    self.show_viz_window( False )
                else: self.exit_script( True )
        except: traceback.print_exc()
            
    def exit_script( self, restart=False ):
        if ( self.Timer ): self.Timer.cancel()
        self.close()
        if ( restart ): xbmc.executebuiltin( "XBMC.RunScript(%s)" % ( os.path.join( os.getcwd().replace( ";", "" ), "default.py" ), ) )

    def onControl(self, control):
        if control == self.controls[ 5 ][ "control" ]:
            self.get_lyrics_from_list( self.controls[ 5 ][ "control" ].getSelectedPosition() )

    def onAction(self, action):
        button_key = self.controller_action.get( action.getButtonCode(), "n/a" )
        if ( button_key == "Keyboard ESC Button" or button_key == "Back Button" or button_key == "Remote Menu Button" ):
            self.exit_script()
        elif ( button_key == "Keyboard Menu Button" or button_key == "Y Button" or button_key == "Remote Title Button" or button_key == "White Button" ):
            self.change_settings()
        else: self.update_label()
    
    # getDummyTimer() and self.Timer are currently used for the Player() subclass so when an onPlayback* event occurs, 
    # it calls myPlayerChanged() immediately.
    def getDummyTimer( self ):
        self.Timer = threading.Timer( 60*60*60, self.getDummyTimer,() )
        self.Timer.start()
    
    def getMyPlayer( self ):
        self.MyPlayer = MyPlayer( xbmc.PLAYER_CORE_PAPLAYER, function = self.myPlayerChanged )
        self.myPlayerChanged( 2 )
    
    def myPlayerChanged( self, event ):
        #print ["stopped","ended","started"][event]
        if ( event < 2 ): 
            self.exit_script()
        else:
            song = self.song
            for cnt in range( 5 ):
                if ( xbmc.getInfoLabel( "MusicPlayer.Title" ) != self.song ): break
                xbmc.sleep( 50 )
            self.song = xbmc.getInfoLabel( "MusicPlayer.Title" )
            self.artist = xbmc.getInfoLabel( "MusicPlayer.Artist" )
            self.controls[ 6 ][ "control" ].setImage( xbmc.getInfoImage( "MusicPlayer.Cover" ) )
            self.get_lyrics( self.artist, self.song )


## Thanks Thor918 for this class ##
class MyPlayer( xbmc.Player ):
    def  __init__( self, *args, **kwargs ):
        if ( kwargs.has_key( "function" ) ): 
            self.function = kwargs[ "function" ]
            xbmc.Player.__init__( self )

    def onPlayBackStopped( self ):
        self.function( 0 )
    
    def onPlayBackEnded( self ):
        self.function( 1 )
    
    def onPlayBackStarted( self ):
        self.function( 2 )

    
if ( __name__ == "__main__" ):
    if ( xbmc.Player().isPlayingAudio() ):
        current_wid = xbmcgui.getCurrentWindowId()
        ui = GUI()
        if ( ui.gui_loaded ): ui.doModal()
        del ui
    else:
        xbmcgui.Dialog().ok( __scriptname__, _( 638 ), _( 639 ) )
