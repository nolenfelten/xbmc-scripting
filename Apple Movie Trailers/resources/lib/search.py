"""
Search module

Nuka1195
"""

import sys
import os
import xbmc
import xbmcgui

from utilities import *
import database

_ = sys.modules[ "__main__" ].__language__
__scriptname__ = sys.modules[ "__main__" ].__scriptname__
__version__ = sys.modules[ "__main__" ].__version__
__svn_revision__ = sys.modules[ "__main__" ].__svn_revision__


class GUI( xbmcgui.WindowXMLDialog ):
    """ Settings module: used for changing settings """
    CONTROL_GENRE_LIST = 100
    CONTROL_STUDIO_LIST = 110
    CONTROL_ACTOR_LIST = 120
    CONTROL_RATING_LIST = 130
    CONTROL_QUALITY_LIST = 140
    CONTROL_EXTRA_LIST = 150
    CONTROL_SQL_TEXTBOX = 75
    CONTROL_TITLE_LABEL = 20
    CONTROL_VERSION_LABEL = 30
    CONTROL_SQL_RESULTS_LABEL = 40
    CONTROL_BUTTONS = ( 250, 251, 257, 258, )
    CONTROL_LISTS = ( CONTROL_GENRE_LIST, CONTROL_STUDIO_LIST, CONTROL_ACTOR_LIST, CONTROL_RATING_LIST, CONTROL_QUALITY_LIST, CONTROL_EXTRA_LIST, )
    CONTROL_LISTS_NOT = ( CONTROL_GENRE_LIST + 2, CONTROL_STUDIO_LIST + 2, CONTROL_ACTOR_LIST + 2, CONTROL_RATING_LIST + 2, CONTROL_QUALITY_LIST + 2, CONTROL_EXTRA_LIST + 2, )

    def __init__( self, *args, **kwargs ):
        self.dialog = xbmcgui.DialogProgress()
        self.caps = kwargs[ "caps" ]
        self.dialog.create( _( 106 ), _( 97 ), _( 1005 ) )
        xbmcgui.lock()

    def onInit( self ):
        self._set_labels()
        self._clear_variables()
        self._set_functions()
        self._setup_special()
        xbmcgui.unlock()
        self.dialog.close()

    def _capitalize_text( self, text ):
        return ( text, text.upper(), )[ self.caps ]

    def _set_labels( self ):
        try:
            self.getControl( self.CONTROL_TITLE_LABEL ).setLabel( self._capitalize_text( __scriptname__ ) )
            self.getControl( self.CONTROL_VERSION_LABEL ).setLabel( self._capitalize_text( "%s: %s-%s" % ( _( 1006 ), __version__, __svn_revision__, ) ) )
            self.getControl( self.CONTROL_SQL_RESULTS_LABEL ).setLabel( self._capitalize_text( "%s:" % ( _( 93 ), ) ) )
            self.getControl( 102 ).setLabel( self._capitalize_text( _( 113 ) ) )
            self.getControl( 112 ).setLabel( self._capitalize_text( _( 114 ) ) )
            self.getControl( 122 ).setLabel( self._capitalize_text( _( 115 ) ) )
            self.getControl( 132 ).setLabel( self._capitalize_text( _( 116 ) ) )
            self.getControl( 142 ).setLabel( self._capitalize_text( _( 117 ) ) )
            self.getControl( 152 ).setLabel( self._capitalize_text( _( 118 ) ) )
            for button in self.CONTROL_BUTTONS:
                self.getControl( button ).setLabel( self._capitalize_text( _( button ) ) )
        except: pass

    def _set_functions( self ):
        self.functions = {}
        self.functions[ self.CONTROL_BUTTONS[ 0 ] ] = self._perform_search
        self.functions[ self.CONTROL_BUTTONS[ 1 ] ] = self._close_dialog
        self.functions[ self.CONTROL_BUTTONS[ 2 ] ] = self._save_sql
        self.functions[ self.CONTROL_BUTTONS[ 3 ] ] = self._clear_sql

    def _clear_variables( self ):
        self.query = ""
        self.query_genres = ""
        self.query_studios = ""
        self.query_actors = ""
        self.query_ratings = ""
        self.query_qualities = ""
        self.query_genres_not = False
        self.query_studios_not = False
        self.query_actors_not = False
        self.query_ratings_not = False
        self.query_qualities_not = False
        self.query_extras_not = False
        self.query_search_incomplete = ""
        self.query_search_favorites = ""
        self.query_search_saved = ""
        self.query_search_watched = ""

    def _setup_special( self ):
        """ calls any special defs """
        self._setup_trailer_quality()
        self._setup_categories()

    def _setup_categories( self ):
        query = database.Query()
        records = database.Records()
        self.genres = records.fetch( query[ "genre_category_list" ], all=True )
        self.studios = records.fetch( query[ "studio_category_list" ], all=True )
        self.actors = records.fetch( query[ "actor_category_list" ], all=True )
        self.ratings = [ ( _( 92 ), ) ]
        self.ratings += records.fetch( query[ "rating_category_list" ], all=True )
        records.close()
        self._get_custom_sql( True )

    def _fill_lists( self, fill=True, query="" ):
        for count, genre in enumerate( self.genres ):
            if ( fill ):
                self.getControl( self.CONTROL_GENRE_LIST ).addItem( self._capitalize_text( genre[ 1 ].replace( "Newest", _( 150 ) ).replace( "Exclusives", _( 151 ) ) ) )
            selected = ( "idGenre=%d\n" % genre[ 0 ] in query or "idGenre=%d)" % genre[ 0 ] in query or "idGenre!=%d\n" % genre[ 0 ] in query or "idGenre!=%d)" % genre[ 0 ] in query )
            self.getControl( self.CONTROL_GENRE_LIST ).getListItem( count ).select( selected )
        self.getControl( self.CONTROL_GENRE_LIST + 2 ).setSelected( "idGenre!=" in query )
        for count, studio in enumerate( self.studios ):
            if ( fill ):
                self.getControl( self.CONTROL_STUDIO_LIST ).addItem( self._capitalize_text( studio[ 1 ] ) )
            selected = ( "idStudio=%d\n" % studio[ 0 ] in query or "idStudio=%d)" % studio[ 0 ] in query or "idStudio!=%d\n" % studio[ 0 ] in query or "idStudio!=%d)" % studio[ 0 ] in query )
            self.getControl( self.CONTROL_STUDIO_LIST ).getListItem( count ).select( selected )
        self.getControl( self.CONTROL_STUDIO_LIST + 2 ).setSelected( "idStudio!=" in query )
        for count, actor in enumerate( self.actors ):
            if ( fill ):
                self.getControl( self.CONTROL_ACTOR_LIST ).addItem( self._capitalize_text( actor[ 1 ] ) )
            selected = ( "idActor=%d\n" % actor[ 0 ] in query or "idActor=%d)" % actor[ 0 ] in query or "idActor!=%d\n" % actor[ 0 ] in query or "idActor!=%d)" % actor[ 0 ] in query )
            self.getControl( self.CONTROL_ACTOR_LIST ).getListItem( count ).select( selected )
        self.getControl( self.CONTROL_ACTOR_LIST + 2 ).setSelected( "idActor!=" in query )
        for count, rating in enumerate( self.ratings ):
            if ( fill ):
                self.getControl( self.CONTROL_RATING_LIST ).addItem( self._capitalize_text( rating[ 0 ] ) )
            selected = ( "rating='%s'" % rating[ 0 ] in query or "rating!='%s'" % rating[ 0 ] in query )
            self.getControl( self.CONTROL_RATING_LIST ).getListItem( count ).select( selected )
        self.getControl( self.CONTROL_RATING_LIST + 2 ).setSelected( "rating!=" in query )
        for count, quality in enumerate( self.quality ):
            if ( fill ):
                self.getControl( self.CONTROL_QUALITY_LIST ).addItem( self._capitalize_text( quality ) )
            quality_text = ( "%320.mov%", "%480.mov%", "%640%.mov%", "%480p.mov%", "%720p.mov%", "%1080p.mov%", )[ count ]
            selected = "trailer_urls LIKE '%s'" % quality_text in query
            self.getControl( self.CONTROL_QUALITY_LIST ).getListItem( count ).select( selected )
        self.getControl( self.CONTROL_QUALITY_LIST + 2 ).setSelected( "NOT (movies.trailer_urls" in query )
        if ( fill ):
            self.getControl( self.CONTROL_EXTRA_LIST ).addItem( self._capitalize_text( _( 2150 ) ) )
        selected = ( query != "" and "trailer_urls IS NOT NULL" not in query )
        self.getControl( self.CONTROL_EXTRA_LIST ).getListItem( 0 ).select( selected )
        if ( fill ):
            self.getControl( self.CONTROL_EXTRA_LIST ).addItem( self._capitalize_text( _( 2151 ) ) )
        selected = "movies.favorite" in query
        self.getControl( self.CONTROL_EXTRA_LIST ).getListItem( 1 ).select( selected )
        if ( fill ):
            self.getControl( self.CONTROL_EXTRA_LIST ).addItem( self._capitalize_text( _( 2152 ) ) )
        selected = "saved_location" in query
        self.getControl( self.CONTROL_EXTRA_LIST ).getListItem( 2 ).select( selected )
        if ( fill ):
            self.getControl( self.CONTROL_EXTRA_LIST ).addItem( self._capitalize_text( _( 2153 ) ) )
        selected = "times_watched" in query
        self.getControl( self.CONTROL_EXTRA_LIST ).getListItem( 3 ).select( selected )
        self.getControl( self.CONTROL_EXTRA_LIST + 2 ).setSelected( "favorite!=" in query or "saved_location=" in query or "times_watched=" in query )
        if ( query ): self._create_sql( force_build=True )

    def _setup_trailer_quality( self ):
        self.quality = ( _( 2020 ), _( 2021 ), _( 2022 ), "480p", "720p", "1080p", )

    def _create_sql( self, controlId=-1, force_build=False ):
        # set genre selections
        if ( controlId in ( self.CONTROL_GENRE_LIST, self.CONTROL_GENRE_LIST + 2, ) or force_build ):
            genres = ""
            self.query_genres_not = self.getControl( self.CONTROL_GENRE_LIST + 2 ).getSelected()
            for pos, genre in enumerate( self.genres ):
                if ( self.getControl( self.CONTROL_GENRE_LIST ).getListItem( pos ).isSelected() ):
                    genres += "genre_link_movie.idGenre%s=%d\n %s " % ( ( "", "!", )[ self.query_genres_not ], genre[ 0 ], ( "OR", "AND", )[ self.query_genres_not ] )
            if ( genres ):
                genres = "(genre_link_movie.idMovie=movies.idMovie\n AND (%s))" % ( genres[ : -5 ].strip(), )
            self.query_genres = genres

        if ( controlId in ( self.CONTROL_STUDIO_LIST, self.CONTROL_STUDIO_LIST + 2, ) or force_build ):
            # set studio selections
            studios = ""
            self.query_studios_not = self.getControl( self.CONTROL_STUDIO_LIST + 2 ).getSelected()
            for pos, studio in enumerate( self.studios ):
                if ( self.getControl( self.CONTROL_STUDIO_LIST ).getListItem( pos ).isSelected() ):
                    studios += "studio_link_movie.idStudio%s=%d\n %s " % ( ( "", "!", )[ self.query_studios_not ], studio[ 0 ], ( "OR", "AND", )[ self.query_studios_not ] )
            if ( studios ):
                studios = "(studio_link_movie.idMovie=movies.idMovie\n AND (%s))" % ( studios[ : -5 ].strip(), )
            self.query_studios = studios

        if ( controlId in ( self.CONTROL_ACTOR_LIST, self.CONTROL_ACTOR_LIST + 2, ) or force_build ):
            # set actor selections
            actors = ""
            self.query_actors_not = self.getControl( self.CONTROL_ACTOR_LIST + 2 ).getSelected()
            for pos, actor in enumerate( self.actors ):
                if ( self.getControl( self.CONTROL_ACTOR_LIST ).getListItem( pos ).isSelected() ):
                    actors += "actor_link_movie.idActor%s=%d\n %s " % ( ( "", "!", )[ self.query_actors_not ], actor[ 0 ], ( "OR", "AND", )[ self.query_actors_not ] )
            if ( actors ):
                actors = "(actor_link_movie.idMovie=movies.idMovie\n AND (%s))" % ( actors[ : -5 ].strip(), )
            self.query_actors = actors

        if ( controlId in ( self.CONTROL_RATING_LIST, self.CONTROL_RATING_LIST + 2, ) or force_build ):
            # set rating selections
            ratings = ""
            self.query_ratings_not = self.getControl( self.CONTROL_RATING_LIST + 2 ).getSelected()
            for pos, rating in enumerate( self.ratings ):
                if ( self.getControl( self.CONTROL_RATING_LIST ).getListItem( pos ).isSelected() ):
                    ratings += "movies.rating%s='%s'\n %s " % ( ( "", "!", )[ self.query_ratings_not ], ( rating[ 0 ], "", )[ rating[ 0 ] == _( 92 ) ], ( "OR", "AND", )[ self.query_ratings_not ] )
            if ( ratings ):
                ratings = "(%s)" % ( ratings[ : -4 ].strip(), )
            self.query_ratings = ratings

        if ( controlId in ( self.CONTROL_QUALITY_LIST, self.CONTROL_QUALITY_LIST + 2, ) or force_build ):
            # set trailer quality selections
            qualities = ""
            self.query_qualities_not = self.getControl( self.CONTROL_QUALITY_LIST + 2 ).getSelected()
            for pos, quality in enumerate( self.quality ):
                if ( self.getControl( self.CONTROL_QUALITY_LIST ).getListItem( pos ).isSelected() ):
                    quality_text = ( "%320.mov%", "%480.mov%", "%640%.mov%", "%480p.mov%", "%720p.mov%", "%1080p.mov%", )[ pos ]
                    qualities += "movies.trailer_urls LIKE '%s'\n %s " % ( quality_text, ( "OR", "AND", )[ self.query_qualities_not ] )
            if ( qualities ):
                qualities = "%s(%s)" % ( ( "", "NOT ", )[ self.query_qualities_not ], qualities[ : -5 ].strip(), )
            self.query_qualities = qualities

        search_incomplete = ""
        if ( not self.getControl( self.CONTROL_EXTRA_LIST ).getListItem( 0 ).isSelected() ):
            search_incomplete = "\n AND movies.trailer_urls IS NOT NULL"
        self.query_search_incomplete = search_incomplete
        if ( controlId in ( self.CONTROL_EXTRA_LIST, self.CONTROL_EXTRA_LIST + 2, ) or force_build ):
            self.query_extras_not = self.getControl( self.CONTROL_EXTRA_LIST + 2 ).getSelected()
            # set extra settings selections
            search_favorites = ""
            if ( self.getControl( self.CONTROL_EXTRA_LIST ).getListItem( 1 ).isSelected() ):
                search_favorites = "\n AND movies.favorite%s=1" % ( ( "", "!", )[ self.query_extras_not ], )
            self.query_search_favorites = search_favorites
            search_saved = ""
            if ( self.getControl( self.CONTROL_EXTRA_LIST ).getListItem( 2 ).isSelected() ):
                search_saved = "\n AND movies.saved_location%s=''" % ( ( "!", "", )[ self.query_extras_not ], )
            self.query_search_saved = search_saved
            search_watched = ""
            if ( self.getControl( self.CONTROL_EXTRA_LIST ).getListItem( 3 ).isSelected() ):
                search_watched = "\n AND movies.times_watched%s0" % ( ( ">", "=", )[ self.query_extras_not ], )
            self.query_search_watched = search_watched

        self.query = ""
        if ( self.query_genres or self.query_studios or self.query_actors or self.query_ratings or self.query_qualities ):
            tables = "movies"
            where = ""
            if ( self.query_genres ):
                tables += ", genre_link_movie"
                where += self.query_genres
                where += "\n AND "
            if ( self.query_studios ):
                tables += ", studio_link_movie"
                where += self.query_studios
                where += "\n AND "
            if ( self.query_actors ):
                tables += ", actor_link_movie"
                where += self.query_actors
                where += "\n AND "
            if ( self.query_ratings ):
                where += self.query_ratings
                where += "\n AND "
            if ( self.query_qualities ):
                where += self.query_qualities
                where += "\n AND "
            where = "\n WHERE " + where[ : -6 ]
            self.query = "SELECT DISTINCT movies.*\n FROM " + tables + where
            self.query += self.query_search_incomplete + self.query_search_favorites + self.query_search_saved + self.query_search_watched
            self.query += "\n ORDER BY movies.title;"
        self._set_sql()
        if ( self.query ): self._run_sql()
            
    def _set_sql( self ):
        self.getControl( self.CONTROL_SQL_TEXTBOX ).reset()
        if ( not self.query ):
            self.getControl( self.CONTROL_SQL_TEXTBOX ).setText( self._capitalize_text( _( 94 ) ) )
        else:
            self.getControl( self.CONTROL_SQL_TEXTBOX ).setText( self._capitalize_text( self.query ) )
        self.getControl( self.CONTROL_BUTTONS[ 0 ] ).setEnabled( self.query != "" )
        self.getControl( self.CONTROL_BUTTONS[ 2 ] ).setEnabled( self.query != "" )
        self._enable_load_button()

    def _run_sql( self ):
        self.getControl( self.CONTROL_SQL_RESULTS_LABEL ).setLabel( self._capitalize_text( "%s: %s" % ( _( 93 ), _( 85 ),) ) )
        records = database.Records()
        trailers = records.fetch( self.query, all=True )
        records.close()
        self.getControl( self.CONTROL_SQL_RESULTS_LABEL ).setLabel( self._capitalize_text( "%s: %d" % ( _( 93 ), len( trailers ),) ) )

    def _clear_sql( self ):
        xbmcgui.lock()
        try:
            if ( self.query ):
                self._clear_variables()
                self._set_sql()
                self._fill_lists( False, self.query )
                self.getControl( self.CONTROL_SQL_RESULTS_LABEL ).setLabel( "%s:" % ( _( 93 ), ) )
            else: self._get_custom_sql()
            self._enable_load_button()
        except: pass
        xbmcgui.unlock()

    def _save_sql( self ):
        ok = save_custom_sql( self.query )

    def _get_custom_sql( self, fill=False ):
        xbmcgui.lock()
        try:
            self.query = get_custom_sql()
            self._set_sql()
            self._fill_lists( fill, self.query )
            if ( self.query ): self._run_sql()
        except: pass
        xbmcgui.unlock()

    def _enable_load_button( self ):
        label = ( os.path.isfile( os.path.join( BASE_DATA_PATH, "custom.sql" ) ) and self.query == "" )
        self.getControl( self.CONTROL_BUTTONS[ 3 ] ).setLabel( self._capitalize_text( _( 258 + label ) ) )

    def _perform_search( self ):
        self._close_dialog( self.query )

    def _close_dialog( self, query=None ):
        """ closes this dialog window """
        self.query = query
        self.close()

    def onClick( self, controlId ):
        if ( controlId in self.CONTROL_LISTS ):
            self.getControl( controlId ).getSelectedItem().select( not self.getControl( controlId ).getSelectedItem().isSelected() )
            self._create_sql( controlId )
        elif ( controlId in self.CONTROL_LISTS_NOT ):
            self._create_sql( controlId )
        elif ( controlId in self.CONTROL_BUTTONS ):
            self.functions[ controlId ]()

    def onFocus( self, controlId ):
        pass

    def onAction( self, action ):
        if ( action.getButtonCode() in CANCEL_DIALOG ):
            self._close_dialog()
