import urllib
from sgmllib import SGMLParser
import sys

debug = False
debugWrite = False

class _SongListParser( SGMLParser ):
    """ Main song list parser """
    def reset( self ):
        SGMLParser.reset( self )
        self.song_list = []
        self.url = 'None'

    def start_a( self, attrs ):
        for key, value in attrs:
            if ( key == 'href' ):
                if ( not value[ 0 ] == '#' and not value[ : 10 ] =='/Category:' and
                    not value[ : 11 ] == '/LyricWiki:' and not value == '/Main_Page' ):
                    self.url = value
            elif ( key == 'title' ):
                if ( urllib.unquote( self.url[ 1 : ] ) == urllib.unquote( value.replace( ' ', '_' ).replace( '&amp;', '&' ) ) ):
                    self.song_list += [ ( urllib.unquote( value ), self.url, ) ]
            else:
                self.url = 'None'

class _LyricsParser( SGMLParser ):
    """ Main lyrics parser """
    def reset( self ):
        SGMLParser.reset( self )
        self.lyrics_found = False
        self.lyrics = ''

    def start_div( self, attrs ):
        for key, value in attrs:
            if ( key == 'id' and value == 'lyric' ):
                self.lyrics_found = True
            else: self.lyrics_found = False
                
    def start_pre( self, attrs ):
        self.lyrics_found = True

    def handle_data( self, text ):
        if ( self.lyrics_found ):
            self.lyrics += text

class LyricsFetcher:
    def __init__( self ):
        self.url = 'http://www.lyricwiki.org'
        
    def get_lyrics( self, artist, song ):
        """ *required: returns song lyrics or a list of choices from artist & song """
        url = self.url + '/%s:%s'
        artist = self._format_param( artist )
        song = self._format_param( song )
        lyrics = self._fetch_lyrics( url % ( artist, song, ) )
        if ( not lyrics ):
            song_list = self._get_song_list( artist )
            return song_list
        else: return self._clean_text( lyrics )
    
    def get_lyrics_from_list( self, item ):
        """ *required: returns song lyrics from user selection - item[1]"""
        lyrics = self._fetch_lyrics( self.url + item[ 1 ] )
        return self._clean_text( lyrics )
        
    def _fetch_lyrics( self, url ):
        """ Fetch lyrics if available """
        # Open url or local file (if debug == True)
        if (not debug): usock = urllib.urlopen( url )
        else:
            usock = open( sys.path[ 0 ] + '\\lyrics_source.txt','r' )
        htmlSource = usock.read()
        usock.close()
        # Save htmlSource to a file for testing parser
        if (debugWrite):
            usock = open( sys.path[0] + '\\lyrics_source.txt','w' )
            usock.write( htmlSource )
            usock.close
        # Parse htmlSource
        parser = _LyricsParser()
        parser.feed( htmlSource )
        parser.close()
        return parser.lyrics
        
    def _get_song_list( self, artist ):
        """ If no lyrics found, fetch a list of choices """
        url = self.url + '/%s'
        # Open url or local file (if debug == True)
        if (not debug): usock = urllib.urlopen( url % ( artist, ) )
        else:
            usock = open( sys.path[ 0 ] + '\\song_source.txt','r' )
        htmlSource = usock.read()
        usock.close()
        # Save htmlSource to a file for testing parser
        if ( debugWrite ):
            usock = open( sys.path[0] + '\\song_source.txt', 'w' )
            usock.write( htmlSource )
            usock.close
        # Parse htmlSource
        parser = _SongListParser()
        parser.feed( htmlSource )
        parser.close()
        # Create sorted return list
        song_list = self._remove_dupes( parser.song_list )
        return song_list

    def _remove_dupes( self, song_list ):
        """ Returns a sorted list with duplicates removed """
        dupes = {}
        for x in song_list:
            dupes[ x ] = x
        new_song_list = dupes.values()
        new_song_list.sort()
        return new_song_list

    def _format_param( self, param, caps = True):
        """ convert param to the form expected by site """
        retVal = ''
        for word in param.split():
            if ( caps ): word = word.capitalize()
            word = word.replace( '/', '_' ).replace( 'Ac_dc', 'AC_DC' )
            retVal += urllib.quote( word ) + '_'
        return retVal[ : -1 ]
    
    def _clean_text( self, text ):
        """ covert line terminators and html entities """
        text = text.replace( '<br> ', '\n' )
        text = text.replace( '<br>', '\n' )
        text = text.replace( '<br /> ', '\n' )
        text = text.replace( '<br />', '\n' )
        text = text.replace( '<div>', '\n' )
        text = text.replace( '> ', '\n' )
        text = text.replace( '>', '\n' )
        text = text.replace( '&amp;', '&' )
        text = text.replace( '&gt;', '>' )
        text = text.replace( '&lt;', '<' )
        text = text.replace( '&quot;', '"' )
        return text

if ( __name__ == '__main__' ):
    # --------------------------------------------------------------------#
    # Used to test get_lyrics() 
    artist = "Kim Mitchell"
    song = "Go for Soda"
    lyrics = LyricsFetcher().get_lyrics( artist, song )
    # --------------------------------------------------------------------#
    
    # --------------------------------------------------------------------#
    # Used to test get_lyrics_from_list() 
    #url = ('Big & Rich:Save a Horse (Ride a Cowboy)', '/Big_%26_Rich:Save_a_Horse_%28Ride_a_Cowboy%29')
    #lyrics = LyricsFetcher().get_lyrics_from_list( url )
    # --------------------------------------------------------------------#
    
    if ( type( lyrics ) == str ):
        print lyrics
    else:
        for song in lyrics:
            print song
            

