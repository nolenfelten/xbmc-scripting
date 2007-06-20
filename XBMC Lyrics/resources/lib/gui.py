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

from utilities import *

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
        self.setup_all()#Start( function=self.setup_all ).start()

    def setup_all( self ):
        self.setup_variables()
        self.get_settings()
        self.get_scraper()
        self.getDummyTimer()
        self.getMyPlayer()
        self.show_viz_window()

    def get_settings( self ):
        self.settings = Settings().get_settings()
        
    def get_scraper( self ):
        sys.path.append( os.path.join( BASE_RESOURCE_PATH, "scrapers", self.settings[ "scraper" ] ) )
        import lyricsScraper
        self.LyricsScraper = lyricsScraper.LyricsFetcher()
        self.getControl( 200 ).setLabel( lyricsScraper.__title__ )

    def setup_variables( self ):
        self.artist = None
        self.song = None
        self.Timer = None
        self.controlId = -1
        self.allow_exception = False

    def show_viz_window( self, startup=True ):
        if ( self.settings[ "show_viz" ] ):
            xbmc.executebuiltin( "XBMC.ActivateWindow(2006)" )
        else:
            if ( current_dlg_id != 9999 or not startup ):
                xbmc.executebuiltin( "XBMC.ActivateWindow(%s)" % ( current_win_id, ) )

    def show_control( self, controlId ):
        self.getControl( 100 ).setVisible( controlId == 100 )
        self.getControl( 110 ).setVisible( controlId == 110 )
        self.getControl( 120 ).setVisible( controlId == 120 )
        page_control = ( controlId == 100 )
        try: self.setFocus( self.getControl( controlId + page_control ) )
        except: self.setFocus( self.getControl( controlId ) )

    def get_lyrics(self, artist, song):
        self.menu_items = []
        self.reset_controls()
        self.allow_exception = False
        current_song = self.song
        lyrics = self.get_lyrics_from_file( artist, song )
        if ( lyrics is not None ):
            if ( current_song == self.song ):
                self.show_lyrics( lyrics )
                self.getControl( 200 ).setEnabled( False )
        else:
            self.getControl( 200 ).setEnabled( True )
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
            if ( not os.path.isdir( os.path.split( song_path )[ 0 ] ) ):
                os.makedirs( os.path.split( song_path )[ 0 ] )
            lyrics_file = open( song_path, "w" )
            lyrics_file.write( lyrics.encode( "utf-8", "ignore" ) )
            lyrics_file.close()
            return True
        except:
            LOG( LOG_ERROR, "%s (ver: %s) GUI::save_lyrics_to_file [%s]", __scriptname__, __version__, sys.exc_info()[ 1 ], )
            return False

    def make_fatx_compatible( self, name, extension=False ):
        if ( len( name ) > 42 ):
            if ( extension ): name = "%s_%s" % ( name[ : 37 ], name[ -4 : ], )
            else: name = name[ : 42 ]
        name = name.replace( ",", "_" ).replace( "*", "_" ).replace( "=", "_" ).replace( "\\", "_" ).replace( "|", "_" )
        name = name.replace( "<", "_" ).replace( ">", "_" ).replace( "?", "_" ).replace( ";", "_" ).replace( ":", "_" )
        name = name.replace( '"', "_" ).replace( "+", "_" ).replace( "/", "_" )
        if ( os.path.supports_unicode_filenames ):
            name = unicode( name, "utf-8", "ignore" )
        return name
        
    def show_lyrics( self, lyrics, save=False ):
        xbmcgui.lock()
        if ( lyrics == "" ):
            self.getControl( 100 ).setText( _( 632 ) )
            self.getControl( 110 ).addItem( _( 632 ) )
        else:
            self.getControl( 100 ).setText( lyrics )
            for x in lyrics.split( "\n" ):
                self.getControl( 110 ).addItem( x )
            self.getControl( 110 ).selectItem( 0 )
            if ( self.settings[ "save_lyrics" ] and save ): success = self.save_lyrics_to_file( lyrics )
        self.show_control( 100 + ( self.settings[ "smooth_scrolling" ] * 10 ) )
        xbmcgui.unlock()
        
    def show_choices( self, choices ):
        xbmcgui.lock()
        for song in choices:
            self.getControl( 120 ).addItem( song[ 0 ] )
        self.getControl( 120 ).selectItem( 0 )
        self.menu_items = choices
        self.show_control( 120 )
        xbmcgui.unlock()
    
    def reset_controls( self ):
        self.getControl( 100 ).reset()
        self.getControl( 110 ).reset()
        self.getControl( 120 ).reset()
        
    def change_settings( self ):
        import settings
        settings = settings.GUI( "script-%s-settings.xml" % ( __scriptname__.replace( " ", "_" ), ), BASE_RESOURCE_PATH, "Default" )
        settings.doModal()
        ok = False
        if ( settings.changed ):
            self.get_settings()
            if ( settings.restart ):
                ok = xbmcgui.Dialog().yesno( __scriptname__, _( 240 ), "", _( 241 ) % ( __scriptname__, ), _( 256 ), _( 255 ) )
            if ( not ok ):
                if ( self.controlId in ( 100, 101, 110, 111, ) ): 
                    self.show_control( 100 + ( self.settings[ "smooth_scrolling" ] * 10 ) )
                self.show_viz_window( False )
                if ( settings.refresh ):
                    self.myPlayerChanged( 2, True )
            else: self.exit_script( True )
        del settings

    def get_exception( self ):
        """ user modified exceptions """
        if ( sys.modules[ "lyricsScraper" ].__allow_exceptions__ ):
            artist = self.LyricsScraper._format_param( self.artist, False )
            alt_artist = get_keyboard( artist, "%s: %s" % ( _( 100 ), unicode( self.artist, "utf-8", "ignore" ), ) )
            if ( alt_artist != artist ):
                exception = ( artist, alt_artist, )
                self.LyricsScraper._set_exceptions( exception )
                self.myPlayerChanged( 2, True )

    def exit_script( self, restart=False ):
        if ( self.Timer is not None ): self.Timer.cancel()
        self.close()
        if ( restart ): xbmc.executebuiltin( "XBMC.RunScript(%s)" % ( os.path.join( os.getcwd().replace( ";", "" ), "default.py" ), ) )

    def onClick( self, controlId ):
        pass

    def onFocus( self, controlId ):
        self.controlId = controlId

    def onAction( self, action ):
        if ( action.getButtonCode() in EXIT_SCRIPT ):
            self.exit_script()
        elif ( action.getButtonCode() in SETTINGS_MENU ):
            self.change_settings()
        elif ( self.allow_exception and ( action.getButtonCode() in GET_EXCEPTION ) ):
            self.get_exception()
        elif ( self.controlId == 120 and action.getButtonCode() in SELECT_ITEM ):
            self.get_lyrics_from_list( self.getControl( 120 ).getSelectedPosition() )

    def _get_artist_from_filename( self, filename ):
        artist = filename.split( "-", 1 )[ 0 ].strip()
        song = os.path.splitext( filename.split( "-", 1 )[ 1 ].strip() )[ 0 ]
        return artist, song

    # getDummyTimer() and self.Timer are currently used for the Player() subclass so when an onPlayback* event occurs, 
    # it calls myPlayerChanged() immediately.
    def getDummyTimer( self ):
        self.Timer = threading.Timer( 60*60*60, self.getDummyTimer,() )
        self.Timer.start()
    
    def getMyPlayer( self ):
        self.MyPlayer = MyPlayer( xbmc.PLAYER_CORE_PAPLAYER, function=self.myPlayerChanged )
        self.myPlayerChanged( 2 )

    def myPlayerChanged( self, event, force_update=False ):
        LOG( LOG_DEBUG, "%s (ver: %s) GUI::myPlayerChanged [%s]", __scriptname__, __version__, ["stopped","ended","started"][event] )
        if ( event < 2 ): 
            self.exit_script()
        else:
            for cnt in range( 5 ):
                song = xbmc.getInfoLabel( "MusicPlayer.Title" )
                artist = xbmc.getInfoLabel( "MusicPlayer.Artist" )
                if ( ( song != self.song and song and self.artist != artist ) or ( force_update and song ) ):
                    self.artist = artist
                    self.song = song
                    if ( not artist or self.settings[ "use_filename" ] ):
                        if ( self.settings[ "use_filename" ] ):
                            song = os.path.basename( xbmc.Player().getPlayingFile() )
                        artist, song = self._get_artist_from_filename( song )
                    self.get_lyrics( artist, song )
                    break
                else: xbmc.sleep( 50 )


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
