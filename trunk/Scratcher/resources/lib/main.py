# official python modules
import os
# official xbmc modules
import xbmcgui
# script modules
import common

class ScriptWindow( common.gui.BaseScriptWindow ):
    def __init__( self ):
        self.file = None
        self.eol = str() # end of line string used by file
        self.file_write_access = False
        self.changed = False
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
                def renumber_lines( line_number ):
                    # renumbers lines starting from line_number
                    for i in range( self.window.getListSize() ):
                        if i >= line_number:
                            # for pretty line numbers, increase by one for display
                            self.window.getListItem( i ).setLabel2( str( i + 1 ) )
                # set up functions to perform menu item selections
                def edit():
                    new_text = None
                    # show keyboard for user to change the text
                    new_text = common.gui.dialog.keyboard( original_text, common.localize( 1004 ) )
                    # perform the changes, assuming that the new text is not blank
                    #   or the same as the old text
                    if len( new_text ) and ( new_text != original_text ):
                        item.setLabel( new_text )
                        self.changed = True
                def insert():
                    # make line number for new item
                    new_id = id - 1
                    if new_id < 0:
                        new_id = 0
                    # insert the new item
                    item = xbmcgui.ListItem( '', str( new_id + 1 ) )
                    self.window.addItem( item, new_id )
                    # reorganize line numbers
                    renumber_lines( new_id )
                    # select the new inserted line
                    self.window.setCurrentItem( new_id )
                    # make sure we've got the handle to the proper 
                    #   ListItem still
                    item = self.window.getListItem( new_id )
                    new_text = None
                    # show keyboard for user to change the text
                    new_text = common.gui.dialog.keyboard( '', common.localize( 1004 ) )
                    if len( new_text ):
                        item.setLabel( new_text )
                    self.changed = True
                def delete():
                    self.window.removeItem( id )
                    # reorganize the line numbers
                    renumber_lines( id )
                    self.changed = True
                # menu items
                items = dict()
                items[len(items.keys())+1] = {
                    'label': common.localize( 501 ), # Edit
                    'thumb': 'script-line-changed.png',
                    'onClick': edit,
                }
                items[len(items.keys())+1] = {
                    'label': common.localize( 503 ), # Insert
                    'thumb': 'script-line-inserted.png',
                    'onClick': insert,
                }
                items[len(items.keys())+1] = {
                    'label': common.localize( 502 ), # Delete
                    'thumb': 'script-line-deleted.png',
                    'onClick': delete,
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
            try:
                # open the file in read only mode
                # TODO: check for write access here?
                self.file = open( filepath, 'rb' )
                def determine_eol():
                    # determine file EOL character string
                    end_of_line_chars = [ '\r', '\n' ]
                    # read single line out of file
                    line_one = self.file.readline()
                    # reset the seek position for later reads
                    self.file.seek(0)
                    # reset self.eol
                    self.eol = str()
                    # look at last two characters in the line
                    if len( line_one ) < 2:
                        eol = line_one
                    else:
                        eol = line_one[-2:]
                    for char in eol:
                        # we don't want any characters that aren't actually EOL to be
                        #   considered as such
                        if char in end_of_line_chars:
                            self.eol = self.eol + char
                    # readline() splits on '\n', so mac files won't split
                    #   note that the code above will not always result in self.eol
                    #   being an empty string, for example, if mac file ends in 
                    #   multiple empty lines, self.eol would be '\r\r' and valid to
                    #   the above code - need to check for that here too
                    file_len = int( os.stat( self.file.name ).st_size )
                    # if the file ended without a newline, see if this is mac file
                    if len( line_one ) == file_len:
                        # if a mac file ends in multiple newlines, set self.eol 
                        #   to only one EOL character
                        if len( self.eol ) > 1:
                            if self.eol[-1] == '\r':
                                self.eol = '\r'
                        # file had no EOL at the end of line_one, so check the
                        #   string to be sure that there aren't any mac EOL chars
                        if not len( self.eol ):
                            if line_one.find( '\r' ) > -1:
                                self.eol = '\r'
                    # still no eol encountered in this file, so set to default
                    if not len( self.eol ):
                        self.eol = os.linesep
                # self.changed will be True if the last opened file was edited
                # TODO: ask to save changes to last opened file
                if self.changed:
                    pass
                # clear the list before adding new items
                self.window.clearList()
                # add a new item to the list for each line of text in the file
                line_number = 0
                def line_cleanup( line ):
                    # strip all EOL characters out of the line for display
                    for char in self.eol:
                        line = line.replace( char, '' )
                    return line
                # figure out the EOL format
                determine_eol()
                if self.eol == '\r':
                    # mac line endings aren't recognized by readline()
                    #   but, don't do it this way unless it's required, 
                    #   because it is slower than using the for line in 
                    #   self.file method
                    lines = self.file.read( file_len ).split( self.eol )
                else:
                    lines = self.file
                # cleanup and add the lines as ListItems
                for line in lines:
                    line = line_cleanup( line )
                    line_number = line_number + 1
                    item = xbmcgui.ListItem( line, str( line_number ) )
                    self.window.addItem( item )
            except:
                import traceback
                traceback.print_exc()

# init the window instance
window = ScriptWindow()
# browse for a file to open
window.open_new_file()
# turn over control to the window
window.show()