import urllib
from sgmllib import SGMLParser
import sys
debug = False
debugWrite = False

class Song_List_Parser( SGMLParser ):
    def reset( self ):
        self.song_found = False
        self.song_list = []
        self.url = 'None'
        SGMLParser.reset(self)

    def start_a( self, attrs ):
        for key, value in attrs:
            if ( key == 'href' and not value[ 0 ] == '#' and not value[ : 10 ] =='/Category:' and
                not value[ : 11 ] == '/LyricWiki:' and not value == '/Main_Page' ):
                self.url = value
            elif ( key == 'title' and self.url[ 1 : ] == value.replace( ' ', '_' ) ):
                self.song_list += [ ( value, self.url, ) ]
            else:
                self.url = 'None'

class Lyrics_Parser( SGMLParser ):
    def reset( self ):
        self.lyrics_found = False
        self.lyrics = ''
        SGMLParser.reset(self)

    def start_div( self, attrs ):
        for key, value in attrs:
            if ( key == 'id' and value == 'lyric' ):
                self.lyrics_found = True
            else: self.lyrics_found = False
                
    def handle_data( self, text ):
        if ( self.lyrics_found ):
            self.lyrics += text

        
class Lyrics_Fetcher:
    def get_lyrics( self, artist, song ):
        url = 'http://www.lyricwiki.org/%s:%s'
        artist = self.format_param( artist )
        song = self.format_param( song )
        lyrics = self.fetch_lyrics( url % ( artist, song, ) )
        if ( not lyrics ):
            song_list = self.get_song_list( artist )
            return song_list
        else: return self.clean_text( lyrics )
    
    def fetch_lyrics( self, url ):
        if (not debug): usock = urllib.urlopen( url )
        else:
            usock = open( sys.path[ 0 ] + '\\lyrics_source.txt','r' )
        htmlSource = usock.read()
        usock.close()
        ####################### write source for testing #######################
        if (debugWrite):
            usock = open( sys.path[0] + '\\lyrics_source.txt','w' )
            usock.write( htmlSource )
            usock.close
        ##############################################################
        parser = Lyrics_Parser()
        parser.feed( htmlSource )
        parser.close()
        return parser.lyrics
        
    def format_param( self, param, caps = True):
        retVal = ''
        for word in param.split():
            if ( caps ): word = word.capitalize()
            word = word.replace( '/', '_' ).replace( 'Ac_dc', 'AC_DC' )
            retVal += urllib.quote( word ) + '_'
        return retVal[ : -1 ]
    
    def clean_text( self, text ):
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

    def get_song_list( self, artist ):
        url ="http://www.lyricwiki.org/%s"
        if (not debug): usock = urllib.urlopen( url % ( artist, ) )
        else:
            usock = open( sys.path[ 0 ] + '\\song_source.txt','r' )
        htmlSource = usock.read()
        usock.close()
        ####################### write source for testing #######################
        if (debugWrite):
            usock = open( sys.path[0] + '\\song_source.txt','w' )
            usock.write( htmlSource )
            usock.close
        ##############################################################
        parser = Song_List_Parser()
        parser.feed( htmlSource )
        parser.close()
        song_list = self.remove_dupes( parser.song_list )
        return song_list

    def remove_dupes( self, song_list ):
        dupes = {}
        for x in song_list:
            dupes[ x ] = x
        new_song_list = dupes.values()
        new_song_list.sort()
        return new_song_list

    def get_lyrics_from_list( self, item ):
        url = 'http://www.lyricwiki.org%s' % ( item[ 1 ], )
        lyrics = self.fetch_lyrics( url )
        return self.clean_text( lyrics )
        
if ( __name__ == '__main__' ):
    artist = "KISS"
    song = "I Love it Loud"
    lyrics = Lyrics_Fetcher().get_lyrics( artist, song )
    if ( type( lyrics ) == str ):
        print lyrics
    else:
        for song in lyrics:
            print song
            

