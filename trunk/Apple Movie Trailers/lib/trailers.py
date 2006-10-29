import os, sys, traceback
import xbmc, xbmcgui
import cacheurl
import elementtree.ElementTree as ET
import default
import language
import pil_util
import database
DB = database.Database()

fetcher = cacheurl.HTTP()
_ = language.Language().string

class Movie:
    def __init__( self, *args, **kwargs ):
        '''
            0   ( 'title', 'text', True ),
            1   ( 'urls', 'text', None ),
            2   ( 'genre', 'integer', False ),
            3   ( 'poster', 'text', None ),
            4   ( 'thumbnail', 'text', None ),
            5   ( 'thumbnail_watched', 'text', None ),
            6   ( 'plot', 'text', None ),
            7   ( 'actors', 'text', None ),
            8   ( 'studio', 'text', None ),
            9   ( 'rating', 'text', None ),
            10  ( 'rating_url', 'text', None ),
            11  ( 'year', 'integer', None ),
            12  ( 'times_watched', 'integer', None ),
            13  ( 'last_watched', 'text', None ),
            14  ( 'favorite', 'integer', None ),
            15  ( 'saved_location', 'text', None ),
        '''
        self.title = args[0][0]
        self.trailer_urls = eval( args[0][1] )
        self.genre = args[0][2]
        self.poster = args[0][3]
        #self.thumbnail = args[0][4 + ( self.watched > 0 )]
        self.thumbnail = args[0][4]
        self.thumbnail_watched = args[0][5]
        self.plot = args[0][6]
        self.cast = eval( args[0][7] )
        self.studio = args[0][8]
        self.rating = args[0][9]
        self.rating_url = args[0][10]
        self.year = args[0][11]
        self.watched = args[0][12]
        self.watched_date = args[0][13]
        self.favorite = args[0][14]
        self.saved = args[0][15]
        
class Category:
    def __init__( self, *args, **kwargs ):
        self.title = args[0][0]
        if ( len( args[0] ) > 1 ): self.count = args[0][1]
        else: self.count = None
        if ( len( args[0] ) > 2 ): self.url = args[0][2]
        else: self.url = None
        if ( len( args[0] ) > 3 ): self.id = args[0][3]
        else: self.id = None
        if ( len( args[0] ) > 4 ): self.loaded = args[0][4]
        else: self.loaded = None
        
        
class Trailers:
    def __init__( self, genre = 'Exclusives' ):
        self.createDatabase()
        
    def ns( self, text ):
        BASENS = '{http://www.apple.com/itms/}'
        result = list()
        for each in text.split( '/' ):
            result += [ BASENS + each ]
        return '/'.join( result )

    def createDatabase( self ):
        self.categories = []
        self.BASEURL = 'http://www.apple.com'
        self.BASEXML = self.BASEURL + '/moviesxml/h/index.xml'
        self.loadGenres()
        self.loadMovies()
            
    def loadGenres( self ):
        try:
            '''
            self.tables['Genres'] = (
                ( 'title', 'text', True ),
                ( 'url', 'text', None ),
                ( 'id', 'integer', None ), 
                ( 'count', 'integer', None ),
                ( 'loaded', 'integer', None ),
                ( 'trailer_urls', 'blob', None ),
                )
            '''
           
            genre_list = DB.getRecords( 'SELECT title, count, url, id, loaded FROM Genres ORDER BY title', all = True )
            #columns = 'title, url, id, count, loaded', table = 'Genres', orderby = 'title', all = True )
            self.categories = []
            if (genre_list):
                print 'YES GENRE LIST'
                #self.categories = genre_list
                for genre in genre_list:
                    self.categories += [Category( genre )]
            else:
                self.dialog = xbmcgui.DialogProgress()
                self.dialog.create('Loading genre info into database...')
                
                base_xml = fetcher.urlopen( self.BASEXML )
                base_xml = ET.fromstring( base_xml )

                view_matrix = {
                    'view1': 'Exclusives',
                    'view2': 'Newest',
                    }
                elements = base_xml.getiterator( self.ns('Include') )
                genre_id = 0
                genre_dict = dict()
                for each in elements:
                    url = each.get( 'url' )
                    for view in view_matrix:
                        if view in url:
                            url = '/moviesxml/h/' + url
                            #self.dialog.update( -1, 'Current genre: %s' % view_matrix[view] )
                            genre_dict.update( { view_matrix[view]: url } )
                elements = base_xml.getiterator( self.ns('GotoURL') )
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
                genres = genre_dict.keys()
                genres.sort()
                total_cnt = len( genres )
                pct_sect = float( 100 ) / total_cnt
                for cnt, genre in enumerate( genres ):
                    self.dialog.update( int( cnt * pct_sect ), 'Current genre: %s - (%d of %d)' % (genre, cnt + 1, total_cnt, ), '', '' )
                    trailer_urls = self.loadGenreInfo( genre, 2**genre_id, genre_dict[genre], cnt, total_cnt, pct_sect )
                    if ( trailer_urls ):
                        success = DB.addRecord( ( genre, genre_dict[genre], 2**genre_id, len( trailer_urls), 0, repr( trailer_urls) ), 'Genres' )
                        self.categories += [Category( ( genre, genre_dict[genre], 2**genre_id, len( trailer_urls), 0 ) )]
                        ##success = DB.addRecord( ( genre, genre_dict[genre], 2**genre_id, 0, repr( [] ) ), 'Genres' )
                    genre_id += 1
                self.dialog.close()

        except:
            #dialog.close()
            traceback.print_exc()
            #return []
    
    def loadGenreInfo( self, genre, genre_id, url, genre_cnt, total_cnt, pct_sect ):
        try:
            '''
            self.tables['Genres'] = (
                ( 'title', 'text' ),
                ( 'url', 'text' ),
                ( 'id', 'integer' ), 
                ( 'count', 'integer' ),
                ( 'trailer_urls', 'text' ),
                )
            '''
            trailer_urls = DB.getRecords( 'SELECT trailer_urls FROM Genres WHERE title=?', ( genre, ) )
            #columns = 'trailer_urls', table = 'Genres', condition = 'title=', values = ( genre, ) )
            if ( trailer_urls ):
                #print 'trailer_urls',trailer_urls
                return eval( trailer_urls[0] )
            else:
                if url[:7] != 'http://':
                    url = self.BASEURL + url
                is_special = genre in [ 'Exclusives', 'Newest' ]
                next_url = url
                first_url = True
                trailer_dict = dict()
                while next_url:
                    try:
                        element = fetcher.urlopen( next_url )
                        if '<Document' not in element:
                            element = '<Document>' + element + '</Document>'
                        element = ET.fromstring( element )
                        lookup = 'GotoURL'
                        if not is_special:
                            lookup = self.ns( lookup )
                        elements = element.getiterator( lookup )
                        if first_url:
                            next_url = elements[0].get( 'url' )
                            first_url = False
                        else:
                            next_url = elements[2].get( 'url' )
                        if next_url[0] != '/':
                            next_url = '/'.join( url.split( '/' )[:-1] + [ next_url ] )
                        else:
                            next_url = None
                        for element in elements:
                            url2 = element.get( 'url' )
                            title = None
                            if is_special:
                                title = element.getiterator( 'b' )[0].text.encode( 'ascii', 'ignore' )
                            if 'index_1' in url2:
                                continue
                            if '/moviesxml/g' in url2:
                                continue
                            if url2[0] != '/':
                                continue
                            if url2 in trailer_dict.keys():
                                lookup = 'b'
                                if not is_special:
                                    lookup = 'B'
                                    lookup = self.ns( lookup )
                                title = element.getiterator( lookup )[0].text.encode( 'ascii', 'ignore' )
                                trailer_dict[url2] =  title.strip()
                                continue
                            trailer_dict.update( { url2: title } )
                    except:
                        break

                reordered_dict = dict()
                trailer_urls = []
                for key in trailer_dict:
                    reordered_dict.update( { trailer_dict[key]: key } )

                keys = reordered_dict.keys()
                keys.sort()
                trailer_urls = []
                for cnt, key in enumerate( keys ):
                    try:
                        trailer_urls.append( ( key, reordered_dict[key] ) )
                    except:
                        continue
                return trailer_urls
        except:
            ##dialog.close()
            traceback.print_exc()
            return []

    def loadMovies( self ):
        total_cnt = 0
        total_genre_cnt = 0
        for genre in self.categories:
            if ( genre.loaded == 0 ):
                total_cnt += genre.count
                total_genre_cnt += 1
        if ( total_cnt > 0 ):
            if ( xbmcgui.Dialog().yesno('Would you like to load all movie info?', 'Not all movie info is loaded. This process can take from 15 to 45 minutes.', 'No, means you choose to load the info per request.', 'The search function will not be accurate until complete.' ) ):
                try:
                    dialog = xbmcgui.DialogProgress()
                    dialog.create('Loading movie info into database...')
                    pct_sect = float( 100 ) / total_cnt
                    cnt = 0
                    genre_cnt = 0
                    for genre in self.categories :
                        if ( genre.loaded == 0 ):
                            genre_cnt += 1
                            trailer_urls = DB.getRecords( 'SELECT trailer_urls FROM Genres WHERE title=?', ( genre.title, ) )
                            #DB.getRecords( columns = 'trailer_urls', table = 'Genres', condition = 'title=?', values = ( genre.title, ) )
                            for movie in eval( trailer_urls[0] ):
                                cnt += 1
                                dialog.update( int( cnt * pct_sect ) , 'Current genre: %s - (%d of %d)' % (genre.title, genre_cnt, total_genre_cnt, ), '', 'Current trailer: %s' % movie[0] )
                                self.loadMovieInfo( movie[0], genre.id, movie[1] )
                                if ( dialog.iscanceled() ): raise
                            success = DB.updateRecord( columns = ( 'loaded', ), table = 'Genres', values = ( genre.count, ), key_value = genre.title )
                    dialog.close()
                except:
                    dialog.close()
                    traceback.print_exc()
                    xbmcgui.Dialog().ok( 'Loading movie info into database...', 'The operation was aborted.' )
                
    def loadMovieInfo( self, title, genre_id, url ):
        try:
            self.trailer_urls = []
            self.poster = ''
            self.__thumbnail__ = ''
            self.__thumbnail_watched__ = ''
            self.plot = ''
            self.actors = []
            self.studio = ''
            self.rating = ''
            self.rating_url = ''

            genre = DB.getRecords( 'SELECT genre FROM Movies WHERE title=?', ( title, ) )
            if ( genre ):
                if ( not genre_id&genre[0] > 0 ):
                    genre_id += genre[0]
                    success = DB.updateRecord( columns = ( 'genre', ), table = 'Movies', values = ( genre_id, ), key_value = title )
            else:
                if url[:7] != 'http://':
                    url = self.BASEURL + url
                # xml parsing
                element = fetcher.urlopen( url )
                element = ET.fromstring( element )

                # -- thumbnail --
                poster = element.getiterator( self.ns('PictureView') )[1].get( 'url' )
                # download the actual poster to the local filesystem (or get the cached filename)
                poster = fetcher.urlretrieve( poster )
                if poster:
                    self.poster = poster
                    self.__thumbnail__, self.__thumbnail_watched__ = pil_util.makeThumbnails( poster )

                # -- plot --
                plot = element.getiterator( self.ns('SetFontStyle') )[2].text.encode( 'ascii', 'ignore' )
                plot = plot.strip()
                # remove any linefeeds so we can wrap properly to the text control this is displayed in
                plot = plot.replace( '\r\n', ' ' )
                plot = plot.replace( '\r', ' ' )
                plot = plot.replace( '\n', ' ' )
                if plot:
                    self.plot = plot

                # -- actors --
                SetFontStyles = element.getiterator( self.ns('SetFontStyle') )
                actors = list()
                try:
                    for i in range( 5, 10 ):
                        actor = SetFontStyles[i].text.encode( 'ascii', 'ignore' ).strip()
                        if len( actor ):
                            actors += [ actor ]
                            actor_exists = DB.getRecords( 'SELECT count FROM Actors WHERE name=?', ( actor, ) )
                            if ( actor_exists ):
                                success = DB.updateRecord( ( 'count', ) , 'Actors', ( actor_exists[0] + 1, ), key = 'name', key_value = actor )
                            else:
                                success = DB.addRecord( ( actor, 1, ) , 'Actors' )
                except:
                    pass
                self.actors = actors

                # -- studio --
                studio = element.getiterator( self.ns('PathElement') )[1].get( 'displayName' )
                if studio:
                    self.studio = studio.strip()
                    studio_exists = DB.getRecords( 'SELECT count FROM Studios WHERE title=?', ( self.studio, ) )
                    if ( studio_exists ):
                        success = DB.updateRecord( ( 'count', ) , 'Studios', ( studio_exists[0] + 1, ), key_value = self.studio )
                    else:
                        success = DB.addRecord( ( self.studio, 1, ) , 'Studios' )

                # -- rating --2
                url = element.getiterator( self.ns('PictureView') )[2].get( 'url' )
                if url:
                    if '/mpaa' in url:
                        rating_url = fetcher.urlretrieve( url )
                        if rating_url:
                            self.rating_url = rating_url
                            self.rating = os.path.split( url )[1][:-4].replace( 'mpaa_', '' )
                            
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
                        if text.replace( '//', '/' ).replace( '/', '//', 1 ) in trailer_urls:
                            continue
                        trailer_urls += [ text.replace( '//', '/' ).replace( '/', '//', 1 ) ]
                    self.trailer_urls = trailer_urls
                
                info_list = [title]
                info_list += [repr( self.trailer_urls )]
                info_list += [genre_id]
                info_list += [self.poster]
                info_list += [self.__thumbnail__]
                info_list += [self.__thumbnail_watched__]
                info_list += [self.plot]
                info_list += [repr( self.actors )]
                info_list += [self.studio]
                info_list += [self.rating]
                info_list += [self.rating_url]
                info_list += [0]
                info_list += [0]
                info_list += ['']
                info_list += [0]
                info_list += ['']
                success = DB.addRecord( info_list, 'Movies' )
                
            
        except:
            pass#traceback.print_exc()
            
    def updateRecord( self, columns, table, values, key = 'title', key_value = None ):
        success = DB.updateRecord( columns = columns, table = table, values = values, key = key, key_value = key_value )
        return success
        
    def getMovies( self, sql, params = None, all = True ):
        try:
            dialog = xbmcgui.DialogProgress()
            dialog.create( 'Executing query...', 'Please wait a moment.' )
            dialog.update( -1 )
            #print '>>>>>>>>>>>>>>> GET MOVIES <<<<<<<<<<<<<<<<'
            movie_list = DB.getRecords( sql, params, all )
            self.movies = []
            for movie in movie_list:
                self.movies += [Movie( movie )]
        finally:
            dialog.close()
            
    def getCategories( self, sql, params = None, all = True ):
        try:
            dialog = xbmcgui.DialogProgress()
            dialog.create( 'Executing query...', 'Please wait a moment.' )
            dialog.update( -1 )
            category_list = DB.getRecords( sql, params, all )
            self.categories = []
            for category in category_list:
                self.categories += [Category( category )]
        finally:
            dialog.close()
