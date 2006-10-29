import xbmcgui, xbmc
import sys, os, default
cwd = os.path.dirname( sys.modules['default'].__file__ )
from pysqlite2 import dbapi2 as sqlite
import traceback

COMPATIBLE_VERSIONS = [ '0.95' ]

class Database:
    def __init__( self ):
        if ( not os.path.isdir( os.path.join( cwd, 'data' ) ) ):
            os.makedirs( os.path.join( cwd, 'data' ) )
        db = os.path.join( cwd, 'data', 'AMT.db' )
        self.setupTables()
        self.con = sqlite.connect( db )#, detect_types=sqlite.PARSE_DECLTYPES|sqlite.PARSE_COLNAMES)
        self.db_version = self.getVersion()
        #print 'version', self.db_version[0]
        if ( not self.db_version ): 
            print 'no database exists'
            #cleanup database
            #del self.con
            #remove db if exists
            
    def getVersion( self ):
        version = self.getRecords( 'SELECT version FROM Version' )
        if ( not version ): version = self.createDatabase()
        elif ( version not in COMPATIBLE_VERSIONS ): version = self.convertDatabase( version )
        return version

    def convertDatabase( self, version ):
        print version
        print default.__version__
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
        self.tables['Playlist'] = ( 
                                            ('title', 'text', True),
                                        )
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
                                            ( 'urls', 'text', None ),
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
            dialog = xbmcgui.DialogProgress()
            dialog.create('Creating database...')
            for table in self.tables.keys():
                dialog.update(-1,'Table: %s' % table)
                success = self.createTable( table )
                if ( not success ):
                    raise
            success = self.addRecord( ( default.__version__, ),  'Version' )
            dialog.close()
            if ( success ): return default.__version__
            else: return None
        except:
            dialog.close()
            xbmcgui.Dialog().ok( 'Apple Movie Trailers', 'There was a problem creating the database' )
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
            
    #def saveRecord( self, columns, table, condition = ('title='), value = (None) ):
    #    if ( not value ): value = columns[0]
    #    exists = self.getRecords( 'title', table, condition, value )
    #    if ( exists ):
    #        success = self.updateRecord( columns, table, condition, value )
    #    else:
    #        success = self.addRecord( columns, table )
            
    def addRecord( self, columns, table ):
        try:
            cur = self.con.cursor()
            sql='INSERT INTO %s (' % ( table, )
            for item in self.tables[table]:
                sql += '%s, ' % item[0]
            sql = sql[:-2] + ') VALUES (' + ( '?, '*len( columns ) )
            sql = sql[:-2] + ')'
            print sql
            cur.execute( sql, columns )
            self.con.commit()
            return True
        except:
            return False
            
    def updateRecord( self, columns, table, values, key = 'title', key_value = None ):
        try:
            cur = self.con.cursor()
            sql = "UPDATE %s SET " % ( table, )
            for col in columns:
                sql += "%s=?, " % col
            sql = sql[:-2] + " WHERE %s=?" % ( key, )
            print sql
            cur.execute( sql, values + ( key_value, ) )
            self.con.commit()
            return True
        except:
            traceback.print_exc()
            return False

    #def getRecords( self, columns, table = 'Movies', condition = None, values = None, orderby = None, all = False ):
    def getRecords( self, sql, params = None, all = False ):
        try:
            cur = self.con.cursor()
            ##sql = "SELECT %s FROM %s" % ( columns, table, )
            ##if ( condition != None and values != None ):
            ##    sql += ' WHERE %s' % ( condition, )
            ##if ( orderby ):
            ##    sql += ' ORDER BY %s' % ( orderby, )
            ###print sql
            ##if ( condition != None and values != None ):
            ##    cur.execute( sql , values )
            ##else: 
            ##    cur.execute( sql )
            print sql
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
        return retval
'''
UPDATE Person SET FirstName = 'Nina'
WHERE LastName = 'Rasmussen'

#cur.execute("insert into Movies(title, genre) values (?, ?)", ('Ultraviolet', 3))
#cur.execute("insert into Movies(title, genre) values (?, ?)", ('Flushed Away', 5))
#con.commit()

#sqlite.enable_callback_tracebacks(True)
db = database()
##db.createDatabase()


table ='Movies'
record = ( 'Ultraviolet', '1', 'HTTP://1', 'HTTP://2', 'HTTP://3', 'HTTP://4', 'HTTP://5', 'HTTP://6',
                '2', 'F:\\poster', 'F:\\Thumbnail', 'F:\\Thumbnail_watched', 'plot', 'actor1', 'actor2',
                'actor3','actor4','actor5','Fox Studios','2005','3','10-21-2006','1','F:\\Trailers' )
#db.addRecord( table, record )

cur = db.con.cursor()
cur.execute("select title, genre from Movies where (?&genre)>0", (1,))
print cur.fetchall()
cur.execute( 'SELECT * FROM Movies' )
print len(cur.fetchall())
cur.execute("select genre from Movies where (title)=?", ('Flushed Away',))
print cur.fetchone()


##k = [(key,value) for key, value in l.items() if value['controlId'] == Id]


headings = 'insert into %s (%s%s)' % (table, '%s, '*(len(db.tables[table]) - 1), '%s',)
print headings
print
print db.tables[table]

print headings % (heading for heading in db.tables[table])
#headings_sql = headings % (heading for heading in db.tables[table])
#print headings_sql
print

values = 'values (%s%s)' % ('%s, '*(len(record) - 1), '%s',)
values_sql = values % record
print values_sql



#db.addRecord( table, record )
#db.con.row_factory = sqlite.Row

#cur =db.con.cursor()
#cur.execute("select * from Movies where (?&genre)>0", (4,))
#records = cur.fetchall()
#for record in records:
#    print record['saved_location'].replace('\\\\', '\\')
'''