# official python modules
import os
# official xbmc modules
import xbmcgui
# script modules
import common

class ScriptWindow( common.gui.BaseScriptWindow ):
    def __init__( self ):
        self.file = None
        self.file_write_access = False
        self.changed_lines = {
            # line_num: new_text,
        }
        self.deleted_lines = {
            # line_num: old_text,
        }
        self.controls_map = {
            1: { # LABEL: script name
                'label': common.scriptname,
            },
            50: { # LIST: text area
                'onClick': self.change_line,
            },
            101: { # BUTTON: open
                'onClick': self.open_new_file,
            },
            102: { # BUTTON: save
                'onClick': None,
            },
        }
        common.gui.BaseScriptWindow.__init__( self )

    def change_line( self ):
        if not self.check_access( self.file.name ):
            # file is read-only, don't allow line changes
            dialog = xbmcgui.Dialog()
            dialog.ok(
                os.path.split( self.file.name )[-1],
                common.localize( 1002 ),
                common.localize( 1003 )
            )
        else:
            try:
                # find the current id and ListItem object
                id = self.window.getCurrentListPosition()
                item = self.window.getListItem( id )
                try:
                    # get text from the ListItem
                    original_text = item.getLabel()
                except:
                    # text missing, default to empty string
                    original_text = str()
                def edit():
                    new_text = None
                    # show keyboard for user to change the text
                    new_text = common.gui.dialog.keyboard( original_text, common.localize( 1004 ) )
                    # perform the changes, assuming that the new text is not blank
                    #   or the same as the old text
                    if new_text and new_text is not original_text:
                        try:
                            item.setThumbnailImage( 'script-line-changed.png' )
                            item.setLabel( new_text )
                            self.changed_lines[id] = new_text
                        except:
                            print 'unable to set the new text'
                def delete():
                    # flag the line for removal
                    try:
                        item.setThumbnailImage( 'script-line-deleted.png' )
                        self.deleted_lines[id] = original_text
                    except:
                        print 'unable to delete the line'
                # menu items
                items = {
                    1: {
                        'label': 'Edit',
                        'thumb': 'script-line-changed.png',
                        'onClick': edit,
                    },
                    2: {
                        'label': 'Delete',
                        'thumb': 'script-line-deleted.png',
                        'onClick': delete,
                    },
                }
                # show the menu
                menu = common.gui.dialog.popupmenu( items )
            except:
                import traceback
                traceback.print_exc()
                print 'error changing the line of text'

    def close( self ):
        # close the file
        self.file.close()
        # close the window
        common.gui.BaseScriptWindow.close( self )

    def check_access( self, filepath ):
        return os.access( filepath, os.W_OK )

    def open_new_file( self ):
        # get a path to the file 
        filepath = common.gui.dialog.browse( heading = common.localize( 1001 ) )
        if len( filepath ):
            # open the file in read only mode
            # TODO: check for write access here?
            self.file = open( filepath, 'r' )
            # ensure that the changed_lines dictionary is blank
            # TODO: if not blank already, ask to save changes to last file
            self.changed_lines = dict()
            # clear the list before adding new items
            self.window.clearList()
            # function to beautify each line of text for display
            def line_cleanup( line ):
                end_of_line_chars = [ '\r', '\n' ]
                for char in end_of_line_chars: line = line.replace( char, '' )
                return line
            # add a new item to the list for each line of text in the file
            line_number = 0
            for line in self.file:
                line = line_cleanup( line )
                line_number = line_number + 1
                item = xbmcgui.ListItem( line, str( line_number ) )
                self.window.addItem( item )

# init the window instance
window = ScriptWindow()
# browse for a file to open
window.open_new_file()
# turn over control to the window
window.show()