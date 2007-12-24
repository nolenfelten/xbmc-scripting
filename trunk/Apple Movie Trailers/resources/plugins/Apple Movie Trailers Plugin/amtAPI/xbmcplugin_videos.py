"""
    Videos module: fetches a list of playable streams for a specific category
"""

# main imports
import sys
import os
import xbmc
import xbmcgui
import xbmcplugin

import re
from random import randrange

from pysqlite2 import dbapi2 as sqlite


class _Info:
    def __init__( self, *args, **kwargs ):
        self.__dict__.update( kwargs )


class Main:
    # base paths
    BASE_DATABASE_PATH = sys.modules[ "__main__" ].BASE_DATABASE_PATH
    BASE_DATA_PATH = xbmc.translatePath( os.path.join( "T:\\script_data", sys.modules[ "__main__" ].__script__ ) )

    def __init__( self ):
        self._get_settings()
        self._parse_argv()
        self.get_videos()

    def _parse_argv( self ):
        # call _Info() with our formatted argv to create the self.args object
        exec "self.args = _Info(%s)" % ( sys.argv[ 2 ][ 1 : ].replace( "&", ", " ), )

    def _get_settings( self ):
        self.settings = {}
        self.settings[ "quality" ] = int( xbmcplugin.getSetting( "quality" ) )
        self.settings[ "only_hd" ] = xbmcplugin.getSetting( "only_hd" ) == "true"
        self.settings[ "play_all" ] = xbmcplugin.getSetting( "play_all" ) == "true"
        self.settings[ "rating" ] = int( xbmcplugin.getSetting( "rating" ) )
        self.settings[ "mode" ] = int( xbmcplugin.getSetting( "mode" ) )
        self.settings[ "download_path" ] = xbmcplugin.getSetting( "download_path" )
        self.settings[ "whole_words" ] = xbmcplugin.getSetting( "whole_words" ) == "true"

    def get_videos( self ):
        try:
            # fetch trailers from database
            if ( self.args.genre_id == -99 ):
                trailers = self._search_query()
            else:
                trailers = self._genre_query()
            # fill media list
            ok = self._fill_media_list( trailers )
            # set content
            if (ok): xbmcplugin.setContent( handle=int( sys.argv[ 1 ] ), content="movies" )
        except:
            # oops print error message
            print sys.exc_info()[ 1 ]
            ok = False
        # send notification we're finished, successfully or unsuccessfully
        xbmcplugin.endOfDirectory( handle=int( sys.argv[ 1 ] ), succeeded=ok )

    def _parse_extra_info( self, records ):
        if ( not records ): return self.args.genre, "", []
        genre = ""
        studio = records[ 0 ][ 1 ]
        cast = []
        for record in records:
            if ( record[ 0 ] not in genre ):
                genre += record[ 0 ] + " / "
            if ( record[ 2 ] not in cast ):
                cast += [ record[ 2 ] ]
        genre = genre[ : -3 ]
        return genre, studio, cast

    def _fill_media_list( self, trailers ):
        try:
            records = Records()
            ok = True
            # enumerate through the list of trailers and add the item to the media list
            for trailer in trailers:
                # if trailer was saved use this as the url
                if ( eval( trailer[ 13 ] ) ):
                    url = self._get_trailer_url( eval( trailer[ 13 ] ), True )
                else:
                    # select the correct trailer quality.
                    url = self._get_trailer_url( eval( trailer[ 3 ] ) )
                if ( url ):
                    # check for a valid thumbnail
                    thumbnail = ""
                    if ( trailer[ 4 ] and trailer[ 4 ] is not None ):
                        thumbnail = os.path.join( self.BASE_DATA_PATH, ".cache", trailer[ 4 ][ 0 ], trailer[ 4 ] )
                    # set the default icon
                    icon = "DefaultVideo.png"
                    # if a rating exists format it
                    rating = ( "", "[%s]" % trailer[ 7 ], )[ trailer[ 7 ] != "" ]
                    # if a plot does not exist, use a default message
                    plot = ( "No synopsis provided by the studio.", trailer[ 5 ], )[ trailer[ 5 ] != "" ]
                    # only need to add label, icon and thumbnail, setInfo() and addSortMethod() takes care of label2
                    listitem = xbmcgui.ListItem( trailer[ 1 ], rating, iconImage=icon, thumbnailImage=thumbnail )
                    # fetch extra info
                    result = records.fetch( Query()[ "extra" ], ( trailer[ 0 ], ) )
                    # parse information
                    genre, studio, cast = self._parse_extra_info( result )
                    # set watched status
                    watched = trailer[ 10 ] > 0
                    # set an overlay if one is practical
                    overlay = ( xbmcgui.ICON_OVERLAY_NONE, xbmcgui.ICON_OVERLAY_HD, )[ "720p.mov" in url or "1080p.mov" in url ]
                    overlay = ( overlay, xbmcgui.ICON_OVERLAY_WATCHED, )[ watched ]
                    # add the different infolabels we want to sort by
                    listitem.setInfo( type="Video", infoLabels={ "Watched": watched, "Overlay": overlay, "Duration": trailer[ 6 ], "MPAA": rating, "Plot": plot, "Plotoutline": plot, "Title": trailer[ 1 ], "year": trailer[ 9 ], "Genre": genre, "Studio": studio, "Cast": cast } )
                    # add the item to the media list
                    ok = xbmcplugin.addDirectoryItem( handle=int( sys.argv[ 1 ] ), url=url, listitem=listitem, totalItems=len(trailers) )
                    # if user cancels, call raise to exit loop
                    if ( not ok ): raise
        except:
            # user cancelled dialog or an error occurred
            print sys.exc_info()[ 1 ]
            ok = False
        records.close()
        # if successful and user did not cancel, add all the required sort methods
        if ( ok ):
            xbmcplugin.addSortMethod( handle=int( sys.argv[ 1 ] ), sortMethod=xbmcplugin.SORT_METHOD_LABEL )
            xbmcplugin.addSortMethod( handle=int( sys.argv[ 1 ] ), sortMethod=xbmcplugin.SORT_METHOD_MPAA_RATING )
            xbmcplugin.addSortMethod( handle=int( sys.argv[ 1 ] ), sortMethod=xbmcplugin.SORT_METHOD_VIDEO_RUNTIME )
            xbmcplugin.addSortMethod( handle=int( sys.argv[ 1 ] ), sortMethod=xbmcplugin.SORT_METHOD_VIDEO_YEAR )
            xbmcplugin.addSortMethod( handle=int( sys.argv[ 1 ] ), sortMethod=xbmcplugin.SORT_METHOD_STUDIO )
        return ok

    def _get_trailer_url( self, trailer_urls, saved=False ):
        # pick a random url (only really applies to multiple urls)
        rnd = randrange( len( trailer_urls ) )
        total = rnd + 1
        url = ""
        if ( self.settings[ "play_all" ] and len( trailer_urls ) > 1 ):
            rnd = 0
            total = len( trailer_urls )
        for count in range( rnd, total ):
            if ( saved ):
                url += trailer_urls[ count ][ 0 ] + " , "
            else:
                # get intial choice
                choice = ( self.settings[ "quality" ], len( trailer_urls[ count ] ) - 1, )[ self.settings[ "quality" ] >= len( trailer_urls[ count ] ) ]
                # if quality is non progressive
                if ( self.settings[ "quality" ] <= 2 ):
                    # select the correct non progressive trailer
                    while ( trailer_urls[ count ][ choice ].endswith( "p.mov" ) and choice != -1 ): choice -= 1
                # quality is progressive
                else:
                    # select the proper progressive quality
                    quality = ( "480p", "720p", "1080p", )[ self.settings[ "quality" ] - 3 ]
                    # select the correct progressive trailer
                    while ( quality not in trailer_urls[ count ][ choice ] and trailer_urls[ count ][ choice ].endswith( "p.mov" ) and choice != -1 ): choice -= 1
                # if there was a valid trailer set it
                if ( choice >= 0 and ( not self.settings[ "only_hd" ] or self.settings[ "quality" ] < 4 or ( self.settings[ "only_hd" ] and self.settings[ "quality" ] > 3 and ( "720p.mov" in trailer_urls[ count ][ choice ] or "1080p.mov" in trailer_urls[ count ][ choice ] ) ) ) ):
                    url += trailer_urls[ count ][ choice ] + " , "
        if ( url.endswith( " , " ) ):
            url = url[ : -3 ]
            if ( url and self.settings[ "play_all" ] and " , " in url ):
                url = "stack://" + url
        if ( url and self.settings[ "mode" ] > 0 ):
            url = '%s?download_url="""%s"""' % ( sys.argv[ 0 ], url, )
        return url

    def _fetch_records( self, query, params=None ):
        records = Records()
        result = records.fetch( query, params )
        records.close()
        return result

    def _genre_query( self ):
        trailers = self._fetch_records( Query()[ "movies" ] % self._get_limits(), ( self.args.genre_id, ) )
        return trailers

    def _get_limits( self ):
        # HD sql statement
        hd_sql = ( "", "AND (movies.trailer_urls LIKE '%720p.mov%' OR movies.trailer_urls LIKE '%1080p.mov%')", )[ self.settings[ "only_hd" ] and ( self.settings[ "quality" ] > 3 ) ]
        # mpaa ratings
        mpaa_ratings = [ "G", "PG", "PG-13", "R", "NC-17" ]
        rating_sql = ""
        # if the user set a valid rating add all up to the selection
        if ( self.settings[ "rating" ] < len( mpaa_ratings ) ):
            user_rating = mpaa_ratings[ self.settings[ "rating" ] ]
            rating_sql = "AND ("
            # enumerate through mpaa ratings and add the selected ones to our sql statement
            for rating in mpaa_ratings:
                rating_sql += "rating='%s' OR " % ( rating, )
                # if we found the users choice, we're finished
                if ( rating == user_rating ): break
            # fix the sql statement
            rating_sql = rating_sql[ : -4 ] + ") "
        return ( hd_sql, rating_sql, )

    def _search_query( self ):
        trailers = []
        qv = self.get_keyboard( heading="Enter keywords: separate words with and/or/not" )
        xbmc.sleep(10)
        if ( qv ):
            keywords = qv.split()
            where = ""
            compare = False
            pattern = ( "LIKE '%%%s%%'", "regexp('\\b%s\\b')", )[ self.settings[ "whole_words" ] ]
            for word in keywords:
                if ( word.upper() == "AND" or word.upper() == "OR" ):
                    where += " %s " % word.upper()
                    compare = False
                    continue
                elif ( word.upper() == "NOT" ):
                    where += "NOT "
                    continue
                elif ( compare ):
                    where += " AND "
                    compare = False
                where += "(title %s OR " % ( pattern % ( word, ), )
                where += "plot %s OR " % ( pattern % ( word, ), )
                where += "actor %s OR " % ( pattern % ( word, ), )
                where += "studio %s OR " % ( pattern % ( word, ), )
                where += "genre %s)" % ( pattern % ( word, ), )
                compare = True
            trailers = self._fetch_records( Query()[ "search" ] % ( ( where, ) + self._get_limits() ), )
        return trailers

    def get_keyboard( self, default="", heading="", hidden=False ):
        """ shows a keyboard and returns a value """
        keyboard = xbmc.Keyboard( default, heading, hidden )
        keyboard.doModal()
        if ( keyboard.isConfirmed() ):
            return keyboard.getText()
        return default

class Records:
    # base paths
    BASE_DATABASE_PATH = sys.modules[ "__main__" ].BASE_DATABASE_PATH

    def __init__( self, *args, **kwargs ):
        self.connect()

    def connect( self ):
        self.db = sqlite.connect( os.path.join( self.BASE_DATABASE_PATH, "AMT.db" ) )
        self.db.create_function( "regexp", 2, self.regexp )
        self.cursor = self.db.cursor()
    
    def regexp( self, pattern, item ):
        return re.search( pattern, item, re.IGNORECASE ) is not None

    def close( self ):
        self.db.close()
    
    def fetch( self, sql, params=None ):
        try:
            if ( params is not None ): self.cursor.execute( sql, params )
            else: self.cursor.execute( sql )
            retval = self.cursor.fetchall()
        except:
            # oops print error message
            print sys.exc_info()[ 1 ]
            retval = []
        return retval


class Query( dict ):
    def __init__( self ):
        self[ "extra" ] = """
                                    SELECT genres.genre, studios.studio, actors.actor 
                                    FROM movies, genres, genre_link_movie, studios, studio_link_movie, actors, actor_link_movie 
                                    WHERE movies.idMovie=? 
                                    AND studio_link_movie.idMovie=movies.idMovie 
                                    AND studio_link_movie.idStudio=studios.idStudio 
                                    AND actor_link_movie.idMovie=movies.idMovie 
                                    AND actor_link_movie.idActor=actors.idActor 
                                    AND genre_link_movie.idMovie=movies.idMovie 
                                    AND genre_link_movie.idGenre=genres.idGenre;
                                """

        self[ "movies" ] = """
                                    SELECT movies.* 
                                    FROM movies, genre_link_movie
                                    WHERE genre_link_movie.idMovie=movies.idMovie 
                                    AND genre_link_movie.idGenre=? 
                                    AND movies.trailer_urls IS NOT NULL 
                                    AND movies.trailer_urls!='[]' 
                                    %s
                                    %s;
                                """

        self[ "search" ] = """
                                    SELECT DISTINCT movies.*
                                    FROM movies, genres, genre_link_movie, studios, studio_link_movie, actors, actor_link_movie 
                                    WHERE %s 
                                    AND movies.trailer_urls IS NOT NULL 
                                    AND movies.trailer_urls!='[]' 
                                    %s
                                    %s
                                    AND studio_link_movie.idMovie=movies.idMovie 
                                    AND studio_link_movie.idStudio=studios.idStudio 
                                    AND actor_link_movie.idMovie=movies.idMovie 
                                    AND actor_link_movie.idActor=actors.idActor 
                                    AND genre_link_movie.idMovie=movies.idMovie 
                                    AND genre_link_movie.idGenre=genres.idGenre;
                                """ 
