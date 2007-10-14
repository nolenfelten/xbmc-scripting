"""
    Movie Theater: Module plays an optional intro video, random trailers then selected video
"""

# create the progress dialog (we do it here so there is minimal delay with nothing displayed)
import xbmcgui
pDialog = xbmcgui.DialogProgress()
pDialog.create( "Movie Theater Plugin", "Getting random trailers..." )

# main imports
import sys
import os
import xbmc

from pysqlite2 import dbapi2 as sqlite


class _Info:
    def __init__( self, *args, **kwargs ):
        self.__dict__.update( kwargs )


class Main:
    # base paths
    BASE_CACHE_PATH = os.path.join( "P:\\", "Thumbnails", "Video" )

    def __init__( self ):
        self._parse_argv()
        # play the videos
        self.play_videos()

    def _parse_argv( self ):
        # call _Info() with our formatted argv to create the self.args object
        exec "self.args = _Info(%s)" % ( sys.argv[ 2 ][ 1 : ].replace( "&", ", " ), )
        # backslashes cause issues when passed in the url
        self.args.path = self.args.path.replace( "[[BACKSLASH]]", "\\" )
        self.args.trailer_intro_path = self.args.trailer_intro_path.replace( "[[BACKSLASH]]", "\\" )
        self.args.movie_intro_path = self.args.movie_intro_path.replace( "[[BACKSLASH]]", "\\" )

    def play_videos( self ):
        # create a video playlist
        playlist = xbmc.PlayList( 1 )
        # clear any possible items
        playlist.clear()
        # if there is an trailer intro video add it first
        if ( self.args.trailer_intro_path ):
            playlist.add( self.args.trailer_intro_path )
        # fetch our random trailers
        trailers = self._fetch_records()
        # enumerate through our list of trailers and add them to our playlist
        for trailer in trailers:
            # we need to select the proper trailer url
            url = self._get_trailer_url( eval( trailer[ 3 ] ) )
            playlist.add( url )
        # if there is an movie intro video add it first
        if ( self.args.movie_intro_path ):
            playlist.add( self.args.movie_intro_path )
        # add the selected video to our playlist
        playlist.add( self.args.path )
        pDialog.close()
        if ( not pDialog.iscanceled() ):
            # call _get_thumbnail() for the path to the cached thumbnail
            #thumbnail = self._get_thumbnail( sys.argv[ 0 ] + sys.argv[ 2 ] )
            #listitem = xbmcgui.ListItem( self.args.title, thumbnailImage=thumbnail )
            #listitem.setInfo( "video", { "Title": self.args.title, "Director": self.args.director, "Genre": self.args.genre, "Rating": self.args.rating, "Count": self.args.count, "Date": self.args.date } )
            xbmc.Player().play( playlist )

    def _fetch_records( self ):
        try:
            records = Records()
            # select only trailers with valid trailer urls
            sql = """
                SELECT * FROM movies 
                WHERE trailer_urls IS NOT NULL 
                AND trailer_urls!='[]' 
                %s
                %s
                ORDER BY RANDOM() 
                LIMIT %d;
                """
            # mpaa ratings
            mpaa_ratings = [ "G", "PG", "PG-13", "R", "NC-17" ]
            rating_sql = ""
            # if the user set a valid rating add all up to the selection
            if ( self.args.rating in mpaa_ratings ):
                # use this one if we want to limit ourselves to the exact rating
                #rating_sql = "AND rating='%s' " % ( self.args.rating, )
                rating_sql = "AND ("
                # enumerate through mpaa ratings and add the selected ones to our sql statement
                for rating in mpaa_ratings:
                    rating_sql += "rating='%s' OR " % ( rating, )
                    # if we found the users choice, we're finished
                    if ( rating == self.args.rating ): break
                # fix the sql statement
                rating_sql = rating_sql[ : -4 ] + ") "
            hd_sql = ( "", "AND (trailer_urls LIKE '%720p.mov%' OR trailer_urls LIKE '%1080p.mov%')", )[ self.args.only_hd ]
            # fetch our trailers
            result = records.fetch( sql % ( hd_sql, rating_sql, self.args.number_trailers, ) )
            records.close()
            return result
        except:
            # oops print error message
            print sys.exc_info()[ 1 ]

    def _get_thumbnail( self, url ):
        # make the proper cache filename and path
        filename = xbmc.getCacheThumbName( url )
        filepath = xbmc.translatePath( os.path.join( self.BASE_CACHE_PATH, filename[ 0 ], filename ) )
        return filepath

    def _get_trailer_url( self, trailer_urls ):
        qualities = [ "Low", "Medium", "High", "480p", "720p", "1080p" ]
        trailer_quality = 2
        if ( self.args.quality in qualities ):
            trailer_quality = qualities.index( self.args.quality )
        url = ""
        # get intial choice
        choice = ( trailer_quality, len( trailer_urls ) - 1, )[ trailer_quality >= len( trailer_urls ) ]
        # if quality is non progressive
        if ( trailer_quality <= 2 ):
            # select the correct non progressive trailer
            while ( trailer_urls[ choice ].endswith( "p.mov" ) and choice != -1 ): choice -= 1
        # quality is progressive
        else:
            # select the proper progressive quality
            quality = ( "480p", "720p", "1080p", )[ trailer_quality - 3 ]
            # select the correct progressive trailer
            while ( quality not in trailer_urls[ choice ] and trailer_urls[ choice ].endswith( "p.mov" ) and choice != -1 ): choice -= 1
        # if there was a valid trailer set it
        if ( choice >= 0 ):
            url = trailer_urls[ choice ]
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

