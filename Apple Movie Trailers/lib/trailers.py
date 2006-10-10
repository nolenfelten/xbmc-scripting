import os, sys, traceback
import xbmc, xbmcgui
import cacheurl
import elementtree.ElementTree as ET
import default
import language
import amt_util

AMT_PK_COMPATIBLE_VERSIONS = [ '0.92' ]

fetcher = cacheurl.HTTP()
_ = language.Language().string

class Info( object ):
    def __init__( self, title = None, url = None ):
        self.DEBUG = os.path.isfile( os.path.join( os.path.dirname( os.path.dirname( sys.modules['trailers'].__file__ ) ), 'debug.txt' ) )
        if title:
            self.title = title
        self.BASEURL = 'http://www.apple.com'
        if url:
            if url[:7] != 'http://':
                url = self.BASEURL + url
            self.url = url
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
        try:
            if self.title:
                root.set( 'title', self.__dict__[ 'title' ] )
            if self.url:
                root.set( 'url', self.__dict__[ 'url' ] )
        except:
            pass

        #begin serialization
        serialize_items = list()
        serialize_items += self.__serialize_items__

        for item in serialize_items:
            itemtype = type( self.__dict__[ item ] )
            itemvalue = itemtype()
            itemelement = ET.SubElement( root, item )
            itemelement.set( 'type', str( itemtype ).split('\'')[1] )
            # doesn't do nested lists below one level
            if itemtype == type( list() ):
                for i in self.__dict__[ item ]:
                    if str( type( i ) ).split()[0] == '<class':
                        ielement = i.serialize()
                        ielement.set( 'type', 'class' )
                        itemelement.append( ielement )
                    else:
                        itemvalue = str( i )
                        itemelement.set( 'type', str( itemtype ).split('\'')[1] )
                        itemelement.text = itemvalue
            elif str( itemtype ).split()[0] == '<class':
                ielement = self.__dict__[ item ].serialize()
                ielement.set( 'type', 'class' )
                itemelement.append( ielement )
            else:
                if itemtype == type( bool() ):
                    itemvalue = str( int( self.__dict__[ item ] ) )
                itemvalue = str( self.__dict__[ item ] )
                itemelement.set( 'type', str( itemtype ).split('\'')[1] )
                itemelement.text = itemvalue
        self.__serializing__ = False
        return root

    def deserialize( self, element ):
        items = element.getchildren()
        for item in items:
            itemtype = item.get( 'type' )
            itemtitle = item.get( 'title', None )
            itemurl = item.get( 'url', None )
            if itemtype == 'class':
                itemvalue = eval( '%s( \'%s\', \'%s\' )' % ( item.tag, itemtitle, itemurl ) )
                itemvalue.deserialize( item )
            elif itemtype == 'list':
                itemvalue = item.text
                if not itemvalue:
                    itemvalue = list()
                    children = item.getchildren()
                    for child in children:
                        childtype = child.get( 'type' )
                        childtitle = child.get( 'title', None )
                        childurl = child.get( 'url', None )
                        if childtype == 'class':
                            childvalue = eval( '%s( \"%s\", \"%s\" )' % ( child.tag, str( childtitle ), str( childurl ) ) )
                            childvalue.deserialize( child )
                        elif childtype == 'list':
                            childvalue = list( child.text )
                        else:
                            childvalue = child.text
                            try:
                                childvalue = eval( '%s(%s)' % ( childtype, childvalue ) )
                            except:
                                childvalue = eval( '%s(%s)' % ( childtype, repr( childvalue ) ) )
                        itemvalue += [ childvalue ]
            else:
                itemvalue = item.text
                try:
                    itemvalue = eval( '%s(%s)' % ( itemtype, itemvalue ) )
                except:
                    itemvalue = eval( '%s(%s)' % ( itemtype, repr( itemvalue ) ) )
            self.__setattr__( item.tag, itemvalue )

    def ns( self, text ):
        BASENS = '{http://www.apple.com/itms/}'
        result = list()
        for each in text.split( '/' ):
            result += [ BASENS + each ]
        return '/'.join( result )

    def __set_defaults__( self ):
        self.__update_items__ = list()
        self.__serialize_items__ = [ '__updated__' ]

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
        - poster (string path to image file, blank string if not found)
        - plot (string)
        - cast (??? string ???)
        - trailer_urls (list of string urls to trailers)
        - watched (boolean)
        - favorite (boolean)
    """
    def __init__( self, title, url ):
        Info.__init__( self, title, url )
        # needs to fill thumbnail, description, cast, trailer_urls

    def __set_defaults__( self ):
        Info.__set_defaults__( self )
        self.__update_items__ += [ '__thumbnail__', '__thumbnail_watched__', 'poster', 'plot', 'cast', 'trailer_urls' ]
        self.__serialize_items__ += self.__update_items__ + [ 'watched', 'favorite' ]
        self.__thumbnail__ = ''
        self.__thumbnail_watched__ = ''
        self.poster = ''
        self.plot = _(400) # No description could be retrieved for this title.
        self.cast = 'FIXME: CAST INFO GOES HERE'
        self.trailer_urls = list()
        self.watched = False
        self.favorite = False

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
            poster = element.getiterator( self.ns('PictureView') )[1].get( 'url' )
            # download the actual poster to the local filesystem (or get the cached filename)
            poster = fetcher.urlretrieve( poster )
            if poster:
                self.poster = poster
                self.__thumbnail_unwatched__, self.__thumbnail__ = amt_util.makeThumbnails( poster )
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

    def __getattribute__( self, name ):
        retval = ''
        try:
            retval = Info.__getattribute__( self, name )
            if name == 'thumbnail':
                if self.watched:
                    retval = self.__thumbnail_watched__
                else:
                    retval = self.__thumbnail__
        except:
            pass
        return retval

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
        self.__serialize_items__ += self.__update_items__
        self.movies = list()

    def __update__( self ):
        try:
            next_url = self.url
            first_url = True
            trailer_dict = dict()
            dialog = xbmcgui.DialogProgress()
            dialog.create( _(66), _(67) )
            dialog.update( 0 )
            while next_url:
                try:
                    element = fetcher.urlopen( next_url )
                    if '<Document' not in element:
                        element = '<Document>' + element + '</Document>'
                    element = ET.fromstring( element )
                    
                    lookup = 'GotoURL'
                    if not self.is_special:
                        lookup = self.ns( lookup )
                    elements = element.getiterator( lookup )

                    if first_url:
                        next_url = elements[0].get( 'url' )
                        first_url = False
                    else:
                        next_url = elements[2].get( 'url' )
                    if next_url[0] != '/':
                        next_url = '/'.join( self.url.split( '/' )[:-1] + [ next_url ] )
                    else:
                        next_url = None

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
                except:
                    break

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
            dialog.close()
        except:
            traceback.print_exc()
            self.__set_defaults__()
            dialog.close()
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
        self.loadDatabase()

    def __set_defaults__( self ):
        Info.__set_defaults__( self )
        self.__update_items__ += [ 'genres' ]
        self.__serialize_items__ += self.__update_items__
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

    def loadDatabase( self ):
        datafile = None
        try:
            if not os.path.isfile( self.DATAFILE ):
                return
            datafile = open( self.DATAFILE, 'r' )
            data = datafile.read()
            root = ET.fromstring( data )
            version = root.get( 'version', default = '0.00' )
            if version not in AMT_PK_COMPATIBLE_VERSIONS:
                header = _(59) # Database file invalid...
                line1 = _(60).split('|')[0] # Your database file is incompatible with this version
                line2 = _(60).split('|')[1] # of AMT. It must be regenerated.
                xbmcgui.Dialog().ok( header, line1, line2 )
                datafile.close()
                if os.path.isfile( self.DATAFILE ):
                    os.remove( self.DATAFILE )
            else:
                if ET.iselement( root ):
                    element = root.getchildren()[0]
                    self.deserialize( element )
        except:
            if datafile:
                datafile.close()
            traceback.print_exc()
            header = _(64) # Error
            line1 = 'Unable to properly load AMT.pk' # Unable to properly load AMT.pk
            xbmcgui.Dialog().ok( header, line1 )
            raise
        if datafile:
            datafile.close()

    def saveDatabase( self ):
        root = ET.Element( 'AMT' )
        root.set( 'version', default.__version__ )
        root.append( self.serialize() )

        # ready to save to file
        datafile = None
        try:
            datadir = os.path.dirname( self.DATAFILE )
            if not os.path.isdir( datadir ):
                os.makedirs( datadir )
            if os.path.isfile( self.DATAFILE ):
                os.remove( self.DATAFILE )
            datafile = open( self.DATAFILE, 'w' )
            data = ET.tostring( root )
            datafile.write( data )
        except:
            if datafile:
                datafile.close()
            traceback.print_exc()
            header = _(64) # Error
            line1 = _(65) # Unable to properly update AMT.pk
            xbmcgui.Dialog().ok( header, line1 )
            raise
        if datafile:
            datafile.close()


