"""
Credits modules

Nuka1195
"""

import sys
import xbmcgui
import guibuilder
import utilities


class GUI( xbmcgui.WindowDialog ):
    def __init__( self, *args, **kwargs ):
        self._ = kwargs['language']
        self.gui_loaded = self._load_gui( kwargs['skin'] )
        if ( not self.gui_loaded ): self._close_dialog()
        else:
            self._show_credits()
            
    def _load_gui( self, skin ):
        """ sets up the gui using guibuilder """
        gb = guibuilder.GUIBuilder()
        gui_loaded, image_path = gb.create_gui( self, skin=skin, xml_name="credits", language=self._ )
        return gui_loaded
        
    def _show_credits( self ):
        try:
            xbmcgui.lock()
            # Team credits
            self.controls['Credits Label']['control'].setLabel( sys.modules[ "__main__" ].__scriptname__ )
            self.controls['Credits Version Label']['control'].setLabel( '%s: %s' % ( self._( 900 ), sys.modules[ "__main__" ].__version__, ) )
            self.controls['Team Credits Label']['control'].setLabel( self._( 901 ) )
            self.controls['Team Credits List']['control'].reset()
            l = xbmcgui.ListItem( sys.modules[ "__main__" ].__credits_l1__, sys.modules[ "__main__" ].__credits_r1__ )
            self.controls['Team Credits List']['control'].addItem( l )
            l = xbmcgui.ListItem( sys.modules[ "__main__" ].__credits_l2__, sys.modules[ "__main__" ].__credits_r2__ )
            self.controls['Team Credits List']['control'].addItem( l )
            l = xbmcgui.ListItem( sys.modules[ "__main__" ].__credits_l3__, sys.modules[ "__main__" ].__credits_r3__ )
            self.controls['Team Credits List']['control'].addItem( l )
            
            # Additional credits
            self.controls['Additional Credits Label']['control'].setLabel( self._( 902 ) )
            self.controls['Additional Credits List']['control'].reset()
            l = xbmcgui.ListItem( sys.modules[ "__main__" ].__acredits_l1__, sys.modules[ "__main__" ].__acredits_r1__ )
            self.controls['Additional Credits List']['control'].addItem( l )
            l = xbmcgui.ListItem( sys.modules[ "__main__" ].__acredits_l2__, sys.modules[ "__main__" ].__acredits_r2__ )
            self.controls['Additional Credits List']['control'].addItem( l )
            l = xbmcgui.ListItem( sys.modules[ "__main__" ].__acredits_l3__, sys.modules[ "__main__" ].__acredits_r3__ )
            self.controls['Additional Credits List']['control'].addItem( l )
        except: print 'Credits Removed'
        xbmcgui.unlock()
        
    def _close_dialog( self ):
        self.close()
        
    def onControl( self, control ):
        pass
    
    def onAction( self, action ):
        if ( action.getButtonCode() in utilities.CANCEL_DIALOG ):
            self._close_dialog()
