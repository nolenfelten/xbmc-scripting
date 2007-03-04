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

class GUI( xbmcgui.Window ):
    def __init__( self ):
        global dialog
        self.gui_loaded = self.setupGUI()
        if (not self.gui_loaded): 
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
        gb = guibuilder.GUIBuilder()
        ok = gb.create_gui( self, title=__scriptname__, useDescAsKey=True, dlg=dialog, pct=60 )
        return ok

    def onAction( self, action ):
        if action == 10: self.close()

if ( __name__ == "__main__" ):
    ui = GUI()
    if (ui.gui_loaded): ui.doModal()
    del ui