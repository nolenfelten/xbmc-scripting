"""
Settings module

Nuka1195
"""

import sys
import os
import xbmc
import xbmcgui

from utilities import *
import chooser

_ = sys.modules[ "__main__" ].__language__
__scriptname__ = sys.modules[ "__main__" ].__scriptname__
__version__ = sys.modules[ "__main__" ].__version__
__svn_revision__ = sys.modules[ "__main__" ].__svn_revision__


class GUI( xbmcgui.WindowXMLDialog ):
    """ Settings module: used for changing settings """
    def __init__( self, *args, **kwargs ):
        xbmcgui.WindowXMLDialog.__init__( self, *args, **kwargs )
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

    def _get_settings( self, defaults=False ):
        """ reads settings """
        self.settings = Settings().get_settings( defaults=defaults )

    def _set_labels( self ):
        try:
            self.getControl( 20 ).setLabel( __scriptname__ )
            self.getControl( 30 ).setLabel( "%s: %s-%s" % ( _( 1006 ), __version__, __svn_revision__, ) )
            self.getControl( 250 ).setLabel( _( 250 ) )
            self.getControl( 251 ).setLabel( _( 251 ) )
            self.getControl( 252 ).setLabel( _( 252 ) )
            self.getControl( 253 ).setLabel( _( 253 ) )
            self.getControl( 254 ).setLabel( _( 254 ) )
            self.getControl( 255 ).setLabel( _( 255 ) )
            ## setEnabled( False ) if not used
            #self.getControl( 253 ).setVisible( False )
            #self.getControl( 253 ).setEnabled( False )
            #for x in range( 1, len( self.settings ) ):
            #    self.getControl( 200 + x ).setLabel( _( 200 + x ) )
        except: pass

    def _set_functions( self ):
        self.functions = {}
        self.functions[ 250 ] = self._save_settings
        self.functions[ 251 ] = self._close_dialog
        self.functions[ 252 ] = self._update_script
        self.functions[ 253 ] = self._show_credits
        self.functions[ 254 ] = self._install_plugin
        self.functions[ 255 ] = self._get_defaults
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
        self._setup_showtimes_scrapers()

    def _setup_startup_categories( self ):
        self.startup_categories = {}
        self.startup_titles = []
        for count, genre in enumerate( self.genres ):
            self.startup_categories[ count ] = genre.title.replace( "Newest", _( 150 ) ).replace( "Exclusives", _( 151 ) )
        self.startup_categories[ FAVORITES ] = _( 152 )
        self.startup_categories[ DOWNLOADED ] = _( 153 )
        self.startup_categories[ HD_TRAILERS ] = _( 160 )
        self.startup_categories[ NO_TRAILER_URLS ] = _( 161 )
        self.startup_categories[ CUSTOM_SEARCH ] = _( 162 )
        self.startup_categories[ WATCHED ] = _( 163 )
        self.startup_categories[ RECENTLY_ADDED ] = _( 164 )
        self.startup_categories[ MULTIPLE_TRAILERS ] = _( 165 )
        for title in self.startup_categories.values():
            self.startup_titles += [ title ]
        self.startup_titles.sort()

    def _setup_thumbnail_display( self ):
        self.thumbnail = ( _( 2050 ), _( 2051 ), _( 2052 ), )
        
    def _setup_playback_mode( self ):
        self.mode = ( _( 2030 ), _( 2031 ), "%s (%s)" % ( _( 2032 ), _( 84 ), ), "%s (%s)" % ( _( 2032 ), _( 86 ), ), )
    
    def _setup_trailer_quality( self ):
        self.quality = ( _( 2020 ), _( 2021 ), _( 2022 ), "480p", "720p", "1080p" )

    def _setup_skins( self ):
        """ special def for setting up scraper choices """
        self.skins = os.listdir( os.path.join( os.getcwd().replace( ";", "" ), "resources", "skins" ) )
        try: self.current_skin = self.skins.index( self.settings[ "skin" ] )
        except: self.current_skin = 0

    def _setup_showtimes_scrapers( self ):
        """ special def for setting up scraper choices """
        self.showtimes_scrapers = os.listdir( os.path.join( os.getcwd().replace( ";", "" ), "resources", "showtimes_scrapers" ) )
        try: self.current_showtimes_scraper = self.showtimes_scrapers.index( self.settings[ "showtimes_scraper" ] )
        except: self.current_showtimes_scraper = 0

    def _setup_videoplayer( self ):
        self.videoplayer_displayresolutions = ( "1080i 16x9", "720p 16x9", "480p 4x3", "480p 16x9", "NTSC 4x3", "NTSC 16x9", "PAL 4x3", "PAL 16x9", "PAL60 4x3", "PAL60 16x9", _( 2110 ) )

    def _set_restart_required( self ):
        """ copies self.settings and adds any settings that require a restart on change """
        self.settings_original = self.settings.copy()
        self.settings_restart = ( "skin", "showtimes_scraper" )
        self.settings_refresh = ( "thumbnail_display", "fade_thumb", )

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
            self.getControl( 201 ).setLabel( _( 201 ), label2=self.settings[ "skin" ] )
            self.getControl( 202 ).setLabel( _( 202 ), label2=self.quality[ self.settings[ "trailer_quality" ] ] )
            self.getControl( 203 ).setLabel( _( 203 ), label2=self.mode[ self.settings[ "mode" ] ] )
            self.getControl( 204 ).setLabel( _( 204 ), label2=self.settings[ "save_folder" ] )
            self.getControl( 204 ).setEnabled( self.settings[ "mode" ] >= 1 )
            self.getControl( 205 ).setLabel( _( 205 ) )
            self.getControl( 205 ).setSelected( self.settings[ "auto_play_all" ] )
            self.getControl( 206 ).setLabel( _( 206 ), label2=self.thumbnail[ self.settings[ "thumbnail_display" ] ] )
            self.getControl( 207 ).setLabel( _( 207 ) )
            self.getControl( 207 ).setSelected( self.settings[ "fade_thumb" ] )
            self.getControl( 207 ).setEnabled( self.settings[ "thumbnail_display" ] == 0 )
            self.getControl( 208 ).setLabel( _( 208 ), label2=self.startup_categories[ self.settings[ "startup_category_id" ] ] )
            self.getControl( 209 ).setLabel( _( 209 ), label2=self.startup_categories[ self.settings[ "shortcut1" ] ] )
            self.getControl( 210 ).setLabel( _( 210 ), label2=self.startup_categories[ self.settings[ "shortcut2" ] ] )
            self.getControl( 211 ).setLabel( _( 211 ), label2=self.startup_categories[ self.settings[ "shortcut3" ] ] )
            self.getControl( 212 ).setLabel( _( 212 ) )
            self.getControl( 212 ).setSelected( self.settings[ "refresh_newest" ] )
            self.getControl( 213 ).setLabel( _( 213 ) )
            self.getControl( 213 ).setSelected( self.settings[ "use_simple_search" ] )
            self.getControl( 214 ).setLabel( _( 214 ) )
            self.getControl( 214 ).setSelected( self.settings[ "match_whole_words" ] )
            self.getControl( 214 ).setEnabled( self.settings[ "use_simple_search" ] )
            self.getControl( 215 ).setLabel( _( 215 ), label2=self.videoplayer_displayresolutions[ self.settings[ "videoplayer_displayresolution" ] ] )
            self.getControl( 216 ).setLabel( _( 216 ), label2= self.settings[ "showtimes_local" ] )
            self.getControl( 217 ).setLabel( _( 217 ), label2=self.settings[ "showtimes_scraper" ] )
            self.getControl( 218 ).setLabel( _( 218 ) )
            self.getControl( 218 ).setSelected( self.settings[ "refresh_trailers" ] )
            self.getControl( 250 ).setEnabled( self.settings_original != self.settings )
        except:
            pass
        xbmcgui.unlock()

    def _change_setting1( self ):
        """ changes settings #1 """
        try: original_selection = self.skins.index( self.settings_original[ "skin" ] )
        except: original_selection = 0
        selection = self._get_chooser( self.skins, original_selection, self.current_skin, 0, "%s %s" % ( _( 200 ), _( self.controlId ), ) )
        if ( selection is not None ):
            self.current_skin = selection
            self.settings[ "skin" ] = self.skins[ self.current_skin ]
            self._set_controls_values()

    def _change_setting2( self ):
        """ changes settings #2 """
        selection = self._get_chooser( self.quality, self.settings_original[ "trailer_quality" ], self.settings[ "trailer_quality" ], 1, "%s %s" % ( _( 200 ), _( self.controlId ), ) )
        if ( selection is not None ):
            self.settings[ "trailer_quality" ] = selection
            self._set_controls_values()

    def _change_setting3( self ):
        """ changes settings #3 """
        selection = self._get_chooser( self.mode, self.settings_original[ "mode" ], self.settings[ "mode" ], 1, "%s %s" % ( _( 200 ), _( self.controlId ), ) )
        if ( selection is not None ):
            self.settings[ "mode" ] = selection
            self._set_controls_values()

    def _change_setting4( self ):
        """ changes settings #4 """
        shares = [ "video", "files" ][ self.settings[ "mode" ] == 3 ]
        self.settings[ "save_folder" ] = get_browse_dialog( self.settings[ "save_folder" ], _( self.controlId ), 3, shares )
        self._set_controls_values()

    def _change_setting5( self ):
        """ changes settings #5 """
        self.settings[ "auto_play_all" ] = not self.settings[ "auto_play_all" ]
        self._set_controls_values()

    def _change_setting6( self ):
        """ changes settings #6 """
        selection = self._get_chooser( self.thumbnail, self.settings_original[ "thumbnail_display" ], self.settings[ "thumbnail_display" ], 1, "%s %s" % ( _( 200 ), _( self.controlId ), ) )
        if ( selection is not None ):
            self.settings[ "thumbnail_display" ] = selection
            self._set_controls_values()

    def _change_setting7( self ):
        """ changes settings #7 """
        self.settings[ "fade_thumb" ] = not self.settings[ "fade_thumb" ]
        self._set_controls_values()
    
    def _change_setting8( self ):
        """ changes settings #8 """
        selection = self._get_category_from_setting( self.settings[ "startup_category_id" ] )
        original_selection = self._get_category_from_setting( self.settings_original[ "startup_category_id" ] )
        selection = self._get_chooser( self.startup_titles, original_selection, selection, 1, "%s %s" % ( _( 200 ), _( self.controlId ), ) )
        if ( selection is not None ):
            self.settings[ "startup_category_id" ] = self._get_setting_from_category( selection )
            self._set_controls_values()

    def _change_setting9( self ):
        """ changes settings #9 """
        selection = self._get_category_from_setting( self.settings[ "shortcut1" ] )
        original_selection = self._get_category_from_setting( self.settings_original[ "shortcut1" ] )
        selection = self._get_chooser( self.startup_titles, original_selection, selection, 1, "%s %s" % ( _( 200 ), _( self.controlId ), ) )
        if ( selection is not None ):
            self.settings[ "shortcut1" ] = self._get_setting_from_category( selection )
            self._set_controls_values()

    def _change_setting10( self ):
        """ changes settings #10 """
        selection = self._get_category_from_setting( self.settings[ "shortcut2" ] )
        original_selection = self._get_category_from_setting( self.settings_original[ "shortcut2" ] )
        selection = self._get_chooser( self.startup_titles, original_selection, selection, 1, "%s %s" % ( _( 200 ), _( self.controlId ), ) )
        if ( selection is not None ):
            self.settings[ "shortcut2" ] = self._get_setting_from_category( selection )
            self._set_controls_values()

    def _change_setting11( self ):
        """ changes settings #11 """
        selection = self._get_category_from_setting( self.settings[ "shortcut3" ] )
        original_selection = self._get_category_from_setting( self.settings_original[ "shortcut3" ] )
        selection = self._get_chooser( self.startup_titles, original_selection, selection, 1, "%s %s" % ( _( 200 ), _( self.controlId ), ) )
        if ( selection is not None ):
            self.settings[ "shortcut3" ] = self._get_setting_from_category( selection )
            self._set_controls_values()

    def _change_setting12( self ):
        """ changes settings #12 """
        self.settings[ "refresh_newest" ] = not self.settings[ "refresh_newest" ]
        self._set_controls_values()

    def _change_setting13( self ):
        """ changes settings #13 """
        self.settings[ "use_simple_search" ] = not self.settings[ "use_simple_search" ]
        self._set_controls_values()

    def _change_setting14( self ):
        """ changes settings #14 """
        self.settings[ "match_whole_words" ] = not self.settings[ "match_whole_words" ]
        self._set_controls_values()

    def _change_setting15( self ):
        """ changes settings #15 """
        selection = self._get_chooser( self.videoplayer_displayresolutions, self.settings_original[ "videoplayer_displayresolution" ], self.settings[ "videoplayer_displayresolution" ], 1, "%s %s" % ( _( 200 ), _( self.controlId ), ) )
        if ( selection is not None ):
            self.settings[ "videoplayer_displayresolution" ] = selection
            self._set_controls_values()

    def _change_setting16( self ):
        """ changes settings #16 """
        self.settings[ "showtimes_local" ] = get_keyboard( self.settings[ "showtimes_local" ], _( self.controlId ) )
        self._set_controls_values()

    def _change_setting17( self ):
        """ changes settings #17 """
        try: original_selection = self.showtimes_scrapers.index( self.settings_original[ "showtimes_scraper" ] )
        except: original_selection = 0
        selection = self._get_chooser( self.showtimes_scrapers, original_selection, self.current_showtimes_scraper, 1, "%s %s" % ( _( 200 ), _( self.controlId ), ) )
        if ( selection is not None ):
            self.current_showtimes_scraper = selection
            self.settings[ "showtimes_scraper" ] = self.showtimes_scrapers[ self.current_showtimes_scraper ]
            self._set_controls_values()

    def _change_setting18( self ):
        """ changes settings #18 """
        self.settings[ "refresh_trailers" ] = not self.settings[ "refresh_trailers" ]
        self._set_controls_values()

    def _install_plugin( self ):
        selection = self._get_chooser( ( _( 700 ), _( 704 ), ), -1, 0, 1, "%s %s" % ( _( 200 ), _( 713 ), ) )
        if ( selection is not None ):
            install_plugin( selection )

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
        del c

    def _get_defaults( self ):
        """ resets values to defaults """
        self._get_settings( defaults=True )
        self._set_controls_values()

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
        xbmc.sleep( 5 )
        self.controlId = self.getFocusId()

    def onAction( self, action ):
        if ( action in ACTION_CANCEL_DIALOG ):
            self._close_dialog()
