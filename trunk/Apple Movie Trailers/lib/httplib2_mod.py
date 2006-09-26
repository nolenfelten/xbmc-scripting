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
        datafile = None
        try:
            try:
                # datafile = file( filename, 'rb' )
                datafile = file( filename, 'r' )
                data = datafile.read()
            except:
                data = ''
        finally:
            if datafile:
                datafile.close()
        return data

    def urlretrieve( self, url ):
        response, content = self.fetcher.request( url )
        filename = os.path.join( self.cache_dir, self.fetcher.cache.last_accessed_file )
        if content:
            datafile = None
            try:
                try:
                    # datafile = file( filename, 'wb' )
                    datafile = file( filename, 'w' )
                    datafile.write( content )
                except:
                    import traceback
                    traceback.print_exc()
            finally:
                if datafile:
                    datafile.close()
        return filename
