"""
Scraper for embedded lyrics with LAME 3.92

Nuka1195
"""

import sys, os
import xbmc
import re

class LyricsFetcher:
    """ required: Fetcher Class for www.lyricwiki.org """
    def __init__( self ):
        self.pattern = "USLT.*[A-Za-z0-9]*\x00([^\x00]*)TEXT"

    def get_lyrics( self, artist, song ):
        """ *required: Returns song lyrics or a blank string if none found """
        file_path = xbmc.Player().getPlayingFile()
        lyrics = self._fetch_lyrics( file_path )
        # if no lyrics found return blank string as there is no song list for embedded lyrics
        if ( not lyrics ):
            return ""
        else: return self._clean_text( lyrics )
    
    def get_lyrics_from_list( self, item ):
        """ *required: Returns song lyrics from user selection - item[1]"""
        return None

    def _fetch_lyrics( self, file_path ):
        """ Fetch lyrics if available """
        try:
            file_object = open( file_path , "rb" )
            file_data = file_object.read()
            file_object.close()
            lyrics = re.findall( self.pattern, file_data )
            return lyrics[ 0 ]
        except:
            return None

    def _clean_text( self, text ):
        """ Convert line terminators and html entities """
        text = text.replace( "\t", "" )
        text = text.replace( "\r\n", "\n" )
        text = text.replace( "\r", "\n" )
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
    
    # print the results
    print lyrics.encode( "utf-8", "ignore" )
