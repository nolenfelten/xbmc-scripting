"""
Settings module

Nuka1195
"""

import sys
import os
import xbmc
import xbmcgui

import utilities

_ = sys.modules[ "__main__" ].__language__
__scriptname__ = sys.modules[ "__main__" ].__scriptname__
__version__ = sys.modules[ "__main__" ].__version__


class GUI( xbmcgui.WindowXMLDialog ):
    """ Settings module: used for changing settings """
    def __init__( self, *args, **kwargs ):
        pass

    def onInit( self ):
        self._set_labels()
        self._set_variables()
        self._get_settings()
        self._setup_special()
        self._set_controls_values()
        self._set_restart_required()

    def _set_labels( self ):
        xbmcgui.lock()
        try:
            self.getControl( 20 ).setLabel( __scriptname__ )
            self.getControl( 30 ).setLabel( "%s: %s" % ( _( 1006 ), __version__, ) )
            self.getControl( 201 ).setLabel( _( 201 ) )
            self.getControl( 202 ).setLabel( _( 202 ) )
            self.getControl( 203 ).setLabel( _( 203 ) )
            self.getControl( 204 ).setLabel( _( 204 ) )
            self.getControl( 205 ).setLabel( _( 205 ) )
            self.getControl( 250 ).setLabel( _( 250 ) )
            self.getControl( 251 ).setLabel( _( 251 ) )
            self.getControl( 252 ).setLabel( _( 252 ) )
            self.getControl( 253 ).setLabel( _( 253 ) )
        except: pass
        xbmcgui.unlock()

    def _set_variables( self ):
        """ initializes variables """
        # setEnabled( False ) if not used
        self.getControl( 253 ).setVisible( False )
        self.getControl( 253 ).setEnabled( False )

    def _get_settings( self ):
        """ reads settings """
        self.settings = utilities.Settings().get_settings()

    def _save_settings( self ):
        """ saves settings """
        ok = utilities.Settings().save_settings( self.settings )
        if ( not ok ):
            ok = xbmcgui.Dialog().ok( __scriptname__, _( 230 ) )
        else:
            self._check_for_restart()

    def _get_keyboard( self, default="", heading="", hidden=False ):
        """ shows a keyboard and returns a value """
        keyboard = xbmc.Keyboard( default, heading, hidden )
        keyboard.doModal()
        if ( keyboard.isConfirmed() ):
            return keyboard.getText()
        return default

    def _get_numeric( self, default="", heading="", type=3 ):
        """ shows a numeric dialog and returns a value
            - 0 : ShowAndGetNumber		(default format: #)
            - 1 : ShowAndGetDate			(default format: DD/MM/YYYY)
            - 2 : ShowAndGetTime			(default format: HH:MM)
            - 3 : ShowAndGetIPAddress	(default format: #.#.#.#)
        """
        dialog = xbmcgui.Dialog()
        value = dialog.numeric( type, heading, default )
        return value

    def _get_browse_dialog( self, default="", heading="", type=1, shares="files", mask="", use_thumbs=False, treat_as_folder=False ):
        """ shows a browse dialog and returns a value
            - 0 : ShowAndGetDirectory
            - 1 : ShowAndGetFile
            - 2 : ShowAndGetImage
            - 3 : ShowAndGetWriteableDirectory
        """
        dialog = xbmcgui.Dialog()
        value = dialog.browse( type, heading, shares, mask, use_thumbs, treat_as_folder, default )
        return value

##### Start of unique defs #####################################################

##### Special defs, script dependent, remember to call them from _setup_special #################
    
    def _set_restart_required( self ):
        """ copies self.settings and adds any settings that require a restart on change """
        self.settings_original = self.settings.copy()
        self.settings_restart = ( "scraper", )

    def _setup_special( self ):
        """ calls any special defs """
        self._setup_scrapers()

    def _setup_scrapers( self ):
        """ special def for setting up scraper choices """
        import re
        self.scrapers_title = []
        pattern = """__title__.*?["'](.*?)["']"""
        base_path = os.path.join( os.getcwd().replace( ";", "" ), "resources", "scrapers" )
        self.scrapers = os.listdir( base_path )
        for scraper in self.scrapers:
            try:
                file_object = open( os.path.join( base_path, scraper, "lyricsScraper.py" ), "r" )
                file_data = file_object.read()
                file_object.close()
                title = re.findall( pattern, file_data )
                if ( not title ): raise
            except: title = [ scraper ]
            self.scrapers_title += title
        try: self.current_scraper = self.scrapers.index( self.settings[ "scraper" ] )
        except: self.current_scraper = 0

###### End of Special defs #####################################################

    def _set_controls_values( self ):
        """ sets the value labels """
        xbmcgui.lock()
        try:
            self.getControl( 221 ).setLabel( self.scrapers_title[ self.current_scraper ] )
            self.getControl( 222 ).setSelected( self.settings[ "save_lyrics" ] )
            self.getControl( 203 ).setEnabled( self.settings[ "save_lyrics" ] )
            self.getControl( 223 ).setLabel( self.settings[ "lyrics_path" ] )
            self.getControl( 223 ).setEnabled( self.settings[ "save_lyrics" ] )
            self.getControl( 224 ).setSelected( self.settings[ "smooth_scrolling" ] )
            self.getControl( 225 ).setSelected( self.settings[ "show_viz" ] )
        except: pass
        xbmcgui.unlock()
    
    def _change_setting1( self ):
        """ changes settings #1 """
        self.current_scraper += 1
        if ( self.current_scraper == len( self.scrapers ) ): self.current_scraper = 0
        self.settings[ "scraper" ] = self.scrapers[ self.current_scraper ]
    
    def _change_setting2( self ):
        """ changes settings #2 """
        self.settings[ "save_lyrics" ] = not self.settings[ "save_lyrics" ]
        
    def _change_setting3( self ):
        """ changes settings #3 """
        self.settings[ "lyrics_path" ] = self._get_browse_dialog( self.settings[ "lyrics_path" ], _( 203 ), 3 )

    def _change_setting4( self ):
        """ changes settings #4 """
        self.settings[ "smooth_scrolling" ] = not self.settings[ "smooth_scrolling" ]
        
    def _change_setting5( self ):
        """ changes settings #5 """
        self.settings[ "show_viz" ] = not self.settings[ "show_viz" ]
    
##### End of unique defs ######################################################
    
    def _update_script( self ):
        """ checks for updates to the script """
        import update
        updt = update.Update()
        del updt
            
    def _show_credits( self ):
        """ shows a credit window """
        import credits
        c = credits.GUI()
        c.doModal()
        del c

    def _check_for_restart( self ):
        """ checks for any changes that require a restart to take effect """
        restart = False
        for setting in self.settings_restart:
            if ( self.settings_original[ setting ] != self.settings[ setting ] ):
                restart = True
                break
        self._close_dialog( True, restart )

    def _close_dialog( self, changed=False, restart=False ):
        """ closes this dialog window """
        self.changed = changed
        self.restart = restart
        self.close()
        
    def onClick( self, controlId ):
        if ( controlId == 250 ):
            self._save_settings()
        elif ( controlId == 251 ):
            self._close_dialog()
        elif ( controlId == 252 ):
            self._update_script()
        elif ( controlId == 253 ):
            self._show_credits()
        else:
            if ( controlId == 201 ):
                self._change_setting1()
            elif ( controlId == 202 ):
                self._change_setting2()
            elif ( controlId == 203 ):
                self._change_setting3()
            elif ( controlId == 204 ):
                self._change_setting4()
            elif ( controlId == 205 ):
                self._change_setting5()
            self._set_controls_values()

    def onFocus( self, controlId ):
        pass
            
    def onAction( self, action ):
        if ( action.getButtonCode() in utilities.CANCEL_DIALOG ):
            self._close_dialog()
