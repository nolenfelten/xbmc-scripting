"""
Language module

Nuka1195
05/01/2008 Some changes by BigBellyBilly
"""

import os, sys
import xbmc
import xml.dom.minidom


class Language:
    """ Language Class: creates a dictionary of localized strings { int: string } """
    def __init__( self ):
        """ initializer """
        self.default_language = "english"
        # language folder
        module_dir = os.path.dirname( sys.modules['language'].__file__ )
        base_path = os.path.join( os.path.dirname( module_dir ), 'language' )

        # get language
        language = self._get_language( base_path )
        if not language:
            xbmc.output("No language files found")
        else:
	        # create strings dictionary
	        self._create_localized_dict( base_path, language )
        
    def _get_language( self, base_path ):
        """ returns the current language if a strings.xml file exists else returns english """
        # get the current users language setting
        language = ""
        langList = [xbmc.getLanguage(), self.default_language]
        for lang in langList:
            if ( not os.path.isfile( os.path.join( base_path, lang.lower(), "strings.xml" ) ) ):
                xbmc.output( "requested language strings missing: " + lang )
            else:
                language = lang
                break

        xbmc.output("_get_language() language= " + language)
        return language

    def _create_localized_dict( self, base_path, language ):
        """ initializes self.strings and calls _parse_strings_file """
        # localized strings dictionary
        self.strings = {}
        # add localized strings
        if self._parse_strings_file( os.path.join( base_path, language, "strings.xml" ) ):
        	# fill-in missing strings with english strings
            if ( language != self.default_language ):
                self._parse_strings_file( os.path.join( base_path, self.default_language, "strings.xml" ) )
        
    def _parse_strings_file( self, language_path ):
        """ adds localized strings to self.strings dictionary """
        xbmc.output("_parse_strings_file() " + language_path)
        success = False
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

            success = True
        except:
            # print the error message to the log and debug window
            xbmc.output( "ERROR: Parsing language file: %s" % ( language_path, ) )
        # clean-up document object
        try: doc.unlink()
        except: pass

        return success

    def localized( self, code ):
        """ returns the localized string if it exists """
        return self.strings.get( code, "Invailid Id %d" % ( code, ) )
