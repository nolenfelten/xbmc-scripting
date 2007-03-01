"""
Language module

Nuka1195
"""
import sys, os
import xbmc
import xml.dom.minidom

class Language:
    """ Language Class: creates a dictionary of { int: string } """
    def __init__( self ):
        self._get_language()
        
    def _get_language( self ):
        """ gets the current language """
        self.strings = {}
        # language folder
        cwd = os.path.join( os.getcwd().replace( ";", "" ), "resources", "language" )
        # get the current users language setting
        language = xbmc.getLanguage().lower()
        language_path = os.path.join( cwd, language, "strings.xml" )
        # if no strings.xml exists, default to english
        if ( not os.path.isfile( language_path ) ):
            language = "english"
            language_path = os.path.join( cwd, language, "strings.xml" )
        # add localized strings
        ok = self._parse_strings_file( language_path )
        # fill-in missing strings with english strings
        if ( language != "english" ):
            ok = self._parse_strings_file( os.path.join( cwd, "english", "strings.xml" ) )
        
    def _parse_strings_file( self, language_path ):
        """ adds localized strings to the strings dictionary """
        try:
            # load and parse strings.xml file
            doc = xml.dom.minidom.parse( language_path )
            # make sure this is a valid <strings> xml file
            root = doc.documentElement
            if ( not root or root.tagName != "strings" ): raise
            # parse and resolve each <string>
            strings = root.getElementsByTagName( "string" )
            for string in strings:
                if ( string.hasAttributes() ):
                    string_id = string.getAttribute( "id" )
                if ( string_id and not self.strings.has_key( string_id ) ):
                    if ( string.hasChildNodes() ): 
                        self.strings[ int( string_id ) ] = string.firstChild.nodeValue
            ok = True
        except:
            print "ERROR: Language file %s can't be opened" % ( language_path, )
            ok = False
        try: doc.unlink()
        except: pass
        return ok

    def string( self, code ):
        """ returns the localized string if it exists """
        return self.strings.get( int( code ), str( code ) )
