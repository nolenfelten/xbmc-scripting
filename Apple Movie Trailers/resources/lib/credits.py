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
        try:
            self._ = kwargs['language']
            self.skin = kwargs['skin']
            self.gui_loaded = self.setupGUI()
            if ( not self.gui_loaded ): self.close()
            else:
                self.setupVariables()
                self.showCredits()
        except: 
            self.close()
                
    def setupVariables( self ):
        self.controller_action = utilities.setControllerAction()

    def setupGUI( self ):
        """ sets up the gui using guibuilder """
        gb = guibuilder.GUIBuilder()
        ok, image_path = gb.create_gui( self, skin=self.skin, xml_name="credits", language=self._ )
        return ok
        
    def showCredits( self ):
        try:
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
    
    def closeDialog( self ):
        self.close()
        
    def onControl( self, control ):
        pass
    
    def onAction( self, action ):
        button_key = self.controller_action.get( action.getButtonCode(), 'n/a' )
        if ( button_key == 'Keyboard Backspace Button' or button_key == 'B Button' or button_key == 'Remote Back Button' ):
            self.closeDialog()
        elif ( button_key == 'Keyboard ESC Button' or button_key == 'Back Button' or button_key == 'Remote Menu Button' ):
            self.closeDialog()
