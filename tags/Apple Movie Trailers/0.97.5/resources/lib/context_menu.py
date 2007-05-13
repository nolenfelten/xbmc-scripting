"""
Context menu module

Nuka1195
"""

import sys
import xbmcgui

import guibuilder
import utilities

_ = sys.modules[ "__main__" ].__language__
__scriptname__ = sys.modules[ "__main__" ].__scriptname__
__version__ = sys.modules[ "__main__" ].__version__


class GUI( xbmcgui.WindowDialog ):
    def __init__( self, skin="Default" ):
        self.gui_loaded = self._load_gui( skin )
        if ( not self.gui_loaded ): self._close_dialog()
            
    def _load_gui( self, skin ):
        """ sets up the gui using guibuilder """
        gb = guibuilder.GUIBuilder()
        gui_loaded, image_path = gb.create_gui( self, skin=skin, xml_name="context_menu", language=_ )
        return gui_loaded

    def show_context_menu( self, area, labels ):
        try:
            xbmcgui.lock()
            self._hide_buttons()
            self._setup_menu( area, labels )
            self.setFocus( self.controls[ "Context Menu Button1" ][ "control" ] )
        except: pass
        xbmcgui.unlock()
        self.doModal()

    def _hide_buttons( self ):
        for button in range( 1, 9 ):
            self.controls[ "Context Menu Button%d" % ( button, ) ][ "control" ].setVisible( False )
            self.controls[ "Context Menu Button%d" % ( button, ) ][ "control" ].setEnabled( False )

    def _setup_menu( self, area, labels ):
        """ centers the context_menu within an area """
        # get positions and dimensions
        button_height = self.controls[ "Context Menu Button1" ][ "control" ].getHeight()
        button_posx, button_posy = self.controls[ "Context Menu Button1" ][ "control" ].getPosition()
        dialog_width = self.controls[ "Context Menu Background Top" ][ "control" ].getWidth()
        dialog_top_height = self.controls[ "Context Menu Background Top" ][ "control" ].getHeight()
        dialog_bottom_height = self.controls[ "Context Menu Background Bottom" ][ "control" ].getHeight()
        dialog_top_posx, dialog_top_posy = self.controls[ "Context Menu Background Top" ][ "control" ].getPosition()
        dialog_middle_posy = self.controls[ "Context Menu Background Middle" ][ "control" ].getPosition()[ 1 ]
        dialog_middle_offsety = dialog_middle_posy - dialog_top_posy
        # calculate position
        button_offsetx = button_posx - dialog_top_posx
        button_offsety = button_posy - dialog_top_posy
        button_gap = 2
        dialog_middle_height = ( len( labels ) * ( button_height + button_gap ) ) - button_gap
        dialog_height = dialog_middle_height + dialog_top_height + dialog_bottom_height
        dialog_posx = int( float( area[ 2 ] - dialog_width ) / 2 ) + area[ 0 ]
        dialog_posy = int( float( area[ 3 ] - dialog_height ) / 2 ) + area[ 1 ]
        button_posx = dialog_posx + button_offsetx
        button_posy = dialog_posy + button_offsety
        # position and size menu
        self.controls[ "Context Menu Background Middle" ][ "control" ].setHeight( dialog_middle_height )
        self.controls[ "Context Menu Background Top" ][ "control" ].setPosition( dialog_posx, dialog_posy )
        self.controls[ "Context Menu Background Middle" ][ "control" ].setPosition( dialog_posx, dialog_posy + dialog_middle_offsety )
        self.controls[ "Context Menu Background Bottom" ][ "control" ].setPosition( dialog_posx, dialog_posy + dialog_middle_offsety + dialog_middle_height )
        # position buttons and set labels
        for button in range( len( labels ) ):
            self.controls[ "Context Menu Button%d" % ( button + 1, ) ][ "control" ].setPosition( button_posx, button_posy + ( ( button_height + button_gap ) * button ) )
            self.controls[ "Context Menu Button%d" % ( button + 1, ) ][ "control" ].setLabel( labels[ button ] )
            self.controls[ "Context Menu Button%d" % ( button + 1, ) ][ "control" ].setVisible( True )
            self.controls[ "Context Menu Button%d" % ( button + 1, ) ][ "control" ].setEnabled( True )

    def _close_dialog( self, selection=None ):
        self.selection = selection
        self.close()

    def onControl( self, control ):
        if ( control is self.controls[ "Context Menu Button1" ][ "control" ] ):
            self._close_dialog( 0 )
        elif ( control is self.controls[ "Context Menu Button2" ][ "control" ] ):
            self._close_dialog( 1 )
        elif ( control is self.controls[ "Context Menu Button3" ][ "control" ] ):
            self._close_dialog( 2 )
        elif ( control is self.controls[ "Context Menu Button4" ][ "control" ] ):
            self._close_dialog( 3 )
        elif ( control is self.controls[ "Context Menu Button5" ][ "control" ] ):
            self._close_dialog( 4 )
        elif ( control is self.controls[ "Context Menu Button6" ][ "control" ] ):
            self._close_dialog( 5 )
        elif ( control is self.controls[ "Context Menu Button7" ][ "control" ] ):
            self._close_dialog( 6 )
        else:
            self._close_dialog( 7 )

    def onAction( self, action ):
        if ( action.getButtonCode() in ( utilities.CANCEL_DIALOG + utilities.CONTEXT_MENU ) ):
            self._close_dialog()
