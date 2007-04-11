"""
Settings module

Nuka1195
"""

import sys
import os
import xbmc
import xbmcgui

import guibuilder
import utilities

_ = sys.modules[ "__main__" ].__language__
__scriptname__ = sys.modules[ "__main__" ].__scriptname__
__version__ = sys.modules[ "__main__" ].__version__


class GUI( xbmcgui.WindowDialog ):
    """ Settings module: used for changing settings """
    def __init__( self, skin="Default" ):
        self.gui_loaded = self._load_gui( skin )
        if ( not self.gui_loaded ): self._close_dialog()
        else:
            self._set_variables()
            self._get_settings()
            self._setup_special()
            self._set_controls_values()
            self._set_restart_required()
            
    def _load_gui( self, skin ):
        """ sets up the gui using guibuilder """
        gb = guibuilder.GUIBuilder()
        ok, image_path = gb.create_gui( self, skin=skin, xml_name="settings", language=_ )
        return ok

    def _set_variables( self ):
        """ initializes variables """
        self.get_control( "Title Label" ).setLabel( sys.modules[ "__main__" ].__scriptname__ )
        self.get_control( "Version Label" ).setLabel( "%s: %s" % ( _( 1006 ), sys.modules[ "__main__" ].__version__, ) )
        # setEnabled( False ) if not used
        self.get_control( "Credits Button" ).setVisible( False )
        self.get_control( "Credits Button" ).setEnabled( False )

    def _get_settings( self ):
        """ reads settings """
        self.settings = utilities.Settings().get_settings()

    def _save_settings( self ):
        """ saves settings """
        ok = utilities.Settings().save_settings( self.settings )
        if ( not ok ):
            ok = xbmcgui.Dialog().ok( sys.modules[ "__main__" ].__scriptname__, _( 230 ) )
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
            self.get_control( "Setting1 Value" ).setLabel( self.scrapers_title[ self.current_scraper ] )
            self.get_control( "Setting2 Value" ).setSelected( self.settings[ "save_lyrics" ] )
            self.get_control( "Setting3 Button" ).setEnabled( self.settings[ "save_lyrics" ] )
            self.get_control( "Setting3 Value" ).setLabel( self.settings[ "lyrics_path" ] )
            self.get_control( "Setting3 Value" ).setEnabled( self.settings[ "save_lyrics" ] )
            self.get_control( "Setting4 Value" ).setSelected( self.settings[ "smooth_scrolling" ] )
            self.get_control( "Setting5 Value" ).setSelected( self.settings[ "show_viz" ] )
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
        if ( c.gui_loaded ): c.doModal()
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
        
    def get_control( self, key ):
        """ returns the control that matches the key """
        try: return self.controls[ key ][ "control" ]
        except: return None

    def onControl( self, control ):
        if ( control is self.get_control( "Ok Button" ) ):
            self._save_settings()
        elif ( control is self.get_control( "Cancel Button" ) ):
            self._close_dialog()
        elif ( control is self.get_control( "Update Button" ) ):
            self._update_script()
        elif ( control is self.get_control( "Credits Button" ) ):
            self._show_credits()
        else:
            if ( control is self.get_control( "Setting1 Button" ) ):
                self._change_setting1()
            elif ( control is self.get_control( "Setting2 Button" ) ):
                self._change_setting2()
            elif ( control is self.get_control( "Setting3 Button" ) ):
                self._change_setting3()
            elif ( control is self.get_control( "Setting4 Button" ) ):
                self._change_setting4()
            elif ( control is self.get_control( "Setting5 Button" ) ):
                self._change_setting5()
            self._set_controls_values()
            
    def onAction( self, action ):
        if ( action.getButtonCode() in utilities.CANCEL_DIALOG ):
            self._close_dialog()
