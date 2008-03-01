# official python modules
import os
# script modules
import common.gui

class ExampleScriptWindow( common.gui.BaseScriptWindow ):
    def __init__( self, xmlFile, resourcePath ):
        self.controls_map = {
            101: {
                'onClick': self.close,
                'onFocus': None,
            },
        }
        common.gui.BaseScriptWindow.__init__( self, xmlFile, resourcePath )

xmlFile = 'script-%s-window.xml' % common.gui.__scriptname__.replace( ' ', '_' )
window = ExampleScriptWindow( xmlFile, common.gui.RESPATH )
window.doModal()