# official python modules
import os
# official xbmc modules
import xbmcgui
# script modules
import common

class ScriptWindow( common.gui.BaseScriptWindow ):
    def __init__( self, xmlFile, resourcePath ):
        self.controls_map = {
            2: { # LABEL: script name
                'label': common.scriptname,
            },
            101: { # BUTTON: open
                'onClick': self.open_new_file,
            },
        }
        common.gui.BaseScriptWindow.__init__( self, xmlFile, resourcePath )
    def open_new_file( self ):
        # get a path to the file 
        filepath = common.gui.show_browse_dialog( heading = common.localize( 1001 ) )
        filehandle = open( filepath, 'r' )
        # clear the list before adding new items
        self.clearList()
        # function to beautify each line of text for display
        def line_cleanup( line ):
            end_of_line_chars = [ '\r', '\n' ]
            for char in end_of_line_chars: line = line.replace( char, '' )
            return line
        # add a new item to the list for each line of text in the file
        line_number = 0
        for line in filehandle:
            line = line_cleanup( line )
            line_number = line_number + 1
            item = xbmcgui.ListItem( line, str( line_number ) )
            self.addItem( item )
        # close the file
        filehandle.close()

# construct the xml filename
xmlFile = 'script-%s-window.xml' % common.scriptname.replace( ' ', '_' )
# init the window instance
window = ScriptWindow( xmlFile, common.resource_path )
# browse for a file to open
window.open_new_file()
# turn over control to the window
window.doModal()