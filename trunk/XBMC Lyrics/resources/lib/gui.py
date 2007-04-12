"""
	Credits:	
		EnderW:					Original Author
		Stanley87:				PM3 Integration and AD Removal
		solexalex:
		TomKun:
		Thor918:				MyPlayer Class
		Smuto:					Skinning Mod
		Spiff:						Unicode support
		Nuka1195:				lyricwiki & embedded Scraper and Modulization
				
Please report any bugs: http://www.xboxmediacenter.com/forum/showthread.php?t=10187
"""

import sys
import os
import xbmc
import xbmcgui
import threading
#import traceback

import utilities

try: current_dlg_id = xbmcgui.getCurrentWindowDialogId()
except: current_dlg_id = 0
current_win_id = xbmcgui.getCurrentWindowId()

_ = sys.modules[ "__main__" ].__language__
__scriptname__ = sys.modules[ "__main__" ].__scriptname__
__version__ = sys.modules[ "__main__" ].__version__


class GUI( xbmcgui.WindowXMLDialog ):
    def __init__( self, *args, **kwargs ):
        pass

    def onInit( self ):
        self.set_controls()
        self.setup_all()#Start( function=self.setup_all ).start()

    def set_controls( self ):
        self.controls = {}
        self.controls[ 100 ] = self.getControl( 100 )
        try: self.controls[ 101 ] = self.getControl( 101 )
        except: pass
        self.controls[ 110 ] = self.getControl( 110 )
        self.controls[ 120 ] = self.getControl( 120 )
        self.controls[ 200 ] = self.getControl( 200 )

    def setup_all( self ):
        self.get_settings()
        self.get_scraper()
        self.setup_variables()
        self.getDummyTimer()
        self.getMyPlayer()
        self.show_viz_window()

    def get_settings( self ):
        self.settings = utilities.Settings().get_settings()
        
    def get_scraper( self ):
        sys.path.append( os.path.join( utilities.BASE_RESOURCE_PATH, "scrapers", self.settings[ "scraper" ] ) )
        import lyricsScraper
        self.LyricsScraper = lyricsScraper.LyricsFetcher()
        self.controls[ 200 ].setLabel( lyricsScraper.__title__ )

    def setup_variables( self ):
        self.artist = None
        self.song = None
        self.Timer = None
        self.controlId = -1

    def show_viz_window( self, startup=True ):
        if ( self.settings[ "show_viz" ] ):
            xbmc.executebuiltin( "XBMC.ActivateWindow(2006)" )
        else:
            if ( current_dlg_id != 9999 or not startup ):
                xbmc.executebuiltin( "XBMC.ActivateWindow(%s)" % ( current_win_id, ) )

    def show_control( self, controlId ):
        #print controlId
        self.controls[ 100 ].setVisible( controlId == 100 )
        self.controls[ 110 ].setVisible( controlId == 110 )
        self.controls[ 120 ].setVisible( controlId == 120 )
        if ( controlId == 100 ): page_control = 1
        else: page_control = 0
        try: self.setFocus( self.controls[ controlId + page_control ] )
        except: self.setFocus( self.controls[ controlId ] )

    def get_lyrics(self, artist, song):
        self.menu_items = []
        self.reset_controls()
        self.allow_exception = False
        current_song = self.song
        lyrics = self.get_lyrics_from_file( artist, song )
        if ( lyrics is not None ):
            if ( current_song == self.song ):
                self.show_lyrics( lyrics )
                self.controls[ 200 ].setEnabled( False )
        else:
            self.controls[ 200 ].setEnabled( True )
            lyrics = self.LyricsScraper.get_lyrics( artist, song )
            if ( current_song == self.song ):
                if ( isinstance( lyrics, basestring ) ):
                    self.show_lyrics( lyrics, True )
                elif ( isinstance( lyrics, list ) and lyrics ):
                    self.show_choices( lyrics )
                else:
                    self.show_lyrics( _( 631 ) )
                    self.allow_exception = True

    def get_lyrics_from_list( self, item ):
        ##self.reset_controls()
        lyrics = self.LyricsScraper.get_lyrics_from_list( self.menu_items[ item ] )
        self.show_lyrics( lyrics, True )

    def get_lyrics_from_file( self, artist, song ):
        try:
            self.artist_filename = self.make_fatx_compatible( artist )
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
        
    def make_fatx_compatible( self, name, extension=False ):
        if len( name ) > 42:
            if ( extension ): name = "%s_%s" % ( name[ : 37 ], name[ -4 : ], )
            else: name = name[ : 42 ]
        name = name.replace( ",", "_" ).replace( "*", "_" ).replace( "=", "_" ).replace( "\\", "_" ).replace( "|", "_" )
        name = name.replace( "<", "_" ).replace( ">", "_" ).replace( "?", "_" ).replace( ";", "_" ).replace( ":", "_" )
        name = name.replace( '"', "_" ).replace( "+", "_" ).replace( "/", "_" )
        return unicode( name, "utf-8", "ignore" )
        
    def show_lyrics( self, lyrics, save=False ):
        xbmcgui.lock()
        if ( lyrics == "" ):
            self.controls[ 100 ].setText( _( 632 ) )
            self.controls[ 110 ].addItem( _( 632 ) )
        else:
            self.controls[ 100 ].setText( lyrics )
            for x in lyrics.split( "\n" ):
                self.controls[ 110 ].addItem( x )
            self.controls[ 110 ].selectItem( 0 )
            if ( self.settings[ "save_lyrics" ] and save ): success = self.save_lyrics_to_file( lyrics )
        self.show_control( 100 + ( self.settings[ "smooth_scrolling" ] * 10 ) )
        xbmcgui.unlock()
        
    def show_choices( self, choices ):
        xbmcgui.lock()
        for song in choices:
            self.controls[ 120 ].addItem( song[ 0 ] )
        self.controls[ 120 ].selectItem( 0 )
        self.menu_items = choices
        self.show_control( 120 )
        xbmcgui.unlock()
    
    def reset_controls( self ):
        self.controls[ 100 ].reset()
        self.controls[ 110 ].reset()
        self.controls[ 120 ].reset()
        
    def change_settings( self ):
        import settings
        settings = settings.GUI( "script-XBMC_Lyrics-settings.xml", utilities.BASE_RESOURCE_PATH, "Default" )
        settings.doModal()
        ok = False
        if ( settings.changed ):
            self.get_settings()
            if ( settings.restart ):
                ok = xbmcgui.Dialog().yesno( __scriptname__, _( 240 ), "", _( 241 ) % ( __scriptname__, ), _( 256 ), _( 255 ) )
            if ( not ok ):
                if ( self.controlId == 100 or self.controlId == 101 or self.controlId == 110 or self.controlId == 111 ): 
                    self.show_control( 100 + ( self.settings[ "smooth_scrolling" ] * 10 ) )
                self.show_viz_window( False )
            else: self.exit_script( True )
        del settings

    def get_exception( self ):
        """ user modified exceptions """
        if ( lyricsScraper.__allow_exceptions__ ):
            artist = self.LyricsScraper._format_param( self.artist, False )
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
        if ( self.Timer is not None ): self.Timer.cancel()
        self.close()
        if ( restart ): xbmc.executebuiltin( "XBMC.RunScript(%s)" % ( os.path.join( os.getcwd().replace( ";", "" ), "default.py" ), ) )

    def onClick( self, controlId ):
        pass

    def onFocus( self, controlId ):
        self.controlId = controlId

    def onAction( self, action ):
        if ( action.getButtonCode() in utilities.EXIT_SCRIPT ):
            self.exit_script()
        elif ( action.getButtonCode() in utilities.SETTINGS_MENU ):
            self.change_settings()
        elif ( self.allow_exception and ( action.getButtonCode() in utilities.GET_EXCEPTION ) ):
            self.get_exception()
        elif ( self.controlId == 120 and action.getButtonCode() in utilities.SELECT_ITEM ):
            self.get_lyrics_from_list( self.controls[ 120 ].getSelectedPosition() )

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
                #self.controls[ 6 ].setImage( xbmc.getInfoImage( "MusicPlayer.Cover" ) )
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
        xbmc.sleep( 300 )
        if ( not xbmc.Player().isPlayingAudio() ):
            self.function( 1 )
    
    def onPlayBackStarted( self ):
        self.function( 2 )


#class Start( threading.Thread ):
#    """ Thread Class used to allow gui to show before all checks are done at start of script """
#    def __init__( self, *args, **kwargs ):
#        threading.Thread.__init__( self )
#        self.function = kwargs[ "function" ]
#
#    def run(self):
#        self.function()
