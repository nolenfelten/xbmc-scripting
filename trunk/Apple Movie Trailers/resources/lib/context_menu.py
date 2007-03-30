"""
Context menu module

Nuka1195
"""

import os
import xbmcgui
import guibuilder
import utilities


class GUI( xbmcgui.WindowDialog ):
    def __init__( self, *args, **kwargs ):
        self.win = kwargs[ "win" ]
        self._ = kwargs[ "language" ]
        self.list_control = kwargs[ "list_control" ]
        self.gui_loaded = self.setupGUI( self.win.skin )
        if ( not self.gui_loaded ): self.close()
        else:
            self.setupVariables()
            self.showContextMenu()
            
    def setupVariables( self ):
        self.controller_action = utilities.setControllerAction()
        self.list_item = self.win.controls[ self.list_control ][ "control" ].getSelectedPosition()
        if ( self.list_control == "Trailer List" ):
            self.saved = self.win.trailers.movies[ self.list_item ].saved != ""
            self.cached = ( self.win.trailers.movies[ self.list_item ].title == self.win.flat_cache[ 0 ] )

    def setupGUI( self, skin ):
        """ sets up the gui using guibuilder """
        gb = guibuilder.GUIBuilder()
        ok, image_path = gb.create_gui( self, skin=skin, xml_name="context_menu", language=self._ )
        return ok

    def showContextMenu( self ):
        try:
            xbmcgui.lock()
            self.hideButtons()
            self.setButtonLabels()
            self.setMenuPosition()
            self.setFocus( self.controls[ "Context Menu Button1" ][ "control" ] )
        except: pass
        xbmcgui.unlock()
            
    def setButtonLabels( self ):
        self.buttons = 1
        if ( self.list_control == "Trailer List" ):
            self.controls[ "Context Menu Button1" ][ "control" ].setLabel( self._( 510 ) )
            self.controls[ "Context Menu Button2" ][ "control" ].setLabel( self._( 502 + self.win.trailers.movies[self.list_item].favorite ) )
            watched = self.win.trailers.movies[ self.list_item ].watched
            if ( watched ): watched_lbl = "  (%d)" % ( watched, )
            else: watched_lbl = ""
            self.controls[ "Context Menu Button3" ][ "control" ].setLabel( "%s" % (self._( 504 + ( watched > 0 ) ) + watched_lbl, ) )
            self.controls[ "Context Menu Button4" ][ "control" ].setLabel( self._( 506 ) )
            if ( self.saved ):
                self.controls[ "Context Menu Button5" ][ "control" ].setLabel( self._( 509 ) )
            elif ( self.cached ):
                self.controls[ "Context Menu Button5" ][ "control" ].setLabel( self._( 501 ) )
            if ( not self.win.trailers.complete ):
                self.controls[ "Context Menu Button%s" % ( ( self.saved or self.cached ) + 5, ) ][ "control" ].setLabel( self._( 508 ) )
            self.buttons = 4 + ( self.saved or self.cached ) + ( not self.win.trailers.complete )
            #self.controls[ "Context Menu Button6" ][ "control" ].setLabel( self._( 510 ) )
        elif ( self.list_control == "Category List" ):
            if ( self.win.category_id == utilities.GENRES ):
                self.controls[ "Context Menu Button1" ][ "control" ].setLabel( self._( 511 ) )
                self.controls[ "Context Menu Button2" ][ "control" ].setLabel( self._( 507 ) )
                if ( not self.win.trailers.complete ): 
                    self.controls[ "Context Menu Button3" ][ "control" ].setLabel( self._( 508 ) )
                    self.buttons = 3
                else: self.buttons = 2
            elif ( self.win.category_id ==  utilities.STUDIOS ):
                self.controls[ "Context Menu Button1" ][ "control" ].setLabel( self._( 512 ) )
                if ( not self.win.trailers.complete ): 
                    self.controls[ "Context Menu Button2" ][ "control" ].setLabel( self._( 508 ) )
                    self.buttons = 2
            elif ( self.win.category_id ==  utilities.ACTORS ):
                self.controls[ "Context Menu Button1" ][ "control" ].setLabel( self._( 513 ) )
                if ( not self.win.trailers.complete ): 
                    self.controls[ "Context Menu Button2" ][ "control" ].setLabel( self._( 508 ) )
                    self.buttons = 2
        elif ( self.list_control == "Cast List" ):
                self.controls[ "Context Menu Button1" ][ "control" ].setLabel( self._( 513 ) )
                if ( not self.win.trailers.complete ): 
                    self.controls[ "Context Menu Button2" ][ "control" ].setLabel( self._( 508 ) )
                    self.buttons = 2
    
    def setMenuPosition( self ):
        # get positions and dimensions
        button_height = self.controls[ "Context Menu Button1" ][ "control" ].getHeight()
        button_posx, button_posy = self.controls[ "Context Menu Button1" ][ "control" ].getPosition()
        dialog_width = self.controls[ "Context Menu Background Top" ][ "control" ].getWidth()
        dialog_top_height = self.controls[ "Context Menu Background Top" ][ "control" ].getHeight()
        dialog_bottom_height = self.controls[ "Context Menu Background Bottom" ][ "control" ].getHeight()
        dialog_top_posx, dialog_top_posy = self.controls[ "Context Menu Background Top" ][ "control" ].getPosition()
        dialog_middle_posy = self.controls[ "Context Menu Background Middle" ][ "control" ].getPosition()[ 1 ]
        dialog_middle_offsety = dialog_middle_posy - dialog_top_posy
        list_width = self.win.controls[ self.list_control ][ "control" ].getWidth()
        list_height = self.win.controls[ self.list_control ][ "control" ].getHeight() - self.win.controls[ self.list_control ][ "control" ].getItemHeight()
        list_posx, list_posy = self.win.controls[ self.list_control ][ "control" ].getPosition()
        
        # calculate position
        button_offsetx = button_posx - dialog_top_posx
        button_offsety = button_posy - dialog_top_posy
        button_gap = 2
        dialog_middle_height = ( self.buttons * ( button_height + button_gap ) ) - button_gap
        dialog_height = dialog_middle_height + dialog_top_height + dialog_bottom_height
        dialog_posx = int( float( list_width - dialog_width ) / 2 ) + list_posx
        dialog_posy = int( float( list_height - dialog_height ) / 2 ) + list_posy
        button_posx = dialog_posx + button_offsetx
        button_posy = dialog_posy + button_offsety
        
        # position and size menu
        self.controls[ "Context Menu Background Middle" ][ "control" ].setHeight( dialog_middle_height )
        self.controls[ "Context Menu Background Top" ][ "control" ].setPosition( dialog_posx, dialog_posy )
        self.controls[ "Context Menu Background Middle" ][ "control" ].setPosition( dialog_posx, dialog_posy + dialog_middle_offsety )
        self.controls[ "Context Menu Background Bottom" ][ "control" ].setPosition( dialog_posx, dialog_posy + dialog_middle_offsety + dialog_middle_height )
        for button in range( self.buttons ):
            self.controls[ "Context Menu Button%d" % ( button + 1, ) ][ "control" ].setPosition( button_posx, button_posy + ( ( button_height + button_gap ) * button ) )
            self.controls[ "Context Menu Button%d" % ( button + 1, ) ][ "control" ].setVisible( True )
            self.controls[ "Context Menu Button%d" % ( button + 1, ) ][ "control" ].setEnabled( True )
            
    def hideButtons( self ):
        for button in range( 1, 7 ):
            self.controls[ "Context Menu Button%d" % ( button, ) ][ "control" ].setVisible( False )
            self.controls[ "Context Menu Button%d" % ( button, ) ][ "control" ].setEnabled( False )
        
    def closeDialog( self ):
        #del self.win
        self.close()
        
    def onControl( self, control ):
        self.closeDialog()
        try:
            if ( control is self.controls[ "Context Menu Button1" ][ "control" ] ):
                if ( self.list_control == "Trailer List" ):
                    self.win.playTrailer()
                elif ( self.list_control == "Category List" ):
                    self.win.getTrailerGenre()
                elif ( self.list_control == "Cast List" ):
                    self.win.getActorChoice()
            elif ( control is self.controls[ "Context Menu Button2" ][ "control" ] ):
                if ( self.list_control == "Trailer List" ):
                    self.win.toggleAsFavorite()
                elif ( self.list_control == "Category List" and self.win.category_id == utilities.GENRES ):
                    self.win.refreshInfo( True )
                else:# ( self.list_control == "Cast List" ):
                    self.win.force_full_update()
            elif ( control is self.controls[ "Context Menu Button3" ][ "control" ] ):
                if ( self.list_control == "Trailer List" ):
                    self.win.toggleAsWatched()
                elif ( self.list_control == "Category List" ):
                    self.win.force_full_update()
            elif ( control is self.controls[ "Context Menu Button4" ][ "control" ] ):
                if ( self.list_control == "Trailer List" ):
                    self.win.refreshInfo( False )
            elif ( control is self.controls[ "Context Menu Button5" ][ "control" ] ):
                if ( self.list_control == "Trailer List" ):
                    if ( self.cached ): self.win.saveCachedMovie()
                    elif ( self.saved ): self.win.deleteSavedTrailer()
                    else: self.win.force_full_update()
            elif ( control is self.controls[ "Context Menu Button6" ][ "control" ] ):
                if ( self.list_control == "Trailer List" ):
                    self.win.force_full_update()
        except: pass
            
    def onAction( self, action ):
        control = self.getFocus()
        button_key = self.controller_action.get( action.getButtonCode(), "n/a" )
        if ( button_key == "Keyboard Backspace Button" or button_key == "B Button" or button_key == "Remote Back Button" ):
            self.closeDialog()
        elif ( button_key == "Keyboard ESC Button" or button_key == "Back Button" or button_key == "Remote Menu Button" ):
            self.closeDialog()
        elif ( button_key == "Keyboard Menu Button" or button_key == "Remote Title Button" or button_key == "White Button" ):
            self.closeDialog()
