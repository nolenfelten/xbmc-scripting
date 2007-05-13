import sys
import os

__scriptname__ = "Apple Movie Trailers"
__author__ = "Apple Movie Trailers (AMT) Team"
__url__ = "http://code.google.com/p/xbmc-scripting/"
__svn_url__ = "http://xbmc-scripting.googlecode.com/svn/trunk/Apple%20Movie%20Trailers"
__credits__ = "XBMC TEAM, freenode/#xbmc-scripting"
__version__ = "pre-0.98"

__credits_l1__ = "Head Developer & Coder"
__credits_r1__ = "Killarny"
__credits_l2__ = "Coder & Skinning"
__credits_r2__ = "Nuka1195"
__credits_l3__ = "Graphics & Skinning"
__credits_r3__ = "Jezz_X & Pike"

__add_credits_l1__ = "Xbox Media Center"
__add_credits_r1__ = "Team XBMC"
__add_credits_l2__ = "Usability"
__add_credits_r2__ = "Spiff"
__add_credits_l3__ = ""
__add_credits_r3__ = ""

BASE_RESOURCE_PATH = os.path.join( os.getcwd().replace( ";", "" ), "resources" )
sys.path.append( os.path.join( BASE_RESOURCE_PATH, "lib" ) )
import language
__language__ = language.Language().localized

if __name__ == "__main__":
    import gui
