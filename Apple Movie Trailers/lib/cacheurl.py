import os

class HTTP:
    def __init__( self, cache = '.cache' ):
        # this module's path
        import sys
        self.module_dir = os.path.dirname( sys.modules['cacheurl'].__file__ )
        del sys

        # set the cache directory; default to a .cache directory off of the location where this module is
        self.cache_dir = cache
        if self.cache_dir[0] == '.':
            self.cache_dir = os.path.join( self.module_dir, self.cache_dir )
        if not os.path.isdir( self.cache_dir ):
            os.makedirs( self.cache_dir )

        # set default blocksize (this may require tweaking; cachedhttp1.3 had it set at 8192)
        self.blocksize = 8192

    def urlopen( self, url ):
        # retrieve the file so it is cached
        filepath = self.urlretrieve( url )
        # read the data out of the file
        filehandle = open( filepath, 'rb' )
        data = filehandle.read()
        return data

    def urlretrieve( self, url ):
        import urllib2
        opened = urllib2.urlopen( url )
        del urllib2

        # this is the actual url that we got (redirection, etc)
        actual_url = opened.geturl()
        # info dict about the file (headers and such)
        info = opened.info()
        # construct the filename
        import md5
        filename = md5.new( actual_url ).hexdigest() + os.path.splitext( actual_url )[1]
        del md5
        # ..and the filepath
        filepath = os.path.join( self.cache_dir, filename )
        # save the total expected size of the file, based on the Content-Length header
        totalsize = int( info['Content-Length'] )

        # if the file is already in the cache, return that filename
        if os.path.isfile( filepath ) and os.path.getsize( filepath ) == totalsize:
            return filepath

        # write the data to the cache
        filehandle = open( filepath, 'wb' )
        filedata = '...'
        size_read_so_far = 0
        do_continue = True
        while len( filedata ):
            filedata = opened.read( self.blocksize )
            if len( filedata ):
                filehandle.write( filedata )
                size_read_so_far += len( filedata )
                do_continue = self.on_data( actual_url, filepath, totalsize, size_read_so_far )
            if len( filedata ) < self.blocksize:
                break
            if not do_continue:
                break
        filehandle.close()
        is_completed = os.path.getsize( filepath ) == totalsize

        # notify handler of being finished
        self.on_finished( actual_url, filepath, totalsize, is_completed )

        # if the file transfer was halted before completing, remove the partial file from cache
        if not is_completed:
            os.remove( filepath )
            filepath = None

        return filepath

    def on_data( self, url, filepath, filesize, size_read_so_far ):
        return True

    def on_finished( self, url, filepath, filesize, is_completed ):
        pass


import xbmcgui

class HTTPProgress( HTTP ):
    def __init__( self, cache = '.cache' ):
        HTTP.__init__( self, cache )
        self.dialog = xbmcgui.DialogProgress()

    def urlretrieve( self, url ):
        self.dialog.create( 'Downloading..', url, '> ' )
        self.dialog.update( 0 )
        return HTTP.urlretrieve( self, url )

    def on_data( self, url, filepath, filesize, size_read_so_far ):
        percentage = int( float( size_read_so_far ) / filesize ) * 100
        self.dialog.update( percentage, url, '> ' + os.path.split( filepath )[1] )
        if self.dialog.iscanceled():
            return False
        return True

    def on_finished( self, url, filepath, filesize, is_completed ):
        self.dialog.close()

