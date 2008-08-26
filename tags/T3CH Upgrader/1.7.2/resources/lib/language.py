"""
Language module

Nuka1195
Some mods by BBB:
  Defined STRINGS_FILENAME, DEFAULT_LANGUAGE
  Added get_base_path() so external scripts can discover the current language path.

"""

import os, sys
import xbmc
import xml.dom.minidom


class Language:
    """ Language Class: creates a dictionary of localized strings { int: string } """
    LANGUAGE_DIR_NAME = 'language'
    STRINGS_FILENAME = 'strings.xml'
    DEFAULT_LANGUAGE = "English"

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
        """ returns the current language if a strings.xml file exists else returns default language """
        # get the current users language setting
        language = xbmc.getLanguage()
        # if no strings.xml file exists, use default language
        if ( not os.path.isfile( os.path.join( base_path, language, Language.STRINGS_FILENAME ) ) ):
            language = self.DEFAULT_LANGUAGE
        return language

    def _create_localized_dict( self, base_path, language ):
        """ initializes self.strings and calls _parse_strings_file """
        # localized strings dictionary
        self.strings = {}
        # add localized strings
        self._parse_strings_file( os.path.join( base_path, language, Language.STRINGS_FILENAME ) )
        # fill-in missing strings with default language strings
        if ( language != self.DEFAULT_LANGUAGE ):
            self._parse_strings_file( os.path.join( base_path, Language.DEFAULT_LANGUAGE, Language.STRINGS_FILENAME ) )
        
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
            xbmc.output( "Language file parsed successfully: %s" % language_path)
        except:
            # print the error message to the log and debug window
            xbmc.output( "ERROR: Language file %s can't be parsed!" % ( language_path, ) )
        # clean-up document object
        try: doc.unlink()
        except: pass

    def localized( self, code ):
        """ returns the localized string if it exists """
        return self.strings.get( code, "Invalid Id %d" % ( code, ) )
