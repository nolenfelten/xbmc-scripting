"""
    This is a simple script that lets me keep track of which version of 
    httplib2 I'm using.
"""
HTTPLIB2_DIR = 'httplib2-0.2.0'

import sys, os
path = os.path.join( os.path.dirname( sys.modules['httplib2_mod'].__file__ ), HTTPLIB2_DIR )
sys.path.insert( 0, path )
from httplib2 import *
from httplib2 import FileCache

class FileCache_mod( FileCache ):
    def __init__( self, cache ):
        actual_cache = os.path.join( cache, '.cache' )
        FileCache.__init__( self, actual_cache )

    def get( self, key ):
        self.last_accessed_file = key
        return FileCache.get( self, key )

    def set( self, key, value ):
        self.last_accessed_file = key
        return FileCache.set( self, key, value )

class Http_mod:
    def __init__( self, cache ):
        self.cache_dir = cache
        self.fetcher = Http( FileCache_mod( cache ) )

    def urlopen( self, url ):
        filename = self.urlretrieve( url )
        try:
            data = open( filename, 'r' ).read()
        except:
            data = ''
        return data

    def urlretrieve( self, url ):
        response, content = self.fetcher.request( url )
        filename = os.path.join( self.cache_dir, self.fetcher.cache.last_accessed_file )
        if content:
            file = None
            try:
                try:
                    print 'attempting to write:', filename
                    file = open( filename, 'w' )
                    print repr( content[:100] )
                    file.write( content )
                except:
                    import traceback
                    traceback.print_exc()
            finally:
                if file:
                    file.close()
        print 'cached file:', filename
        return filename

    def get_cache_location( self ):
        return self.fetcher.cache.cache
