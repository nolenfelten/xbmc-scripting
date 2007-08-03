import sys
import os
import xbmcgui
import xbmc

__scriptname__ = "XBMC Lyrics"
__author__ = "XBMC Lyrics Team"
__url__ = "http://code.google.com/p/xbmc-scripting/"
__svn_url__ = "http://xbmc-scripting.googlecode.com/svn/trunk/XBMC%20Lyrics"
__credits__ = "XBMC TEAM, freenode/#xbmc-scripting"
__version__ = "1.5.5"

BASE_RESOURCE_PATH = os.path.join( os.getcwd().replace( ";", "" ), "resources" )
sys.path.append( os.path.join( BASE_RESOURCE_PATH, "lib" ) )
import language
__language__ = language.Language().localized

__credits_l1__ = __language__( 910 )#"Head Developer & Coder"
__credits_r1__ = "Nuka1195"
__credits_l2__ = __language__( 911 )#"Original author"
__credits_r2__ = "EnderW"
__credits_l3__ = __language__( 912 )#"Original skinning"
__credits_r3__ = "Smuto"

__add_credits_l1__ = __language__( 1 )#"Xbox Media Center"
__add_credits_r1__ = "Team XBMC"
__add_credits_l2__ = __language__( 913 )#"Unicode support"
__add_credits_r2__ = "Spiff"
__add_credits_l3__ = __language__( 914 )#"Language file"
__add_credits_r3__ = __language__( 2 )#"Translators name"


if ( __name__ == "__main__" ):
    if ( xbmc.Player().isPlayingAudio() ):
        import gui
        window = "main"
    else:
        import settings as gui
        window = "settings"
    ui = gui.GUI( "script-%s-%s.xml" % ( __scriptname__.replace( " ", "_" ), window, ), BASE_RESOURCE_PATH, "Default" )
    ui.doModal()
    del ui
