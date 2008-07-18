"""
Language module

Nuka1195

Modified to work with XinBox by Stanley87
"""

import os
import xbmc
import xml.dom.minidom, traceback


class Language:
    try:
        title = ""
        def __init__(self,title):
            self.title = title
        
        def load(self,thepath):
            self.strings = {}
            tempstrings = []
            language = xbmc.getLanguage()
            if ( not os.path.isfile( os.path.join( thepath,language,"strings.xml" ) ) ):
                language = "English"
            self.strings = {}
            self._parse_strings_file( os.path.join( thepath,language,"strings.xml" ) )
            if ( language != "English" ):
                self._parse_strings_file( os.path.join( thepath, "English", "strings.xml" ) )


        def _parse_strings_file( self, language_path ):
            try:
                doc = xml.dom.minidom.parse( language_path )
                root = doc.documentElement
                if ( not root or root.tagName != "strings" ): raise
                strings = root.getElementsByTagName( "string" )
                for string in strings:
                    string_id = int( string.getAttribute( "id" ) )
                    if ( string_id not in self.strings and string.hasChildNodes() ):
                        self.strings[ string_id ] = string.firstChild.nodeValue
            except:
                xbmc.output( "ERROR: Language file %s can't be parsed!" % ( language_path, ) )
            try: doc.unlink()
            except: pass        

        def string(self,code):
            return self.strings.get(code)
    except:traceback.print_exc()
