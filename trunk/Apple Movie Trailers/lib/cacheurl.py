import os, urllib2, md5, traceback

__scriptname__ = 'cacheurl'
__version__ = '0.1'

DEBUG = False

class HTTP:
    def __init__( self, cache = '.cache', actual_filename = False, flat_cache = False ):
        # this module's path
        import sys
        self.module_dir = os.path.dirname( sys.modules['cacheurl'].__file__ )
        self.default_data_dir = os.path.join( os.path.dirname( self.module_dir ), 'data' )
        del sys

        # set the cache directory; default to a .cache directory off of the location where this module is
        self.cache_dir = cache
        if self.cache_dir[0] == '.':
            self.cache_dir = os.path.join( self.default_data_dir, self.cache_dir )
        if DEBUG: print 'cache dir: %s' % self.cache_dir

        # flat_cache means that each request will be cached in a single reused file; basically a non-persistent cache
        self.flat_cache = flat_cache

        # normally, an md5 hexdigest will be used to determine a unique filename for each request, but with actual_filename set to True, the real filename will be used
        # this can result in overwriting previously cached results if not used carefully
        self.actual_filename = actual_filename

        # set default blocksize (this may require tweaking; cachedhttp1.3 had it set at 8192)
        self.blocksize = 8192

    def clear_cache( self ):
        try:
            for root, dirs, files in os.walk( self.cache_dir, topdown = False ):
                for name in files:
                    os.remove( os.path.join( root, name ) )
                os.rmdir( root )
        except:
            traceback.print_exc()
            raise

    def urlopen( self, url ):
        # retrieve the file so it is cached
        filepath = self.urlretrieve( url )
        # read the data out of the file
        data = ''
        if filepath:
            filehandle = open( filepath, 'rb' )
            data = filehandle.read()
            if DEBUG: print data[:100]
        return data

    def urlretrieve( self, url ):
        try:
            request = urllib2.Request( url )
            request.add_header( 'User-Agent', '%s/%s' % ( __scriptname__, __version__ ) )
            opened = urllib2.urlopen( request )
        except:
            traceback.print_exc()

        # this is the actual url that we got (redirection, etc)
        actual_url = opened.geturl()
        if DEBUG: print 'Actual Url: %s' % actual_url
        # info dict about the file (headers and such)
        info = opened.info()
        if DEBUG: print 'Headers:'
        for header in info:
            if DEBUG: print ' %s: %s' % ( header, info[header] )
        # construct the filename
        if self.flat_cache:
            filename = 'flat_cache' + os.path.splitext( actual_url )[1]
        elif self.actual_filename:
            filename = actual_url.split( '/' )[-1]
        else:
            filename = md5.new( actual_url ).hexdigest() + os.path.splitext( actual_url )[1]
        # ..and the filepath
        filepath = os.path.join( self.cache_dir, filename )
        if DEBUG: print 'File path: %s' % filepath
        # save the total expected size of the file, based on the Content-Length header
        totalsize = int( info['Content-Length'] )
        if DEBUG: print 'File size: %i' % totalsize
        try:
            is_completed = os.path.getsize( filepath ) == totalsize
        except:
            is_completed = False
        if DEBUG: print 'Is file complete?: %s' % is_completed

        # if the file is already in the cache, return that filename
        if os.path.isfile( filepath ) and is_completed:
            # notify handler of being finished
            self.on_finished( actual_url, filepath, totalsize, is_completed )
            return filepath

        # create the cache dir if it doesn't exist
        if not os.path.isdir( self.cache_dir ):
            os.makedirs( self.cache_dir )

        # write the data to the cache
        try:
            filehandle = open( filepath, 'wb' )
            filedata = '...'
            size_read_so_far = 0
            do_continue = True
            while len( filedata ):
                filedata = opened.read( self.blocksize )
                if len( filedata ):
                    if DEBUG: print 'got filedata'
                    filehandle.write( filedata )
                    size_read_so_far += len( filedata )
                    do_continue = self.on_data( actual_url, filepath, totalsize, size_read_so_far )
                if len( filedata ) < self.blocksize:
                    break
                if not do_continue:
                    break
            filehandle.close()
        except OSError:
            xbmcgui.Dialog().ok( 'OS Error...', OSError.errno, OSError.strerror )
        except IOError:
            xbmcgui.Dialog().ok( 'IO Error...', IOError.errno, IOError.strerror )

        try:
            is_completed = os.path.getsize( filepath ) == totalsize
        except:
            is_completed = False
        if DEBUG: print 'Is file complete?: %s' % is_completed

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
    def __init__( self, cache = '.cache', actual_filename = False, flat_cache = False ):
        HTTP.__init__( self, cache, actual_filename, flat_cache )
        self.dialog = xbmcgui.DialogProgress()
        self.status_symbols = [ '-', '\\', '|', '/' ]
        self.status_symbol = 0

    def urlretrieve( self, url ):
        self.dialog.create( 'Downloading...', url.split( '/' )[-1] )
        self.dialog.update( 0 )
        return HTTP.urlretrieve( self, url )

    def on_data( self, url, filepath, filesize, size_read_so_far ):
        percentage = int( float( size_read_so_far ) / filesize * 100 )
        self.status_symbol += 1
        if self.status_symbol >= len( self.status_symbols ):
            self.status_symbol = 0
        self.dialog.update( percentage, url.split( '/' )[-1], '%i%% (%i/%i) %s ' % ( percentage, size_read_so_far, filesize, self.status_symbols[self.status_symbol] ) )
        if self.dialog.iscanceled():
            return False
        return True

    def on_finished( self, url, filepath, filesize, is_completed ):
        self.dialog.close()
        self.status_symbol = 0

class HTTPProgressSave( HTTPProgress ):
    def __init__( self, save_location = None ):
        if save_location:
            HTTPProgress.__init__( self, save_location, actual_filename = True )
        else:
            HTTPProgress.__init__( self, flat_cache = True )

    def on_finished( self, url, filepath, filesize, is_completed ):
        if is_completed and os.path.splitext( filepath )[1] in [ '.mov', '.avi' ]:
            try:
                if ( not os.path.isfile( filepath + '.conf' ) ):
                    f = open( filepath + '.conf' , 'w' )
                    f.write( 'nocache=1' )
                    f.close()
            except:
                traceback.print_exc()
                pass
        return HTTPProgress.on_finished( self, url, filepath, filesize, is_completed )
