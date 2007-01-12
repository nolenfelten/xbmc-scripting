import sys, os
cwd = sys.path[0]
sys.path.append( os.path.join( cwd, 'lib' ) )
from pysqlite2 import dbapi2 as sqlite
import traceback
try:
    
    db = os.path.join( cwd, 'data', 'AMT.db' )
    con = sqlite.connect( db )#, detect_types=sqlite.PARSE_DECLTYPES|sqlite.PARSE_COLNAMES)
    cur = con.cursor()
    #'SELECT DISTINCT studio FROM "Movies" ORDER BY studio'
    sql = 'SELECT actors FROM Movies WHERE actors LIKE ?'# ORDER BY studio'
    cur.execute( sql, ( '%Pierce Brosnan%', ) )
    print cur.fetchall()
except:
    print 'error'