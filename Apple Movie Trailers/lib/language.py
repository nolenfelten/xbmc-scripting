"""
    Language Class:
    Is used to translate a language file like Xbox Media Center's language files.
    Originally Coded by Rockstar, Recoded by Donno :D
"""
import xbmc, re, os

class Language:
    def __init__( self ):
        cwd = os.path.join( os.getcwd(), 'language' ).replace( ';', '' )
        self.strings = {}
        temp_strings = []
        language = xbmc.getLanguage().lower()
        language_path = os.path.join( cwd, language, 'strings.xml' )
        if ( not os.path.isfile( language_path ) ):
            language = 'english'
            language_path = os.path.join( cwd, language, 'strings.xml' )
        
        try:
            f = open( language_path, 'r' )
            temp_strings = f.read()
            f.close()
            pattern = '<string id="(.*?)">(.*?)</string>'
            strings = re.findall(pattern, temp_strings)
            for item in strings:
                self.strings[int( item[0] )] = str( item[1] )
        
            if ( language != 'english' ):
                language_path = os.path.join( cwd, 'english', 'strings.xml' )
                temp_strings = f.read()
                f.close()
                pattern = '<string id="(.*?)">(.*?)</string>'
                strings = re.findall(pattern, temp_strings)
                for item in strings:
                    if ( not self.strings.has_key(int( item[0] ) ) ):
                        self.strings[int( item[0] )] = str( item[1] )
        except:
            print "ERROR: Language file %s can't be opened" % ( language_path, )

    def string( self, code ):
        try:
            if ( self.strings.has_key( int( code ) ) ):
                retVal = self.strings[int( code )].replace( '&amp;', '&' )
            else: retVal = None
        finally: return retVal
