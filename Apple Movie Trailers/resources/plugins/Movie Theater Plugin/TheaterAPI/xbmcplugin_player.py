"""
    Movie Theater: Module plays:
    - optional coming attractions video
    - # of random trailers
    - optional feature presentation video
    - selected video
    - optional end of presentation video
"""

# TODO: remove this when dialog issue is resolved
import xbmc
# set our studio (only works if the user is using the video library)
g_studio = xbmc.getInfoLabel( "ListItem.Studio" )
# set our genre (only works if the user is using the video library)
g_genre = xbmc.getInfoLabel( "ListItem.Genre" )
# set our rating (only works if the user is using the video library)
g_mpaa_rating = xbmc.getInfoLabel( "ListItem.MPAA" )

# create the progress dialog (we do it here so there is minimal delay with nothing displayed)
import xbmcgui
pDialog = xbmcgui.DialogProgress()
pDialog.create( "Movie Theater Plugin", "Choosing random trailers..." )

# main imports
import sys
import os
##import xbmc

from random import randrange

from pysqlite2 import dbapi2 as sqlite


class _Info:
    def __init__( self, *args, **kwargs ):
        self.__dict__.update( kwargs )


class Main:
    # base paths
    BASE_CACHE_PATH = os.path.join( "P:\\", "Thumbnails", "Video" )
    BASE_DATA_PATH = xbmc.translatePath( os.path.join( "T:\\", "script_data", sys.modules[ "__main__" ].__script__ ) )

    def __init__( self ):
        self._parse_argv()
        # create the playlist
        playlist = self._create_playlist()
        # play the videos
        self._play_videos( playlist )

    def _parse_argv( self ):
        # call _Info() with our formatted argv to create the self.args object
        exec "self.args = _Info(%s)" % ( sys.argv[ 2 ][ 1 : ].replace( "&", ", " ), )
        # backslashes cause issues when passed in the url
        self.args.path = self.args.path.replace( "[[BACKSLASH]]", "\\" )
        self.args.trailer_intro_path = self.args.trailer_intro_path.replace( "[[BACKSLASH]]", "\\" )
        self.args.movie_intro_path = self.args.movie_intro_path.replace( "[[BACKSLASH]]", "\\" )
        self.args.movie_end_path = self.args.movie_end_path.replace( "[[BACKSLASH]]", "\\" )

    def _create_playlist( self ):
        # create a video playlist
        playlist = xbmc.PlayList( xbmc.PLAYLIST_VIDEO )
        # clear any possible items
        playlist.clear()
        # if there is a trailer intro video add it
        if ( self.args.trailer_intro_path ):
            # create our trailer record
            trailer = ( self.args.trailer_intro_path, os.path.splitext( os.path.basename( self.args.trailer_intro_path ) )[ 0 ], "", self.args.trailer_intro_path, "", "", "", "", "", 0, "", "", "", "", "", "", "Coming Attractions Intro", )
            # create the listitem and fill the infolabels
            listitem = self._get_listitem( trailer )
            # add our item to the playlist
            playlist.add( self.args.trailer_intro_path, listitem )
        # fetch our random trailers
        trailers = self._fetch_records()
        # enumerate through our list of trailers and add them to our playlist
        for trailer in trailers:
            # we need to select the proper trailer url
            url = self._get_trailer_url( eval( trailer[ 3 ] ) )
            # create the listitem and fill the infolabels
            listitem = self._get_listitem( trailer )
            # add our item to the playlist
            playlist.add( url, listitem )
        # if there is a movie intro video add it
        if ( self.args.movie_intro_path ):
            # create our trailer record
            trailer = ( self.args.movie_intro_path, os.path.splitext( os.path.basename( self.args.movie_intro_path ) )[ 0 ], "", self.args.movie_intro_path, "", "", "", "", "", 0, "", "", "", "", "", "", "Feature Presentation Intro", )
            # create the listitem and fill the infolabels
            listitem = self._get_listitem( trailer )
            # add our item to the playlist
            playlist.add( self.args.movie_intro_path, listitem )
        # TODO: use these when dialog issue is resolved
        # set our studio (only works if the user is using the video library)
        ##studio = xbmc.getInfoLabel( "ListItem.Studio" )
        studio = g_studio
        # set our genre (only works if the user is using the video library)
        ##genre = xbmc.getInfoLabel( "ListItem.Genre" )
        genre = g_genre
        if ( not genre ):
            genre = "Feature Presentation"
        # add the selected video to our playlist
        trailer = ( sys.argv[ 0 ] + sys.argv[ 2 ], os.path.splitext( os.path.basename( self.args.path ) )[ 0 ], "", self.args.path, "", "", "", "", "", 0, "", "", "", "", "", studio, genre, )
        # create the listitem and fill the infolabels
        listitem = self._get_listitem( trailer )
        # add our item to the playlist
        playlist.add( self.args.path, listitem )
        # if there is a end of movie video add it
        if ( self.args.movie_end_path ):
            # create our trailer record
            trailer = ( self.args.movie_end_path, os.path.splitext( os.path.basename( self.args.movie_end_path ) )[ 0 ], "", self.args.movie_end_path, "", "", "", "", "", 0, "", "", "", "", "", "", "End of Feature Presentation", )
            # create the listitem and fill the infolabels
            listitem = self._get_listitem( trailer )
            # add our item to the playlist
            playlist.add( self.args.movie_end_path, listitem )
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
            if ( self.args.rating in mpaa_ratings ):
                rating_sql = "AND ("
                # enumerate through mpaa ratings and add the selected ones to our sql statement
                for rating in mpaa_ratings:
                    rating_sql += "rating='%s' OR " % ( rating, )
                    # if we found the users choice, we're finished
                    if ( rating == self.args.rating ): break
                # fix the sql statement
                rating_sql = rating_sql[ : -4 ] + ") "
            hd_sql = ( "", "AND (trailer_urls LIKE '%720p.mov%' OR trailer_urls LIKE '%1080p.mov%')", )[ self.args.only_hd ]
            genre_sql = ""
            mpaa_sql = ""
            # if the use sets limit query limit our search to the genre and rating of the movie
            if ( self.args.limit_query ):
                # genre limit
                ##movie_genres = xbmc.getInfoLabel( "ListItem.Genre" ).split( "/" )
                movie_genres = g_genre.split( "/" )
                if ( movie_genres[ 0 ] != "" ):
                    genre_sql = "AND ("
                    for genre in movie_genres:
                        genre_sql += "genres.genre='%s' OR " % ( genre.strip(), )
                    # fix the sql statement
                    genre_sql = genre_sql[ : -4 ] + ") "
                # rating limit TODO: decide if this should override the set rating limit
                ##movie_rating = xbmc.getInfoLabel( "ListItem.MPAA" ).split( "/" )
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
            result = records.fetch( sql % ( hd_sql, rating_sql, genre_sql, self.args.number_trailers, ) )
            records.close()
            return result
        except:
            # oops print error message
            print sys.exc_info()[ 1 ]

    def _get_listitem( self, trailer ):
        # check for a valid thumbnail
        thumbnail = ""
        if ( trailer[ 4 ] and trailer[ 4 ] is not None ):
            thumbnail = os.path.join( self.BASE_DATA_PATH, ".cache", trailer[ 4 ][ 0 ], trailer[ 4 ] )
        else:
            thumbnail = self._get_thumbnail( trailer[ 3 ], trailer[ 0 ] )
        # only need to add label and thumbnail, setInfo() and addSortMethod() takes care of label2
        listitem = xbmcgui.ListItem( trailer[ 1 ], thumbnailImage=thumbnail )
        # add the different infolabels we want to sort by
        listitem.setInfo( type="Video", infoLabels={ "Title": trailer[ 1 ], "year": trailer[ 9 ], "Studio": trailer[ 15 ], "Genre": trailer[ 16 ] } )
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
                    thumbnail = "defaultVideoBig.png"
        return thumbnail

    def _get_trailer_url( self, trailer_urls ):
        # pick a random url (only applies to multiple urls)
        r = randrange( len( trailer_urls ) )
        # get the preferred quality
        qualities = [ "Low", "Medium", "High", "480p", "720p", "1080p" ]
        trailer_quality = 2
        if ( self.args.quality in qualities ):
            trailer_quality = qualities.index( self.args.quality )
        url = ""
        # get intial choice
        choice = ( trailer_quality, len( trailer_urls[ r ] ) - 1, )[ trailer_quality >= len( trailer_urls[ r ] ) ]
        # if quality is non progressive
        if ( trailer_quality <= 2 ):
            # select the correct non progressive trailer
            while ( trailer_urls[ r ][ choice ].endswith( "p.mov" ) and choice != -1 ): choice -= 1
        # quality is progressive
        else:
            # select the proper progressive quality
            quality = ( "480p", "720p", "1080p", )[ trailer_quality - 3 ]
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
