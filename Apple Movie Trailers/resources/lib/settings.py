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
import chooser
#import traceback


class GUI( xbmcgui.WindowDialog ):
    """ Settings module: used for changing settings """
    def __init__( self, skin="Default", language=None, genres=None ):
        try:
            self.chooser = None
            self.skin = skin
            self._ = language
            self.genres = genres
            self.gui_loaded = self._load_gui( skin )
            if ( not self.gui_loaded ): self._close_dialog()
            else:
                self._set_variables()
                self._get_settings()
                self._setup_special()
                self._set_controls_values()
                self._set_restart_required()
                ##self.chooser = chooser.GUI( skin=self.skin, language=self._ )
        except: pass#traceback.print_exc()
            
    def _load_gui( self, skin ):
        """ sets up the gui using guibuilder """
        gb = guibuilder.GUIBuilder()
        gui_loaded, image_path = gb.create_gui( self, skin=skin, xml_name="settings", language=self._ )
        return gui_loaded

    def _set_variables( self ):
        """ initializes variables """
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
        self.startup_titles = []
        for count, genre in enumerate( self.genres ):
            self.startup_categories[ count ] = str( genre.title )
        self.startup_categories[ utilities.FAVORITES ] = self._( 152 )
        self.startup_categories[ utilities.DOWNLOADED ] = self._( 153 )
        for title in self.startup_categories.values():
            self.startup_titles += [ title ]
        self.startup_titles.sort()
            

    def _setup_thumbnail_display( self ):
        self.thumbnail = ( self._( 2050 ), self._( 2051 ), self._( 2052 ), )
        
    def _setup_playback_mode( self ):
        self.mode = ( self._( 2030 ), self._( 2031 ), "%s (videos)" % self._( 2032 ), "%s (files)" % self._( 2032 ), )
    
    def _setup_trailer_quality( self ):
        self.quality = ( self._( 2020 ), self._( 2021 ), self._( 2022 ), )

    def _setup_skins( self ):
        """ special def for setting up scraper choices """
        self.skins = os.listdir( os.path.join( os.getcwd().replace( ";", "" ), "resources", "skins" ) )
        try: self.current_skin = self.skins.index( self.settings[ "skin" ] )
        except: self.current_skin = 0

###### End of Special defs #####################################################

    def _get_setting_from_category( self, category ):
        for key, value in self.startup_categories.items():
            if ( value == self.startup_titles[ category ] ):
                return key
        return 0
    
    def _get_category_from_setting( self, setting ):
        for count, value in enumerate( self.startup_titles ):
            if ( value == self.startup_categories[ setting ] ):
                return count
        return 0
        
    def _set_controls_values( self ):
        """ sets the value labels """
        xbmcgui.lock()
        try:
            self.get_control( "Setting1 Value" ).setLabel( self.settings[ "skin" ] )
            self.get_control( "Setting2 Value" ).setLabel( self.quality[ self.settings[ "trailer_quality" ] ] )
            self.get_control( "Setting3 Value" ).setLabel( self.mode[ self.settings[ "mode" ] ] )
            self.get_control( "Setting4 Value" ).setLabel( self.settings[ "save_folder" ] )
            self.get_control( "Setting4 Value" ).setEnabled( self.settings[ "mode" ] >= 1 )
            self.get_control( "Setting4 Button" ).setEnabled( self.settings[ "mode" ] >= 1 )
            self.get_control( "Setting5 Value" ).setLabel( self.thumbnail[ self.settings[ "thumbnail_display" ] ] )
            self.get_control( "Setting6 Value" ).setLabel( self.startup_categories[ self.settings[ "startup_category_id" ] ] )
            self.get_control( "Setting7 Value" ).setLabel( self.startup_categories[ self.settings[ "shortcut1" ] ] )
            self.get_control( "Setting8 Value" ).setLabel( self.startup_categories[ self.settings[ "shortcut2" ] ] )
            self.get_control( "Setting9 Value" ).setLabel( self.startup_categories[ self.settings[ "shortcut3" ] ] )
            self.get_control( "Setting10 Value" ).setSelected( self.settings[ "refresh_newest" ] )
        except: pass
        xbmcgui.unlock()
    
    def _change_setting1( self ):
        """ changes settings #1 """
        self.chooser.show_chooser( choices=self.skins, selection=self.current_skin, list_control=1, title="%s %s" % ( self._( 200 ), self._( 201 ) ) )
        if ( self.chooser.selection is not None ):
            self.current_skin = self.chooser.selection
            self.settings[ "skin" ] = self.skins[ self.current_skin ]
            
    def _change_setting2( self ):
        """ changes settings #2 """
        self.chooser.show_chooser( choices=self.quality, selection=self.settings[ "trailer_quality" ], list_control=2, title="%s %s" % ( self._( 200 ), self._( 202 ) ) )
        if ( self.chooser.selection is not None ):
            self.settings[ "trailer_quality" ] = self.chooser.selection
        
    def _change_setting3( self ):
        """ changes settings #3 """
        self.chooser.show_chooser( choices=self.mode, selection=self.settings[ "mode" ], list_control=2, title="%s %s" % ( self._( 200 ), self._( 203 ) ) )
        if ( self.chooser.selection is not None ):
            self.settings[ "mode" ] = self.chooser.selection
        
    def _change_setting4( self ):
        """ changes settings #4 """
        shares = [ "video", "files" ][ self.settings[ "mode" ] == 3 ]
        self.settings[ "save_folder" ] = self._get_browse_dialog( self.settings[ "save_folder" ], self._( 204 ), 3, shares )
        
    def _change_setting5( self ):
        """ changes settings #5 """
        self.chooser.show_chooser( choices=self.thumbnail, selection=self.settings[ "thumbnail_display" ], list_control=2, title="%s %s" % ( self._( 200 ), self._( 205 ) ) )
        if ( self.chooser.selection is not None ):
            self.settings[ "thumbnail_display" ] = self.chooser.selection
        
    def _change_setting6( self ):
        """ changes settings #6 """
        selection = self._get_category_from_setting( self.settings[ "startup_category_id" ] )
        self.chooser.show_chooser( choices=self.startup_titles, selection=selection, list_control=2, title="%s %s" % ( self._( 200 ), self._( 206 ) ) )
        if ( self.chooser.selection is not None ):
            self.settings[ "startup_category_id" ] = self._get_setting_from_category( self.chooser.selection )
        
    def _change_setting7( self ):
        """ changes settings #7 """
        selection = self._get_category_from_setting( self.settings[ "shortcut1" ] )
        self.chooser.show_chooser( choices=self.startup_titles, selection=selection, list_control=2, title="%s %s" % ( self._( 200 ), self._( 207 ) ) )
        if ( self.chooser.selection is not None ):
            self.settings[ "shortcut1" ] = self._get_setting_from_category( self.chooser.selection )
        
    def _change_setting8( self ):
        """ changes settings #8 """
        selection = self._get_category_from_setting( self.settings[ "shortcut2" ] )
        self.chooser.show_chooser( choices=self.startup_titles, selection=selection, list_control=2, title="%s %s" % ( self._( 200 ), self._( 208 ) ) )
        if ( self.chooser.selection is not None ):
            self.settings[ "shortcut2" ] = self._get_setting_from_category( self.chooser.selection )
        
    def _change_setting9( self ):
        """ changes settings #9 """
        selection = self._get_category_from_setting( self.settings[ "shortcut3" ] )
        self.chooser.show_chooser( choices=self.startup_titles, selection=selection, list_control=2, title="%s %s" % ( self._( 200 ), self._( 209 ) ) )
        if ( self.chooser.selection is not None ):
            self.settings[ "shortcut3" ] = self._get_setting_from_category( self.chooser.selection )

    def _change_setting10( self ):
        """ changes settings #10 """
        self.settings[ "refresh_newest" ] = not self.settings[ "refresh_newest" ]
    
##### End of unique defs ######################################################
    
    def _update_script( self ):
        """ checks for updates to the script """
        import update
        updt = update.Update( language=self._ )
        del updt
            
    def _show_credits( self ):
        """ shows a credit window """
        import credits
        c = credits.GUI( skin=self.skin, language=self._ )
        if ( c.gui_loaded ):
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
        ##if ( self.chooser is not None ): del self.chooser
        self.close()
        
    def get_control( self, key ):
        """ returns the control that matches the key """
        try: return self.controls[ key ][ "control" ]
        except: return None

    def onControl( self, control ):
        #xbmc.sleep( 5 )
        if ( control is self.get_control( "Ok Button" ) ):
            self._save_settings()
        elif ( control is self.get_control( "Cancel Button" ) ):
            self._close_dialog()
        elif ( control is self.get_control( "Update Button" ) ):
            self._update_script()
        elif ( control is self.get_control( "Credits Button" ) ):
            self._show_credits()
        else:
            self.chooser = chooser.GUI( skin=self.skin, language=self._ )
            if ( self.chooser.gui_loaded ):
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
                elif ( control is self.get_control( "Setting10 Button" ) ):
                    self._change_setting10()
                self._set_controls_values()
            del self.chooser

    def onAction( self, action ):
        if ( action.getButtonCode() in utilities.CANCEL_DIALOG ):
            self._close_dialog()
