import os
import xbmc, xbmcgui
import guibuilder
import lyricsutil
import traceback

class GUI( xbmcgui.WindowDialog ):
    def __init__( self, *args, **kwargs ):
        try:
            self._ = kwargs[ 'language' ]
            self.__scriptname__ = kwargs[ 'scriptname' ]
            self.__version__ = kwargs[ 'version' ]
            self.setupGUI()
            if ( not self.SUCCEEDED ): self.close()
            else:
                #self.show()
                self._set_variables()
                self._get_settings()
                self._setup_scrapers()
                self._set_controls_values()
        except:
            traceback.print_exc()
            self.close()

    def setupGUI( self ):
        cwd = os.getcwd().replace( ";", "" )
        current_skin = xbmc.getSkinDir()
        if ( not os.path.exists( os.path.join( cwd, 'resources', 'skins', current_skin ))): current_skin = 'default'
        skin_path = os.path.join( cwd, 'resources', 'skins', current_skin )
        image_path = os.path.join( skin_path, 'gfx' )
        if ( self.getResolution() == 0 or self.getResolution() % 2 ): xml_file = 'settings_16x9.xml'
        else: xml_file = 'settings.xml'
        if ( not os.path.isfile( os.path.join( skin_path, xml_file ))): xml_file = 'settings.xml'
        guibuilder.GUIBuilder( self, os.path.join( skin_path, xml_file ), image_path, useDescAsKey=True, language=self._, fastMethod=True, debug=False )

    def _set_variables( self ):
        self.controller_action = lyricsutil.setControllerAction()
        self.controls[ 'Version Label' ][ 'control' ].setLabel( '%s: %s' % ( self._( 100 ), self.__version__, ) )
        
    def _setup_scrapers( self ):
        scrapers = []
        self.current_scraper = 0
        os.path.walk( os.path.join( os.getcwd().replace( ";", "" ), 'resources', 'scrapers' ), self._add_scraper, scrapers )
        self.scrapers = scrapers
        for cnt, scraper in enumerate( scrapers ):
            if ( scraper == self.settings[ "scraper" ] ):
                self.current_scraper = cnt
                break
        
    def _add_scraper( self, scrapers, path, files ):
        tmp_scraper = os.path.split( path )[ 1 ]
        if ( tmp_scraper.lower() != 'scrapers' ):
            scrapers += [ tmp_scraper ]

    def _get_settings( self ):
        self.settings = lyricsutil.Settings().get_settings()
        self.SCRAPER = self.settings[ "scraper" ]
        #self.settings_start = lyricsutil.Settings()
        
    def _set_controls_values( self ):
        #xbmcgui.lock()
        self.controls['Scraper Button Value']['control'].setLabel( '%s' % ( self.settings[ "scraper" ], ) )
        self.controls['Save Lyrics Button Value']['control'].setLabel( '%s' % ( str( self.settings[ "save_lyrics" ], ) ) )
        self.controls['Save Folder Button']['control'].setEnabled( self.settings[ "save_lyrics" ] )
        self.controls['Save Folder Button Value']['control'].setLabel( '%s' % ( self.settings[ "lyrics_path" ], ) )
        self.controls['Save Folder Button Value']['control'].setEnabled( self.settings[ "save_lyrics" ]  )
        self.controls['Smooth Scroll Button Value']['control'].setLabel( '%s' % ( str( self.settings[ "smooth_scrolling" ], ) ) )
        self.controls['Show Viz Button Value']['control'].setLabel( '%s' % ( str( self.settings[ "show_viz" ], ) ) )
        #xbmcgui.lock()
    
    def _toggle_scraper( self ):
        self.current_scraper += 1
        if ( self.current_scraper == len( self.scrapers ) ): self.current_scraper = 0
        self.settings[ "scraper" ] = self.scrapers[ self.current_scraper ]
    
    def _toggle_save_lyrics( self ):
        self.settings[ "save_lyrics" ] = not self.settings[ "save_lyrics" ]

    def _toggle_smooth_scrolling( self ):
        self.settings[ "smooth_scrolling" ] = not self.settings[ "smooth_scrolling" ]

    def _toggle_show_viz( self ):
        self.settings[ "show_viz" ] = not self.settings[ "show_viz" ]

    def _browse_for_folder( self ):
        dialog = xbmcgui.Dialog()
        folder = dialog.browse( 3, self._( 40 ), 'files' )
        if ( folder ):
            self.settings[ "lyrics_path" ] = folder
    
    def _save_settings( self ):
        ret = lyricsutil.Settings().save_settings( self.settings )
        if ( not ret ):
            ok = xbmcgui.Dialog().ok( self._( 0 ), self._( 12 ) )
        else:
            if ( self.SCRAPER != self.settings[ "scraper" ]):
                ok = xbmcgui.Dialog().ok( self._( 0 ), self._( 13 )  )
            self._close_dialog()
            
    def _update_script( self ):
        import update
        updt = update.Update( language=self._, script=self.__scriptname__, version=self.__version__ )
        del updt

    def _close_dialog( self ):
        self.close()
        
    def onControl( self, control ):
        if ( control is self.controls['Cancel Button']['control'] ):
            self._close_dialog()
        elif ( control is self.controls['Ok Button']['control'] ):
            self._save_settings()
        elif ( control is self.controls['Update Button']['control'] ):
            self._update_script()
        #elif ( control is self.controls['Credits Button']['control'] ):
        #    self.showCredits()
        else:
            if ( control is self.controls['Scraper Button']['control'] ):
                self._toggle_scraper()
            elif ( control is self.controls['Save Lyrics Button']['control'] ):
                self._toggle_save_lyrics()
            elif ( control is self.controls['Save Folder Button']['control'] ):
                self._browse_for_folder()
            elif ( control is self.controls['Smooth Scroll Button']['control'] ):
                self._toggle_smooth_scrolling()
            elif ( control is self.controls['Show Viz Button']['control'] ):
                self._toggle_show_viz()
            self._set_controls_values()
            
    def onAction( self, action ):
        try:
            control = self.getFocus()
            button_key = self.controller_action.get( action.getButtonCode(), 'n/a' )
            if ( button_key == 'Keyboard Backspace Button' or button_key == 'B Button' or button_key == 'Remote Back Button' ):
                self._close_dialog()
            elif ( button_key == 'Keyboard ESC Button' or button_key == 'Back Button' or button_key == 'Remote Menu Button' ):
                self._save_settings()
        except:
            traceback.print_exc()
