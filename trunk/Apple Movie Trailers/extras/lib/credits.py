import xbmc, xbmcgui
import os, guibuilder, sys
import amt_util, default

class GUI( xbmcgui.WindowDialog ):
    def __init__( self, *args, **kwargs ):
        try:
            self.cwd = os.path.dirname( sys.modules['default'].__file__ )
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
        
    def setupGUI( self ):
        if ( self.skin == 'Default' ): current_skin = xbmc.getSkinDir()
        else: current_skin = self.skin
        if ( not os.path.exists( os.path.join( self.cwd, 'extras', 'skins', current_skin ))): current_skin = 'default'
        skin_path = os.path.join( self.cwd, 'extras', 'skins', current_skin )
        image_path = os.path.join( skin_path, 'gfx' )
        if ( self.getResolution() == 0 or self.getResolution() % 2 ): xml_file = 'credits_16x9.xml'
        else: xml_file = 'credits.xml'
        if ( not os.path.isfile( os.path.join( skin_path, xml_file ))): xml_file = 'credits.xml'
        guibuilder.GUIBuilder( self, os.path.join( skin_path, xml_file ), image_path, useDescAsKey=True, useLocal=True, fastMethod=True, debug=False )
        
    def showCredits( self ):
        try:
            # Team credits
            self.controls['Credits Label']['control'].setLabel( self._(0) )
            self.controls['Credits Version Label']['control'].setLabel( '%s: %s' % ( self._(100), default.__version__, ) )
            self.controls['Team Credits Label']['control'].setLabel( self._(101) )
            self.controls['Team Credits List']['control'].reset()
            l = xbmcgui.ListItem( default.__credits_l1__, default.__credits_r1__ )
            self.controls['Team Credits List']['control'].addItem( l )
            l = xbmcgui.ListItem( default.__credits_l2__, default.__credits_r2__ )
            self.controls['Team Credits List']['control'].addItem( l )
            l = xbmcgui.ListItem( default.__credits_l3__, default.__credits_r3__ )
            self.controls['Team Credits List']['control'].addItem( l )
            
            # Additional credits
            self.controls['Additional Credits Label']['control'].setLabel( self._(102) )
            self.controls['Additional Credits List']['control'].reset()
            l = xbmcgui.ListItem( default.__acredits_l1__, default.__acredits_r1__ )
            self.controls['Additional Credits List']['control'].addItem( l )
            l = xbmcgui.ListItem( default.__acredits_l2__, default.__acredits_r2__ )
            self.controls['Additional Credits List']['control'].addItem( l )
            l = xbmcgui.ListItem( default.__acredits_l3__, default.__acredits_r3__ )
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
