"""
Language module

Nuka1195
24/01/2008 Some changes by BigBellyBilly
"""

import os, sys
import xbmc
import xml.dom.minidom

class Language:
    """ Language Class: creates a dictionary of localized strings { int: string } """
    LANGUAGE_DIR_NAME = 'language'
    STRINGS_FILENAME = 'strings.xml'
    DEFAULT_LANG = 'english'
    
    def __init__( self ):
        """ initializer """
        # language folder
        base_path = self.get_base_path()
        # get the current language
        language = self._get_language( base_path )
        # create strings dictionary
        self._create_localized_dict( base_path, language )

    def get_base_path( self ):
        """ returns full language base path """
        module_dir = os.path.dirname( sys.modules['language'].__file__ )
        return os.path.join( os.path.dirname( module_dir ), Language.LANGUAGE_DIR_NAME )

    def _get_language( self, base_path ):
        """ returns the current language if a strings.xml file exists else returns english """
        # get the current users language setting
        language = xbmc.getLanguage().lower()
        # if no strings.xml file exists, default to english
        if ( not os.path.isfile( os.path.join( base_path, language, Language.STRINGS_FILENAME ) ) ):
            language = Language.DEFAULT_LANG
        return language

    def _create_localized_dict( self, base_path, language ):
        """ initializes self.strings and calls _parse_strings_file """
        # localized strings dictionary
        self.strings = {}
        # add localized strings
        self._parse_strings_file( os.path.join( base_path, language, Language.STRINGS_FILENAME ) )
        # fill-in missing strings with english strings
        if ( language != Language.DEFAULT_LANG ):
            self._parse_strings_file( os.path.join( base_path, Language.DEFAULT_LANG, Language.STRINGS_FILENAME ) )
        
    def _parse_strings_file( self, language_path ):
        """ adds localized strings to self.strings dictionary """
        try:
            # load and parse strings.xml file
            doc = xml.dom.minidom.parse( language_path )
            # make sure this is a valid <strings> xml file
            root = doc.documentElement
            if ( not root or root.tagName != "strings" ): raise
            # parse and resolve each <string id="#"> tag
            strings = root.getElementsByTagName( "string" )
            for string in strings:
                # convert id attribute to an integer
                string_id = int( string.getAttribute( "id" ) )
                # if a valid id add it to self.strings dictionary
                if ( string_id not in self.strings and string.hasChildNodes() ):
                    self.strings[ string_id ] = string.firstChild.nodeValue
        except:
            # print the error message to the log and debug window
            xbmc.output( "ERROR: Language file %s can't be parsed!" % ( language_path, ) )
        # clean-up document object
        try: doc.unlink()
        except: pass

    def localized( self, code ):
        """ returns the localized string if it exists """
        return self.strings.get( code, "Invailid Id %d" % ( code, ) )
