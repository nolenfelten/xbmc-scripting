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
                'onClick': self.test,
            },
            2: {
                'label': 'item 2',
                'onClick': self.test,
            },
        }
        popupmenu = common.gui.dialog.popupmenu( items )
    def test( self ):
        print 'balha'

window = ExampleScriptWindow()
window.show()