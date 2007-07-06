"""
helper module for settings

Nuka1195
"""

import sys
import os
import xbmcgui
import xbmc
#import traceback

from utilities import *

_ = sys.modules[ "__main__" ].__language__
__scriptname__ = sys.modules[ "__main__" ].__scriptname__
__version__ = sys.modules[ "__main__" ].__version__


class GUI( xbmcgui.WindowXMLDialog ):
    """ Settings module: used for changing settings """
    def __init__( self, *args, **kwargs ):
        xbmcgui.lock()
        self.controlId = 0
        self.base_path = os.path.join( BASE_RESOURCE_PATH, "skins" )
        self.choices = kwargs[ "choices" ]
        self.original = kwargs[ "original" ]
        self.selection = kwargs[ "selection" ]
        self.list_control = kwargs[ "list_control" ]
        self.title = kwargs[ "title" ]
        self.doModal()

    def onInit( self ):
        self.show_chooser()
        xbmcgui.unlock()

    def show_chooser( self ):
        self.getControl( 500 ).setLabel( self.title )
        self.getControl( 502 ).setLabel( _( 231 ) )
        self._setup_list()
        if ( self.list_control == 0 ):
            self._get_thumb( self.getControl( 503 ).getSelectedItem().getLabel() )

    def _setup_list( self ):
        self.getControl( 502 ).setVisible( False )
        self.getControl( 503 ).setVisible( self.list_control == 0 )
        self.getControl( 504 ).setVisible( self.list_control == 1 )
        self.getControl( 503 + self.list_control ).reset()
        for count, choice in enumerate( self.choices ):
            self.getControl( 503 + self.list_control ).addItem( choice )
            if ( count == self.original ):
                self.getControl( 503 + self.list_control ).selectItem( count )
                self.getControl( 503 + self.list_control ).getSelectedItem().select( True )
        self.getControl( 503 + self.list_control ).selectItem( self.selection )
        self.setFocus( self.getControl( 503 + self.list_control ) )

    def _get_thumb( self, choice ):
        xbmc.executebuiltin( "Skin.SetString(AMT-chooser-thumbfolder,%s)" % ( os.path.join( self.base_path, choice, "media", "thumbs" ), ) )
        self.getControl( 502 ).setVisible( os.path.isfile( os.path.join( self.base_path, choice, "warning.txt" ) ) )

    def _close_dialog( self, selection=None ):
        #xbmc.sleep( 5 )
        self.selection = selection
        self.close()

    def onClick( self, controlId ):
        if ( controlId in ( 503, 504, ) ):
            self._close_dialog( self.getControl( controlId ).getSelectedPosition() )

    def onFocus( self, controlId ):
        self.controlId = controlId

    def onAction( self, action ):
        if ( action.getButtonCode() in CANCEL_DIALOG ):
            self._close_dialog()
        #elif ( self.controlId in ( 503, 504, ) and action.getButtonCode() in SELECT_ITEM ):
        #    self._close_dialog( self.getControl( self.controlId ).getSelectedPosition() )
        elif ( self.controlId == 503 ):
            self._get_thumb( self.getControl( 503 ).getSelectedItem().getLabel() )
