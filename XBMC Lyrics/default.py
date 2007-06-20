import sys
import os
import xbmcgui
import xbmc

__scriptname__ = "XBMC Lyrics"
__author__ = "XBMC Lyrics Team"
__url__ = "http://code.google.com/p/xbmc-scripting/"
__svn_url__ = "http://xbmc-scripting.googlecode.com/svn/trunk/XBMC%20Lyrics"
__credits__ = "XBMC TEAM, freenode/#xbmc-scripting"
__version__ = "1.5.2"

BASE_RESOURCE_PATH = os.path.join( os.getcwd().replace( ";", "" ), "resources" )
sys.path.append( os.path.join( BASE_RESOURCE_PATH, "lib" ) )
import language
__language__ = language.Language().localized

if ( __name__ == "__main__" ):
    if ( xbmc.Player().isPlayingAudio() ):
        import gui
        ui = gui.GUI( "script-XBMC_Lyrics-main.xml", BASE_RESOURCE_PATH, "Default" )
        ui.doModal()
        del ui
    else:
        xbmcgui.Dialog().ok( __scriptname__, __language__( 638 ), __language__( 639 ) )
