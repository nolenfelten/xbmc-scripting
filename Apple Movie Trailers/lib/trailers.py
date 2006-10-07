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
        self.DEBUG = os.path.isfile( os.path.join( os.path.dirname( os.path.dirname( sys.modules['trailers'].__file__ ) ), 'debug.txt' ) )
        if title:
            self.title = title
        self.BASEURL = 'http://www.apple.com'
        if url:
            self.url = self.BASEURL + url
        if self.DEBUG:
            if self.title and self.url:
                print '%s: %s' % ( self.title, self.url )
            else:
                if self.title:
                    print self.title
                if self.url:
                    print self.url
        self.__set_defaults__()
        self.__updated__ = False
        self.__updating__ = False
        self.__serializing__ = False
        self.dialog = xbmcgui.DialogProgress()

    def serialize( self ):
        self.__serializing__ = True
        classname = str( self.__class__ ).split( '\'' )[1].split( '.' )[1]
        
        #root element
        root = ET.Element( classname )

        #begin serialization
        serialize_items = list()
        try:
            if self.title:
                serialize_items += [ 'title' ]
            if self.url:
                serialize_items += [ 'url' ]
        except:
            pass
        serialize_items += self.__update_items__

        for item in serialize_items:
            itemtype = type( self.__dict__[ item ] )
            itemvalue = itemtype()
            itemelement = ET.SubElement( root, item, { 'type': str( itemtype ).split('\'')[1] } )
            # doesn't do nested lists below one level
            if itemtype == type( list() ):
                for i in self.__dict__[ item ]:
                    if str( type( i ) ).split()[0] == '<class':
                        itemelement.append( i.serialize() )
                    else:
                        itemvalue = str( i )
                        itemelement.text = itemvalue
            elif str( itemtype ).split()[0] == '<class':
                itemelement.append( self.__dict__[ item ].serialize() )
            else:
                itemvalue = str( self.__dict__[ item ] )
                itemelement.text = itemvalue
        self.__serializing__ = False
        return root

    def ns( self, text ):
        BASENS = '{http://www.apple.com/itms/}'
        result = list()
        for each in text.split( '/' ):
            result += [ BASENS + each ]
        return '/'.join( result )

    def __set_defaults__( self ):
        self.__update_items__ = list()

    def __update__( self ):
        pass

    def __getattribute__( self, name ):
        try:
            if name in super( Info, self ).__getattribute__( '__update_items__' ):
                if not self.__updated__:
                    if not self.__updating__ and not self.__serializing__:
                        self.__updating__ = True
                        try:
                            self.__update__()
                            self.__updated__ = True
                        except:
                            traceback.print_exc()
                            pass
                        self.__updating__ = False
        except:
            pass
        return super( Info, self ).__getattribute__( name )

    def __setattr__( self, name, value ):
        try:
            self.__dict__[name] = value
        except:
            self.__dict__.update( { name: value } )

class Movie( Info ):
    """
        Exposes the following:
        - title (string)
        - thumbnail (string path to image file, blank string if not found)
        - plot (string)
        - cast (??? string ???)
        - trailer_urls (list of string urls to trailers)
        - watched (boolean)
    """
    def __init__( self, title, url ):
        Info.__init__( self, title, url )
        # needs to fill thumbnail, description, cast, trailer_urls

    def __set_defaults__( self ):
        Info.__set_defaults__( self )
        self.__update_items__ += [ 'thumbnail', 'plot', 'cast', 'trailer_urls', 'watched' ]
        self.thumbnail = ''
        self.plot = _(400) # No description could be retrieved for this title.
        self.cast = 'FIXME: CAST INFO GOES HERE'
        self.trailer_urls = list()
        self.watched = False

    def __update__( self ):
        try:
            # dialog
            self.dialog.create( self.title )
            self.dialog.update( 0 )

            # xml parsing
            element = fetcher.urlopen( self.url )
            element = ET.fromstring( element )
            self.dialog.update( 20 )

            # -- thumbnail --
            thumbnail = element.getiterator( self.ns('PictureView') )[1].get( 'url' )
            # download the actual thumbnail to the local filesystem (or get the cached filename)
            thumbnail = fetcher.urlretrieve( thumbnail )
            if thumbnail:
                self.thumbnail = thumbnail
            self.dialog.update( 40 )

            # -- plot --
            plot = element.getiterator( self.ns('SetFontStyle') )[2].text.encode( 'ascii', 'ignore' )
            plot = plot.strip()
            # remove any linefeeds so we can wrap properly to the text control this is displayed in
            plot = plot.replace( '\r\n', ' ' )
            plot = plot.replace( '\r', ' ' )
            plot = plot.replace( '\n', ' ' )
            if plot:
                self.plot = plot
            self.dialog.update( 60 )

            # -- cast --
            cast = 'FIXME: CAST INFO GOES HERE'
            if cast:
                self.cast = cast
            self.dialog.update( 80 )

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
            self.dialog.update( 100 )
        except:
            traceback.print_exc()
            self.__set_defaults__()
            self.dialog.close()
            raise
        self.dialog.close()


class Genre( Info ):
    """
        Exposes the following:
        - title (string)
        - movies (sorted list of Movie() object instances)
    """
    def __init__( self, title, url ):
        Info.__init__( self, title, url )
        self.is_special = title in [ 'Exclusives', 'Newest' ]
        # needs to provide Movie(), Movie()

    def __set_defaults__( self ):
        Info.__set_defaults__( self )
        self.__update_items__ += [ 'movies' ]
        self.movies = list()

    def __update__( self ):
        try:
            element = fetcher.urlopen( self.url )
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
        self.__update_items__ += [ 'genres' ]
        self.genres = list()

    def __update__( self ):
        try:
            base_xml = fetcher.urlopen( self.BASEXML )
            base_xml = ET.fromstring( base_xml )

            view_matrix = {
                'view1': 'Exclusives',
                'view2': 'Newest',
            }
            elements = base_xml.getiterator( self.ns('Include') )
            for each in elements:
                url = each.get( 'url' )
                for view in view_matrix:
                    if view in url:
                        url = '/moviesxml/h/' + url
                        self.genres += [ Genre( view_matrix[view], url ) ]

            elements = base_xml.getiterator( self.ns('GotoURL') )
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
        except:
            traceback.print_exc()
            self.__set_defaults__()
            raise

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

    def loadDatabase( self ):
        pass

    def saveDatabase( self ):
        root = ET.Element( 'AMT' )
        root.set( 'version', '0.92' )
        root.append( self.serialize() )
        
        # ready to save to file
        print ET.tostring( root )


