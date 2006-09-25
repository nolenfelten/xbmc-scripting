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
        retval = FileCache.get( self, key )
        cache_dir = os.path.dirname( self.cache )
        self.last_accessed_file = os.path.join( cache_dir, key )
        return retval

    def set( self, key, value ):
        retval = FileCache.set( self, key, value )
        cache_dir = os.path.dirname( self.cache )
        self.last_accessed_file = os.path.join( cache_dir, key )
        try:
            file = open( self.last_accessed_file, 'w' )
            file.write( '\r\n\r\n'.join( value.split( '\r\n\r\n' )[1:] ) )
            file.close
        except:
            self.last_accessed_file = None
        return retval

class Http_mod:
    def __init__( self, cache ):
        self.fetcher = Http( FileCache_mod( cache ) )

    def urlopen( self, url ):
        filename = self.urlretrieve( url )
        data = open( filename, 'r' ).read()
        return data

    def urlretrieve( self, url ):
        self.fetcher.request( url )
        return self.fetcher.cache.last_accessed_file

    def get_cache_location( self ):
        return self.fetcher.cache.cache
