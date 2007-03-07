COMPATIBLE_VERSIONS = [ 'pre-0.96', '0.96', 'pre-0.97', '0.97'  ]

import xbmcgui, xbmc
import sys, os, default
from pysqlite2 import dbapi2 as sqlite
import traceback

if ( not os.path.isdir( os.path.join( os.path.dirname( sys.modules['default'].__file__ ), 'extras', 'data' ) ) ):
    os.makedirs( os.path.join( os.path.dirname( sys.modules['default'].__file__ ), 'extras', 'data' ) )
db_filename = os.path.join( os.path.dirname( sys.modules['default'].__file__ ), 'extras', 'data', 'AMT.db' )


class Database:
    "main initializing of the database"
    def __init__( self, *args, **kwargs ):
        self._ = kwargs[ 'language' ]
        self.query = Query()
        self.db_version, self.complete = self.getVersion()
        if ( not self.db_version ): 
            print 'no database exists', default.__version__

    def getVersion( self ):
        records = Records()
        record = records.fetchone( self.query[ 'version' ] )
        if ( record ):
            version = record[ 1 ]
            complete = record[ 2 ]
            if ( record[ 1 ] not in COMPATIBLE_VERSIONS ): 
                version, complete = self.convertDatabase( version )
        else: version, complete = self.createDatabase()
        return version, complete
    
    def createDatabase( self ):
        tables = Tables()# language = self._
        success = tables.createTables( self._ )
        if ( success ):
            success = self.writeVersion()
            if ( success ): return default.__version__, False
        return None, False

    def writeVersion( self ):
        records = Records()
        lastrowid = records.add( 'version', ( default.__version__, False, ) )
        if ( lastrowid ): success = records.commit()
        records.close()
        return lastrowid

    def convertDatabase( self, version ):
        return None, False
        pass
        '''
        if ( version[ 0 ] == 'pre-0.95' ):
            try:
                dialog = xbmcgui.DialogProgress()
                dialog.create( self._( 53 ) )
                replace_string = os.path.join( os.path.dirname( sys.modules['default'].__file__ ), 'extras', 'data', '.cache\\' )
                sql = 'SELECT title, poster, thumbnail, thumbnail_watched, rating_url FROM Movies WHERE poster != ?'
                dialog.update( -1, self._( 48 ) )
                records = self.getRecords( sql, params=( '', ), all=True )
                if ( records ):
                    changed_records = ()
                    total_cnt = len( records )
                    pct_sect = float( 100 ) / total_cnt
                    for cnt, record in enumerate( records ):
                        #xbmc.sleep(100)
                        new_field = ()
                        dialog.update( int( ( cnt + 1 ) * pct_sect ), '%s: (%d of %d)' % ( self._( 45 ), cnt + 1, total_cnt, ), '%s: %s' % ( self._( 88 ), record[ 0 ], ), '' )
                        for item in record[ 1 : 5 ]:
                            new_field += ( item.replace( replace_string, '' ), )
                        new_field += ( record[ 0 ], )
                        changed_records += ( new_field, )
                        if ( dialog.iscanceled == True ): raise
                    dialog.update( 100 , '%s: (%d of %d)' % ( self._( 45 ), cnt + 1, total_cnt, ), '%s: %s' % ( self._( 88 ), record[ 0 ], ), '-----> %s <-----' % ( self._( 43 ), ) )
                    succeeded = self.updateRecords( 'Movies', ( 'poster', 'thumbnail', 'thumbnail_watched', 'rating_url', ), changed_records, 'title' )
                    if ( succeeded ): self.updateRecords( 'Version', ( 'version', ), ( ( default.__version__, version[ 0 ], ), ), 'version' )
                    #xbmc.sleep(1000)
                    dialog.close()
                    if ( succeeded ): return ( default.__version__, )
                    else: return version
            except:
                traceback.print_exc()
                dialog.close()
                xbmcgui.Dialog().ok( self._( 53 ), self._( 46 ) )
                return version
        '''        

    '''
    def updateVersion( self ):
        records = Records()
        success = records.update( 'version', ( 'version', ), ( '0.98.85', default.__version__, ), 'version' )
        records.commit()
        records.close()
        return success
    '''


class Tables( dict ):
    def __init__( self, *args, **kwargs ):
        #{ column name, type, auto increment, index , index columns }
        self['version'] = (
            ( 'idVersion', 'integer PRIMARY KEY', 'AUTOINCREMENT', '', '' ),
            ( 'version', 'text', '', '', '' ),
            ( 'complete', 'integer', '', '', '' ),
        )
        self['genres'] = (
            ( 'idGenre', 'integer PRIMARY KEY', 'AUTOINCREMENT', '', '' ),
            ( 'genre', 'text', '', '', '' ),
            ( 'urls', 'blob', '', '', '' ),
            ( 'trailer_urls', 'blob', '', '', '' ),
        )
        self['actors'] = (
            ( 'idActor', 'integer PRIMARY KEY', 'AUTOINCREMENT', '', '' ),
            ( 'actor', 'text', '', '', '' ),
        )
        self['studios'] = ( 
            ( 'idStudio', 'integer PRIMARY KEY', 'AUTOINCREMENT', '', '' ),
            ( 'studio', 'text', '', '', '' ),
        )
        self['movies'] = (
            ( 'idMovie', 'integer PRIMARY KEY', 'AUTOINCREMENT', '', '' ), 
            ( 'title', 'text', '', '', '' ),
            ( 'url', 'text',  '', '', '' ),
            ( 'trailer_urls', 'text', '', '', '' ),
            ( 'poster', 'text', '', '', '' ),
            ( 'plot', 'text', '', '', '' ),
            ( 'rating', 'text', '', '', '' ),
            ( 'rating_url', 'text', '', '', '' ),
            ( 'year', 'integer', '', '', '' ),
            ( 'times_watched', 'integer', '', '', '' ),
            ( 'last_watched', 'text', '', '', '' ),
            ( 'favorite', 'integer', '', '', '' ),
            ( 'saved_location', 'text', '', '', '' ),
        )
        self['genre_link_movie'] = ( 
            ( 'idGenre', 'integer', '', 'UNIQUE INDEX', '(idGenre, idMovie)' ),
            ( 'idMovie', 'integer', '', 'UNIQUE INDEX', '(idMovie, idGenre)' ),
        )
        self['actor_link_movie'] = ( 
            ( 'idActor', 'integer', '', 'UNIQUE INDEX', '(idActor, idMovie)' ),
            ( 'idMovie', 'integer', '', 'UNIQUE INDEX', '(idMovie, idActor)' ),
        )
        self['studio_link_movie'] = ( 
            ( 'idStudio', 'integer', '', 'UNIQUE INDEX', '(idStudio, idMovie)' ),
            ( 'idMovie', 'integer', '', 'UNIQUE INDEX', '(idMovie, idStudio)' ),
        )

    def connect( self ):
        self.db = sqlite.connect( db_filename )#, detect_types=sqlite.PARSE_DECLTYPES|sqlite.PARSE_COLNAMES)
    
    def close( self ):
        self.db.close()

    def createTables( self, _ ):
        try:
            dialog = xbmcgui.DialogProgress()
            dialog.create( _( 44 ) )
            self.connect()
            for table in self.keys():
                dialog.update( -1, '%s: %s' % ( _( 47 ), table, ) )
                success = self.createTable( table )
                if ( not success ): raise
            self.close()
            dialog.close()
            return True
        except:
            dialog.close()
            xbmcgui.Dialog().ok( _( 0 ), _( 89 ) )
            return False

    def createTable( self, table ):
        try:
            sql = 'CREATE TABLE %s (' % table
            for item in self[table]:
                sql += '%s %s %s, ' % ( item[ 0 ], item[ 1 ], item[ 2 ])
            sql = sql[:-2].strip() + ');'
            self.db.execute( sql )
            for item in self[table]:
                if ( item[3] != '' ):
                    sql = 'CREATE %s %s_%s_idx ON %s %s;' % ( item[ 3 ], table, item[0], table, item[4], )
                    self.db.execute( sql )
            return True
        except: return False


class Records:
    "add, update and fetch records"
    def __init__( self, *args, **kwargs ):
        self.tables = Tables()
        self.connect()

    def connect( self ):
        self.db = sqlite.connect( db_filename )#, detect_types=sqlite.PARSE_DECLTYPES|sqlite.PARSE_COLNAMES)
        self.cursor = self.db.cursor()
    
    def commit( self ):
        try:
            self.db.commit()
            return True
        except: return False
    
    def close( self ):
        self.db.close()
    
    def add( self, table, params ):
        try:
            auto_increment = 0
            sql='INSERT INTO %s (' % ( table, )
            for item in self.tables[table]:
                if ( not item[ 2 ] == '' ):
                    auto_increment += 1
                else: sql += '%s, ' % item[0]
            sql = sql[:-2] + ') VALUES (' + ( '?, '*( len( self.tables[ table ] ) - auto_increment ) )
            sql = sql[:-2] + ');'
            self.cursor.execute( sql, params )
            return self.cursor.lastrowid
        except:
            print '*** ERROR: Records.add() ***'
            print sql
            print params
            traceback.print_exc()
            return False

    def update( self, table, columns, params, key, commit=False ):
        try:
            if ( columns[0] == '*' ):
                start_column = columns[ 1 ]
                columns = ()
                for item in self.tables[table][ start_column : ]:
                    columns += ( item[0], )
            sql = "UPDATE %s SET " % ( table, )
            for col in columns:
                sql += "%s=?, " % col
            sql = sql[:-2] + " WHERE %s=?;" % ( key, )
            self.cursor.execute( sql, params )
            return True
        except:
            print '*** ERROR: Records.update() ***'
            print sql
            print params
            traceback.print_exc()
            return False

    def fetchone( self, sql, params = False ):
        try:
            if ( params ): self.cursor.execute( sql , params )
            else: self.cursor.execute( sql )
            retval = self.cursor.fetchone()
        except:
            retval = None
        return retval
        
    def fetchall( self, sql, params = False ):
        try:
            if ( params ): 
                self.cursor.execute( sql , params )
            else: self.cursor.execute( sql )
            retval = self.cursor.fetchall()
        except:
            retval = None
        return retval

    
    '''
    def fetch( self, sql, params = False, all = False ):
        try:
            if ( params ): self.cursor.execute( sql , params )
            else: self.cursor.execute( sql )
            if ( all ): retval = self.cursor.fetchall()
            else: retval = self.cursor.fetchone()
        except:
            if ( all ): retval = []
            else: retval = None
        self.close()
        return retval
    '''

class Query( dict ):
    "all sql statments. add as needed"
    def __init__( self ):
        #good sql statements
        self[ 'movie_by_movie_id' ]		= "SELECT movies.* FROM movies WHERE movies.idMovie=?;"
        self[ 'studio_by_movie_id' ]		= "SELECT studios.studio FROM studio_link_movie, studios, movies WHERE studio_link_movie.idMovie = movies.idMovie AND studio_link_movie.idStudio = studios.idStudio AND movies.idMovie=?;"
        self[ 'actors_by_movie_id' ]		= "SELECT actors.actor FROM actor_link_movie, actors, movies WHERE actor_link_movie.idMovie = movies.idMovie AND actor_link_movie.idActor = actors.idActor AND movies.idMovie=? ORDER BY actors.actor;"

        self[ 'movies_by_genre_id' ]		= "SELECT movies.* FROM movies, genres, genre_link_movie WHERE genre_link_movie.idGenre=genres.idGenre AND genre_link_movie.idMovie=movies.idMovie AND genres.idGenre=? ORDER BY movies.title;"
        self[ 'movies_by_studio_id' ]		= "SELECT movies.* FROM movies, studios, studio_link_movie WHERE studio_link_movie.idStudio=studios.idStudio AND studio_link_movie.idMovie=movies.idMovie AND studios.idStudio=? ORDER BY movies.title;"
        self[ 'movies_by_actor_id' ]		= "SELECT movies.* FROM movies, actors, actor_link_movie WHERE actor_link_movie.idActor=actors.idActor AND actor_link_movie.idMovie=movies.idMovie AND actors.idActor=? ORDER BY movies.title;"

        self[ 'movies_by_genre_name' ]	= "SELECT movies.* FROM movies, genres, genre_link_movie WHERE genre_link_movie.idGenre=genres.idGenre AND genre_link_movie.idMovie=movies.idMovie AND genres.genre=? ORDER BY movies.title;"
        self[ 'movies_by_studio_name' ]	= "SELECT movies.* FROM movies, studios, studio_link_movie WHERE studio_link_movie.idStudio=studios.idStudio AND studio_link_movie.idMovie=movies.idMovie AND upper(studios.studio)=? ORDER BY movies.title;"
        self[ 'movies_by_actor_name' ]	= "SELECT movies.* FROM movies, actors, actor_link_movie WHERE actor_link_movie.idActor=actors.idActor AND actor_link_movie.idMovie=movies.idMovie AND upper(actors.actor) LIKE ? ORDER BY movies.title;"
        
        self[ 'incomplete_movies' ]		= "SELECT * FROM movies WHERE poster='' ORDER BY title;"
        self[ 'version' ]						= "SELECT * FROM version;"
        
        self[ 'genre_category_list' ]		= "SELECT genres.genre, count(genre_link_movie.idGenre) FROM genre_link_movie, genres WHERE genre_link_movie.idGenre=genres.idGenre GROUP BY genres.genre;"
        self[ 'studio_category_list' ]		= "SELECT studios.studio, count(studio_link_movie.idStudio) FROM studio_link_movie, studios WHERE studio_link_movie.idStudio=studios.idStudio GROUP BY upper(studios.studio);"
        self[ 'actor_category_list' ]		= "SELECT actors.actor, count(actor_link_movie.idActor) FROM actor_link_movie, actors WHERE actor_link_movie.idActor=actors.idActor GROUP BY upper(actors.actor);"

        self[ 'genre_table_list' ]			= 'SELECT idGenre, genre, urls FROM genres ORDER BY genre;'
        
        self[ 'movie_exists' ]				= 'SELECT idMovie FROM movies WHERE upper(title)=?;'
        self[ 'actor_exists' ]					= "SELECT idActor FROM actors WHERE upper(actor)=?;"
        self[ 'studio_exists' ]				= "SELECT idStudio FROM studios WHERE upper(studio)=?;"

        self[ 'favorites' ]						= "SELECT * FROM movies WHERE favorite=? ORDER BY title;"
        self[ 'downloaded' ]					= "SELECT * FROM movies WHERE saved_location!=? ORDER BY title;"



'''
SELECT movies.*, actors.actor, studios.studio FROM movies, actors, actor_link_movie, studios, studio_link_movie WHERE movies.idMovie = ? AND actor_link_movie.idActor = actors.idActor AND actor_link_movie.idMovie = movies.idmovie AND studio_link_movie.idStudio = studios.idStudio AND studio_link_movie.idMovie = movies.idMovie;
SELECT movies.*, actors.actor FROM movies, genres, genre_link_movie, actors, actor_link_movie WHERE genres.idGenre = ? AND genre_link_movie.idGenre=genres.idGenre AND movies.idMovie=genre_link_movie.idMovie and actor_link_movie.idActor = actors.idActor and actor_link_movie.idMovie = movies.idMovie order BY movies.title;
select movies.* from movies, genres, genre_link_movie
where genres.idGenre = 11 and genre_link_movie.idGenre=genres.idGenre
and movies.idMovie = genre_link_movie.idMovie order by movies.title;

select genre_link_movie.idMovie,
 movies.title, movies.url
 from genre_link_movie, movies, genres
 where genre_link_movie.idMovie = movies.idMovie and
 genre_link_movie.idGenre = genres.idGenre and movies.trailer_urls is Null
 order by movies.title;
        
select actors.actor from actors, actor_link_movie, movies
 where actor_link_movie.idMovie = movies.idMovie
 and actors.idActor = actor_link_movie.idActor
 and movies.idMovie=100 order by actors.actor;
        
        
 '''
        