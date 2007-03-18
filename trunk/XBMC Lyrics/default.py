"""
	Credits:	
		EnderW:					Original Author
		Stanley87:				PM3 Integration and AD Removal
		solexalex:
		TomKun:
		Smuto:					Skinning Mod
		Spiff:						Unicode support
		Nuka1195:				lyricwiki & embedded Scraper and Modulization
				
Please report any bugs: http://www.xboxmediacenter.com/forum/showthread.php?t=10187
"""
__scriptname__ = "XBMC Lyrics"
__author__ = "XBMC Lyrics Team"
__url__ = "http://code.google.com/p/xbmc-scripting/"
__credits__ = "XBMC TEAM, freenode/#xbmc-scripting"
__version__ = "1.4"


import os, sys
import xbmc, xbmcgui
import threading

resource_path = os.path.join( os.getcwd().replace( ";", "" ), "resources" )
sys.path.append( os.path.join( resource_path, "lib" ) )
import language, utilities
import guibuilder
_ = language.Language().string

class GUI( xbmcgui.WindowDialog ):
    def __init__( self ):
        try:
            self.Timer = None
            self.gui_loaded, image_path = self.setupGUI()
            if ( not self.gui_loaded ): self.exit_script()
            else:
                self.startScript = Start( function=self.setup_all ).start()
        except: 
            self.exit_script()
            
    def setup_all( self ):
        self.get_settings()
        self.setup_variables()
        self.get_scraper()
        self.getDummyTimer()
        self.show_viz_window()
        self.getMyPlayer()

    def setupGUI( self ):
        gb = guibuilder.GUIBuilder()
        ok = gb.create_gui( self, use_desc_as_key=False, language=_ )
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
        else:
            if ( current_dlg_id != 9999 or not startup ):
                xbmc.executebuiltin( "XBMC.ActivateWindow(%s)" % ( current_win_id, ) )

    def get_scraper( self ):
        sys.path.append( os.path.join( resource_path, "scrapers", self.settings[ "scraper" ] ) )
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
        self.allow_exception = False
        current_song = self.song
        lyrics = self.get_lyrics_from_file( artist, song )
        if ( lyrics ):
            if ( current_song == self.song ):
                self.show_lyrics( lyrics )
        else:
            lyrics = self.LyricsScraper.get_lyrics( artist, song )
            if ( current_song == self.song ):
                if ( type( lyrics ) == str or type( lyrics ) == unicode ):
                    self.show_lyrics( lyrics, True )
                elif ( type( lyrics ) == list and lyrics ):
                    self.show_choices( lyrics )
                else:
                    self.show_lyrics( _( 631 ) )
                    self.allow_exception = True

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
        return unicode( name, "utf-8", "ignore" )
        
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
        except: pass
            
    def get_exception( self ):
        """ user modified exceptions """
        artist = self.LyricsScraper._format_param( self.artist, False )
        if ( artist ):
            alt_artist = self.get_keyboard( artist, "%s %s" % ( _( 100 ), unicode( self.artist, "utf-8", "ignore" ), ) )
            if ( alt_artist != artist ):
                exception = ( artist, alt_artist, )
                self.LyricsScraper._set_exceptions( exception )
                self.myPlayerChanged( 2, True )
        
    def get_keyboard( self, default="", heading="", hidden=False ):
        """ shows a keyboard and returns a value """
        keyboard = xbmc.Keyboard( default, heading, hidden )
        keyboard.doModal()
        if ( keyboard.isConfirmed() ):
            return keyboard.getText()
        return default

    def exit_script( self, restart=False ):
        if ( self.Timer ): self.Timer.cancel()
        self.close()
        if ( restart ): xbmc.executebuiltin( "XBMC.RunScript(%s)" % ( os.path.join( os.getcwd().replace( ";", "" ), "default.py" ), ) )

    def onControl( self, control ):
        if control == self.controls[ 5 ][ "control" ]:
            self.get_lyrics_from_list( self.controls[ 5 ][ "control" ].getSelectedPosition() )

    def onAction( self, action ):
        button_key = self.controller_action.get( action.getButtonCode(), "n/a" )
        if ( button_key == "Keyboard ESC Button" or button_key == "Back Button" or button_key == "Remote Menu Button" ):
            self.exit_script()
        elif ( button_key == "Keyboard Menu Button" or button_key == "Y Button" or button_key == "Remote Title Button" or button_key == "White Button" ):
            self.change_settings()
        elif ( self.allow_exception and ( button_key == "Keyboard Backspace Button" or button_key == "Black Button" or button_key == "Remote Back Button" ) ):
            self.get_exception()
        else: self.update_label()
    
    # getDummyTimer() and self.Timer are currently used for the Player() subclass so when an onPlayback* event occurs, 
    # it calls myPlayerChanged() immediately.
    def getDummyTimer( self ):
        self.Timer = threading.Timer( 60*60*60, self.getDummyTimer,() )
        self.Timer.start()
    
    def getMyPlayer( self ):
        self.MyPlayer = MyPlayer( xbmc.PLAYER_CORE_PAPLAYER, function=self.myPlayerChanged )
        self.myPlayerChanged( 2 )
    
    def myPlayerChanged( self, event, force_update=False ):
        #print ["stopped","ended","started"][event]
        if ( event < 2 ): 
            self.exit_script()
        else:
            song = self.song
            for cnt in range( 5 ):
                self.song = xbmc.getInfoLabel( "MusicPlayer.Title" )
                if ( song != self.song and self.song ): break
                xbmc.sleep( 50 )
            if ( song != self.song or force_update ):
                self.artist = xbmc.getInfoLabel( "MusicPlayer.Artist" )
                self.controls[ 6 ][ "control" ].setImage( xbmc.getInfoImage( "MusicPlayer.Cover" ) )
                if ( self.song and self.artist ): self.get_lyrics( self.artist, self.song )
                else: self.reset_controls()


## Thanks Thor918 for this class ##
class MyPlayer( xbmc.Player ):
    """ Player Class: calls function when song changes or playback ends """
    def __init__( self, *args, **kwargs ):
        xbmc.Player.__init__( self )
        self.function = kwargs[ "function" ]

    def onPlayBackStopped( self ):
        self.function( 0 )
    
    def onPlayBackEnded( self ):
        self.function( 1 )
    
    def onPlayBackStarted( self ):
        self.function( 2 )


class Start( threading.Thread ):
    """ Thread Class used to allow gui to show before all checks are done at start of script """
    def __init__( self, *args, **kwargs ):
        threading.Thread.__init__( self )
        self.function = kwargs[ "function" ]

    def run(self):
        self.function()


if ( __name__ == "__main__" ):
    if ( xbmc.Player().isPlayingAudio() ):
        try: current_dlg_id = xbmcgui.getCurrentWindowDialogId()
        except: current_dlg_id = 0
        current_win_id = xbmcgui.getCurrentWindowId()
        ui = GUI()
        if ( ui.gui_loaded ): ui.doModal()
        del ui
    else:
        xbmcgui.Dialog().ok( __scriptname__, _( 638 ), _( 639 ) )
