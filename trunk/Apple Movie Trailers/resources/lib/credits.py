import sys, os
import xbmc, xbmcgui
import guibuilder
import utilities

class GUI( xbmcgui.WindowDialog ):
    def __init__( self, *args, **kwargs ):
        try:
            self._ = kwargs['language']
            self.skin = kwargs['skin']
            self.setupGUI()
            if ( not self.SUCCEEDED ): self.close()
            else:
                self.setupVariables()
                self.showCredits()
        except: 
            self.close()
                
    def setupVariables( self ):
        self.controller_action = amt_util.setControllerAction()

    def setupGUI( self, skin ):
        """ sets up the gui using guibuilder """
        gb = guibuilder.GUIBuilder()
        ok =  gb.create_gui( self, skin=skin, skinXML="credits", useDescAsKey=True, language=self._, fastMethod=True )
        return ok
        
    def showCredits( self ):
        try:
            # Team credits
            self.controls['Credits Label']['control'].setLabel( self._(0) )
            self.controls['Credits Version Label']['control'].setLabel( '%s: %s' % ( self._(100), sys.modules[ "__main__" ].__version__, ) )
            self.controls['Team Credits Label']['control'].setLabel( self._(101) )
            self.controls['Team Credits List']['control'].reset()
            l = xbmcgui.ListItem( sys.modules[ "__main__" ].__credits_l1__, sys.modules[ "__main__" ].__credits_r1__ )
            self.controls['Team Credits List']['control'].addItem( l )
            l = xbmcgui.ListItem( sys.modules[ "__main__" ].__credits_l2__, sys.modules[ "__main__" ].__credits_r2__ )
            self.controls['Team Credits List']['control'].addItem( l )
            l = xbmcgui.ListItem( sys.modules[ "__main__" ].__credits_l3__, sys.modules[ "__main__" ].__credits_r3__ )
            self.controls['Team Credits List']['control'].addItem( l )
            
            # Additional credits
            self.controls['Additional Credits Label']['control'].setLabel( self._(102) )
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
