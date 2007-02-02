import xbmcgui, xbmc
import sys, os, default
cwd = os.path.dirname( sys.modules['default'].__file__ )
from pysqlite2 import dbapi2 as sqlite
import traceback

COMPATIBLE_VERSIONS = [ 'pre-0.95', '0.95' ]

class Database:
    def __init__( self, *args, **kwargs ):
        self._ = kwargs[ 'language' ]
        if ( not os.path.isdir( os.path.join( cwd, 'extras', 'data' ) ) ):
            os.makedirs( os.path.join( cwd, 'extras', 'data' ) )
        db = os.path.join( cwd, 'extras', 'data', 'AMT.db' )
        self.setupTables()
        self.con = sqlite.connect( db )#, detect_types=sqlite.PARSE_DECLTYPES|sqlite.PARSE_COLNAMES)
        self.cur = self.con.cursor()
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
        elif ( version not in COMPATIBLE_VERSIONS ): version = self.convertDatabase( version )
        return version

    def convertDatabase( self, version ):
        #print version
        #print default.__version__
        #succeeded = self.updateRecord( ( 'version', ), 'Version', ( default.__version__, ), 'version', version[0] )
        #xbmcgui.Dialog().ok( 'Converted database...', 'The conversion succeeded %s' % ( succeeded, ) )
        #if ( succeeded ): return ( default.__version__, )
        #else: return version
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
            dialog.create('Creating database...')
            for table in self.tables.keys():
                dialog.update( -1, 'Table: %s' % table )
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
            self.con.execute( sql )
            for item in self.tables[table]:
                if ( item[2] != None ):
                    sql = 'CREATE %s INDEX %s_%s_idx ON %s (%s)' % ( index[item[2]], table, item[0], table, item[0], )
                    self.con.execute( sql )
            return True
        except: return False
            
    #def saveRecord( self, table, columns = None, key = None, key_value = None ):
    #    exists = self.getRecords( 'title', table, condition, value )
    #    if ( exists ):
    #        success = self.updateRecord( columns, table, condition, value )
    #    else:
    #        success = self.addRecords( columns, table )
            
    def addRecords( self, table, values  ):
        try:
            sql='INSERT INTO %s (' % ( table, )
            for item in self.tables[table]:
                sql += '%s, ' % item[0]
            sql = sql[:-2] + ') VALUES (' + ( '?, '*len( self.tables[ table ] ) )
            sql = sql[:-2] + ')'
            #cur = self.con.cursor()
            self.cur.executemany( sql, values )
            self.con.commit()
            return True
        except:
            print sql
            print values
            traceback.print_exc()
            return False
            
    def updateRecords( self, table, columns, values, key ):
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
            self.cur.executemany( sql, values )
            self.con.commit()
            return True
        except:
            print sql
            print values[0]
            traceback.print_exc()
            return False

    def getRecords( self, sql, params = None, all = False ):
        try:
            #cur = self.con.cursor()
            if ( params != None ):
                self.cur.execute( sql , params )
            else: 
                self.cur.execute( sql )
            if ( all ):
                retval = self.cur.fetchall()
            else:
                retval = self.cur.fetchone()
        except: 
            if ( all ): retval = []
            else: retval = None
        return retval
