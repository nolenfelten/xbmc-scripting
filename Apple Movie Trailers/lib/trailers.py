import os, sys
import xbmc, xbmcgui
import cachedhttp_mod as cachedhttp
import elementtree.ElementTree as ET

def append_ns( text ):
    BASENS = '{http://www.apple.com/itms/}'
    result = list()
    for each in text.split( '/' ):
        result += [ BASENS + each ]
    return '/'.join( result )
ns = append_ns

fetcher = cachedhttp.CachedHTTP()
fetcher_with_dialog = cachedhttp.CachedHTTPWithProgress()

class Trailers:
    def __init__( self ):
        self.BASEURL = 'http://www.apple.com'
        self.BASEXML = self.BASEURL + '/moviesxml/h/index.xml'
        self.DATAFILE = os.path.join( os.path.dirname( os.path.dirname( sys.modules['trailers'].__file__ ) ), 'data', 'AMT.pk' )
        self.genres = dict()
        import pickle
        try:
            if not os.path.isfile( self.DATAFILE ):
                raise
            datafile = open( self.DATAFILE, 'r' )
            self.genres = pickle.load( datafile )
        except:
            self.__update_genre_list__()
            datafile = open( self.DATAFILE, 'w' )
            pickle.dump( self.genres, datafile )
        datafile.close()

    def __update_genre_list__( self ):
        base_xml = fetcher.urlopen( self.BASEXML )
        base_xml = ET.fromstring( base_xml )

        self.genres = {
            'special': dict(),
            'standard': dict(),
        }
        elements = base_xml.getiterator( ns('GotoURL') )
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
                self.genres['standard'].update( { name: url } )

        view_matrix = {
            'view1': 'Exclusives',
            'view2': 'Newest',
        }
        elements = base_xml.getiterator( ns('Include') )
        # make self.genres as such:
        #   {
        #       'special': {
        #           'Exclusives': url,
        #           'Newest': url,
        #       }
        #       'standard': {
        #       }
        #   }
        for each in elements:
            url = each.get( 'url' )
            for view in view_matrix:
                if view in url:
                    url = '/moviesxml/h/' + url
                    self.genres['special'].update( { view_matrix[view]: url } )    
        # make self.genres as such:
        #   {
        #       'special': {
        #           'Exclusives': category_url,
        #           'Newest': category_url,
        #       }
        #       'standard': {
        #           genre: {
        #               movie_title: movie_url
        #           }
        #           ...
        #       }
        #   }
        xbmc.log( '--- genre info ---' )
        i = 0
        dialog = xbmcgui.DialogProgress()
        i += 1
        xbmc.log( str( i ) )
        dialog_header = 'Fetching category and genre information..'
        i += 1
        xbmc.log( str( i ) )
        dialog_line1 = 'Please wait a moment.'
        i += 1
        xbmc.log( str( i ) )
        dialog_errorline = ''
        i += 1
        xbmc.log( str( i ) )
        dialog_percentage = 0
        i += 1
        xbmc.log( str( i ) )
        dialog.create( dialog_header, dialog_line1 )
        i += 1
        xbmc.log( str( i ) )
        dialog.update( dialog_percentage )
        i += 1
        xbmc.log( str( i ) )
        pos = 0
        xbmc.log( str( self.genres ) )
        for each in self.genres['standard']:
            xbmc.log( each + str( dialog_percentage ) )
            try:
                dialog.update( dialog_percentage, dialog_line1, 'Fetching: ' + each, dialog_errorline )
                self.genres['standard'][each] = self.__update_trailer_dict__( each )
            except:
                dialog_errorline = 'Error retrieving information for one or more genres.'
            pos += 1
            dialog_percentage = int( float( pos ) / len( self.genres['standard'] ) * 100 )
        i += 1
        xbmc.log( str( i ) )
        dialog.close()
        xbmc.log( '------------------' )
        # update information for each movie in each genre
        # make self.genres as such:
        #   {
        #       'special': {
        #           'Exclusives': category_url,
        #           'Newest': category_url,
        #       }
        #       'standard': {
        #           genre: {
        #               movie_title: [ thumbnail, description, [ trailer_url, ... ] ]
        #           }
        #           ...
        #       }
        #   }
        xbmc.log( '--- movie info ---' )
        dialog = xbmcgui.DialogProgress()
        dialog_header = 'Fetching movie information..'
        dialog_errorline = ''
        genre_percentage = 0
        dialog.create( dialog_header )
        dialog.update( dialog_percentage )
        genre_pos = 0
        for genre in self.genres['standard']:
            movie_pos = 0
            xbmc.log( genre + str( genre_percentage ) )
            dialog.update( genre_percentage, 'Genre: ' + genre, '', dialog_errorline )
            if dialog.iscanceled():
                break
            movie_percentage = 0
            for movie in self.genres['standard'][genre]:
                xbmc.log( movie + str( movie_percentage ) )
                if dialog.iscanceled():
                    break
                try:
                    dialog.update( dialog_percentage, 'Genre: ' + genre, 'Fetching: ' + movie, dialog_errorline )
                    self.genres['standard'][genre][movie] = self.__update_trailer_info__( genre, movie )
                except:
                    dialog_errorline = 'Error retrieving information for one or more movie titles.'
                movie_pos += 1
                movie_percentage = int( float( movie_pos ) / len( self.genres['standard'][genre] ) * 10 ) + genre_percentage
            genre_pos += 1
            genre_percentage = int( float( genre_pos ) / len( self.genres['standard'] ) * 100 )
        dialog.close()

    def __update_trailer_dict__( self, genre ):
        """
            return a dict with movie titles and urls for the given genre
        """
        url = self.BASEURL + self.genres['standard'][genre]
        element = fetcher.urlopen( url )
        if '<Document' not in element:
            element = '<Document>' + element + '</Document>'
        element = ET.fromstring( element )
        elements = element.getiterator( ns('GotoURL') )
        trailer_dict = dict()
        for element in elements:
            url2 = element.get( 'url' )
            title = None
            if 'index_1' in url2:
                continue
            if '/moviesxml/g' in url2:
                continue
            if url2[0] != '/':
                continue
            if url2 in trailer_dict.keys():
                title = element.getiterator( ns('B') )[0].text.encode( 'ascii', 'ignore' )
                trailer_dict[url2] = title
                continue
            trailer_dict.update( { url2: title } )
        reordered_dict = dict()
        for key in trailer_dict:
            reordered_dict.update( { trailer_dict[key]: key } )
        return reordered_dict

    def __update_trailer_info__( self, genre, title ):
        url = self.BASEURL + self.genres['standard'][genre][title]
        element = fetcher.urlopen( url )
        element = ET.fromstring( element )
        thumbnail = element.getiterator( ns('PictureView') )[1].get( 'url' )
        # download the actual thumbnail to the local filesystem (or get the cached filename)
        thumbnail = fetcher.urlretrieve( thumbnail )
        if not thumbnail:
            # default if the actual thumbnail couldn't be found for some reason
            thumbnail = os.path.join( self.imagePath, 'blank_thumbnail.png' )
        description = element.getiterator( ns('SetFontStyle') )[2].text.encode( 'ascii', 'ignore' )
        description = description.strip()
        # remove any linefeeds so we can wrap properly to the text control this is displayed in
        description = description.replace( '\r\n', ' ' )
        description = description.replace( '\r', ' ' )
        description = description.replace( '\n', ' ' )
        if not description or len( description ) is 0:
            description = 'No description could be retrieved for this title.'
        urls = list()
        for each in element.getiterator( ns('GotoURL') ):
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
        return [ thumbnail, description, urls ]

    def get_video( self, url ):
        url = self.BASEURL + url
        element = fetcher.urlopen( url )
        element = ET.fromstring( element )
        trailer_urls = list()
        for each in element.getiterator( ns('string') ):
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
        try:
            dialog = xbmcgui.Dialog()
            trailer_url_filenames = list()
            for each in trailer_urls:
                trailer_url_filenames += [ os.path.split( each )[1] ]
            selection = dialog.select( 'Choose a trailer to view:', trailer_url_filenames )
            selection = trailer_urls[selection].replace( '//', '/' ).replace( '/', '//', 1 )
            return selection
        except:
            return None

    def get_genre_list( self ):
        genre_list = self.genres['standard'].keys()
        genre_list.sort()
        return genre_list

    def get_trailer_dict( self, genre ):
        return self.genres['standard'][genre]

    def get_trailer_info( self, genre, movie_title ):
        return self.genres['standard'][genre][movie_title]

    def get_exclusives_dict( self ):
        url = self.genres['special']['Exclusives']
        return None

    def get_newest_dict( self ):
        url = self.genres['special']['Newest']
        return None
