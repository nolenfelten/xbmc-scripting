# official python modules
import os
# script modules
import common

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
        print 'popup goes here'

window = ExampleScriptWindow()
window.show()