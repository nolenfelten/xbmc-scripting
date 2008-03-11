# official python modules
import os
# script modules
import common

class ExampleScriptDialog( common.gui.BaseScriptDialog ):
    def __init__( self ):
        self.controls_map = {
            110: { # BUTTON: close
                'onClick': self.close,
            },
        }
        common.gui.BaseScriptDialog.__init__( self )

class ExampleScriptWindow( common.gui.BaseScriptWindow ):
    def __init__( self ):
        self.controls_map = {
            1: { # LABEL: script name
                'label': common.scriptname,
            },
            101: { # BUTTON: show popup menu
                'onClick': self.popup,
            },
            110: { # BUTTON: quit
                'onClick': self.close,
            },
        }
        common.gui.BaseScriptWindow.__init__( self )
    def popup( self ):
        items = {
            1: {
                'label': 'item 1',
                'onClick': self.item1,
            },
            2: {
                'label': 'item 2',
                'onClick': self.item2,
            },
        }
        popupmenu = common.gui.dialog.popupmenu( items )
    def item1( self ):
        print 'item 1 selected'
    def item2( self ):
        print 'item 2 selected'

window = ExampleScriptWindow()
window.show()