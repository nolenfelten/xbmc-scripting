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
        self._parse_argv()
        self.get_videos()

    def _parse_argv( self ):
        # call _Info() with our formatted argv to create the constants
        exec "self.args = _Info(%s)" % ( sys.argv[ 2 ].replace( "?", "" ).replace( "=", "='" ).replace( "&", "', " ) + "'", )

    def get_videos( self ):
        try:
            # fetch trailers from database
            if ( self.args.genre_id == "-99" ):
                trailers = self._search_query()
            else:
                trailers = self._fetch_records( Query()[ "movies" ], ( int( self.args.genre_id ), ) )
            # concatenate actors
            trailers = self._parse_actors( trailers )
            # fill media list
            ok = self._fill_media_list( trailers )
        except:
            # oops print error message
            print sys.exc_info()[ 1 ]
            ok = False
        # send notification we're finished, successfully or unsuccessfully
        xbmcplugin.endOfDirectory( handle=int( sys.argv[ 1 ] ), succeeded=ok )

    def _parse_actors( self, trailers ):
        ftrailers = []
        idMovie = -1
        genre = ""
        # enumerate through the list of trailers, eliminating duplicates and adding the actors to the cast list
        for trailer in trailers:
            # if it's a new trailer convert the tuple to a list and add the actor as a cast list
            if ( trailer[ 0 ] != idMovie ):
                idMovie = trailer[ 0 ]
                ftrailers += [ list( trailer[ : 17 ] ) ]
                ftrailers[ -1 ] += [ [ trailer[ 17 ] ] ]
                genre = trailer[ 16 ]
            else:
                # if it's the same genre add the next actor to the cast list
                if ( genre == trailer[ 16 ] ):
                    ftrailers[ -1 ][ 17 ] += [ trailer[ 17 ] ]
                # if it's a new genre add the new genre to the genre string
                elif ( isinstance( trailer[ 16 ], basestring ) and trailer[ 16 ] not in ftrailers[ -1 ][ 16 ] ):
                    ftrailers[ -1 ][ 16] += " / %s" % trailer[ 16 ]
        return ftrailers

    def _fill_media_list( self, trailers ):
        try:
            ok = True
            # enumerate through the list of trailers and add the item to the media list
            for trailer in trailers:
                # if trailer was saved use this as the url
                if ( eval( trailer[ 13 ] ) ):
                    url = eval( trailer[ 13 ] )[ self._get_random_number( len( eval( trailer[ 13 ] ) ) ) ][ 0 ]
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
                    # get genre
                    if ( isinstance( trailer[ 16 ], int ) ):
                        genre = self.args.genre
                    else:
                        genre = trailer[ 16 ]
                    # set our overlay image
                    overlay = ( xbmcgui.ICON_OVERLAY_NONE, xbmcgui.ICON_OVERLAY_HD, )[ "720p.mov" in url or "1080p.mov" in url ]
                    # add the different infolabels we want to sort by
                    listitem.setInfo( type="Video", infoLabels={ "Overlay": overlay, "Cast": trailer[ 17 ], "Duration": trailer[ 6 ], "Studio": trailer[ 15 ], "Genre": genre, "MPAA": rating, "Plot": plot, "Title": trailer[ 1 ], "year": trailer[ 9 ] } )
                    # add the item to the media list
                    ok = xbmcplugin.addDirectoryItem( handle=int( sys.argv[ 1 ] ), url=url, listitem=listitem, totalItems=len(trailers) )
                    # if user cancels, call raise to exit loop
                    if ( not ok ): raise
        except:
            # user cancelled dialog or an error occurred
            print sys.exc_info()[ 1 ]
            ok = False
        # if successful and user did not cancel, add all the required sort methods
        if ( ok ):
            xbmcplugin.addSortMethod( handle=int( sys.argv[ 1 ] ), sortMethod=xbmcplugin.SORT_METHOD_LABEL )
            xbmcplugin.addSortMethod( handle=int( sys.argv[ 1 ] ), sortMethod=xbmcplugin.SORT_METHOD_MPAA_RATING )
            xbmcplugin.addSortMethod( handle=int( sys.argv[ 1 ] ), sortMethod=xbmcplugin.SORT_METHOD_VIDEO_RUNTIME )
            xbmcplugin.addSortMethod( handle=int( sys.argv[ 1 ] ), sortMethod=xbmcplugin.SORT_METHOD_VIDEO_YEAR )
            xbmcplugin.addSortMethod( handle=int( sys.argv[ 1 ] ), sortMethod=xbmcplugin.SORT_METHOD_STUDIO )
        return ok

    def _get_random_number( self, total ):
        return randrange( total )

    def _get_trailer_url( self, trailer_urls ):
        # pick a random url (only really applies to multiple urls)
        r = self._get_random_number( len( trailer_urls ) )
        url = ""
        # get intial choice
        choice = ( int( self.args.quality ), len( trailer_urls[ r ] ) - 1, )[ int( self.args.quality ) >= len( trailer_urls[ r ] ) ]
        # if quality is non progressive
        if ( int( self.args.quality ) <= 2 ):
            # select the correct non progressive trailer
            while ( trailer_urls[ r ][ choice ].endswith( "p.mov" ) and choice != -1 ): choice -= 1
        # quality is progressive
        else:
            # select the proper progressive quality
            quality = ( "480p", "720p", "1080p", )[ int( self.args.quality ) - 3 ]
            # select the correct progressive trailer
            while ( quality not in trailer_urls[ r ][ choice ] and trailer_urls[ r ][ choice ].endswith( "p.mov" ) and choice != -1 ): choice -= 1
        # if there was a valid trailer set it
        if ( choice >= 0 ):
            url = trailer_urls[ r ][ choice ]
        return url

    def _fetch_records( self, query, params=None ):
        records = Records()
        result = records.fetch( query, params )
        records.close()
        return result

    def _search_query( self ):
        try:
            trailers = []
            qv = self.get_keyboard( heading="Enter keywords: separate words with and/or/not" )
            xbmc.sleep(10)
            if ( qv ):
                keywords = qv.split()
                where = ""
                compare = False
                pattern = ( "LIKE '%%%s%%'", "regexp('\\b%s\\b')", )[ int( self.args.wholewords ) ]
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
                trailers = self._fetch_records( Query()[ "search" ] % ( where, ) )
        except:
            # oops print error message
            print sys.exc_info()[ 1 ]
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
            retval = None
        return retval


class Query( dict ):
    def __init__( self ):
        self[ "movies" ] = """
                                    SELECT DISTINCT movies.*, studios.studio, genre_link_movie.idGenre, actors.actor 
                                    FROM movies, genre_link_movie, studios, studio_link_movie, actors, actor_link_movie 
                                    WHERE genre_link_movie.idMovie=movies.idMovie 
                                    AND genre_link_movie.idGenre=? 
                                    AND movies.trailer_urls IS NOT NULL 
                                    AND movies.trailer_urls!='[]' 
                                    AND studio_link_movie.idMovie=movies.idMovie 
                                    AND studio_link_movie.idStudio=studios.idStudio 
                                    AND actor_link_movie.idMovie=movies.idMovie 
                                    AND actor_link_movie.idActor=actors.idActor 
                                    ORDER BY movies.title;
                                """

        self[ "search" ] = """
                                    SELECT DISTINCT movies.*, studios.studio, genre, actors.actor 
                                    FROM movies, genres, genre_link_movie, studios, studio_link_movie, actors, actor_link_movie 
                                    WHERE %s 
                                    AND movies.trailer_urls IS NOT NULL 
                                    AND movies.trailer_urls!='[]' 
                                    AND studio_link_movie.idMovie=movies.idMovie 
                                    AND studio_link_movie.idStudio=studios.idStudio 
                                    AND actor_link_movie.idMovie=movies.idMovie 
                                    AND actor_link_movie.idActor=actors.idActor 
                                    AND genre_link_movie.idMovie=movies.idMovie 
                                    AND genre_link_movie.idGenre=genres.idGenre 
                                    ORDER BY movies.title;
                                """ 
