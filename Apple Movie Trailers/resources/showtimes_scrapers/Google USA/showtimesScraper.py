"""
Scraper for http://www.google.com/movies

Nuka1195
"""

import sys
import os
from sgmllib import SGMLParser
import urllib
import datetime

__title__ = "Google USA"
__credit__ = "Nuka1195"


class _OpeningDateParser( SGMLParser ):
    """ 
        Parser Class: parses an html document for opening date 
    """
    def reset( self ):
        SGMLParser.reset( self )
        self.url = None
        self.showtimes_date = None

    def start_a( self, attrs ):
        for key, value in attrs:
            if ( key == "href" and value.startswith( "/movies?near=" ) and self.url is None ):
                self.url = value
                s = value.find( "date=" )
                date  = value[ s + 5 : ].split( "-" )
                i = [ "jan", "feb", "mar", "apr", "may", "jun", "jul", "aug", "sep", "oct", "nov", "dec", ].index( date[ 1 ] ) + 1
                self.showtimes_date = "%s-%d-%s" % ( date[ 2 ], i, date[ 0 ], )


class _ShowtimesParser( SGMLParser ):
    """ 
        Parser Class: parses an html document for movie showtimes and date
        - creates a key { theater: [#:##] }
        - formats date (dayofweek, month day, year)
    """
    def reset( self ):
        SGMLParser.reset( self )
        self.theaters = {}
        self.current_theater = ""
        self.theater_found = False
        self.start_theaters = False
        self.showtimes_date = str( datetime.date.today() )
        self.showtimes_date_found = False

    def start_a( self, attrs ):
        for key, value in attrs:
            if ( key == "href" and value.startswith( "/movies?near=" ) ):
                self.theater_found = True
            elif ( key == "href" and value.startswith( "http://www.google.com/url" ) and not self.showtimes_date_found ):
                s = value.find( "date%3D" )
                if ( s >= 0 ):
                    self.showtimes_date  = value[ s + 7 : s +17 ]
                    self.showtimes_date_found = True

    def handle_data( self, text ):
        if ( self.start_theaters and text.strip() ):
            if ( self.theater_found ):
                self.current_theater = text
                self.theaters[ self.current_theater ] = ""
                self.theater_found = False
            elif ( text.strip()[ 0 ].isdigit() and ":" in text ):
                if ( self.theaters[ self.current_theater ] ):
                    self.theaters[ self.current_theater ] += ", "
                self.theaters[ self.current_theater ] += text.strip()
        elif ( text == "Show more movies" ):
            self.start_theaters = True
            self.theater_found = False


class ShowtimesFetcher:
    """ 
        *REQUIRED: Fetcher Class for www.google.com/movies
        - returns a key { theater: [#:##] } and date of showtimes
    """
    def __init__( self ):
        self.base_url = "http://www.google.com"

    def get_showtimes( self, movie, location ):
        """ *REQUIRED: Returns showtimes for each theater in your local """
        movie = self._format_param( movie )
        location = self._format_param( location )
        date, showtimes = self._fetch_showtimes( self.base_url + "/movies?q=%s&near=%s" % ( movie, location, ) )
        date = datetime.date( int( date.split( "-" )[ 0 ] ), int( date.split( "-" )[ 1 ] ), int( date.split( "-" )[ 2 ] ) ).strftime( "%A, %B %d, %Y" )
        return date, showtimes
    
    def _fetch_showtimes( self, url ):
        """ Fetch lyrics if available """
        try:
            showtimes_date = None
            # Open url or local file (if debug)
            if ( not debug ):
                usock = urllib.urlopen( url )
            else:
                usock = open( os.path.join( os.getcwd().replace( ";", "" ), "showtimes_source.txt" ), "r" )
            htmlSource = usock.read()
            usock.close()
            if ( htmlSource.find( "No showtimes were found" ) >= 0 ):
                htmlSource, showtimes_date = self._get_first_date( htmlSource )
            # Save htmlSource to a file for testing scraper (if debugWrite)
            if ( debugWrite ):
                file_object = open( os.path.join( os.getcwd().replace( ";", "" ), "showtimes_source.txt" ), "w" )
                file_object.write( htmlSource )
                file_object.close()
            # Parse htmlSource for showtimes
            parser = _ShowtimesParser()
            parser.feed( htmlSource )
            parser.close()
            date = ( showtimes_date, parser.showtimes_date, )[ showtimes_date is None ]
            return date, parser.theaters
        except:
            return None, None
        
    def _format_param( self, param ):
        """ Converts param to the form expected by www.google.com/movies """
        result = urllib.quote_plus( param )
        return result

    def _get_first_date( self, htmlSource ):
        try:
            if ( debugWrite ):
                file_object = open( os.path.join( os.getcwd().replace( ";", "" ), "showtimes_source2.txt" ), "w" )
                file_object.write( htmlSource )
                file_object.close()
            parser = _OpeningDateParser()
            parser.feed( htmlSource )
            parser.close()
            date = None
            if ( parser.url is not None ):
                if ( not debug ):
                    usock = urllib.urlopen( self.base_url + parser.url )
                else:
                    usock = open( os.path.join( os.getcwd().replace( ";", "" ), "showtimes_source2.txt" ), "r" )
                htmlSource = usock.read()
                usock.close()
                date = parser.showtimes_date
        except:
            pass
        return htmlSource, date
        

# used for testing only
debug = False
debugWrite = False

if ( __name__ == "__main__" ):
    # used to test get_lyrics() 
    movie = [ "Rush Hour 3", "Transformers", "I Now Pronounce You Chuck & Larry" ]
    location = [ "33102", "33102", "33102" ]
    for cnt in range( 1 ):
        date, theaters = ShowtimesFetcher().get_showtimes( movie[ cnt ], location[ cnt ] )
        # print the results
        print "Showtimes for %s Movie: %s - Location: %s" % ( date, movie[ cnt ], location[ cnt ], )
        if ( theaters ):
            theater_names = theaters.keys()
            theater_names.sort()
            for theater in theater_names:
                print theater, theaters[ theater ]#s[theater]
        else:
            print "No showtimes found!"
        print
