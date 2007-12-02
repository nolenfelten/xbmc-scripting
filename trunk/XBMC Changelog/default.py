"""
    XBMC Changelog script
    
    Thanks to Modplug for the idea :)
    Thanks to SleepyP for hosting the changelog
"""

import os
import xbmcgui

__scriptname__ = "XBMC Changelog"
__author__ = "Nuka1195/EnderW/Killarny"
__url__ = "http://code.google.com/p/xbmc-scripting/"
__svn_url__ = "http://xbmc-scripting.googlecode.com/svn/trunk/XBMC%20Changelog"
__credits__ = "XBMC TEAM, freenode/#xbmc-scripting"
__version__ = "1.1"

resource_path = os.path.join( os.getcwd().replace( ";", "" ), "resources" )


class GUI( xbmcgui.WindowXML ):
    def __init__( self, *args, **kwargs ):
        base_url = "http://appliedcuriosity.cc/xbox/changelog.txt"
        self.exit_script = ( 247, 275, 61467, )
        self._fetch_changelog( base_url )

    def onInit( self ):
        self.getControl( 4 ).setLabel( self.header.replace( "\n", "[CR]" ) )
        self.getControl( 5 ).setText( self.changelog.replace( "\n", "[CR]" ) )
        self.getControl( 6 ).setLabel( "Last change: %s" % self.last_change )

    def _fetch_changelog( self, base_url ):
        dialog = xbmcgui.DialogProgress()
        dialog.create( "Fetching changelog..." )
        import urllib
        usock = urllib.urlopen( base_url )
        data = usock.readlines()
        usock.close()
        self.header = "".join( data[ 6 : 8 ] )
        self.changelog = "".join( data[ 8 : ] )
        self.last_change = data[ 8 ].split()[0]
        dialog.close()

    def onClick( self, controlId ):
        pass

    def onFocus( self, controlId ):
        pass

    def onAction( self, action ):
        if ( action.getButtonCode() in self.exit_script ):
            self.close()

if ( __name__ == "__main__" ):
    ui = GUI( "script-XBMC_Changelog-main.xml", resource_path, "Default" )
    ui.doModal()
    del ui