"""
helper module for settings
"""

import os
#import xbmc
import xbmcgui
import guibuilder
import utilities
import traceback

class GUI( xbmcgui.WindowDialog ):
    def __init__( self, skin="Default", language=None ):
        self.base_path = os.path.join( os.getcwd().replace( ";", "" ), "resources", "skins" )
        self.gui_loaded = self.setupGUI( skin, language )
        if ( not self.gui_loaded ): self._close_dialog()
        else:
            self._set_variables()
        
    def setupGUI( self, skin, language ):
        """ sets up the gui using guibuilder """
        gb = guibuilder.GUIBuilder()
        ok, image_path = gb.create_gui( self, skin=skin, xml_name="chooser", language=language )
        return ok

    def _set_variables( self ):
        self.controller_action = utilities.setControllerAction()
            
    def show_chooser( self, choices, selection, list_control, title ):
        self.controls[ "Chooser Label" ][ "control" ].setLabel( title )
        self.choices = choices
        self.selection = selection
        self.list_control = list_control
        self._setup_list()
        self.doModal()

    def _setup_list( self ):
        #xbmcgui.lock()
        self.controls[ "Chooser List1" ][ "control" ].setVisible( self.list_control == 1 )
        self.controls[ "Chooser List2" ][ "control" ].setVisible( self.list_control == 2 )
        self.controls[ "Chooser Warning Label" ][ "control" ].setVisible( False )
        self.controls[ "Chooser Thumb" ][ "control" ].setVisible( self.list_control == 1 )
        self.controls[ "Chooser List%d" % self.list_control ][ "control" ].reset()
        for choice in self.choices:
            self.controls[ "Chooser List%d" % self.list_control ][ "control" ].addItem( choice )
        self.controls[ "Chooser List%d" % self.list_control ][ "control" ].selectItem( self.selection )
        self.setFocus( self.controls[ "Chooser List%d" % self.list_control ][ "control" ] )
        #xbmcgui.unlock()

    def _get_thumb( self, choice ):
        try:
            thumbnail = os.path.join( self.base_path, choice, "thumbnail.tbn" )
            if ( os.path.isfile( thumbnail ) ):
                self.controls[ "Chooser Thumb" ][ "control" ].setImage( thumbnail )
            else:
                self.controls[ "Chooser Thumb" ][ "control" ].setImage( "" )
            self.controls[ "Chooser Warning Label" ][ "control" ].setVisible( os.path.isfile( os.path.join( self.base_path, choice, "warning.txt" ) ) )
        except: traceback.print_exc()
            
    def _close_dialog( self, selection=None ):
        self.selection = selection
        self.close()
        
    def onControl( self, control ):
        if ( control is self.controls[ "Chooser List1" ][ "control" ] ):
            self._close_dialog( self.controls[ "Chooser List1" ][ "control" ].getSelectedPosition() )
        elif ( control is self.controls[ "Chooser List2" ][ "control" ] ):
            self._close_dialog( self.controls[ "Chooser List2" ][ "control" ].getSelectedPosition() )

    def onAction( self, action ):
        button_key = self.controller_action.get( action.getButtonCode(), "n/a" )
        if ( button_key == "Keyboard Backspace Button" or button_key == "B Button" or button_key == "Remote Back Button" ):
            self._close_dialog()
        elif ( button_key == "Keyboard ESC Button" or button_key == "Back Button" or button_key == "Remote Menu Button" ):
            self._close_dialog()
        elif ( self.list_control == 1 ):
            self._get_thumb( self.controls[ "Chooser List1" ][ "control" ].getSelectedItem().getLabel() )
