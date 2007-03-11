"""
Scraper for http://www.lyricwiki.org

Nuka1195
"""

import sys, os
from sgmllib import SGMLParser
import urllib

class _SongListParser( SGMLParser ):
    """ Parses an html document for all song links """
    def reset( self ):
        SGMLParser.reset( self )
        self.song_list = []
        self.url = "None"

    def start_a( self, attrs ):
        for key, value in attrs:
            if ( key == "href" ):
                if ( not value[ 0 ] == "#" and not value[ : 10 ] =="/Category:" and
                    not value[ : 11 ] == "/LyricWiki:" and not value == "/Main_Page" and
                    not value[ : 15 ] == "/Special:Search" ):
                    self.url = value
            elif ( key == "title" ):
                if ( urllib.unquote( self.url[ 1 : ] ) == urllib.unquote( value.replace( " ", "_" ).replace( "&amp;", "&" ) ) ):
                    self.song_list += [ ( unicode( value[ value.find( ":" ) + 1 : ], "utf-8", "ignore" ), self.url, ) ]
            else:
                self.url = "None"

class _LyricsParser( SGMLParser ):
    """ Parses an html document for song lyrics """
    def reset( self ):
        SGMLParser.reset( self )
        self.lyrics_found = False
        self.lyrics = unicode( "", "utf-8" )

    def start_div( self, attrs ):
        for key, value in attrs:
            if ( key == "id" and value == "lyric" ):
                self.lyrics_found = True
            else: self.lyrics_found = False
                
    def start_pre( self, attrs ):
        self.lyrics_found = True

    def handle_data( self, text ):
        if ( self.lyrics_found ):
            try:
                self.lyrics += unicode( text, "utf-8", "ignore" )
            except:
                # bad data so skip it
                pass

class LyricsFetcher:
    """ required: Fetcher class for www.lyricwiki.org """
    def __init__( self ):
        self.url = "http://www.lyricwiki.org"
        self.exceptions = self._get_exceptions()
        
    def get_lyrics( self, artist, song ):
        """ *required: Returns song lyrics or a list of choices from artist & song """
        url = self.url + "/%s:%s"
        artist = self._format_param( artist )
        song = self._format_param( song )
        lyrics = self._fetch_lyrics( url % ( artist, song, ) )
        # if no lyrics found try just artist for a list of songs
        if ( not lyrics ):
            song_list = self._get_song_list( artist )
            return song_list
        else: return self._clean_text( lyrics )
    
    def get_lyrics_from_list( self, item ):
        """ *required: Returns song lyrics from user selection - item[1]"""
        lyrics = self._fetch_lyrics( self.url + item[ 1 ] )
        return self._clean_text( lyrics )
        
    def _get_exceptions( self ):
        """ Reads a rules file for exceptions in formatting artist or song """
        exceptions = []
        try:
            if ( __name__ == "__main__" ):
                ex_path = os.path.join( os.getcwd().replace( ";", "" ), "exceptions.txt" )
            else:
                ex_path = os.path.join( "T:\\script_data", sys.modules[ "__main__" ].__scriptname__, "scrapers", os.path.split( os.path.dirname( sys.modules[ "lyricsScraper" ].__file__ ) )[ 1 ], "exceptions.txt" )
                if ( not os.path.isfile( ex_path ) ):
                    self._make_exception_file( ex_path )
            ex_file = open( ex_path, "r" )
            ex_list = ex_file.read().split("||")
            ex_file.close()
            for ex in ex_list:
                exceptions += [ ( ex.split( "|" )[0], ex.split( "|" )[1], ) ]
        except: pass
        return exceptions

    def _make_exception_file( self, ex_path ):
        try:
            os.makedirs( os.path.split( ex_path )[ 0 ] )
            ex_file = open( ex_path, "w" )
            ex_file.write( "Ac_dc|AC_DC||Abba|ABBA" )
            ex_file.close()
        except: pass

    def _fetch_lyrics( self, url ):
        """ Fetch lyrics if available """
        try:
            # Open url or local file (if debug == True)
            if (not debug): usock = urllib.urlopen( url )
            else:
                usock = open( os.path.join( os.getcwd().replace( ";", "" ), "lyrics_source.txt" ), "r" )
            htmlSource = usock.read()
            usock.close()
            # Save htmlSource to a file for testing scraper (if debugWrite == True)
            if (debugWrite):
                usock = open( os.path.join( os.getcwd().replace( ";", "" ), "lyrics_source.txt" ), "w" )
                usock.write( htmlSource )
                usock.close
            # Parse htmlSource for lyrics
            parser = _LyricsParser()
            parser.feed( htmlSource )
            parser.close()
            return parser.lyrics
        except:
            return None
        
    def _get_song_list( self, artist ):
        """ If no lyrics found, fetch a list of choices """
        try:
            url = self.url + "/%s"
            # Open url or local file (if debug == True)
            if (not debug): usock = urllib.urlopen( url % ( artist, ) )
            else:
                usock = open( os.path.join( os.getcwd().replace( ";", "" ), "songs_source.txt" ), "r" )
            htmlSource = usock.read()
            usock.close()
            # Save htmlSource to a file for testing scraper (if debugWrite == True)
            if ( debugWrite ):
                usock = open( os.path.join( os.getcwd().replace( ";", "" ), "songs_source.txt" ), "w" )
                usock.write( htmlSource )
                usock.close
            # Parse htmlSource for song links
            parser = _SongListParser()
            parser.feed( htmlSource )
            parser.close()
            # Create sorted return list
            song_list = self._remove_dupes( parser.song_list )
            return song_list
        except:
            return None
            
    def _remove_dupes( self, song_list ):
        """ Returns a sorted list with duplicates removed """
        # this is apparently the fastest method
        dupes = {}
        for x in song_list:
            dupes[ x ] = x
        new_song_list = dupes.values()
        new_song_list.sort()
        return new_song_list

    def _format_param( self, param ):
        """ Converts param to the form expected by www.lyricwiki.org """
        caps = True
        result = ""
        # enumerate thru string to properly capitalize words (why doesn't title() do this properly?)
        for letter in param.upper().strip():
            if ( letter == " " ):
                letter = "_"
                caps = True
            elif ( letter in "(_-." ):
                caps = True
            elif ( unicode( letter.isalpha() ) and caps ):
                caps = False
            else:
                letter = letter.lower()
                caps = False
            result += letter
        result = result.replace( "/", "_" )
        # replace any exceptions
        for ex in self.exceptions:
            result = result.replace( ex[ 0 ], ex[ 1 ] )
        # properly quote string for url
        retVal = urllib.quote( result )
        return retVal
    
    def _clean_text( self, text ):
        """ Convert line terminators and html entities """
        try:
            text = text.replace( "\t", "" )
            text = text.replace( "<br> ", "\n" )
            text = text.replace( "<br>", "\n" )
            text = text.replace( "<br /> ", "\n" )
            text = text.replace( "<br />", "\n" )
            text = text.replace( "<div>", "\n" )
            text = text.replace( "> ", "\n" )
            text = text.replace( ">", "\n" )
            text = text.replace( "&amp;", "&" )
            text = text.replace( "&gt;", ">" )
            text = text.replace( "&lt;", "<" )
            text = text.replace( "&quot;", '"' )
        except: pass
        return text

# used for testing only
debug = False
debugWrite = False

if ( __name__ == "__main__" ):
    # used to test get_lyrics() 
    artist = [ "The Charlie Daniels Band", "ABBA", "Jem","Stealers Wheel","Paul McCartney & Wings","ABBA","AC/DC", "Tom Jones", "Kim Mitchell", "Ted Nugent", "Blue Öyster Cult", "The 5th Dimension", "Big & Rich", "Don Felder" ]
    song = [ "(What This World Needs Is) A Few More Rednecks", "S.O.S","24","Stuck in the middle with you","Band on the run", "Dancing Queen", "T.N.T.", "She's A Lady", "Go for Soda", "Free-for-all", "(Don't Fear) The Reaper", "Age of Aquarius", "Save a Horse (Ride a Cowboy)", "Heavy Metal (Takin' a Ride)" ]
    for cnt in range( 0, 1 ):
        lyrics = LyricsFetcher().get_lyrics( artist[ cnt ], song[ cnt ] )
    
    # used to test get_lyrics_from_list() 
    #url = ("Big & Rich:Save a Horse (Ride a Cowboy)", "/Big_%26_Rich:Save_a_Horse_%28Ride_a_Cowboy%29")
    #url = (u"Stuck In The Middle With You", "/Stealers_Wheel:Stuck_In_The_Middle_With_You")
    #lyrics = LyricsFetcher().get_lyrics_from_list( url )
    
    # print the results
    if ( type( lyrics ) == list ):
        for song in lyrics:
            print song
    else:
        print lyrics.encode( "utf-8", "ignore" )
