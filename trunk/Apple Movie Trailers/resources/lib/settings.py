"""
Settings module

Nuka1195
"""

import sys
import os
import xbmc
import xbmcgui
#import traceback

from utilities import *
import chooser

_ = sys.modules[ "__main__" ].__language__
__scriptname__ = sys.modules[ "__main__" ].__scriptname__
__version__ = sys.modules[ "__main__" ].__version__


class GUI( xbmcgui.WindowXMLDialog ):
    """ Settings module: used for changing settings """
    def __init__( self, *args, **kwargs ):
        xbmcgui.lock()
        self.genres = kwargs[ "genres" ]
        self.skin = kwargs[ "skin" ]

    def onInit( self ):
        self._get_settings()
        self._set_labels()
        self._set_functions()
        self._setup_special()
        self._set_restart_required()
        self._set_controls_values()
        xbmcgui.unlock()

    def _get_settings( self ):
        """ reads settings """
        self.settings = Settings().get_settings()

    def _set_labels( self ):
        try:
            self.getControl( 20 ).setLabel( __scriptname__ )
            self.getControl( 30 ).setLabel( "%s: %s" % ( _( 1006 ), __version__, ) )
            self.getControl( 250 ).setLabel( _( 250 ) )
            self.getControl( 251 ).setLabel( _( 251 ) )
            self.getControl( 252 ).setLabel( _( 252 ) )
            self.getControl( 253 ).setLabel( _( 253 ) )
            ## setEnabled( False ) if not used
            #self.getControl( 253 ).setVisible( False )
            #self.getControl( 253 ).setEnabled( False )
            for x in range( 1, len( self.settings ) ):
                self.getControl( 200 + x ).setLabel( _( 200 + x ) )
        except: pass

    def _set_functions( self ):
        self.functions = {}
        self.functions[ 250 ] = self._save_settings
        self.functions[ 251 ] = self._close_dialog
        self.functions[ 252 ] = self._update_script
        self.functions[ 253 ] = self._show_credits
        for x in range( 1, len( self.settings ) ):
            self.functions[ 200 + x ] = eval( "self._change_setting%d" % x )

##### Special defs, script dependent, remember to call them from _setup_special #################
    
    def _setup_special( self ):
        """ calls any special defs """
        self._setup_startup_categories()
        self._setup_thumbnail_display()
        self._setup_playback_mode()
        self._setup_trailer_quality()
        self._setup_skins()
        self._setup_videoplayer()
        
    def _setup_startup_categories( self ):
        self.startup_categories = {}
        self.startup_titles = []
        for count, genre in enumerate( self.genres ):
            self.startup_categories[ count ] = str( genre.title )
        self.startup_categories[ FAVORITES ] = _( 152 )
        self.startup_categories[ DOWNLOADED ] = _( 153 )
        self.startup_categories[ HD_TRAILERS ] = _( 160 )
        for title in self.startup_categories.values():
            self.startup_titles += [ title ]
        self.startup_titles.sort()

    def _setup_thumbnail_display( self ):
        self.thumbnail = ( _( 2050 ), _( 2051 ), _( 2052 ), )
        
    def _setup_playback_mode( self ):
        self.mode = ( _( 2030 ), _( 2031 ), "%s (videos)" % _( 2032 ), "%s (files)" % _( 2032 ), )
    
    def _setup_trailer_quality( self ):
        self.quality = ( _( 2020 ), _( 2021 ), _( 2022 ), "480p", "720p", "1080p" )

    def _setup_skins( self ):
        """ special def for setting up scraper choices """
        self.skins = os.listdir( os.path.join( os.getcwd().replace( ";", "" ), "resources", "skins" ) )
        try: self.current_skin = self.skins.index( self.settings[ "skin" ] )
        except: self.current_skin = 0

    def _set_restart_required( self ):
        """ copies self.settings and adds any settings that require a restart on change """
        self.settings_original = self.settings.copy()
        self.settings_restart = ( "skin", )
        self.settings_refresh = ( "thumbnail_display", "fade_thumb", )

    def _setup_videoplayer( self ):
        self.videoplayer_displayresolutions = ( "1080i 16x9", "720p 16x9", "480p 4x3", "480p 16x9", "NTSC 4x3", "NTSC 16x9", "PAL 4x3", "PAL 16x9", "PAL60 4x3", "PAL60 16x9", _( 2110 ) )

###### End of Special defs #####################################################
    def _get_chooser( self, choices, original, selection, list_control, title ):
        force_fallback = self.skin != "Default"
        ch = chooser.GUI( "script-%s-chooser.xml" % ( __scriptname__.replace( " ", "_" ), ), BASE_RESOURCE_PATH, self.skin, force_fallback, choices=choices, original=original, selection=selection, list_control=list_control, title=title )
        selection = ch.selection
        del ch
        return selection

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
            self.getControl( 221 ).setLabel( self.settings[ "skin" ] )
            self.getControl( 222 ).setLabel( self.quality[ self.settings[ "trailer_quality" ] ] )
            self.getControl( 223 ).setLabel( self.mode[ self.settings[ "mode" ] ] )
            self.getControl( 224 ).setLabel( self.settings[ "save_folder" ] )
            self.getControl( 224 ).setEnabled( self.settings[ "mode" ] >= 1 )
            self.getControl( 204 ).setEnabled( self.settings[ "mode" ] >= 1 )
            self.getControl( 225 ).setLabel( self.thumbnail[ self.settings[ "thumbnail_display" ] ] )
            self.getControl( 226 ).setSelected( self.settings[ "fade_thumb" ] )
            self.getControl( 226 ).setEnabled( self.settings[ "thumbnail_display" ] == 0 )
            self.getControl( 206 ).setEnabled( self.settings[ "thumbnail_display" ] == 0 )
            self.getControl( 227 ).setLabel( self.startup_categories[ self.settings[ "startup_category_id" ] ] )
            self.getControl( 228 ).setLabel( self.startup_categories[ self.settings[ "shortcut1" ] ] )
            self.getControl( 229 ).setLabel( self.startup_categories[ self.settings[ "shortcut2" ] ] )
            self.getControl( 230 ).setLabel( self.startup_categories[ self.settings[ "shortcut3" ] ] )
            self.getControl( 231 ).setSelected( self.settings[ "refresh_newest" ] )
            self.getControl( 232 ).setLabel( self.videoplayer_displayresolutions[ self.settings[ "videoplayer_displayresolution" ] ] )
            self.getControl( 250 ).setEnabled( self.settings_original != self.settings )
        except: pass
        xbmcgui.unlock()

    def _change_setting1( self ):
        """ changes settings #1 """
        try: original_selection = self.skins.index( self.settings_original[ "skin" ] )
        except: original_selection = 0
        selection = self._get_chooser( self.skins, original_selection, self.current_skin, 0, "%s %s" % ( _( 200 ), _( 201 ), ) )
        if ( selection is not None ):
            self.current_skin = selection
            self.settings[ "skin" ] = self.skins[ self.current_skin ]
            self._set_controls_values()

    def _change_setting2( self ):
        """ changes settings #2 """
        selection = self._get_chooser( self.quality, self.settings_original[ "trailer_quality" ], self.settings[ "trailer_quality" ], 1, "%s %s" % ( _( 200 ), _( 202 ), ) )
        if ( selection is not None ):
            self.settings[ "trailer_quality" ] = selection
            self._set_controls_values()

    def _change_setting3( self ):
        """ changes settings #3 """
        selection = self._get_chooser( self.mode, self.settings_original[ "mode" ], self.settings[ "mode" ], 1, "%s %s" % ( _( 200 ), _( 203 ), ) )
        if ( selection is not None ):
            self.settings[ "mode" ] = selection
            self._set_controls_values()

    def _change_setting4( self ):
        """ changes settings #4 """
        shares = [ "video", "files" ][ self.settings[ "mode" ] == 3 ]
        self.settings[ "save_folder" ] = get_browse_dialog( self.settings[ "save_folder" ], _( 204 ), 3, shares )
        self._set_controls_values()

    def _change_setting5( self ):
        """ changes settings #5 """
        selection = self._get_chooser( self.thumbnail, self.settings_original[ "thumbnail_display" ], self.settings[ "thumbnail_display" ], 1, "%s %s" % ( _( 200 ), _( 205 ), ) )
        if ( selection is not None ):
            self.settings[ "thumbnail_display" ] = selection
            self._set_controls_values()

    def _change_setting6( self ):
        """ changes settings #6 """
        self.settings[ "fade_thumb" ] = not self.settings[ "fade_thumb" ]
        self._set_controls_values()
    
    def _change_setting7( self ):
        """ changes settings #7 """
        selection = self._get_category_from_setting( self.settings[ "startup_category_id" ] )
        original_selection = self._get_category_from_setting( self.settings_original[ "startup_category_id" ] )
        selection = self._get_chooser( self.startup_titles, original_selection, selection, 1, "%s %s" % ( _( 200 ), _( 206 ), ) )
        if ( selection is not None ):
            self.settings[ "startup_category_id" ] = self._get_setting_from_category( selection )
            self._set_controls_values()

    def _change_setting8( self ):
        """ changes settings #8 """
        selection = self._get_category_from_setting( self.settings[ "shortcut1" ] )
        original_selection = self._get_category_from_setting( self.settings_original[ "shortcut1" ] )
        selection = self._get_chooser( self.startup_titles, original_selection, selection, 1, "%s %s" % ( _( 200 ), _( 207 ), ) )
        if ( selection is not None ):
            self.settings[ "shortcut1" ] = self._get_setting_from_category( selection )
            self._set_controls_values()

    def _change_setting9( self ):
        """ changes settings #9 """
        selection = self._get_category_from_setting( self.settings[ "shortcut2" ] )
        original_selection = self._get_category_from_setting( self.settings_original[ "shortcut2" ] )
        selection = self._get_chooser( self.startup_titles, original_selection, selection, 1, "%s %s" % ( _( 200 ), _( 208 ), ) )
        if ( selection is not None ):
            self.settings[ "shortcut2" ] = self._get_setting_from_category( selection )
            self._set_controls_values()

    def _change_setting10( self ):
        """ changes settings #10 """
        selection = self._get_category_from_setting( self.settings[ "shortcut3" ] )
        original_selection = self._get_category_from_setting( self.settings_original[ "shortcut3" ] )
        selection = self._get_chooser( self.startup_titles, original_selection, selection, 1, "%s %s" % ( _( 200 ), _( 209 ), ) )
        if ( selection is not None ):
            self.settings[ "shortcut3" ] = self._get_setting_from_category( selection )
            self._set_controls_values()

    def _change_setting11( self ):
        """ changes settings #11 """
        self.settings[ "refresh_newest" ] = not self.settings[ "refresh_newest" ]
        self._set_controls_values()

    def _change_setting12( self ):
        """ changes settings #12 """
        selection = self._get_chooser( self.videoplayer_displayresolutions, self.settings_original[ "videoplayer_displayresolution" ], self.settings[ "videoplayer_displayresolution" ], 1, "%s %s" % ( _( 200 ), _( 211 ), ) )
        if ( selection is not None ):
            self.settings[ "videoplayer_displayresolution" ] = selection
            self._set_controls_values()

##### End of unique defs ######################################################
    
    def _save_settings( self ):
        """ saves settings """
        ok = Settings().save_settings( self.settings )
        if ( not ok ):
            ok = xbmcgui.Dialog().ok( __scriptname__, _( 230 ) )
        else:
            self._check_for_restart()

    def _check_for_restart( self ):
        """ checks for any changes that require a restart to take effect """
        restart = False
        refresh = False
        for setting in self.settings_restart:
            if ( self.settings_original[ setting ] != self.settings[ setting ] ):
                restart = True
                break
        for setting in self.settings_refresh:
            if ( self.settings_original[ setting ] != self.settings[ setting ] ):
                refresh = True
                break
        self._close_dialog( True, restart, refresh )
    
    def _update_script( self ):
        """ checks for updates to the script """
        import update
        updt = update.Update()
        del updt

    def _show_credits( self ):
        """ shows a credit window """
        import credits
        force_fallback = self.skin != "Default"
        c = credits.GUI( "script-%s-credits.xml" % ( __scriptname__.replace( " ", "_" ), ), BASE_RESOURCE_PATH, self.skin, force_fallback )
        c.doModal()
        del c

    def _close_dialog( self, changed=False, restart=False, refresh=False ):
        """ closes this dialog window """
        self.changed = changed
        self.restart = restart
        self.refresh = refresh
        self.close()

    def onClick( self, controlId ):
        #xbmc.sleep(5)
        self.functions[ controlId ]()

    def onFocus( self, controlId ):
        pass

    def onAction( self, action ):
        if ( action.getButtonCode() in CANCEL_DIALOG ):
            self._close_dialog()