"""
Scraper for http://www.lyricwiki.org using their API

Nuka1195
"""

import sys
import os
import urllib
# TODO: remove when json works
import re

if ( __name__ != "__main__" ):
    import xbmc

__title__ = "LyricWiki.org API"
__allow_exceptions__ = True


class XmlUtils :
    def getText (self, nodeParent, childName ):
        # Get child node...
        node = nodeParent.getElementsByTagName( childName )[0]
        
        if node == None :
            return None
        
        # Get child text...
        text = ""
        for child in node.childNodes:
            if child.nodeType == child.TEXT_NODE :
                text = text + child.data
        return text


class LyricsFetcher:
    """ required: Fetcher Class for www.lyricwiki.org """
    def __init__( self ):
        self.base_url = "http://lyricwiki.org/api.php"
        self._set_exceptions()
        
        
        
    def get_lyrics_start(self, *args):
		lyricThread = threading.Thread(target=self.get_lyrics_thread, args=args)
		lyricThread.setDaemon(True)
		lyricThread.start()

    def lyricwiki_format(self, text):
		return urllib.quote(str(unicode(text).title()))

    def get_lyrics_thread(self, artist, title):
		try:
#			timeout = socketgettimeout()
#			socketsettimeout(consts.LYRIC_TIMEOUT)
			lyricpage = urllib.urlopen("http://lyricwiki.org/index.php?title=%s:%s&action=edit" % (self.lyricwiki_format(artist), self.lyricwiki_format(title))).read()
			print ("http://lyricwiki.org/index.php?title=%s:%s&action=edit" % (self.lyricwiki_format(artist), self.lyricwiki_format(title)))
			content = re.split("<textarea[^>]*>", lyricpage)[1].split("</textarea>")[0]
			if content.startswith("#REDIRECT [["):
				addr = "http://lyricwiki.org/index.php?title=%s&action=edit" % urllib.quote(content.split("[[")[1].split("]]")[0])
			        content = urllib.urlopen(addr).read()
			        #print "Cont" + str(content)
			lyrics = content.split("&lt;lyrics&gt;")[1].split("&lt;/lyrics&gt;")[0]
#			print str(lyrics)
#			if lyrics.strip() != "&lt;!-- PUT LYRICS HERE (and delete this entire line) --&gt;":
#				lyrics = misc.unescape_html(lyrics)
#				lyrics = misc.wiki_to_html(lyrics)
#				lyrics = lyrics.decode("utf-8")
			return lyrics 
				#self.call_back(callback, lyrics=lyrics)
#			else:
#				error = "Lyrics not found"
#				return error
		except:
			error = "Fetching lyrics failed"
			return error
			#self.call_back(callback, error=error)        
        
    def get_lyrics( self, artist, song ):
        """ *required: Returns song lyrics or a list of choices from artist & song """
        # format artist and song, check for exceptions
        artist = self._format_param( artist )
        song = self._format_param( song, False )
        # fetch lyrics
        lyrics = self._fetch_lyrics( artist, song )
        # if no lyrics found try just artist for a list of songs
        if ( not lyrics ):
            # fetch song list
            song_list = self._get_song_list( artist )
            return song_list
        else: return lyrics
    
    def get_lyrics_from_list( self, item ):
        """ *required: Returns song lyrics from user selection - item[1]"""
        lyrics = self.get_lyrics( item[ 0 ], item[ 1 ] )
        return lyrics
        
    def _set_exceptions( self, exception=None ):
        """ Sets exceptions for formatting artist """
        try:
            if ( __name__ == "__main__" ):
                ex_path = os.path.join( os.getcwd(), "exceptions.txt" )
            else:
                name = __name__.replace( "resources.scrapers.", "" ).replace( ".lyricsScraper", "" )
                ex_path = os.path.join( xbmc.translatePath( "P:\\script_data" ), os.getcwd(), "scrapers", name, "exceptions.txt" )
            ex_file = open( ex_path, "r" )
            self.exceptions = eval( ex_file.read() )
            ex_file.close()
        except:
            self.exceptions = {}
        if ( exception is not None ):
            self.exceptions[ exception[ 0 ] ] = exception[ 1 ]
            self._save_exception_file( ex_path, self.exceptions )

    def _save_exception_file( self, ex_path, exceptions ):
        """ Saves the exception file as a repr(dict) """
        try:
            if ( not os.path.isdir( os.path.split( ex_path )[ 0 ] ) ):
                os.makedirs( os.path.split( ex_path )[ 0 ] )
            ex_file = open( ex_path, "w" )
            ex_file.write( repr( exceptions ) )
            ex_file.close()
        except: pass
        
    def _fetch_lyrics( self, artist, song ):
        """ Fetch lyrics if available """
        try:
            url = self.base_url + "?action=lyrics&artist=%s&song=%s&fmt=xml&func=getSong"
            # Open url or local file (if debug)
            
            if ( not debug ):
                usock = urllib.urlopen( url % ( artist, song, ) )
                
            else:
                usock = open( os.path.join( os.getcwd(), "lyrics_source.txt" ), "r" )
            # read source
            jsonSource = usock.read()
            print str(jsonSource)
            import xml.dom.minidom
            resultDoc = xml.dom.minidom.parseString(jsonSource)
            xmlUtils  = XmlUtils() 
            result    = xmlUtils.getText(resultDoc, "url")
            print result
            
            # close socket
            usock.close()
            
            weblyr = urllib.urlopen(result)
            lyr = weblyr.read()
            weblyr.close()
            print str(lyr)
            resultDoc = lyr.split()
            print str(resultDoc)
#           xmlUtils  = XmlUtils() 
#            result1    = xmlUtils.getText(resultDoc, "div class='lyricbox'")
            print str(result1)          
            # Save htmlSource to a file for testing scraper (if debugWrite)
            if ( debugWrite ):
                file_object = open( os.path.join( os.getcwd(), "lyrics_source.txt" ), "w" )
                file_object.write( jsonSource )
                file_object.close()
            # exec jsonSource to a native python dictionary
            exec jsonSource
            if ( song[ "lyrics" ] == "Not found" or song[ "lyrics" ].startswith( "{{Wikipedia}}" ) ):
                raise
            lyrics = song[ "lyrics" ]
            return lyrics
        except:
            return None
        
    def _get_song_list( self, artist ):
        """ If no lyrics found, fetch a list of choices """
        try:
            # TODO: change to json when json works
            url = self.base_url + "?func=getArtist&fmt=xml&artist=%s"
            # Open url or local file (if debug)
            if ( not debug ):
                usock = urllib.urlopen( url % ( artist, ) )
            else:
                usock = open( os.path.join( os.getcwd(), "songs_source.txt" ), "r" )
            # read source
            jsonSource = usock.read()
            # close socket
            usock.close()
            # Save htmlSource to a file for testing scraper (if debugWrite)
            if ( debugWrite ):
                file_object = open( os.path.join( os.getcwd(), "songs_source.txt" ), "w" )
                file_object.write( jsonSource )
                file_object.close()
            # exec jsonSource to a native python dictionary
            #exec jsonSource
            # Create sorted return list
            songs = re.findall( "<item>(.*)</item>", jsonSource )
            songs.sort()
            song_list = []
            for song in songs:
                song_list += [ [ song, ( artist, song, ) ] ]
            return song_list
        except:
            return None

    def _format_param( self, param, exception=True ):
        """ Converts param to the form expected by www.lyricwiki.org """
        # properly quote string for url
        result = urllib.quote( param )
        # replace any exceptions
        if ( exception and result in self.exceptions ):
            result = self.exceptions[ result ]
        return result
    
# used for testing only
debug = False
debugWrite = False

if ( __name__ == "__main__" ):
    # used to test get_lyrics() 
    artist = [ "Iron & Wine", "The Charlie Daniels Band", "ABBA", "Jem","Stealers Wheel","Paul McCartney & Wings","ABBA","AC/DC", "Tom Jones", "Kim Mitchell", "Ted Nugent", "Blue yster Cult", "The 5th Dimension", "Big & Rich", "Don Felder" ]
    song = [ "On Your Wings", "(What This World Needs Is) A Few More Rednecks", "S.O.S","24","Stuck in the middle with you","Band on the run", "Dancing Queen", "T.N.T.", "She's A Lady", "Go for Soda", "Free-for-all", "(Don't Fear) The Reaper", "Age of Aquarius", "Save a Horse (Ride a Cowboy)", "Heavy Metal (Takin' a Ride)" ]
    for cnt in range( 2,3 ):
        lyrics = LyricsFetcher().get_lyrics( artist[ cnt ], song[ cnt ] )
    
        # print the results
        if ( isinstance( lyrics, list ) ):
            print "List:"
            for song in lyrics:
                print song
            print "\nSong 1 lyrics:\n____________________"
            lyrics = LyricsFetcher().get_lyrics_from_list( lyrics[ 0 ][ 1 ] )
            print lyrics.encode( "utf-8", "ignore" )
        else:
            print lyrics.encode( "utf-8", "ignore" )
