"""
    Language Class:
    Is used to translate a language file like Xbox Media Center's language files.
    Originally Coded by Rockstar, Recoded by Donno :D
"""
import xbmc, re, os ,sys

class Language:
    def __init__( self ):
        module_dir = os.path.dirname( sys.modules['language'].__file__ )
        cwd = os.path.join( os.path.dirname( module_dir ), 'language' )
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
                self.strings[int( item[0] )] = str( item[1] ).replace( '&amp;', '&' ).replace( '&lt;', '<' ).replace( '&gt;', '>' )
        
            if ( language != 'english' ):
                language_path = os.path.join( cwd, 'english', 'strings.xml' )
                f = open( language_path, 'r' )
                temp_strings = f.read()
                f.close()
                strings = re.findall(pattern, temp_strings)
                for item in strings:
                    if ( not self.strings.has_key(int( item[0] ) ) ):
                        self.strings[int( item[0] )] = str( item[1] ).replace( '&amp;', '&' ).replace( '&lt;', '<' ).replace( '&gt;', '>' )
        except:
            print "ERROR: Language file %s can't be opened" % ( language_path, )

    def string( self, code ):
        return self.strings.get( int( code ), str( code ) )
