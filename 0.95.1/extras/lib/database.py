import xbmcgui, xbmc
import sys, os, default
cwd = os.path.dirname( sys.modules['default'].__file__ )
from pysqlite2 import dbapi2 as sqlite
import traceback

COMPATIBLE_VERSIONS = [ 'pre-0.95.1', '0.95.1' ]

class Database:
    def __init__( self, *args, **kwargs ):
        self._ = kwargs[ 'language' ]
        if ( not os.path.isdir( os.path.join( cwd, 'extras', 'data' ) ) ):
            os.makedirs( os.path.join( cwd, 'extras', 'data' ) )
        self.db = os.path.join( cwd, 'extras', 'data', 'AMT.db' )
        self.setupTables()
        #self.con = sqlite.connect( self.db )#, detect_types=sqlite.PARSE_DECLTYPES|sqlite.PARSE_COLNAMES)
        #self.cur = self.con.cursor()
        self.db_version = self.getVersion()
        if ( not self.db_version ): 
            print 'no database exists', default.__version__
            #cleanup database
            #del self.con
            #remove db if exists
            
    def getVersion( self ):
        version = self.getRecords( 'SELECT version FROM Version' )
        self.created = False
        if ( not version ): version = self.createDatabase()
        elif ( version[ 0 ] not in COMPATIBLE_VERSIONS ): version = self.convertDatabase( version )
        return version
    
    def convertDatabase( self, version ):
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
                
                
    def setupTables( self ):
        self.tables = {}
        self.tables['Actors'] = (
                                            ( 'name', 'text', True ),
                                            ( 'count', 'integer', None ),
                                        )
        self.tables['Studios'] = ( 
                                            ('title', 'text', True),
                                            ( 'count', 'integer', None ),
                                        )
        #self.tables['Playlist'] = ( 
        #                                    ('title', 'text', True),
        #                                )
        self.tables['Version'] = (
                                            ( 'version', 'text', None ),
                                        )
        self.tables['Genres'] = (
                                            ( 'title', 'text', True ),
                                            ( 'url', 'text', None ),
                                            ( 'id', 'integer', None ), 
                                            ( 'count', 'integer', None ),
                                            ( 'loaded', 'integer', None ),
                                            ( 'trailer_urls', 'blob', None ),
                                        )
        self.tables['Movies'] = (
                                            ( 'title', 'text', True ),
                                            ( 'url', 'text', None ),
                                            ( 'trailer_urls', 'text', None ),
                                            ( 'genre', 'integer', False ),
                                            ( 'poster', 'text', None ),
                                            ( 'thumbnail', 'text', None ),
                                            ( 'thumbnail_watched', 'text', None ),
                                            ( 'plot', 'text', None ),
                                            ( 'actors', 'text', None ),
                                            ( 'studio', 'text', None ),
                                            ( 'rating', 'text', None ),
                                            ( 'rating_url', 'text', None ),
                                            ( 'year', 'integer', None ),
                                            ( 'times_watched', 'integer', None ),
                                            ( 'last_watched', 'text', None ),
                                            ( 'favorite', 'integer', None ),
                                            ( 'saved_location', 'text', None ),
                                        )

    def createDatabase( self ):
        try:
            self.created = True
            dialog = xbmcgui.DialogProgress()
            dialog.create( self._( 44 ) )
            for table in self.tables.keys():
                dialog.update( -1, '%s: %s' % ( self._( 47 ), table, ) )
                success = self.createTable( table )
                if ( not success ):
                    raise
            success = self.addRecords( 'Version', ( ( default.__version__, ), ) )
            dialog.close()
            if ( success ): return default.__version__
            else: return None
        except:
            dialog.close()
            xbmcgui.Dialog().ok( self._( 0 ), self._( 89 ) )
            return None

    def createTable( self, table ):
        try:
            sql = 'CREATE TABLE %s (' % table
            index = ( '', 'UNIQUE' )
            for item in self.tables[table]:
                sql += '%s %s, ' % ( item[0], item[1], )
            sql = sql[:-2] + ')'
            con = sqlite.connect( self.db )#, detect_types=sqlite.PARSE_DECLTYPES|sqlite.PARSE_COLNAMES)
            cur = con.cursor()
            con.execute( sql )
            for item in self.tables[table]:
                if ( item[2] != None ):
                    sql = 'CREATE %s INDEX %s_%s_idx ON %s (%s)' % ( index[item[2]], table, item[0], table, item[0], )
                    con.execute( sql )
            con.close()
            return True
        except: return False
            
    #def saveRecord( self, table, columns = None, key = None, key_value = None ):
    #    exists = self.getRecords( 'title', table, condition, value )
    #    if ( exists ):
    #        success = self.updateRecord( columns, table, condition, value )
    #    else:
    #        success = self.addRecords( columns, table )
            
    def addRecords( self, table, values, commit=False  ):
        try:
            sql='INSERT INTO %s (' % ( table, )
            for item in self.tables[table]:
                sql += '%s, ' % item[0]
            sql = sql[:-2] + ') VALUES (' + ( '?, '*len( self.tables[ table ] ) )
            sql = sql[:-2] + ')'
            #cur = self.con.cursor()
            con = sqlite.connect( self.db )#, detect_types=sqlite.PARSE_DECLTYPES|sqlite.PARSE_COLNAMES)
            cur = con.cursor()
            cur.executemany( sql, values )
            con.commit()
            con.close()
            return True
        except:
            print sql
            print values
            traceback.print_exc()
            return False
            
    def updateRecords( self, table, columns, values, key, commit=False ):
        try:
            if ( columns[0] == '*' ):
                start_column = columns[ 1 ]
                columns = ()
                for item in self.tables[table][ start_column : ]:
                    columns += ( item[0], )
            sql = "UPDATE %s SET " % ( table, )
            for col in columns:
                sql += "%s=?, " % col
            sql = sql[:-2] + " WHERE %s=?" % ( key, )
            #cur = self.con.cursor()
            con = sqlite.connect( self.db )#, detect_types=sqlite.PARSE_DECLTYPES|sqlite.PARSE_COLNAMES)
            cur = con.cursor()
            cur.executemany( sql, values )
            con.commit()
            con.close()
            return True
        except:
            print sql
            print values[0]
            traceback.print_exc()
            con.close()
            return False

    def getRecords( self, sql, params = None, all = False ):
        try:
            con = sqlite.connect( self.db )#, detect_types=sqlite.PARSE_DECLTYPES|sqlite.PARSE_COLNAMES)
            cur = con.cursor()
            #cur = self.con.cursor()
            if ( params != None ):
                cur.execute( sql , params )
            else: 
                cur.execute( sql )
            if ( all ):
                retval = cur.fetchall()
            else:
                retval = cur.fetchone()
        except: 
            if ( all ): retval = []
            else: retval = None
        con.close()
        return retval
