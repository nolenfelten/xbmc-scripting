"""
Search module

Nuka1195
"""

import sys
import os
import xbmc
import xbmcgui
import traceback

from utilities import *
import database

_ = sys.modules[ "__main__" ].__language__
__scriptname__ = sys.modules[ "__main__" ].__scriptname__
__version__ = sys.modules[ "__main__" ].__version__


class GUI( xbmcgui.WindowXMLDialog ):
    """ Settings module: used for changing settings """
    CONTROL_GENRE_LIST = 100
    CONTROL_STUDIO_LIST = 110
    CONTROL_ACTOR_LIST = 120
    CONTROL_RATING_LIST = 130
    CONTROL_QUALITY_LIST = 140
    CONTROL_EXTRA_LIST = 150
    CONTROL_SQL_TEXTBOX = 75
    CONTROL_SQL_RESULTS_LABEL = 40
    CONTROL_BUTTONS = ( 250, 251, 257, 258, )
    
    def __init__( self, *args, **kwargs ):
        self.dialog = xbmcgui.DialogProgress()
        self.dialog.create("Search", "Setting up categories", "Please wait...")
        xbmcgui.lock()
        self.sql = ""

    def onInit( self ):
        try:
            self._get_settings()
            self._set_labels()
            self._setup_special()
            self._set_functions()
            self._set_sql()
            #self._set_controls_values()
        except: traceback.print_exc()
        xbmcgui.unlock()
        self.dialog.close()

    def _get_settings( self ):
        """ reads settings """
        self.settings = Settings().get_settings()

    def _set_labels( self ):
        try:
            self.getControl( 20 ).setLabel( __scriptname__ )
            self.getControl( 30 ).setLabel( "%s: %s" % ( _( 1006 ), __version__, ) )
            self.getControl( 40 ).setLabel( "%s:" % ( _( 93 ), ) )
            for button in self.CONTROL_BUTTONS:
                self.getControl( button ).setLabel( _( button ) )
        except: pass

    def _set_functions( self ):
        self.functions = {}
        self.functions[ self.CONTROL_BUTTONS[ 0 ] ] = self._perform_search
        self.functions[ self.CONTROL_BUTTONS[ 1 ] ] = self._close_dialog
        self.functions[ self.CONTROL_BUTTONS[ 2 ] ] = self._run_sql
        self.functions[ self.CONTROL_BUTTONS[ 3 ] ] = self._save_sql

##### Special defs, script dependent, remember to call them from _setup_special #################
    
    def _setup_special( self ):
        """ calls any special defs """
        self._setup_trailer_quality()
        self._setup_categories()

    def _setup_categories( self ):
        try:
            self.query = database.Query()
            records = database.Records()
            self.genres = records.fetch( self.query[ "genre_category_list" ], all=True )
            self.studios = records.fetch( self.query[ "studio_category_list" ], all=True )
            self.actors = records.fetch( self.query[ "actor_category_list" ], all=True )
            self.ratings = [ ( _( 92 ), ) ]
            self.ratings += records.fetch( self.query[ "rating_category_list" ], all=True )
            records.close()
            self.selected = {}
            self.selected[ self.CONTROL_GENRE_LIST ] = []
            for genre in self.genres:
                self.selected[ self.CONTROL_GENRE_LIST ] += [ False ]
                self.getControl( self.CONTROL_GENRE_LIST ).addItem( genre[ 1 ] )
            self.selected[ self.CONTROL_STUDIO_LIST ] = []
            for studio in self.studios:
                self.selected[ self.CONTROL_STUDIO_LIST ] += [ False ]
                self.getControl( self.CONTROL_STUDIO_LIST ).addItem( studio[ 1 ] )
            self.selected[ self.CONTROL_ACTOR_LIST ] = []
            for actor in self.actors:
                self.selected[ self.CONTROL_ACTOR_LIST ] += [ False ]
                self.getControl( self.CONTROL_ACTOR_LIST ).addItem( actor[ 1 ] )
            self.selected[ self.CONTROL_RATING_LIST ] = []
            for rating in self.ratings:
                self.selected[ self.CONTROL_RATING_LIST ] += [ False ]
                self.getControl( self.CONTROL_RATING_LIST ).addItem( rating[ 0 ] )
            self.selected[ self.CONTROL_QUALITY_LIST ] = []
            for quality in self.quality:
                self.selected[ self.CONTROL_QUALITY_LIST ] += [ False ]
                self.getControl( self.CONTROL_QUALITY_LIST ).addItem( quality )

            self.selected[ self.CONTROL_EXTRA_LIST ] = [ False ]
            self.getControl( self.CONTROL_EXTRA_LIST ).addItem( _( 2150 ) )
        except: traceback.print_exc()

    def _setup_trailer_quality( self ):
        self.quality = ( _( 2020 ), _( 2021 ), _( 2022 ), "480p", "720p", "1080p" )

    def _perform_search( self ):
        self._close_dialog( self.sql )

    def _run_sql( self ):
        records = database.Records()
        trailers = records.fetch( self.sql, all=True )
        records.close()
        self.getControl( self.CONTROL_SQL_RESULTS_LABEL ).setLabel( "%s: %d" % ( _( 93 ), len( trailers ),) )

    def _create_sql( self ):
        self.sql = ""
        tables = "movies"
        sql_set = False
        # set genre selections
        genres = ""
        for pos, genre in enumerate( self.genres ):
            if ( self.selected[ self.CONTROL_GENRE_LIST ][ pos ] ):
                genres += "genre_link_movie.idGenre=%d\n OR " % ( genre[ 0 ], )
        if ( genres ):
            genres = "(genre_link_movie.idMovie=movies.idMovie\n AND (" + genres[ : -5 ] + "))"
            tables += ", genre_link_movie"
            sql_set = True

        # set studio selections
        studios = ""
        for pos, studio in enumerate( self.studios ):
            if ( self.selected[ self.CONTROL_STUDIO_LIST ][ pos ] ):
                studios += "studio_link_movie.idStudio=%d\n OR " % ( studio[ 0 ], )
        if ( studios ):
            studios = "(studio_link_movie.idMovie=movies.idMovie\n AND (" + studios[ : -5 ] + "))"
            tables += ", studio_link_movie"
            sql_set = True

        # set actor selections
        actors = ""
        for pos, actor in enumerate( self.actors ):
            if ( self.selected[ self.CONTROL_ACTOR_LIST ][ pos ] ):
                actors += "actor_link_movie.idActor=%d\n OR " % ( actor[ 0 ], )
        if ( actors ):
            actors = "(actor_link_movie.idMovie=movies.idMovie\n AND (" + actors[ : -5 ] + "))"
            tables += ", actor_link_movie"
            sql_set = True

        # set rating selections
        ratings = ""
        for pos, rating in enumerate( self.ratings ):
            if ( self.selected[ self.CONTROL_RATING_LIST ][ pos ] ):
                ratings += "movies.rating='%s'\n OR " % ( ( rating[ 0 ], "", )[ rating[ 0 ] == _( 92 ) ], )
        if ( ratings ):
            ratings = "(" + ratings[ : -5 ] + ")"
            sql_set = True

        # set trailer quality selections
        qualities = ""
        for pos, quality in enumerate( self.quality ):
            if ( self.selected[ self.CONTROL_QUALITY_LIST ][ pos ] ):
                quality_text = ( "%320.mov%", "%480.mov%", "%640%.mov%", "%480p.mov%", "%720p.mov%", "%1080p.mov%", )[ pos ]
                qualities += "movies.trailer_urls LIKE '%s'\n OR " % ( quality_text, )
        if ( qualities ):
            qualities = "(" + qualities[ : -5 ] + ")"
            sql_set = True

        # set extra settings selections
        include_incomplete = ""
        if ( not self.selected[ self.CONTROL_EXTRA_LIST ][ 0 ] ):
            include_incomplete = "\n AND movies.trailer_urls IS NOT NULL"

        if ( sql_set ):
            self.sql = "SELECT DISTINCT movies.*\n FROM "
            self.sql += tables
            where = ""
            
            if ( genres ):
                where += genres
                where += "\n AND "
            if ( studios ):
                where += studios
                where += "\n AND "
            if ( actors ):
                where += actors
                where += "\n AND "
            if ( ratings ):
                where += ratings
                where += "\n AND "
            if ( qualities ):
                where += qualities
                where += "\n AND "

            if ( where ):
                where = "\n WHERE " + where[ : -6 ]
            
            self.sql += where + include_incomplete
            self.sql += "\n ORDER BY movies.title;"
        self._set_sql()
            
    def _set_sql( self ):
        self.getControl( self.CONTROL_SQL_TEXTBOX ).reset()
        if ( not self.sql ):
            self.getControl( self.CONTROL_SQL_TEXTBOX ).setText( "*No search set" )
        else:
            self.getControl( self.CONTROL_SQL_TEXTBOX ).setText( self.sql )
        self.getControl( self.CONTROL_BUTTONS[ 0 ] ).setEnabled( self.sql != "" )
        self.getControl( self.CONTROL_BUTTONS[ 2 ] ).setEnabled( self.sql != "" )
        self.getControl( self.CONTROL_BUTTONS[ 3 ] ).setEnabled( self.sql != "" )

    def _save_sql( self ):
        f = open( os.path.join( BASE_DATA_PATH, "sql.txt", "w" ) )
        f.write( self.sql )
        f.close()

    def _close_dialog( self, query=None ):
        """ closes this dialog window """
        self.query = query
        self.close()

    def onClick( self, controlId ):
        try:
            if ( controlId in ( self.CONTROL_GENRE_LIST, self.CONTROL_STUDIO_LIST, self.CONTROL_ACTOR_LIST, self.CONTROL_RATING_LIST, self.CONTROL_QUALITY_LIST, self.CONTROL_EXTRA_LIST, ) ):
                pos = self.getControl( controlId ).getSelectedPosition()
                self.selected[ controlId ][ pos ] = not self.selected[ controlId ][ pos ]
                self.getControl( controlId ).getSelectedItem().select( self.selected[ controlId ][ pos ] )
                self._create_sql()
            elif ( controlId in self.CONTROL_BUTTONS ):
                self.functions[ controlId ]()
        except: traceback.print_exc()

    def onFocus( self, controlId ):
        pass

    def onAction( self, action ):
        if ( action.getButtonCode() in CANCEL_DIALOG ):
            self._close_dialog()
