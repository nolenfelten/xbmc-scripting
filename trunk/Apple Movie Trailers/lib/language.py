"""
    Language Class:
    Is used to translate a language file like Xbox Media Center's language files.
    Originally Coded by Rockstar, Recoded by Donno :D
"""
import xbmc, re, os#, default


#---Language Class by RockStar and tweaked by Donno--#000000#FFFFFF-----------------------------------------
class Language:
    def __init__( self ):
        thePath = os.path.join( os.getcwd(), 'language' ).replace( ';', '' ) # workaround apparent xbmc bug - os.getcwd() returns an extraneous semicolon (;) at the end of the path
        self.strings = {}
        tempstrings = []
        language = xbmc.getLanguage().lower()
        if ( os.path.exists( os.path.join( thePath, '%s.xml' % ( language, ) ) ) ):
            foundlang = language
        else:
            foundlang = "english"
        langdoc = os.path.join( thePath, '%s.xml' % ( foundlang, ) )
        try:
            f=open( langdoc, 'r' )
            tempstrings=f.read()
            f.close()
            exp='<string id="(.*?)">(.*?)</string>'
            
            res=re.findall(exp,tempstrings)
            for stringdat in res:
                self.strings[int( stringdat[0] )] = str( stringdat[1] )
        except:
            print "ERROR: Language file %s can't be opened" % ( langdoc, )
            #xbmcgui.Dialog().ok(default.__scriptname__, "ERROR!", "Language file %s can't be opened" % ( langdoc, ) )

    def string( self, code ):
        try:
            if ( self.strings.has_key( int( code ) ) ):
                retVal = self.strings[int( code )].replace( '&amp;', '&' )
                
            else: retVal = None
        finally: return retVal
