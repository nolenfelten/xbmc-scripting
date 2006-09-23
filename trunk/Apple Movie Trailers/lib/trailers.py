import os
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
        self.genres = dict()

    def update_genre_list( self ):
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
            if '/moviesxml/g' in url:
                self.genres['standard'].update( { name: url } )

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
                    self.genres['special'].update( { view_matrix[view]: url } )    

    def get_trailer_dict( self, genre, url ):
        url = self.BASEURL + url
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

    def get_trailer_info( self, url ):
        xbmc.log( 'getting info for ' + url )
        url = self.BASEURL + url
        element = fetcher.urlopen( url )
        element = ET.fromstring( element )
        title = element.getiterator( ns('b') )[0].text.encode( 'ascii', 'ignore' )
        thumbnail = element.getiterator( ns('PictureView') )[1].get( 'url' )
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
        xbmc.log( 'done.' )
        return [ title, thumbnail, description, urls ]

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
        genre_list = self.genres['standard'].items()
        # smart capitalization of the genre titles
        genre_list_caps = list()
        for genre, url in genre_list:
            genre_caps = list()
            for word in genre.split():
                # only prevent capitalization of these words if they aren't the leading word in the genre name
                # ie, 'the top rated' becomes 'The Top Rated', but 'action and adventure' becomes 'Action and Adventure'
                cap = True
                if word != genre[0]:
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
            genre_list_caps += [ ( ' '.join( genre_caps ), url ) ]
        genre_list_caps.sort()
        return genre_list_caps

    def get_exclusives_dict( self ):
        url = self.genres['special']['Exclusives']
        edict = self.get_trailer_dict( 'Exclusives', url )
        return edict

    def get_newest_dict( self ):
        url = self.genres['special']['Newest']
        edict = self.get_trailer_dict( 'Newest', url )
        return edict
