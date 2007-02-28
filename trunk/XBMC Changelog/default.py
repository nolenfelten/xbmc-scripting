###XBMC Changelog script################################################
#Coded by SveinT (sveint@gmail.com)
# Updated by Killarny (killarny@gmail.com)
#
#Thanks to Modplug for the idea :)
#Thanks a lot to ChokeManiac for help and of course for his great skins!
#
#Last updated: 2006 August 13
########################################################################

__scriptname__ = 'XBMC Changelog'
__author__ = 'Nuka1195/EnderW/killarny'
__url__ = 'http://code.google.com/p/xbmc-scripting/'
__credits__ = 'XBMC TEAM, freenode/#xbmc-scripting'
__version__ = '1.0.1'

import xbmcgui, xbmc
dialog = xbmcgui.DialogProgress()
dialog.create(__scriptname__)
dialog.update(5, 'Importing modules & initializing...')

import urllib
dialog.update(20)
import sys
dialog.update(40)
import os
dialog.update(60)

# url for the raw changelog
CHANGELOG = 'http://appliedcuriosity.cc/xbox/changelog.txt'
# how many lines of changes to show

sys.path.append(os.path.join( os.getcwd().replace( ";", "" ), 'resources', 'lib' ) )
    
def get_changes():
    # get the actual changelog.txt from sourceforge
    data = urllib.urlopen( CHANGELOG )
    data = data.read()

    # ignore the top 7 lines, as they contain nothing useful
    changes = data.split('\n')[8:]

    # search each line to determine if it has a hyphen as the second
    # character, meaning that it is a new change, and not a multiline
    # change
    changelog = []
    for each in changes:
        # ignore empty lines
        if not len( each ):
            continue
        changelog += [ each ]
    changes = '\n'.join( changelog )
    return changes

class windowOverlay( xbmcgui.Window ):
    def __init__( self ):
        global dialog
        self.setupGUI()
        if (not self.SUCCEEDED): 
            self.close()
        else:
            self.show()
            dialog.close()
            dialog = xbmcgui.DialogProgress()
            dialog.create('XBMC Changelog')
            dialog.update(-1, 'Downloading changelog', 'Please wait...' )
            try:
                change_text = get_changes()
            finally:
                dialog.close()
            self.controls[ 'textarea' ]['control'].setText( change_text )
            
    def setupGUI( self ):
        global dialog
        import guibuilder
        cwd = os.getcwd().replace( ";", "" )
        current_skin = xbmc.getSkinDir()
        if ( not os.path.exists( os.path.join( cwd, 'resources', 'skins', current_skin ))): current_skin = 'default'
        skin_path = os.path.join( cwd, 'resources', 'skins', current_skin )
        image_path = os.path.join( skin_path, 'gfx' )
        if ( self.getResolution() == 0 or self.getResolution() % 2 ): xml_file = 'skin_16x9.xml'
        else: xml_file = 'skin.xml'
        if ( not os.path.isfile( os.path.join( skin_path, xml_file ))): xml_file = 'skin.xml'
        guibuilder.GUIBuilder( self, os.path.join( skin_path, xml_file ), image_path, 
            title=__scriptname__, useDescAsKey=True, dlg=dialog, pct=60 )

    def onAction( self, action ):
        if action == 10: self.close()


MyDisplay = windowOverlay()
if (MyDisplay.SUCCEEDED): MyDisplay.doModal()
del MyDisplay