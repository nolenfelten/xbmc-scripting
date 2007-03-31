import os, sys, traceback
import xbmc, xbmcgui
import cacheurl
import elementtree.ElementTree as ET
import default
import language
import pil_util
import database
#####################################
import time
#####################################

fetcher = cacheurl.HTTP()
_ = language.Language().localized

base_cache_path = fetcher.cache_dir + os.sep

class Movie:
    '''
        Exposes the following:
        - title (string)
        - trailer_urls (string - list of movie urls)
        - poster (string - path to poster)
        - thumbnail (string - path to thumbnail)
        - thumbnail_watched (string - pathe to watched thumbnail)
        - plot (string - movie plot)
        - rating (string - movie rating)
        - rating_url (string - path to rating image file)
        - year (integer - year of movie)
        - watched (integer - number of times watched)
        - watched_date (string - last watched date)
        - favorite (integer - 1=favorite)
        - saved (string - path to saved movie)
        - cast (list - list of actors)
        - studio (string - movies studio)
    '''
    def __init__( self, movie=None ):
        '''
        self.tables['movies'] = (
          0  ( 'idMovie', 'integer', '', 'UNIQUE INDEX', '(idMovie)' ), 
          1  ( 'title', 'text', '', '', '' ),
          2  ( 'url', 'text',  '', '', '' ),
          3  ( 'trailer_urls', 'text', '', '', '' ),
          4  ( 'poster', 'text', '', '', '' ),
          5  ( 'plot', 'text', '', '', '' ),
          6  ( 'rating', 'text', '', '', '' ),
          7  ( 'rating_url', 'text', '', '', '' ),
          8  ( 'year', 'integer', '', '', '' ),
          9  ( 'times_watched', 'integer', '', '', '' ),
         10  ( 'last_watched', 'text', '', '', '' ),
         11  ( 'favorite', 'integer', '', '', '' ),
         12  ( 'saved_location', 'text', '', '', '' ),
        )
        '''
        if ( movie ):
            self.idMovie = movie[0]
            self.title = movie[1]
            self.trailer_urls = eval( movie[3] )
            #self.genre = movie[]
            self.poster = os.path.join( base_cache_path, movie[4] )
            self.thumbnail = os.path.join( base_cache_path, '%s.png' % ( os.path.splitext( movie[4] )[0], ) )
            self.thumbnail_watched = os.path.join( base_cache_path, '%s-w.png' % ( os.path.splitext( movie[4] )[0], ) )
            self.plot = movie[5]
            self.rating = movie[6]
            self.rating_url = os.path.join( base_cache_path, movie[7] )
            self.year = movie[8]
            self.watched = movie[9]
            self.watched_date = movie[10]
            self.favorite = movie[11]
            self.saved = movie[12]
            self.cast = movie[13]
            self.studio = movie[14]
        
class Category:
    '''
        Exposes the following:
        - id (integer)
        - title (string)
        - url (string - url to xml)
        - count (integer - number of movies in category)
    '''
    def __init__( self, idGenre=None, title=None, urls=list(), count=None ):
        '''
        self.tables['genres'] = (
            ( 'idGenre', 'integer', 'AUTO_INCREMENT', 'UNIQUE INDEX', '(idGenre)' ),
            ( 'title', 'text', '', '', '' ),
            ( 'urls', 'blob', '', '', '' ),
            ( 'trailer_urls', 'blob', '', '', '' ),
        )
        '''
        self.id = idGenre
        self.title = title
        # if urls is unicode, evaluate it so it becomes a list type
        if type( urls ) is type( unicode() ):
            self.urls = eval( urls )
        else:
            self.urls = urls
        self.count = count


class Trailers:
    '''
        Exposes the following:
        - categories (sorted list of Category() object instances)
        - trailers (sorted list of Movie() object instances)
    '''
    def __init__( self, genre = 'Exclusives' ):
        self.categories = []
        self.BASEURL = 'http://www.apple.com'
        self.BASEXML = self.BASEURL + '/moviesxml/h/index.xml'
        db = database.Database( language=_ )
        self.query = database.Query()
        self.complete = db.complete
        #####################################
        self.start_time = 0
        #####################################
        newest_genre = self.loadGenres()
        if ( newest_genre ):
            self.updateGenre( newest_genre )
        
    def ns( self, text ):
        BASENS = '{http://www.apple.com/itms/}'
        result = list()
        for each in text.split( '/' ):
            result += [ BASENS + each ]
        return '/'.join( result )
            
    def updateGenre( self, genre ):
        """
            Updates the xml for each genre from the site.
        """
        try:
            dialog = xbmcgui.DialogProgress()
            dialog.create( '%s' % ( _( 66 ), ) )
            idGenre = self.categories[ genre ].id
            title = self.categories[ genre ].title
            url = self.categories[ genre ].urls[ 0 ]
            self.records = database.Records()
            self.removeXML( self.categories[ genre ].urls )
            trailer_urls, genre_urls = self.loadGenreInfo( title, url )
            idMovie_list = self.records.fetchall( self.query[ "idMovie_by_genre_id" ], ( idGenre, ) )
            
            total_cnt = len( trailer_urls )
            pct_sect = float( 100 ) / total_cnt

            for cnt, url in enumerate( trailer_urls ):
                #xbmc.sleep(300)
                dialog.update( int( ( cnt + 1 ) * pct_sect ), '%s: %s' % (_( 87 ), title, ), '%s: (%d of %d)' % ( _( 88 ), cnt + 1, total_cnt, ), url[ 0 ] )
                record = self.records.fetchone( self.query[ 'movie_exists' ], ( url[ 0 ].upper(), ) )
                if ( record is None ):
                    #print "ADD", url
                    idMovie = self.records.add( 'movies', ( url[ 0 ] , url[ 1 ], '[]', '', '', '', '', 0, 0, '', 0, '', ) )
                    success = self.records.add( 'genre_link_movie', ( idGenre, idMovie, ) )
                else:
                    try:
                        #print "EXISTS", url
                        i = idMovie_list.index( record )
                        idMovie_list.pop( i )
                    except: pass
            for record in idMovie_list:
                #print "REMOVE", record
                params = ( idGenre, record[ 0 ], )
                success = self.records.delete( "genre_link_movie", ( "idGenre", "idMovie", ), params )
            success = self.records.commit()
            self.categories[ genre ] = Category( idGenre=idGenre, title=title, urls=genre_urls )
        except: traceback.print_exc()
            
        dialog.close()


    def removeXML( self, urls ):
        for url in urls:
            try:
                filename = fetcher.make_cache_filename( url )
                filename = os.path.join( base_cache_path, filename )
                if os.path.isfile( filename ):
                    os.remove( filename )
            except:
                traceback.print_exc()
                
    def loadGenres( self ):
        try:
            dialog = xbmcgui.DialogProgress()
            self.records = database.Records()
            genre_list = self.records.fetchall( self.query[ 'genre_table_list' ] )
            self.categories = []
            if ( genre_list ):
                for cnt, genre in enumerate( genre_list ):
                    self.categories += [ Category( idGenre=genre[ 0 ], title=genre[ 1 ], urls=genre[ 2 ] )]
                    if ( genre[ 1 ] == "Newest" ):
                        newest_id = cnt
                return newest_id
            else:
                load_all = xbmcgui.Dialog().yesno( _( 44 ), '%s: %s' % ( _( 158 ), _( 40 ), ), '%s: %s' % ( _( 159 ), _( 41 ), ), _( 49 ), _( 159 ), _( 158 ) )
                #####################################
                self.start_time = time.localtime()
                #####################################
                
                dialog.create( '%s   (%s)' % ( _( 66 ), _( 158 + ( not load_all ) ), ) )
                
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
                        if word != name[0] and ( word == 'and' or word == 'of' or word == 'a' ):
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
                    dialog.update( int( ( cnt + 1 ) * pct_sect ), '%s: %s - (%d of %d)' % (_( 87 ), genre, cnt + 1, total_cnt, ), '', '' )
                    trailer_urls, genre_urls = self.loadGenreInfo( genre, genre_dict[genre] )
                    if ( trailer_urls ):
                        idGenre = self.records.add( 'genres', ( genre, repr( genre_urls ), repr( trailer_urls), ) )
                        self.categories += [ Category( idGenre=idGenre, title=genre, urls=genre_urls ) ]
                        total_urls = len( trailer_urls )
                        for url_cnt, url in enumerate( trailer_urls ):
                            dialog.update( int( ( cnt + 1 ) * pct_sect ), '%s: %s - (%d of %d)' % (_( 87 ), genre, cnt + 1, total_cnt, ), '%s: (%d of %d)' % ( _( 88 ), url_cnt + 1, total_urls, ), url[ 0 ] )
                            record = self.records.fetchone( self.query[ 'movie_exists' ], ( url[ 0 ].upper(), ) )
                            if ( record is None ):
                                idMovie = self.records.add( 'movies', ( url[ 0 ] , url[ 1 ], '[]', '', '', '', '', 0, 0, '', 0, '', ) )
                            else: idMovie = record[ 0 ]
                            success = self.records.add( 'genre_link_movie', ( idGenre, idMovie, ) )
                        success = self.records.commit()
                dialog.close()
                self.records.close()
                if ( load_all ): self.fullUpdate()
                else: 
                    #########################################
                    end_time = time.localtime()
                    seconds = time.mktime(end_time) - time.mktime( self.start_time )
                    print "*** (MINIMAL) - Start time: %s - End time: %s - Total time: %s" % ( time.strftime( '%H:%M:%S', self.start_time ), time.strftime( '%H:%M:%S', end_time ), time.strftime( '%M:%S', time.localtime( seconds ) ), )
                    #########################################

        except:
            dialog.close()
            traceback.print_exc()
        return False
        
    def loadGenreInfo( self, genre, url ):
        """
            Follows all links from a genre page and fetches all trailer urls.
            Returns two lists, trailer_urls (contains tuples of ( title, url ) 
            for all trailers in genre and genre_urls (contains urls to all 
            pages of genre)
        """
        try:
            if url[:7] != 'http://':
                url = self.BASEURL + url
            is_special = genre in [ 'Exclusives', 'Newest' ]
            next_url = url
            first_url = True
            trailer_dict = dict()
            genre_urls = list()
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
                    # add next_url to the genre_urls list
                    genre_urls.append( next_url )
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
            return trailer_urls, genre_urls
        except:
            traceback.print_exc()
            return [], []

    def fullUpdate( self ):
        #####################################
        if ( not self.start_time ): self.start_time = time.localtime()
        #####################################
        
        self.dialog = xbmcgui.DialogProgress()
        self.dialog.create( '%s   (%s)' % ( _( 70 ), _( 158 ), ) )
        full = self.getMovieList( self.query[ 'incomplete_movies' ], full = True )
        if ( full ): self.complete = self.updateRecord( 'version', ( 'complete', ), ( full, 1, ), 'idVersion' )

        #########################################
        end_time = time.localtime()
        seconds = time.mktime(end_time) - time.mktime( self.start_time )
        print "*** (FULL) - Start time: %s - End time: %s - Total time: %s" % ( time.strftime( '%H:%M:%S', self.start_time ), time.strftime( '%H:%M:%S', end_time ), time.strftime( '%M:%S', time.localtime( seconds ) ), )
        #########################################

    def setDefaultMovieInfo( self, movie ):
        self.idMovie = movie[ 0 ]
        self.title = movie[ 1 ]
        self.url = str( movie[ 2 ] )
        self.trailer_urls = eval( movie[ 3 ] )
        self.poster = movie[ 4 ]
        self.plot = movie[ 5 ]
        self.rating = movie[ 6 ]
        self.rating_url = movie[ 7 ]
        self.year = movie[ 8 ]
        self.times_watched = movie[ 9 ]
        self.last_watched = movie[ 10 ]
        self.favorite = movie[ 11 ]
        self.saved_location = movie[ 12 ]
        self.actors = movie[ 13 ]
        self.studio = movie[ 14 ]
        
    def loadMovieInfo( self, movie ):
        try:
            self.setDefaultMovieInfo( movie )
            
            if ( self.url[:7] != 'http://' ):
                url = self.BASEURL + self.url
            else:
                url = self.url

            # xml parsing
            element = fetcher.urlopen( url )
            element = ET.fromstring( element )
            
            # -- poster & thumbnails --
            if ( not self.poster ):
                poster = element.getiterator( self.ns('PictureView') )[1].get( 'url' )
                # download the actual poster to the local filesystem (or get the cached filename)
                poster = fetcher.urlretrieve( poster )
                if poster:
                    self.poster = poster.replace( base_cache_path, '' )
                    # make thumbnails
                    success = pil_util.makeThumbnails( poster )
            
            # -- plot --
            if ( not self.plot ):
                plot = element.getiterator( self.ns('SetFontStyle') )[2].text.encode( 'ascii', 'ignore' ).strip()
                if plot:
                    # remove any linefeeds so we can wrap properly to the text control this is displayed in
                    plot = plot.replace( '\r\n', ' ' )
                    plot = plot.replace( '\r', ' ' )
                    plot = plot.replace( '\n', ' ' )
                    self.plot = plot
            
            # -- actors --
            if ( not ( self.actors ) ):
                SetFontStyles = element.getiterator( self.ns('SetFontStyle') )
                actors = list()
                for i in range( 5, 10 ):
                    actor = SetFontStyles[i].text.encode( 'ascii', 'ignore' ).replace( '(The voice of)', '' ).title().strip()
                    if ( len( actor ) and actor[ 0 ] != '.' and actor != '1:46') :
                        actors += [ ( actor, ) ]
                        actor_id = self.records.fetchone( self.query[ 'actor_exists' ], ( actor.upper(), ) )
                        if ( actor_id is None ): idActor = self.records.add( 'actors', ( actor, ) )
                        else: idActor = actor_id[ 0 ]
                        self.records.add( 'actor_link_movie', ( idActor, self.idMovie, ) )
                self.actors = actors
                self.actors.sort()
            
            # -- studio --
            if ( not self.studio ):
                studio = element.getiterator( self.ns('PathElement') )[1].get( 'displayName' ).strip()
                if studio:
                    studio_id = self.records.fetchone( self.query[ 'studio_exists' ], ( studio.upper(), ) )
                    if ( studio_id is None ): idStudio = self.records.add( 'studios', ( studio, ) )
                    else: idStudio = studio_id[ 0 ]
                    self.records.add( 'studio_link_movie', ( idStudio, self.idMovie, ) )
                    self.studio = studio
            
            # -- rating --
            if ( not self.rating ):
                temp_url = element.getiterator( self.ns('PictureView') )[2].get( 'url' )
                if temp_url:
                    if '/mpaa' in temp_url:
                        rating_url = fetcher.urlretrieve( temp_url )
                        if rating_url:
                            self.rating_url = rating_url.replace( base_cache_path, '' )
                            self.rating = os.path.split( temp_url )[1][:-4].replace( 'mpaa_', '' )
            
            # -- trailer urls --
            if ( not self.trailer_urls ):
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
            info_list = ( self.idMovie, )
            info_list += ( self.title, )
            info_list += ( self.url,)
            info_list += (repr( self.trailer_urls ),)
            info_list += (self.poster,)
            info_list += (self.plot,)
            info_list += (self.rating,)
            info_list += (self.rating_url,)
            info_list += (self.year,)
            info_list += (self.times_watched,)
            info_list += (self.last_watched,)
            info_list += (self.favorite,)
            info_list += (self.saved_location,)
            success = self.records.update( 'movies', ( '*', 3 ), ( info_list[ 3: ] ) + ( self.idMovie, ), 'idMovie' )
            info_list += ( self.actors, )
            info_list += ( self.studio, )
            return info_list
        except:
            #traceback.print_exc()
            print 'Trailer XML %s: %s is corrupt' % ( self.idMovie, url, )
            return None
            
    def updateRecord( self, table, columns, values, key = 'title' ):
        try:
            records = database.Records()
            success = records.update( table, columns, values, key )
            records.commit()
            records.close()
        except:
            traceback.print_exc()
            success = False
        return success

    def getMovies( self, sql, params = None ):
        self.dialog = xbmcgui.DialogProgress()
        self.dialog.create( _( 85 ) )
        self.dialog.update( -1, _( 67 ) )
        full = self.getMovieList( sql, params )

    def getActorStudio( self, movie ):
        actor_list = self.records.fetchall( self.query[ 'actors_by_movie_id' ], ( movie[ 0 ], ) )
        if ( actor_list ): movie += ( actor_list, )
        else: movie += ( [], )
        studio = self.records.fetchone( self.query[ 'studio_by_movie_id' ], ( movie[ 0 ], ) )
        if ( studio is not None ): movie += ( studio[ 0 ], )
        else: movie += ( '', )
        return movie
        
    def getMovieList( self, sql, params = None, full = False ):
        try:
            self.records = database.Records()
            movie_list = self.records.fetchall( sql, params )
            if ( movie_list ):
                if ( not full ): self.movies = []
                total_cnt = len( movie_list )
                pct_sect = float( 100 ) / total_cnt
                commit = info_missing = False
                for cnt, movie in enumerate( movie_list ):
                    movie = self.getActorStudio( movie )
                    if ( info_missing or eval( movie[ 3 ] ) == [] ):
                        self.dialog.update( int( ( cnt + 1 ) * pct_sect ), '%s: (%d of %d)' % ( _( 88 ), cnt + 1, total_cnt, ), movie[1], '' )
                        info_missing = True
                        if ( float( cnt + 1) / 100 == int( ( cnt + 1 ) / 100) or self.dialog.iscanceled() or ( cnt + 1 ) == total_cnt ): commit = True
                    if ( eval( movie[ 3 ] ) == [] ): movie = self.loadMovieInfo( movie )
                    if ( movie and not full ): self.movies += [Movie( movie )]
                    if ( commit ):
                        self.dialog.update( int( ( cnt + 1 ) * pct_sect ) , '%s: (%d of %d)' % ( _( 88 ), cnt + 1, total_cnt, ), movie[1], '-----> %s <-----' % (_( 43 ), ) )
                        self.records.commit()
                        commit = False
                        if ( self.dialog.iscanceled() ):
                            full = False
                            break
            else: self.movies = None
        except: traceback.print_exc()#pass
        self.records.close()
        self.dialog.close()
        return full
            
    def getCategories( self, sql, params = False ):
        try:
            dialog = xbmcgui.DialogProgress()
            dialog.create( _( 85 ) )
            dialog.update( -1, _( 67 ) )
            records = database.Records()
            category_list = records.fetchall( sql, params )
            records.close()
            if ( category_list ):
                self.categories = []
                for category in category_list:
                    #def __init__( self, idGenre=None, title=None, url=None, count=None ):
                    self.categories += [Category( title=category[ 0 ], count=category[ 1 ] )]
            else: self.categories = None
        except: traceback.print_exc()
        dialog.close()

