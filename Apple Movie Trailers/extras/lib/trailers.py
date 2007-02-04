import os, sys, traceback
import xbmc, xbmcgui
import cacheurl
import elementtree.ElementTree as ET
import default
import language
import pil_util
import database

fetcher = cacheurl.HTTP()
_ = language.Language().string
DB = database.Database( language=_ )

cwd = os.path.join( os.path.dirname( sys.modules['default'].__file__ ), 'extras', 'data', '.cache\\' )

class Movie:
    def __init__( self, *args, **kwargs ):
        '''
            0   ( 'title', 'text', True ),
            1   ( 'url', 'text', None ),
            2   ( 'trailer_urls', 'text', None ),
            3   ( 'genre', 'integer', False ),
            4   ( 'poster', 'text', None ),
            5   ( 'thumbnail', 'text', None ),
            6   ( 'thumbnail_watched', 'text', None ),
            7   ( 'plot', 'text', None ),
            8   ( 'actors', 'text', None ),
            9   ( 'studio', 'text', None ),
            10  ( 'rating', 'text', None ),
            11  ( 'rating_url', 'text', None ),
            12  ( 'year', 'integer', None ),
            13  ( 'times_watched', 'integer', None ),
            14  ( 'last_watched', 'text', None ),
            15  ( 'favorite', 'integer', None ),
            16  ( 'saved_location', 'text', None ),
        '''
        self.title = args[0][0]
        self.trailer_urls = eval( args[0][2] )
        self.genre = args[0][3]
        self.poster = os.path.join( cwd, args[0][4] )
        #self.thumbnail = args[0][4 + ( self.watched > 0 )]
        self.thumbnail = os.path.join( cwd, args[0][5] )
        self.thumbnail_watched = os.path.join( cwd, args[0][6] )
        self.plot = args[0][7]
        self.cast = eval( args[0][8] )
        self.studio = args[0][9]
        self.rating = args[0][10]
        self.rating_url = os.path.join( cwd, args[0][11] )
        self.year = args[0][12]
        self.watched = args[0][13]
        self.watched_date = args[0][14]
        self.favorite = args[0][15]
        self.saved = args[0][16]
        
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
            self.categories = []
            if (genre_list):
                for genre in genre_list:
                    self.categories += [Category( genre )]
            else:
                dialog = xbmcgui.DialogProgress()
                dialog.create(_( 66 ))
                
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
                genre_records = ()
                for cnt, genre in enumerate( genres ):
                    dialog.update( int( ( cnt + 1 ) * pct_sect ), '%s: %s - (%d of %d)' % (_( 87 ), genre, cnt + 1, total_cnt, ), '', '' )
                    trailer_urls = self.loadGenreInfo( genre, 2**genre_id, genre_dict[genre], cnt, total_cnt, pct_sect )
                    if ( trailer_urls ):
                        genre_records += ( ( genre, genre_dict[genre], 2**genre_id, len( trailer_urls), 0, repr( trailer_urls), ), )
                        self.categories += [Category( ( genre, len( trailer_urls), genre_dict[genre], 2**genre_id, 0 ) )]
                    genre_id += 1
                #dialog.update( 100, _( 43 ) )
                dialog.update( 100, '%s: %s - (%d of %d)' % (_( 87 ), genre, cnt + 1, total_cnt, ), '', '-----> %s <-----' % (_( 43 ), ) )
                success = DB.addRecords( 'Genres', genre_records )
                dialog.close()

        except:
            dialog.close()
            traceback.print_exc()
            #return []
    
    def loadGenreInfo( self, genre, genre_id, url, genre_cnt, total_cnt, pct_sect ):
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
            trailer_urls = DB.getRecords( 'SELECT trailer_urls FROM Genres WHERE title=?', ( genre, ) )
            if ( trailer_urls ):
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
            dialog.close()#####
            traceback.print_exc()
            return []

    def loadMovies( self ):
        total_cnt = 0
        total_genre_cnt = 0
        for genre in self.categories:
            if ( genre.loaded == 0 ):
                total_cnt += genre.count
                total_genre_cnt += 1
        if ( total_cnt > 0 and DB.created == True ):
            self.load_all = xbmcgui.Dialog().yesno( _( 44 ), '%s: %s' % ( _( 229 ), _( 40 ), ), '%s: %s' % ( _( 230 ), _( 41 ), ), '', _( 230 ), _( 229 ) )
            import time
            start_time = time.time()
            try:
                dialog = xbmcgui.DialogProgress()
                dialog.create( '%s   (%s)' % ( _( 70 ), _( 229 + ( not self.load_all ) ), ) )
                pct_sect = float( 100 ) / total_cnt
                cnt = 0
                genre_cnt = 0
                for genre in self.categories :
                    if ( genre.loaded == 0 ):
                        genre_cnt += 1
                        trailer_urls = DB.getRecords( 'SELECT trailer_urls FROM Genres WHERE title=?', ( genre.title, ) )
                        self.clearRecordVariables()#####
                        for movie in eval( trailer_urls[0] ):
                            cnt += 1
                            dialog.update( int( cnt * pct_sect ) , '%s: %s - (%d of %d)' % ( _( 87 ), genre.title, genre_cnt, total_genre_cnt, ), '%s: (%d of %d)' % ( _( 88 ), cnt, total_cnt, ), '%s' % ( movie[0], ) )
                            success = self.loadMovieInfo( movie[0], genre.id, movie[1] )
                            if ( dialog.iscanceled() ): raise
                        dialog.update( int( cnt * pct_sect ), '%s: %s - (%d of %d)' % ( _( 87 ), genre.title, genre_cnt, total_genre_cnt, ), '%s: (%d of %d)' % ( _( 88 ), cnt, total_cnt, ), '-----> %s <-----' % ( _( 43 ), ) )
                        self.writeMovieInfo()#####
                        #if ( self.load_all ):
                        success = DB.updateRecords( 'Genres', ( 'loaded', ), ( ( genre.count, genre.title, ), ), 'title' )
                dialog.close()
                end_time = time.time()
                minutes =  float( end_time - start_time ) / 60
                print "*** Start time: %s - End Time: %s - Total time: %d minutes" % ( time.ctime( start_time ), time.ctime( end_time ), minutes, )
            except:
                dialog.close()
                traceback.print_exc()
                xbmcgui.Dialog().ok( _( 70 ), _( 86 ) )

    def setDefaultMovieInfo( self, title, url, record ):
        if ( not record ):
            record = ( '', '', repr( [] ), 0, '', '', '', '', repr( [] ), '', '', '', 0, 0, '', 0, '', )
        self.trailer_urls = eval( record[ 2 ] )
        self.poster = record[ 4 ]
        self.__thumbnail__ = record[ 5 ]
        self.__thumbnail_watched__ = record[ 6 ]
        self.plot = record[ 7 ]
        self.actors = eval( record[ 8 ] )
        self.studio = record[ 9 ]
        self.rating = record[ 10 ]
        self.rating_url = record[ 11 ]
        self.year = record[ 12 ]
        self.times_watched = record[ 13 ]
        self.last_watched = record[ 14 ]
        self.favorite = record[ 15 ]
        self.saved_location = record[ 16 ]
        
    def loadMovieInfo( self, title, genre_id, url ):
        try:
            record = DB.getRecords( 'SELECT * FROM Movies WHERE title=?', ( title, ) )
            if ( record and genre_id != -1 ):
                if ( not genre_id&record[ 3 ] > 0 ):
                    genre_id += record[ 3 ]
                    success = DB.updateRecords( 'Movies', ( 'genre', ), ( ( genre_id, title, ), ), 'title' )
            else:
                self.setDefaultMovieInfo( title, url, record )
                if ( self.actors or self.studio ): update_other = False
                else: update_other = True
                if ( self.load_all ):
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
                    plot = element.getiterator( self.ns('SetFontStyle') )[2].text.encode( 'ascii', 'ignore' ).strip()
                    if plot:
                        # remove any linefeeds so we can wrap properly to the text control this is displayed in
                        plot = plot.replace( '\r\n', ' ' )
                        plot = plot.replace( '\r', ' ' )
                        plot = plot.replace( '\n', ' ' )
                        self.plot = plot

                    # -- actors --
                    SetFontStyles = element.getiterator( self.ns('SetFontStyle') )
                    actors = list()
                    for i in range( 5, 10 ):
                        #actor = SetFontStyles[i].text.encode( 'ascii', 'ignore' ).replace( '(The voice of)', '' ).replace( '(voice)', '' ).title().strip()
                        actor = SetFontStyles[i].text.encode( 'ascii', 'ignore' ).replace( '(The voice of)', '' ).title().strip()
                        if ( len( actor ) and actor[ 0 ] != '.' and actor != '1:46') :
                            actors += [ actor ]
                    self.actors = actors
                    self.actors.sort()
                    
                    # -- studio --
                    studio = element.getiterator( self.ns('PathElement') )[1].get( 'displayName' ).strip()
                    if studio:
                        self.studio = studio#.strip()
                    
                    # -- rating --2
                    temp_url = element.getiterator( self.ns('PictureView') )[2].get( 'url' )
                    if temp_url:
                        if '/mpaa' in temp_url:
                            rating_url = fetcher.urlretrieve( temp_url )
                            if rating_url:
                                self.rating_url = rating_url
                                self.rating = os.path.split( temp_url )[1][:-4].replace( 'mpaa_', '' )
                                
                    # -- trailer urls --
                    urls = list()
                    for each in element.getiterator( self.ns('GotoURL') ):
                        temp_url = each.get( 'url' )
                        if 'index_1' in temp_url:
                            continue
                        if '/moviesxml/g' in temp_url:
                            continue
                        if temp_url[0] != '/':
                            continue
                        if temp_url in urls:
                            continue
                        urls += [ temp_url ]
                    if len( urls ):
                        temp_url = self.BASEURL + urls[0]
                        element = fetcher.urlopen( temp_url )
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
                info_list = (title,)
                info_list += (url,)
                info_list += (repr( self.trailer_urls ),)
                if ( record ): info_list += (record[ 3 ],)
                else: info_list += (genre_id,)
                info_list += (self.poster.replace( cwd, '' ),)
                info_list += (self.__thumbnail__.replace( cwd, '' ),)
                info_list += (self.__thumbnail_watched__.replace( cwd, '' ),)
                info_list += (self.plot,)
                info_list += (repr( self.actors ),)
                info_list += (self.studio,)
                info_list += (self.rating,)
                info_list += (self.rating_url.replace( cwd, '' ),)
                info_list += (self.year,)
                info_list += (self.times_watched,)
                info_list += (self.last_watched,)
                info_list += (self.favorite,)
                info_list += (self.saved_location,)

                if ( record ):
                    self.movie_records_update += ( ( info_list[ 2: ] ) + ( title, ), )#####
                    #success = DB.updateRecords( 'Movies', ( '*', 2 ), ( ( info_list[ 2 : ] ) + ( title, ), ), 'title' )
                else:
                    self.movie_records_add += ( info_list, )#####
                    #success = DB.addRecords( 'Movies', ( info_list, ) )
                if ( self.load_all and update_other ):
                    if ( self.actors ):#not actor ):
                        actor_records_add = ()
                        actor_records_update = ()
                        for actor in self.actors:
                            count = DB.getRecords( 'SELECT count FROM Actors WHERE name=?', ( actor, ) )
                            if ( count ):
                                actor_records_update += ( ( count[0] + 1, actor, ), )
                                #success = DB.updateRecords( 'Actors', ( 'count', ), ( ( count[0] + 1, actor, ), ), 'name' )
                            else:
                                actor_records_add += ( ( actor, 1, ), )
                                #success = DB.addRecords( 'Actors', ( ( actor, 1, ), ) )
                        if ( actor_records_add ):
                            success = DB.addRecords( 'Actors', actor_records_add )
                        if ( actor_records_update ):
                            success = DB.updateRecords( 'Actors', ( '*', 1 ), actor_records_update, 'name' )
                    if ( self.studio ):#not studio ):
                        count = DB.getRecords( 'SELECT count FROM Studios WHERE title=?', ( self.studio, ) )
                        if ( count ):
                            success = DB.updateRecords( 'Studios', ( 'count', ), ( ( count[0] + 1, self.studio, ), ), 'title' )
                        else:
                            success = DB.addRecords( 'Studios', ( ( self.studio, 1, ), ) )
                
                #if ( record ): 
                return info_list###############################
                #else: return ( title, )
        except:
            #print traceback.print_exc()
            print 'Trailer XML %s: %s is corrupt' % ( title, url, )
            return ( title, )
            
    def clearRecordVariables( self ):#####
        self.movie_records_add = ()
        self.movie_records_update = ()

    def writeMovieInfo( self ):#####
        # add records
        if ( self.movie_records_add ):
            success = DB.addRecords( 'Movies', self.movie_records_add )
        if ( self.movie_records_update ):
            success = DB.updateRecords( 'Movies', ( '*', 2 ), self.movie_records_update, 'title' )
        
    def updateRecord( self, table, columns, values, key = 'title' ):
        success = DB.updateRecords( table, columns, values, key )
        return success

    def getMovies( self, sql, params = None, all = True ):
        try:
            self.clearRecordVariables()#####
            self.load_all = True
            dialog = xbmcgui.DialogProgress()
            dialog.create( _( 85 ) )
            dialog.update( -1, _( 67 ) )
            movie_list = DB.getRecords( sql, params, all )
            if ( movie_list ):
                self.movies = []
                info_missing = False
                total_cnt = len( movie_list )
                pct_sect = float( 100 ) / total_cnt
                for cnt, movie in enumerate( movie_list ):
                    if ( info_missing or eval( movie[ 2 ] ) == [] ):
                        dialog.update( int( ( cnt + 1 ) * pct_sect ), _( 70 ), '%s: (%d of %d)' % ( _( 88 ), cnt + 1, total_cnt ), movie[0] )
                        if ( dialog.iscanceled() ): raise
                        if ( eval( movie[ 2 ] ) == [] ):
                            info_missing = True
                            movie = self.loadMovieInfo( movie[ 0 ], -1, str( movie[ 1 ] ) )
                    if ( len( movie ) > 1 ): 
                        self.movies += [Movie( movie )]
                if ( info_missing ): #####
                    dialog.update( 100, _( 70 ), '%s: (%d of %d)' % ( _( 88 ), cnt + 1, total_cnt ), '-----> %s <-----' % (_( 43 ), ) )
                    self.writeMovieInfo()#####
            else: self.movies = None
        except: pass
        dialog.close()
            
    def getCategories( self, sql, params = None, all = True ):
        try:
            dialog = xbmcgui.DialogProgress()
            dialog.create( _( 85 ) )
            dialog.update( -1, _( 67 ) )
            category_list = DB.getRecords( sql, params, all )
            if ( category_list ):
                self.categories = []
                for category in category_list:
                    self.categories += [Category( category )]
            else: self.categories = None
        finally:
            dialog.close()
