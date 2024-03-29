# main import's
import sys
import os

# Script constants
__scriptname__ = "Apple Movie Trailers"
__author__ = "Apple Movie Trailers (AMT) Team"
__url__ = "http://code.google.com/p/xbmc-scripting/"
__svn_url__ = "http://xbmc-scripting.googlecode.com/svn/trunk/Apple%20Movie%20Trailers"
__credits__ = "XBMC TEAM, freenode/#xbmc-scripting"
__version__ = "pre-0.99.7.3b"
__svn_revision__ = "$Revision$"
__XBMC_Revision__ = "22965"

def _check_compatible():
    try:
        # spam plugin statistics to log
        xbmc.log( "[SCRIPT] - '%s: Version - %s-r%s' initialized!" % ( __scriptname__, __version__, __svn_revision__.replace( "$", "" ).replace( "Revision", "" ).replace( ":", "" ).strip() ), xbmc.LOGNOTICE )
        # get xbmc revision
        xbmc_rev = int( xbmc.getInfoLabel( "System.BuildVersion" ).split( " r" )[ -1 ][ : 5 ] )
        # compatible?
        ok = xbmc_rev >= int( __XBMC_Revision__ )
    except:
        # error, so unknown, allow to run
        xbmc_rev = 0
        ok = 2
    # spam revision info
    xbmc.log( "        ** Required XBMC Revision: r%s **" % ( __XBMC_Revision__, ), xbmc.LOGNOTICE )
    xbmc.log( "        ** Found XBMC Revision: r%d [%s] **" % ( xbmc_rev, ( "Not Compatible", "Compatible", "Unknown", )[ ok ], ), xbmc.LOGNOTICE )
    # if not compatible, inform user
    if ( not ok ):
        import xbmcgui
        import os
        # get localized strings
        _ = xbmc.Language( os.getcwd() ).getLocalizedString
        # inform user
        xbmcgui.Dialog().ok( "%s - %s: %s" % ( __script__, _( 32700 ), __version__, ), _( 32701 ) % ( __script__, ), _( 32702 ) % ( __XBMC_Revision__, ), _( 32703 ) )
    #return result
    return ok


# Shared resources
BASE_RESOURCE_PATH = os.path.join( os.getcwd(), "resources" )
sys.path.append( os.path.join( BASE_RESOURCE_PATH, "lib" ) )
# append the proper platforms folder to our path, xbox is the same as win32
env = ( os.environ.get( "OS", "win32" ), "win32", )[ os.environ.get( "OS", "win32" ) == "xbox" ]
sys.path.append( os.path.join( BASE_RESOURCE_PATH, "platform_libraries", env ) )
# create our language object
__language__ = xbmc.Language( os.getcwd() ).getLocalizedString

# Main team credits
__credits_l1__ = __language__( 910 )#"Head Developer & Coder"
__credits_r1__ = "Killarny"
__credits_l2__ = __language__( 911 )#"Coder & Skinning"
__credits_r2__ = "Nuka1195"
__credits_l3__ = __language__( 912 )#"Graphics & Skinning"
__credits_r3__ = "Pike"

# additional credits
__add_credits_l1__ = __language__( 1 )#"Xbox Media Center"
__add_credits_r1__ = "Team XBMC"
__add_credits_l2__ = __language__( 913 )#"Usability"
__add_credits_r2__ = "Spiff & JMarshall"
__add_credits_l3__ = __language__( 914 )#"Language File"
__add_credits_r3__ = __language__( 2 )#"Translators name"


# Start the main gui
if __name__ == "__main__":
    # only run if compatible
    if ( _check_compatible() ):
        # main window
        import gui
