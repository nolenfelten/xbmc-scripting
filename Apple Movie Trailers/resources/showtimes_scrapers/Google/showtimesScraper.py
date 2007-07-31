"""
Scraper for http://www.google.com/movies

Nuka1195
"""

import sys
import os
from sgmllib import SGMLParser
import urllib
import datetime

__title__ = "Google"
__credit__ = "Nuka1195"


class _TheaterListParser( SGMLParser ):
    """ 
        Parser Class: parses an html document for opening date 
    """
    def reset( self ):
        SGMLParser.reset( self )
        self.theater_list = {}
        self.current_theater = ""
        self.theater_id = None
        self.theater_name_found = False

    def start_a( self, attrs ):
        for key, value in attrs:
            if ( key == "href" and "&tid=" in value ):
                self.theater_id = value
                self.current_theater = ""

    def end_a( self ):
        if ( self.theater_id is not None ):
            self.theater_list[ self.current_theater ] = [ "", "", "", "http://www.google.com%s" % self.theater_id ]
            self.theater_name_found = True
            self.theater_id = None

    def handle_data( self, text ):
        if ( self.theater_id is not None ):
            self.current_theater += text
        elif ( text == "Map" ):
            self.theater_name_found = False
            phone = self.theater_list[ self.current_theater ][ 0 ].find( " - " )
            self.theater_list[ self.current_theater ][ 2 ] = self.theater_list[ self.current_theater ][ 0 ][ phone + 3 : -2 ].strip()
            self.theater_list[ self.current_theater ][ 0 ] = self.theater_list[ self.current_theater ][ 0 ][ : phone ]
        elif ( self.theater_name_found ):
            self.theater_list[ self.current_theater ][ 0 ] += "%s " % text.strip()


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
                #s = value.find( "date=" )
                #date = value[ s + 5 : ].split( "-" )
                #if ( len( date ) == 3 ):
                #    i = [ "jan", "feb", "mar", "apr", "may", "jun", "jul", "aug", "sep", "oct", "nov", "dec", ].index( date[ 1 ] ) + 1
                #    self.showtimes_date = "%s-%d-%s" % ( date[ 2 ], i, date[ 0 ], )


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
        self.theater_id = ""
        self.theater_set = False
        self.start_theaters = False
        self.showtimes_date = str( datetime.date.today() )
        self.showtimes_date_found = False

    def start_a( self, attrs ):
        for key, value in attrs:
            if ( key == "href" and value.startswith( "/movies?near=" ) ):
                self.theater_id = value
                self.current_theater = ""
            elif ( key == "href" and value.startswith( "http://www.google.com/url" ) and not self.showtimes_date_found ):
                s = value.find( "date%3D" )
                if ( s >= 0 ):
                    self.showtimes_date  = value[ s + 7 : s +17 ]
                    self.showtimes_date_found = True

    def end_a( self ):
        if ( self.start_theaters ):
            if ( self.theater_id ):
                self.theaters[ self.current_theater ] = [ "", "", "", "http://www.google.com%s" % self.theater_id ]
                self.theater_id = ""
                self.theater_set = True

    def handle_data( self, text ):
        if ( self.start_theaters and text.strip() ):
            if ( self.theater_id ):
                self.current_theater += text
            elif ( text.strip()[ 0 ].isdigit() and ":" in text ):
                if ( self.theaters[ self.current_theater ][ 1 ] ):
                    self.theaters[ self.current_theater ][ 1 ] += ", "
                self.theaters[ self.current_theater ][ 1 ] += text.strip()
                self.theater_set = False
            elif ( self.theater_set and text != "Map" and text != "Trailer" and text != "IMDb" ):#and not text.endswith( " - " ) ):
                self.theaters[ self.current_theater ][ 0 ] += "%s " % text.strip()
            elif ( self.theater_set ):
                self.theaters[ self.current_theater ][ 0 ] = self.theaters[ self.current_theater ][ 0 ][ : -2 ].strip()
        elif ( text == "Show more movies" or text == "Show more films" or text == "Show more theaters" ):
            self.start_theaters = True
            self.theater_id = ""


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
        if ( showtimes is None ):
            theaters = self._get_theater_list( self.base_url + "/movies?near=%s" % ( location, ) )
            return None, theaters
        else:
            date = datetime.date( int( date.split( "-" )[ 0 ] ), int( date.split( "-" )[ 1 ] ), int( date.split( "-" )[ 2 ] ) ).strftime( "%A, %B %d, %Y" )
            return date, showtimes
    
    def get_selection( self, url ):
        """ *REQUIRED: Returns movies for the selected theater """
        date, showtimes = self._fetch_showtimes( url )
        date = datetime.date( int( date.split( "-" )[ 0 ] ), int( date.split( "-" )[ 1 ] ), int( date.split( "-" )[ 2 ] ) ).strftime( "%A, %B %d, %Y" )
        return date, showtimes

    def _fetch_showtimes( self, url ):
        """ Fetch showtimes if available else return a list of theaters """
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
            if ( htmlSource.find( "Movie Reviews" ) >= 0 ):
                raise
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
        
    def _get_theater_list( self, url ):
        try:
            if ( not debug ):
                usock = urllib.urlopen( url )
            else:
                usock = open( os.path.join( os.getcwd().replace( ";", "" ), "showtimes_source3.txt" ), "r" )
            htmlSource = usock.read()
            usock.close()
            parser = _TheaterListParser()
            parser.feed( htmlSource )
            parser.close()
            if ( debugWrite ):
                file_object = open( os.path.join( os.getcwd().replace( ";", "" ), "showtimes_source3.txt" ), "w" )
                file_object.write( htmlSource )
                file_object.close()
            return parser.theater_list
        except:
            return None

    def _fetch_theater( self, url ):
        try:
            showtimes_date = None
            # Open url or local file (if debug)
            if ( not debug ):
                usock = urllib.urlopen( url )
            else:
                usock = open( os.path.join( os.getcwd().replace( ";", "" ), "showtimes_source.txt" ), "r" )
            htmlSource = usock.read()
            usock.close()
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




# used for testing only
debug = False
debugWrite = False

if ( __name__ == "__main__" ):
    # used to test get_lyrics() 
    movie = [ "Not Real Title", "el cantante", "Rush Hour 3", "The Simpsons Movie", "Transformers", "I Now Pronounce You Chuck & Larry", "Transformers", "I Now Pronounce You Chuck & Larry" ]
    location = [ "Houston", "detroit", "new york", "London", "Toronto", "33102", "W2 4YL", "T1A 3T9" ]
    url = [ "http://www.google.com/movies?near=Monroe,+MI&tid=f91ac86eb99bc459" ]
    for cnt in range( 0,1 ):
        date, theaters = ShowtimesFetcher().get_showtimes( movie[ cnt ], location[ cnt ] )
        #date, theaters = ShowtimesFetcher().get_selection( url[ cnt ] )
    

        # print the results
        print "====================================================="
        print "Showtimes for %s Movie: %s - Location: %s" % ( date, movie[ cnt ], location[ cnt ], )
        print
        if ( theaters ):
            theater_names = theaters.keys()
            theater_names.sort()
            for theater in theater_names:
                print theater
                print theaters[ theater ][ 0 ]#s[theater]
                print theaters[ theater ][ 1 ]#s[theater]
                print theaters[ theater ][ 2 ]#s[theater]
                print theaters[ theater ][ 3 ]#s[theater]
                print
        else:
            print "No showtimes found!"
        print "====================================================="
        print
