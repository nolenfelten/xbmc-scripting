import xbmc, os ,sys
import xml.dom.minidom
import traceback

class Language:
    """ Language Class: Returns a localized string """
    def __init__( self ):
        self._get_language()
        
    def _get_language( self ):
        self.strings = {}
        module_dir = os.path.dirname( sys.modules['language'].__file__ )
        cwd = os.path.join( os.path.dirname( module_dir ), 'language' )
        language = xbmc.getLanguage().lower()
        language_path = os.path.join( cwd, language, 'strings.xml' )
        if ( not os.path.isfile( language_path ) ):
            language = 'english'
            language_path = os.path.join( cwd, language, 'strings.xml' )
        success = self._parse_strings_file( language_path )
        if ( language != 'english' ):
            success = self._parse_strings_file( os.path.join( cwd, 'english', 'strings.xml' ) )
        return success
        
    def _parse_strings_file( self, language_path ):
        """ Main parser for the strings.xml file """
        try:
            # load and parse strings.xml file
            doc = xml.dom.minidom.parse( language_path )

            root = doc.documentElement
            # make sure this is a valid <window> xml file
            if ( not root or root.tagName != 'strings' ): raise
            
            # parse and resolve each <string>
            strings = root.getElementsByTagName( 'string' )
            for string in strings:
                if ( string.hasAttributes() ):
                    string_id = string.getAttribute( 'id' )
                if ( string_id and not self.strings.has_key( string_id ) ):
                    if ( string.hasChildNodes() ): 
                        self.strings[ int( string_id ) ] = string.firstChild.nodeValue
        except:
            traceback.print_exc()
            print "ERROR: Language file %s can't be opened" % ( language_path, )
            try: doc.unlink()
            except: pass
            return False
        else:
            try: doc.unlink()
            except: pass
            return True

    def string( self, code ):
        """ Returns the localized string if it exists """
        return self.strings.get( int( code ), str( code ) )
