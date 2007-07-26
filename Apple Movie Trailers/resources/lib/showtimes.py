"""
Showtimes module

Nuka1195
"""

import sys
import xbmcgui
import traceback

from utilities import *

_ = sys.modules[ "__main__" ].__language__
__scriptname__ = sys.modules[ "__main__" ].__scriptname__
__version__ = sys.modules[ "__main__" ].__version__
__svn_url__ = sys.modules[ "__main__" ].__svn_url__


class GUI( xbmcgui.WindowXMLDialog ):
    def __init__( self, *args, **kwargs ):
        xbmcgui.lock()
        self.caps = kwargs[ "caps" ]
        self.title = kwargs[ "title" ]
        self.date = kwargs[ "date" ]
        self.location = kwargs[ "location" ]
        self.movie_showtimes = kwargs[ "showtimes" ]

    def onInit( self ):
        self._show_dialog()
        xbmcgui.unlock()

    def _capitalize_text( self, text ):
        return ( text, text.upper(), )[ self.caps ]

    def _show_dialog( self ):
        self.getControl( 20 ).setLabel( self._capitalize_text( self.title ) )
        self.getControl( 30 ).setLabel( self._capitalize_text( self.date ) )
        self.getControl( 40 ).setLabel( "%s: %s" % ( _( 601 ), self._capitalize_text( self.location ), ) )
        self.getControl( 100 ).reset()
        theaters = self.movie_showtimes.keys()
        theaters.sort()
        for theater in theaters:
            list_item = xbmcgui.ListItem( self._capitalize_text( theater ), self._capitalize_text( self.movie_showtimes[ theater ] ) )
            self.getControl( 100 ).addItem( list_item )

    def _close_dialog( self ):
        self.close()

    def onClick( self, controlId ):
        pass

    def onFocus( self, controlId ):
        pass

    def onAction( self, action ):
        if ( action.getButtonCode() in CANCEL_DIALOG ):
            self._close_dialog()
