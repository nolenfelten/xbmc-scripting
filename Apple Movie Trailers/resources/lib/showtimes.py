"""
Showtimes module

Nuka1195
"""

import sys
import xbmcgui

import showtimesScraper
ShowtimesFetcher = showtimesScraper.ShowtimesFetcher()
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
        self.location = kwargs[ "location" ]

    def onInit( self ):
        self._show_dialog()
        xbmcgui.unlock()
        self._get_showtimes()

    def _capitalize_text( self, text ):
        return ( text, text.upper(), )[ self.caps ]

    def _show_dialog( self ):
        self.getControl( 20 ).setLabel( self._capitalize_text( self.title ) )
        self.getControl( 30 ).setLabel( "%s:" % self._capitalize_text( _( 602 ) ) )
        self.getControl( 40 ).setLabel( "%s: %s" % ( self._capitalize_text( _( 603 ) ), self._capitalize_text( self.location ), ) )
        self.getControl( 100 ).reset()
        self.getControl( 100 ).addItem( self._capitalize_text( _( 601 ) ) )

    def _get_showtimes( self ):
        date, movie_showtimes = ShowtimesFetcher.get_showtimes( self.title, self.location )
        self.getControl( 30 ).setLabel( "%s: %s" % ( self._capitalize_text( _( 602 ) ), self._capitalize_text( date ), ) )
        self.getControl( 100 ).reset()
        if ( movie_showtimes ):
            theaters = movie_showtimes.keys()
            theaters.sort()
            for theater in theaters:
                list_item = xbmcgui.ListItem( self._capitalize_text( theater ), movie_showtimes[ theater ] )
                self.getControl( 100 ).addItem( list_item )
        else:
            self.getControl( 100 ).addItem( self._capitalize_text( _( 600 ) ) )

    def _close_dialog( self ):
        self.close()

    def onClick( self, controlId ):
        pass

    def onFocus( self, controlId ):
        pass

    def onAction( self, action ):
        if ( action.getButtonCode() in CANCEL_DIALOG ):
            self._close_dialog()
