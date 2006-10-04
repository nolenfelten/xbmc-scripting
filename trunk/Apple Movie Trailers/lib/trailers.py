import os, sys, traceback
import xbmc, xbmcgui
import cacheurl
import elementtree.ElementTree as ET
#import default
import language

AMT_PK_COMPATIBLE_VERSIONS = [ '0.91' ]

fetcher = cacheurl.HTTP()
_ = language.Language().string

class Info( object ):
    def __init__( self, title = None, url = None ):
        if title:
            self.title = title
        self.BASEURL = 'http://www.apple.com'
        if url:
            self.url = self.BASEURL + url
        self.__set_defaults__()
        self.__updated__ = False
        self.__updating__ = False

    def ns( text ):
        BASENS = '{http://www.apple.com/itms/}'
        result = list()
        for each in text.split( '/' ):
            result += [ BASENS + each ]
        return '/'.join( result )

    def __set_defaults__( self ):
        self.__all__ = list()
        try:
            if self.title:
                self.__all__ += [ 'title' ]
            if self.url:
                self.__all__ += [ 'url' ]
        except:
            pass

    def __update__( self ):
        pass

    def __getattribute__( self, name ):
        try:
            if name in super( Info, self ).__getattribute__( '__all__' ):
                if not self.__updated__ and not self.__updating__:
                    self.__updating__ = True
                    try:
                        self.__update__()
                        self.__updated__ = True
                    except:
                        pass
                    self.__updating__ = False
        except:
            pass
        value = super( Info, self ).__getattribute__( name )
        if name != '__dict__':
            print '-- get %s:' % name, value
        return value

    def __setattr__( self, name, value ):
        try:
            self.__dict__[name] = value
        except:
            self.__dict__.update( { name: value } )
        print '-- set %s:' % name, value

class Movie( Info ):
    """
        Exposes the following:
        - title (string)
        - thumbnail (string path to image file, blank string if not found)
        - plot (string)
        - cast (??? string ???)
        - trailer_urls (list of string urls to trailers)
    """
    def __init__( self, title, url ):
        Info.__init__( self, title, url )
        # needs to fill thumbnail, description, cast, trailer_urls

    def __set_defaults__( self ):
        Info.__set_defaults__( self )
        self.__all__ += [ 'thumbnail', 'plot', 'cast', 'trailer_urls' ]
        self.thumbnail = ''
        self.plot = _(400) # No description could be retrieved for this title.
        self.cast = 'FIXME: CAST INFO GOES HERE'
        self.trailer_urls = list()

    def __update__( self ):
        try:
            element = fetcher.urlopen( self.url )
            element = ET.fromstring( element )

            # -- thumbnail --
            thumbnail = element.getiterator( self.ns('PictureView') )[1].get( 'url' )
            # download the actual thumbnail to the local filesystem (or get the cached filename)
            thumbnail = fetcher.urlretrieve( thumbnail )
            if thumbnail:
                self.thumbnail = thumbnail

            # -- plot --
            plot = element.getiterator( self.ns('SetFontStyle') )[2].text.encode( 'ascii', 'ignore' )
            plot = plot.strip()
            # remove any linefeeds so we can wrap properly to the text control this is displayed in
            plot = plot.replace( '\r\n', ' ' )
            plot = plot.replace( '\r', ' ' )
            plot = plot.replace( '\n', ' ' )
            if plot:
                self.plot = plot

            # -- cast --
            cast = 'FIXME: CAST INFO GOES HERE'
            if cast:
                self.cast = cast

            # -- trailer urls --
            urls = list()
            for each in element.getiterator( self.ns('GotoURL') ):
                url = each.get( 'url' )
                if 'index_1' in url:
                    continue
                if '/moviesxml/g' in url:
                    continue
                if url[0] != '/':
                    continue
                if url in urls:
                    continue
                urls += [ url ]
            if len( urls ):
                url = self.BASEURL + urls[0]
                element = fetcher.urlopen( url )
                element = ET.fromstring( element )
                trailer_urls = list()
                for each in element.getiterator( self.ns('string') ):
                    text = each.text
                    if text == None:
                        continue
                    if 'http' not in text:
                        continue
                    if 'movies.apple.com' not in text:
                        continue
                    if text[-3:] == 'm4v':
                        continue
                    if text in trailer_urls:
                        continue
                    trailer_urls += [ text ]
                self.trailer_urls = trailer_urls
        except:
            traceback.print_exc()
            self.__set_defaults__()
            raise


class Genre( Info ):
    """
        Exposes the following:
        - title (string)
        - movies (sorted list of Movie() object instances)
    """
    def __init__( self, title, url ):
        Info.__init__( self, title, url )
        self.is_special = self.title in [ 'Exclusives', 'Newest' ]
        # needs to provide Movie(), Movie()

    def __set_defaults__( self ):
        Info.__set_defaults__( self )
        self.__all__ += [ 'movies' ]
        self.movies = list()

    def __update__( self ):
        try:
            element = fetcher.urlopen( url )
            if '<Document' not in element:
                element = '<Document>' + element + '</Document>'
            element = ET.fromstring( element )
            
            lookup = 'GotoURL'
            if not self.is_special:
                lookup = self.ns( lookup )
            elements = element.getiterator( lookup )
            trailer_dict = dict()
            for element in elements:
                url2 = element.get( 'url' )
                title = None
                if self.is_special:
                    title = element.getiterator( 'b' )[0].text.encode( 'ascii', 'ignore' )
                if 'index_1' in url2:
                    continue
                if '/moviesxml/g' in url2:
                    continue
                if url2[0] != '/':
                    continue
                if url2 in trailer_dict.keys():
                    lookup = 'b'
                    if not self.is_special:
                        lookup = 'B'
                        lookup = self.ns( lookup )
                    title = element.getiterator( lookup )[0].text.encode( 'ascii', 'ignore' )
                    trailer_dict[url2] = title
                    continue
                trailer_dict.update( { url2: title } )
            reordered_dict = dict()
            for key in trailer_dict:
                reordered_dict.update( { trailer_dict[key]: key } )

            movies = list()
            keys = reordered_dict.keys()
            keys.sort()
            for key in keys:
                try:
                    movie = Movie( key, reordered_dict[key] )
                except:
                    continue
                movies += [ movie ]
            if len( movies ):
                self.movies = movies
        except:
            traceback.print_exc()
            self.__set_defaults__()
            raise

class Trailers( Info ):
    """
        Exposes the following:
        - genres (sorted list of Genre() object instances)
    """
    def __init__( self ):
        self.DATAFILE = os.path.join( os.path.dirname( os.path.dirname( sys.modules['trailers'].__file__ ) ), 'data', 'AMT.pk' )
        Info.__init__( self )
        self.BASEXML = self.BASEURL + '/moviesxml/h/index.xml'

    def __set_defaults__( self ):
        # import pickle
        # try:
            # if not os.path.isfile( self.DATAFILE ):
                # raise
            # datafile = open( self.DATAFILE, 'r' )
            # version, data = pickle.load( datafile )
            # datafile.close()
            # if version not in AMT_PK_COMPATIBLE_VERSIONS:
                # header = _(59) # Database file invalid...
                # line1 = _(60).split('|')[0] # Your database file is incompatible with this version
                # line2 = _(60).split('|')[1] # of AMT. It must be regenerated.
                # xbmcgui.Dialog().ok( header, line1, line2 )
                # raise
        # except:
            # data = list()
        # finally:
            # self.genres = data
        # del pickle
        Info.__set_defaults__( self )
        self.__all__ += [ 'genres' ]
        self.genres = list()

    def __update__( self ):
        base_xml = fetcher.urlopen( self.BASEXML )
        base_xml = ET.fromstring( base_xml )

        view_matrix = {
            'view1': 'Exclusives',
            'view2': 'Newest',
        }
        elements = base_xml.getiterator( ns('Include') )
        for each in elements:
            url = each.get( 'url' )
            for view in view_matrix:
                if view in url:
                    url = '/moviesxml/h/' + url
                    self.genres += [ Genre( view_matrix[view], url ) ]

        elements = base_xml.getiterator( ns('GotoURL') )
        genre_dict = dict()
        for each in elements:
            url = each.get( 'url' )
            name = ' '.join( url.split( '/' )[-1].split( '_' )[:-1] )
            genre_caps = list()
            # smart capitalization of the genre name
            for word in name.split():
                # only prevent capitalization of these words if they aren't the leading word in the genre name
                # ie, 'the top rated' becomes 'The Top Rated', but 'action and adventure' becomes 'Action and Adventure'
                cap = True
                if word != name[0]:
                    if word == 'and':
                        cap = False
                    if word == 'of':
                        cap = False
                    if word == 'a':
                        cap = False
                if cap:
                    genre_caps += [ word.capitalize() ]
                else:
                    genre_caps += [ word ]
            name = ' '.join( genre_caps )
            if '/moviesxml/g' in url:
                genre_dict.update( { name: url } )
            genre_list = genre_dict.keys()
            genre_list.sort()
            for genre in genre_list:
                try:
                    self.genres += [ Genre( genre, genre_dict[genre] ) ]
                except:
                    continue

    def update_all( self ):
        pass
        # header = _(61) # Update all genre and movie information...
        # line1 = _(62) # Are you sure you want to do this?
        # line2 = _(63).split('|')[0] # Updating can take anywhere from 5 - 15 minutes,
        # line3 = _(63).split('|')[1] # depending upon your connection speed.
        # if xbmcgui.Dialog().yesno( header, line1, line2, line3 ):
            # try:
                # if os.path.isfile( self.DATAFILE ):
                    # os.remove( self.DATAFILE )
                # header = _(73) # Clear cache folder...
                # line1 = _(74).split('|')[0] # Updating your database will be much faster, but possibly
                # line2 = _(74).split('|')[1] # out of date, without clearing your cache.
                # if xbmcgui.Dialog().yesno( header, line1, line2 ):
                    # fetcher.clear_cache()
            # except:
                # pass
            # import pickle
            # self.genres = dict()
            # try:
                # self.__update_genre_list__()
                # datadir = os.path.dirname( self.DATAFILE )
                # if not os.path.isdir( datadir ):
                    # os.makedirs( datadir )
                # datafile = open( self.DATAFILE, 'w' )
                # pickle.dump( [ default.__version__, self.genres ], datafile )
                # datafile.close()
            # except:
                # traceback.print_exc()
                # header = _(64) # Error
                # line1 = _(65) # Unable to properly update AMT.pk
                # xbmcgui.Dialog().ok( header, line1 )
                # raise
            # del pickle

