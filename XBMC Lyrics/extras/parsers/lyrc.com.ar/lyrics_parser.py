import os
import urllib
import re
import string

class Lyrics_Fetcher:
    def get_lyrics(self, artist, song):
        params = urllib.urlencode({'artist': artist, 'songname': song, 'procesado2': '1', 'Submit': ' S E A R C H '})
        f = urllib.urlopen("http://lyrc.com.ar/en/tema1en.php", params)
        Page = f.read()
        if string.find(Page, "Nothing found :") != -1:
            return None
        elif string.find(Page, "Suggestions :") != -1:
            links_query = re.compile('<br><a href=\"(.*?)\"><font color=\'white\'>(.*?)</font></a>', re.IGNORECASE)
            urls = re.findall(links_query, Page)
            print urls
            links = []
            for x in urls:
                links.append( ( x[1], x[0], ) )
            return links
        else:
            lyrics = self.parse_lyrics( Page )
            return lyrics
    
    def get_lyrics_from_list(self, link):
        self.url = "http://lyrc.com.ar/en/" + link[ 1 ]
        data = urllib.urlopen(self.url)
        Page = data.read()
        lyrics = self.parse_lyrics( Page )
        return lyrics
    
    def parse_lyrics(self, lyrics):
        try:
            query = re.compile('</script></td></tr></table>(.*)<p><hr size=1', re.IGNORECASE | re.DOTALL)
            full_lyrics = re.findall(query, lyrics)
            final = full_lyrics[0].replace("<br />\r\n","\n ")
        except:
            try:
                query = re.compile('</script></td></tr></table>(.*)<br><br><a href="#', re.IGNORECASE | re.DOTALL)
                full_lyrics = re.findall(query, lyrics)
                final = full_lyrics[0].replace("<br />\r\n","\n ")
            except:
                final = None
        return str(final)

if ( __name__ == '__main__' ):
    artist = "KISS"
    song = "I Love it Loud"
    lyrics = Lyrics_Fetcher().get_lyrics( artist, song )
    if ( type( lyrics ) == str ):
        print lyrics
    else:
        for song in lyrics:
            print song
            

