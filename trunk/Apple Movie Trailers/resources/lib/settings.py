import sys, os
import xbmc, xbmcgui
import guibuilder
import utilities
import chooser
import traceback

class GUI( xbmcgui.WindowDialog ):
    """ Settings module: used for changing settings """
    def __init__( self, *args, **kwargs ):
        try:
            self._ = kwargs[ "language" ]
            self.genres = kwargs[ "genres" ]
            self.skin = kwargs[ "skin" ]
            self.gui_loaded = self.setupGUI()
            if ( not self.gui_loaded ): self._close_dialog()
            else:
                self._set_variables()
                self._get_settings()
                self._setup_special()
                self._set_controls_values()
                self._set_restart_required()
                self.chooser = chooser.GUI( skin=self.skin )
        except: traceback.print_exc()
            
    def setupGUI( self ):
        """ sets up the gui using guibuilder """
        gb = guibuilder.GUIBuilder()
        ok, image_path = gb.create_gui( self, skin=self.skin, xml_name="settings", language=self._ )
        return ok

    def _set_variables( self ):
        """ initializes variables """
        self.controller_action = utilities.setControllerAction()
        self.get_control( "Title Label" ).setLabel( sys.modules[ "__main__" ].__scriptname__ )
        self.get_control( "Version Label" ).setLabel( "%s: %s" % ( self._( 1006 ), sys.modules[ "__main__" ].__version__, ) )
        # setEnabled( False ) if not used
        #self.get_control( "Credits Button" ).setVisible( False )
        #self.get_control( "Credits Button" ).setEnabled( False )

    def _get_settings( self ):
        """ reads settings """
        self.settings = utilities.Settings().get_settings()

    def _save_settings( self ):
        """ saves settings """
        ok = utilities.Settings().save_settings( self.settings )
        if ( not ok ):
            ok = xbmcgui.Dialog().ok( sys.modules[ "__main__" ].__scriptname__, self._( 230 ) )
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
           - 0 : ShowAndGetNumber
           - 1 : ShowAndGetDate
           - 2 : ShowAndGetTime
           - 3 : ShowAndGetIPAddress
        """
        dialog = xbmcgui.Dialog()
        value = dialog.numeric( type, heading )
        if ( value ): return value
        else: return default

    def _get_browse_dialog( self, default="", heading="", type=1, shares="files" ):
        """ shows a browse dialog and returns a value
            - 0 : ShowAndGetDirectory
            - 1 : ShowAndGetFile
            - 2 : ShowAndGetImage
            - 3 : ShowAndGetWriteableDirectory
        """
        dialog = xbmcgui.Dialog()
        value = dialog.browse( type, heading, shares )
        if ( value ): return value
        else: return default

##### Start of unique defs #####################################################

##### Special defs, script dependent, remember to call them from _setup_special #################
    
    def _set_restart_required( self ):
        """ copies self.settings and add any settings that require a restart on change """
        self.settings_original = self.settings.copy()
        self.settings_restart = ( "skin", )
    
    def _setup_special( self ):
        """ calls any special defs """
        self._setup_startup_categories()
        self._setup_thumbnail_display()
        self._setup_playback_mode()
        self._setup_trailer_quality()
        self._setup_skins()
        
    def _setup_startup_categories( self ):
        self.startup_categories = {}
        for count, genre in enumerate( self.genres ):
            self.startup_categories[ count ] = str( genre.title )
        self.startup_categories[ utilities.FAVORITES ] = self._( 217 )
        self.startup_categories[ utilities.DOWNLOADED ] = self._( 226 )
        
    def _setup_thumbnail_display( self ):
        self.thumbnail = ( self._( 310 ), self._( 311 ), self._( 312 ), )
        
    def _setup_playback_mode( self ):
        self.mode = ( self._( 330 ), self._( 331 ), "%s (videos)" % self._( 332 ), "%s (files)" % self._( 332 ), )
    
    def _setup_trailer_quality( self ):
        self.quality = ( self._( 320 ), self._( 321 ), self._( 322 ), )

    def _setup_skins( self ):
        """ special def for setting up scraper choices """
        self.skins = os.listdir( os.path.join( os.getcwd().replace( ";", "" ), "resources", "skins" ) )
        try: self.current_skin = self.skins.index( self.settings[ "skin" ] )
        except: self.current_skin = 0

###### End of Special defs #####################################################

    def _set_controls_values( self ):
        """ sets the value labels """
        #xbmcgui.lock()
        #self.controls["Skin Button Value"]["control"].setLabel( "%s" % ( self.settings.skin, ) )
        #self.controls["Trailer Quality Button Value"]["control"].setLabel( "%s" % ( self.quality[self.settings.trailer_quality], ) )
        #self.controls["Mode Button Value"]["control"].setLabel( "%s" % ( self.mode[self.settings[ "mode" ]], ) )
        #self.controls["Save Folder Button"]["control"].setEnabled( self.settings.mode >= 2 )
        #self.controls["Save Folder Button Value"]["control"].setLabel( "%s" % ( self.settings.save_folder, ) )
        #self.controls["Save Folder Button Value"]["control"].setEnabled( self.settings.mode >= 2 )
        #self.controls["Thumbnail Display Button Value"]["control"].setLabel( "%s" % ( self.thumbnail[self.settings.thumbnail_display], ) )
        #self.controls["Startup Category Button Value"]["control"].setLabel( "%s" % ( self.startup_categories[self.startup_category[0]][0], ) )
        #self.controls["Shortcut1 Button Value"]["control"].setLabel( "%s" % ( self.startup_categories[self.startup_category[1]][0], ) )
        #self.controls["Shortcut2 Button Value"]["control"].setLabel( "%s" % ( self.startup_categories[self.startup_category[2]][0], ) )
        #self.controls["Shortcut3 Button Value"]["control"].setLabel( "%s" % ( self.startup_categories[self.startup_category[3]][0], ) )
        try:
            self.get_control( "Setting1 Value" ).setLabel( self.settings[ "skin" ] )
            self.get_control( "Setting2 Value" ).setLabel( self.quality[ self.settings[ "trailer_quality" ] ] )
            self.get_control( "Setting3 Value" ).setLabel( self.mode[ self.settings[ "mode" ] ] )
            self.get_control( "Setting4 Value" ).setLabel( self.settings[ "save_folder" ] )
            self.get_control( "Setting4 Value" ).setEnabled( self.settings[ "mode" ] >= 2 )
            self.get_control( "Setting4 Button" ).setEnabled( self.settings[ "mode" ] >= 2 )
            self.get_control( "Setting5 Value" ).setLabel( self.thumbnail[ self.settings[ "thumbnail_display" ] ] )
            self.get_control( "Setting6 Value" ).setLabel( self.startup_categories[ self.settings[ "startup_category_id" ] ] )
            self.get_control( "Setting7 Value" ).setLabel( self.startup_categories[ self.settings[ "shortcut1" ] ] )
            self.get_control( "Setting8 Value" ).setLabel( self.startup_categories[ self.settings[ "shortcut2" ] ] )
            self.get_control( "Setting9 Value" ).setLabel( self.startup_categories[ self.settings[ "shortcut3" ] ] )
        except: traceback.print_exc()
        #xbmcgui.unlock()
    
    def _change_setting1( self ):
        """ changes settings #1 """
        if ( self.chooser.gui_loaded ):
            self.chooser.show_chooser( choices=self.skins, selection=self.current_skin, list_control=1 )
            if ( not self.chooser.selection is None ):
                self.current_skin = self.chooser.selection
                self.settings[ "skin" ] = self.skins[ self.current_skin ]

    def _change_setting2( self ):
        """ changes settings #2 """
        self.settings[ "trailer_quality" ] += 1
        if ( self.settings[ "trailer_quality" ] == len( self.quality ) ):
            self.settings[ "trailer_quality" ] = 0
        
    def _change_setting3( self ):
        """ changes settings #3 """
        self.settings[ "mode" ] += 1
        if ( self.settings[ "mode" ] == len( self.mode ) ):
            self.settings[ "mode" ] = 0

    def _change_setting4( self ):
        """ changes settings #4 """
        self.settings[ "lyrics_path" ] = self._get_browse_dialog( self.settings[ "lyrics_path" ], self._( 203 ) )
        
    def _change_setting5( self ):
        """ changes settings #5 """
        self.settings[ "show_viz" ] = not self.settings[ "show_viz" ]
    
##### End of unique defs ######################################################
    
    def _update_script( self ):
        """ checks for updates to the script """
        import update
        updt = update.Update( language=self._ )
        del updt
            
    def _show_credits( self ):
        """ shows a credit window """
        import credits
        c = credits.GUI( language=self._ )
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
            elif ( control is self.get_control( "Setting6 Button" ) ):
                self._change_setting6()
            elif ( control is self.get_control( "Setting7 Button" ) ):
                self._change_setting7()
            elif ( control is self.get_control( "Setting8 Button" ) ):
                self._change_setting8()
            elif ( control is self.get_control( "Setting9 Button" ) ):
                self._change_setting9()
            self._set_controls_values()
            
    def onAction( self, action ):
        button_key = self.controller_action.get( action.getButtonCode(), "n/a" )
        if ( button_key == "Keyboard Backspace Button" or button_key == "B Button" or button_key == "Remote Back Button" ):
            self._close_dialog()
        elif ( button_key == "Keyboard ESC Button" or button_key == "Back Button" or button_key == "Remote Menu Button" ):
            self._save_settings()
