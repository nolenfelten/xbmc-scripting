# official python modules
import os
# script modules
import common

class ExampleScriptWindow( common.gui.BaseScriptWindow ):
    def __init__( self ):
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
        }
        common.gui.BaseScriptWindow.__init__( self )

window = ExampleScriptWindow()
window.show()