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
                'onClick': None,
                'onFocus': None,
            },
            101: { # BUTTON: show popup menu
                'label': None,
                'onClick': self.popup,
                'onFocus': None,
            },
            110: { # BUTTON: quit
                'label': None,
                'onClick': self.close,
                'onFocus': None,
            },
        }
        common.gui.BaseScriptWindow.__init__( self )
    def popup( self ):
        items = {
            1: {
                'label': 'item 1',
                'label2': None,
                'icon': None,
                'thumb': None,
                'onClick': self.item1,
                'onFocus': None,
            },
            2: {
                'label': 'item 2',
                'label2': None,
                'icon': None,
                'thumb': None,
                'onClick': self.item2,
                'onFocus': None,
            },
        }
        popupmenu = common.gui.dialog.popupmenu( items )
    def item1( self ):
        print 'item 1 selected'
    def item2( self ):
        print 'item 2 selected'

window = ExampleScriptWindow()
window.show()