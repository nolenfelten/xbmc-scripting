import os
import xbmc, xbmcgui
import guibuilder
import utilities

class GUI( xbmcgui.WindowDialog ):
    def __init__( self, skin="Default" ):
        self.gui_loaded = self.setupGUI( skin )
        if ( not self.gui_loaded ): self.closeDialog()
        else:
            self._set_variables()
    except: self.closeDialog()
        
    def show_chooser( self, choices, selection, list_control ):
        try:
            self.choices = choices
            self.selection = selection
            self.list_control = list_control
            self._setup_list()
            self.doModal()

    def setupGUI( self ):
        """ sets up the gui using guibuilder """
        gb = guibuilder.GUIBuilder()
        ok, image_path = gb.create_gui( self, skin=skin, xml_name="chooser" )
        return ok

    def _set_variables( self ):
        self.controller_action = utilities.setControllerAction()
            
    def _setup_list( self ):
        self.controls[ "Chooser List%d" % self.list_control ][ "control" ].reset()
        for choice in self.choices:
            self.controls[ "Chooser List%d" % self.list_control ][ "control" ].addItem( choice )
    
    def closeDialog( self, selection=None ):
        self.close()
        return selection
        
    def onControl( self, control ):
        if ( control is self.controls[ "Chooser List1" ][ "control" ] ):
            self.closeDialog( self.controls[ "Chooser List1" ][ "control" ].getSelectedPosition() )
        elif ( control is self.controls[ "Chooser List2" ][ "control" ] ):
            self.closeDialog( self.controls[ "Chooser List2" ][ "control" ].getSelectedPosition() )

    def onAction( self, action ):
        button_key = self.controller_action.get( action.getButtonCode(), "n/a" )
        if ( button_key == "Keyboard Backspace Button" or button_key == "B Button" or button_key == "Remote Back Button" ):
            self.closeDialog()
        elif ( button_key == "Keyboard ESC Button" or button_key == "Back Button" or button_key == "Remote Menu Button" ):
            self.closeDialog()
