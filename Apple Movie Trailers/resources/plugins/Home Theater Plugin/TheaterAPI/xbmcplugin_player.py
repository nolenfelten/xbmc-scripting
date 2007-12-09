"""
    Movie Theater: Module plays:
    - # of optional coming attraction videos
    - # of random trailers
    - # of optional feature presentation videos
    - selected video
    - # of optional end of presentation videos
"""

import xbmc
# set our title
g_title = unicode( xbmc.getInfoLabel( "ListItem.Title" ), "utf-8" )
# set our studio (only works if the user is using the video library)
g_studio = unicode( xbmc.getInfoLabel( "ListItem.Studio" ), "utf-8" )
# set our director (only works if the user is using the video library)
g_director = unicode( xbmc.getInfoLabel( "ListItem.Director" ), "utf-8" )
# set our genre (only works if the user is using the video library)
g_genre = unicode( xbmc.getInfoLabel( "ListItem.Genre" ), "utf-8" )
# set our rating (only works if the user is using the video library)
g_mpaa_rating = xbmc.getInfoLabel( "ListItem.MPAA" )
# set our thumbnail
g_thumbnail = xbmc.getInfoImage( "ListItem.Thumb" )
# set our plotoutline
g_plotoutline = unicode( xbmc.getInfoLabel( "ListItem.PlotOutline" ), "utf-8" )
# set our year
g_year = 0
if ( xbmc.getInfoLabel( "ListItem.Year" ) ):
    g_year = int( xbmc.getInfoLabel( "ListItem.Year" ) )
# set our rating
g_rating = 0.0
if ( xbmc.getInfoLabel( "ListItem.Rating" ) ):
    g_rating = float( xbmc.getInfoLabel( "ListItem.Rating" ) )

# create the progress dialog (we do it here so there is minimal delay with nothing displayed)
import xbmcgui
pDialog = xbmcgui.DialogProgress()
pDialog.create( "Movie Theater Plugin", "Choosing random trailers..." )

# main imports
import sys
import os
import xbmcplugin

from random import randrange

from pysqlite2 import dbapi2 as sqlite


class _Info:
    def __init__( self, *args, **kwargs ):
        self.__dict__.update( kwargs )


class Main:
    # base paths
    BASE_CACHE_PATH = os.path.join( "P:\\Thumbnails", "Video" )
    BASE_DATA_PATH = xbmc.translatePath( os.path.join( "T:\\script_data", sys.modules[ "__main__" ].__script__ ) )

    def __init__( self ):
        self._get_settings()
        self._parse_argv()
        # create the playlist
        playlist = self._create_playlist()
        # play the videos
        self._play_videos( playlist )

    def _get_settings( self ):
        self.settings = {}
        self.settings[ "limit_query" ] = xbmcplugin.getSetting( "limit_query" ) == "true"
        self.settings[ "rating" ] = int( xbmcplugin.getSetting( "rating" ) )
        self.settings[ "number_trailers" ] = int( xbmcplugin.getSetting( "number_trailers" ) )
        self.settings[ "quality" ] = int( xbmcplugin.getSetting( "quality" ) )
        self.settings[ "only_hd" ] = xbmcplugin.getSetting( "only_hd" ) == "true"
        self.settings[ "coming_attraction_videos" ] = []
        if ( xbmcplugin.getSetting( "coming_attraction_videos1" ) ):
            self.settings[ "coming_attraction_videos" ] += [ xbmcplugin.getSetting( "coming_attraction_videos1" ) ]
        if ( xbmcplugin.getSetting( "coming_attraction_videos2" ) ):
            self.settings[ "coming_attraction_videos" ] += [ xbmcplugin.getSetting( "coming_attraction_videos2" ) ]
        self.settings[ "feature_presentation_videos" ] = []
        if ( xbmcplugin.getSetting( "feature_presentation_videos1" ) ):
            self.settings[ "feature_presentation_videos" ] += [ xbmcplugin.getSetting( "feature_presentation_videos1" ) ]
        if ( xbmcplugin.getSetting( "feature_presentation_videos2" ) ):
            self.settings[ "feature_presentation_videos" ] += [ xbmcplugin.getSetting( "feature_presentation_videos2" ) ]
        self.settings[ "end_presentation_videos" ] = []
        if ( xbmcplugin.getSetting( "end_presentation_videos1" ) ):
            self.settings[ "end_presentation_videos" ] += [ xbmcplugin.getSetting( "end_presentation_videos1" ) ]
        if ( xbmcplugin.getSetting( "end_presentation_videos2" ) ):
            self.settings[ "end_presentation_videos" ] += [ xbmcplugin.getSetting( "end_presentation_videos2" ) ]

    def _parse_argv( self ):
        # call _Info() with our formatted argv to create the self.args object
        exec "self.args = _Info(%s)" % ( sys.argv[ 2 ][ 1 : ].replace( "&", ", " ), )
        # backslashes cause issues when passed in the url
        self.args.path = self.args.path.replace( "[[BACKSLASH]]", "\\" )

    def _create_playlist( self ):
        # create a video playlist
        playlist = xbmc.PlayList( xbmc.PLAYLIST_VIDEO )
        # clear any possible items
        playlist.clear()
        # if there is a trailer intro video add it
        if ( self.settings[ "coming_attraction_videos" ] ):
            for path in self.settings[ "coming_attraction_videos" ]:
                # create our trailer record
                trailer = ( path, os.path.splitext( os.path.basename( unicode( path, "utf-8" ) ) )[ 0 ], "", path, "", "", "", "", "", 0, "", "", "", "", "", "", "Coming Attractions Intro", 0.0, "", )
                # create the listitem and fill the infolabels
                listitem = self._get_listitem( trailer )
                # add our item to the playlist
                playlist.add( unicode( path, "utf-8" ), listitem )
        # fetch our random trailers
        trailers = self._fetch_records()
        # enumerate through our list of trailers and add them to our playlist
        for trailer in trailers:
            # we need to select the proper trailer url
            url = self._get_trailer_url( eval( trailer[ 3 ] ) )
            # add a false rating
            trailer += ( 0.0, )
            # create the listitem and fill the infolabels
            listitem = self._get_listitem( trailer + ( "", ) )
            # add our item to the playlist
            playlist.add( url, listitem )
        # if there is a movie intro video add it
        if ( self.settings[ "feature_presentation_videos" ] ):
            for path in self.settings[ "feature_presentation_videos" ]:
                # create our trailer record
                trailer = ( path, os.path.splitext( os.path.basename( unicode( path, "utf-8" ) ) )[ 0 ], "", path, "", "", "", "", "", 0, "", "", "", "", "", "", "Feature Presentation Intro", 0.0, "", )
                # create the listitem and fill the infolabels
                listitem = self._get_listitem( trailer )
                # add our item to the playlist
                playlist.add( unicode( path, "utf-8" ), listitem )
        # set the genre if missing
        genre = g_genre
        if ( not g_genre ):
            genre = "Feature Presentation"
        # add the selected video to our playlist
        trailer = ( sys.argv[ 0 ] + sys.argv[ 2 ], g_title, "", self.args.path, g_thumbnail, g_plotoutline, "", "", "", g_year, "", "", "", "", "", g_studio, genre, g_rating, g_director, )
        # create the listitem and fill the infolabels
        listitem = self._get_listitem( trailer )
        # add our item to the playlist
        playlist.add( unicode( self.args.path, "utf-8" ), listitem )
        # if there is a end of movie video add it
        if ( self.settings[ "end_presentation_videos" ] ):
            for path in self.settings[ "end_presentation_videos" ]:
                # create our trailer record
                trailer = ( path, os.path.splitext( os.path.basename( unicode( path, "utf-8" ) ) )[ 0 ], "", path, "", "", "", 0, "", 0, "", "", "", "", "", "", "End of Feature Presentation", 0.0, "", )
                # create the listitem and fill the infolabels
                listitem = self._get_listitem( trailer )
                # add our item to the playlist
                playlist.add( unicode( path, "utf-8" ), listitem )
        return playlist

    def _play_videos( self, playlist ):
        pDialog.close()
        if ( playlist and not pDialog.iscanceled() ):
            xbmc.Player().play( playlist )

    def _fetch_records( self ):
        try:
            records = Records()
            # select only trailers with valid trailer urls
            sql = """
                        SELECT movies.*, studios.studio, genres.genre  
                        FROM movies, genres, genre_link_movie, studios, studio_link_movie 
                        WHERE movies.trailer_urls IS NOT NULL 
                        AND movies.trailer_urls!='[]' 
                        %s
                        %s
                        AND genre_link_movie.idMovie=movies.idMovie 
                        AND genre_link_movie.idGenre=genres.idGenre 
                        AND studio_link_movie.idMovie=movies.idMovie 
                        AND studio_link_movie.idStudio=studios.idStudio 
                        %s
                        ORDER BY RANDOM() 
                        LIMIT %d;
                    """
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
            hd_sql = ( "", "AND (movies.trailer_urls LIKE '%720p.mov%' OR movies.trailer_urls LIKE '%1080p.mov%')", )[ self.settings[ "only_hd" ] and ( self.settings[ "quality" ] > 3 ) ]
            genre_sql = ""
            # if the use sets limit query limit our search to the genre and rating of the movie
            if ( self.settings[ "limit_query" ] ):
                # genre limit
                ##movie_genres = unicode( xbmc.getInfoLabel( "ListItem.Genre" ), "utf-8" ).split( "/" )
                movie_genres = g_genre.split( "/" )
                if ( movie_genres[ 0 ] != "" ):
                    genre_sql = "AND ("
                    for genre in movie_genres:
                        # fix certain genres
                        genre_sql += "genres.genre='%s' OR " % ( genre.strip().replace( "Sci-Fi", "Science Fiction" ).replace( "Action", "Action and Adventure" ).replace( "Adventure", "Action and Adventure" ), )
                    # fix the sql statement
                    genre_sql = genre_sql[ : -4 ] + ") "
                # rating limit TODO: decide if this should override the set rating limit
                ##movie_rating = xbmc.getInfoLabel( "ListItem.MPAA" ).split( " " )
                movie_rating = g_mpaa_rating.split( " " )
                if ( len( movie_rating ) > 1 ):
                    if ( movie_rating[ 1 ] in mpaa_ratings ):
                        rating_sql = "AND ("
                        for rating in mpaa_ratings:
                            rating_sql += "rating='%s' OR " % ( rating, )
                            # if we found the users choice, we're finished
                            if ( rating == movie_rating[ 1 ] ): break
                        # fix the sql statement
                        rating_sql = rating_sql[ : -4 ] + ") "
            # fetch our trailers
            result = records.fetch( sql % ( hd_sql, rating_sql, genre_sql, self.settings[ "number_trailers" ], ) )
            records.close()
        except:
            # oops print error message
            print sys.exc_info()[ 1 ]
            result = []
        return result

    def _get_listitem( self, trailer ):
        # check for a valid thumbnail
        thumbnail = ""
        if ( trailer[ 4 ] and trailer[ 4 ] is not None ):
            thumbnail = os.path.join( self.BASE_DATA_PATH, ".cache", trailer[ 4 ][ 0 ], trailer[ 4 ] )
        else:
            thumbnail = self._get_thumbnail( trailer[ 3 ], trailer[ 0 ] )
        # set the default icon
        icon = "DefaultVideo.png"
        # only need to add label, icon and thumbnail, setInfo() and addSortMethod() takes care of label2
        listitem = xbmcgui.ListItem( trailer[ 1 ], iconImage=icon, thumbnailImage=thumbnail )
        # add the different infolabels we want to sort by
        listitem.setInfo( type="Video", infoLabels={ "Title": trailer[ 1 ], "year": trailer[ 9 ], "Studio": trailer[ 15 ], "Genre": trailer[ 16 ], "PlotOutline": trailer[ 5 ], "Rating": trailer[ 17 ], "Director": trailer[ 18 ] } )
        return listitem

    def _get_thumbnail( self, item, url ):
        # All these steps are necessary for the differnt caching methods of XBMC
        # make the proper cache filename and path so duplicate caching is unnecessary
        filename = xbmc.getCacheThumbName( item )
        thumbnail = xbmc.translatePath( os.path.join( self.BASE_CACHE_PATH, filename[ 0 ], filename ) )
        # if the cached thumbnail does not exist create the thumbnail based on url
        if ( not os.path.isfile( thumbnail ) ):
            filename = xbmc.getCacheThumbName( url )
            thumbnail = xbmc.translatePath( os.path.join( self.BASE_CACHE_PATH, filename[ 0 ], filename ) )
            # if the cached thumbnail does not exist create the thumbnail based on filepath.tbn
            if ( not os.path.isfile( thumbnail ) ):
                # create filepath to a local tbn file
                thumbnail = os.path.splitext( item )[ 0 ] + ".tbn"
                # if there is no local tbn file use a default
                if ( not os.path.isfile( thumbnail ) or thumbnail.startswith( "smb://" ) ):
                    thumbnail = ""
        return thumbnail

    def _get_trailer_url( self, trailer_urls ):
        # pick a random url (only applies to multiple urls)
        r = randrange( len( trailer_urls ) )
        # get the preferred quality
        qualities = [ "Low", "Medium", "High", "480p", "720p", "1080p" ]
        url = ""
        # get intial choice
        choice = ( self.settings[ "quality" ], len( trailer_urls[ r ] ) - 1, )[ self.settings[ "quality" ] >= len( trailer_urls[ r ] ) ]
        # if quality is non progressive
        if ( self.settings[ "quality" ] <= 2 ):
            # select the correct non progressive trailer
            while ( trailer_urls[ r ][ choice ].endswith( "p.mov" ) and choice != -1 ): choice -= 1
        # quality is progressive
        else:
            # select the proper progressive quality
            quality = ( "480p", "720p", "1080p", )[ self.settings[ "quality" ] - 3 ]
            # select the correct progressive trailer
            while ( quality not in trailer_urls[ r ][ choice ] and trailer_urls[ r ][ choice ].endswith( "p.mov" ) and choice != -1 ): choice -= 1
        # if there was a valid trailer set it
        if ( choice >= 0 ):
            url = trailer_urls[ r ][ choice ]
        return url


class Records:
    # base paths
    BASE_DATABASE_PATH = sys.modules[ "__main__" ].BASE_DATABASE_PATH

    def __init__( self, *args, **kwargs ):
        self.connect()

    def connect( self ):
        self.db = sqlite.connect( os.path.join( self.BASE_DATABASE_PATH, "AMT.db" ) )
        self.cursor = self.db.cursor()
    
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
