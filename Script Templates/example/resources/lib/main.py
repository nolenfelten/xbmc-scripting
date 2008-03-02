# official python modules
import os
# script modules
import common

class ExampleScriptWindow( common.gui.BaseScriptWindow ):
    def __init__( self, xmlFile, resourcePath ):
        self.controls_map = {
            # LABEL: xbox media center
            1: None,
            # LABEL: script name
            2: {
                'label': common.scriptname,
            },
            # BUTTON: quit
            101: {
                'onClick': self.close,
            },
            # BUTTON: open
            102: {
                'onClick': self.open_new_file,
            },
        }
        common.gui.BaseScriptWindow.__init__( self, xmlFile, resourcePath )
    def open_new_file( self ):
        # get a path to the file 
        filepath = common.gui.get_browse_dialog( heading = common.localize( 1001 ) )
        filehandle = open( filepath, 'r' )
        # clear the list before adding new items
        self.clearList()
        # add a new item to the list for each line of text in the file
        for line in filehandle:
            self.addItem( line )
        # close the file
        filehandle.close()

xmlFile = 'script-%s-window.xml' % common.scriptname.replace( ' ', '_' )
window = ExampleScriptWindow( xmlFile, common.resource_path )
window.doModal()