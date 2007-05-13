"""
helper module for settings

Nuka1195
"""

import sys
import os
import xbmcgui
#import xbmc

import guibuilder
import utilities

_ = sys.modules[ "__main__" ].__language__
__scriptname__ = sys.modules[ "__main__" ].__scriptname__
__version__ = sys.modules[ "__main__" ].__version__


class GUI( xbmcgui.WindowDialog ):
    def __init__( self, skin="Default" ):
        self.base_path = os.path.join( utilities.BASE_RESOURCE_PATH, "skins" )
        self.gui_loaded = self._load_gui( skin )
        if ( not self.gui_loaded ): self._close_dialog()
            
    def _load_gui( self, skin ):
        """ sets up the gui using guibuilder """
        gb = guibuilder.GUIBuilder()
        gui_loaded, image_path = gb.create_gui( self, skin=skin, xml_name="chooser", language=_ )
        return gui_loaded
            
    def show_chooser( self, choices, selection, list_control, title ):
        try:
            xbmcgui.lock()
            self.controls[ "Chooser Label" ][ "control" ].setLabel( title )
            self.list_control = list_control
            self._setup_list( choices, selection )
            if ( list_control == 1 ):
                self._get_thumb( self.controls[ "Chooser List1" ][ "control" ].getSelectedItem().getLabel() )
        except: pass
        xbmcgui.unlock()
        self.doModal()

    def _setup_list( self, choices, selection ):
        self.controls[ "Chooser List1" ][ "control" ].setVisible( self.list_control == 1 )
        self.controls[ "Chooser List2" ][ "control" ].setVisible( self.list_control == 2 )
        self.controls[ "Chooser Warning Label" ][ "control" ].setVisible( False )
        self.controls[ "Chooser Thumb" ][ "control" ].setVisible( self.list_control == 1 )
        self.controls[ "Chooser List%d" % self.list_control ][ "control" ].reset()
        for choice in choices:
            self.controls[ "Chooser List%d" % self.list_control ][ "control" ].addItem( choice )
        self.controls[ "Chooser List%d" % self.list_control ][ "control" ].selectItem( selection )
        self.setFocus( self.controls[ "Chooser List%d" % self.list_control ][ "control" ] )

    def _get_thumb( self, choice ):
        thumbnail = os.path.join( self.base_path, choice, "thumbnail.tbn" )
        self.controls[ "Chooser Thumb" ][ "control" ].setImage( thumbnail )
        self.controls[ "Chooser Warning Label" ][ "control" ].setVisible( os.path.isfile( os.path.join( self.base_path, choice, "warning.txt" ) ) )

    def _close_dialog( self, selection=None ):
        self.selection = selection
        self.close()
        
    def onControl( self, control ):
        #xbmc.sleep( 5 )
        self._close_dialog( control.getSelectedPosition() )

    def onAction( self, action ):
        if ( action.getButtonCode() in utilities.CANCEL_DIALOG ):
            self._close_dialog()
        elif ( self.list_control == 1 ):
            self._get_thumb( self.controls[ "Chooser List1" ][ "control" ].getSelectedItem().getLabel() )
