import xbmc, xbmcgui
import os, guibuilder, sys
import amt_util, default

class GUI( xbmcgui.WindowDialog ):
    def __init__( self, *args, **kwargs ):
        try:
            self.cwd = os.path.dirname( sys.modules['default'].__file__ )
            self._ = kwargs['language']
            self.win = kwargs['win']
            self.setupGUI()
            if ( not self.SUCCEEDED ): self.close()
            else:
                self.setupVariables()
                self.showContextMenu()
        except: 
            self.close()
                
    def setupVariables( self ):
        self.controller_action = amt_util.setControllerAction()
        self.trailer = self.win.controls['Trailer List']['control'].getSelectedPosition()
        self.saved = self.win.trailers.genres[self.win.genre_id].movies[self.trailer].saved != 'None'
        
    def setupGUI( self ):
        skin_path = os.path.join( self.cwd, 'skins', self.win.skin )
        image_path = os.path.join( skin_path, 'gfx' )
        res = self.getResolution()
        if ( res == 0 or res % 2 ): skin = 'context_menu_16x9.xml'
        else: skin = 'context_menu.xml'
        if ( not os.path.isfile( os.path.join( skin_path, skin ) ) ): skin = 'context_menu.xml'
        guibuilder.GUIBuilder( self, os.path.join( skin_path, skin ), image_path, useDescAsKey=True, useLocal=True, fastMethod=True, debug=False )

    def showContextMenu( self ):
        try:
            xbmcgui.lock()
            self.setButtonLabels()
            self.setMenuPosition()
            self.setMenuVisibility()
        finally:
            xbmcgui.unlock()
        
    def setButtonLabels( self ):
        self.controls['Context Menu Button1']['control'].setLabel( self._( 500 ) )
        self.controls['Context Menu Button2']['control'].setLabel( self._( 502 + self.win.trailers.genres[self.win.genre_id].movies[self.trailer].favorite ) )
        self.controls['Context Menu Button3']['control'].setLabel( self._( 504 + self.win.trailers.genres[self.win.genre_id].movies[self.trailer].watched ) )
        self.controls['Context Menu Button4']['control'].setLabel( self._( 506 ) )
        self.controls['Context Menu Button5']['control'].setLabel( self._( 507 ) )
        self.controls['Context Menu Button6']['control'].setLabel( self._( 509 ) )
    
    def setMenuPosition( self ):
        #posx = self.controls['Context Menu Background']['posx'] + self.coordinates[0]
        #posy = self.controls['Context Menu Background']['posy'] + self.coordinates[1]
        button_height = self.controls['Context Menu Button1']['height'] + 2
        height = self.controls['Context Menu Background']['height']
        height -=  ( button_height * ( not self.saved ) )
        self.controls['Context Menu Background']['control'].setHeight( height )
        #self.controls['Context Menu Background']['control'].setPosition( posx, posy )
    
    def setMenuVisibility( self ):
        self.controls['Context Menu Background']['control'].setVisible( True )
        self.controls['Context Menu Button1']['control'].setVisible( True )
        self.controls['Context Menu Button1']['control'].setEnabled( True )
        self.controls['Context Menu Button2']['control'].setVisible( True )
        self.controls['Context Menu Button2']['control'].setEnabled( True )
        self.controls['Context Menu Button3']['control'].setVisible( True )
        self.controls['Context Menu Button3']['control'].setEnabled( True )
        self.controls['Context Menu Button4']['control'].setVisible( True )
        self.controls['Context Menu Button4']['control'].setEnabled( True )
        self.controls['Context Menu Button5']['control'].setVisible( True )
        self.controls['Context Menu Button6']['control'].setVisible( self.saved )
        self.controls['Context Menu Button6']['control'].setEnabled( self.saved )
        self.setFocus( self.controls['Context Menu Button1']['control'] )
        
    def toggleAsWatched( self ):
        self.win.trailers.genres[self.win.genre_id].movies[self.trailer].watched = not self.win.trailers.genres[self.win.genre_id].movies[self.trailer].watched
        self.win.showTrailers( self.trailer )
        self.closeDialog()
  
    def toggleAsFavorite( self ):
        self.win.trailers.genres[self.win.genre_id].movies[self.trailer].favorite = not self.win.trailers.genres[self.win.genre_id].movies[self.trailer].favorite
        self.win.showTrailers( self.trailer )
        self.closeDialog()

    def refreshInfo( self, refresh_all ):
        if ( refresh_all ):
            self.win.trailers.genres[self.win.genre_id].__update__()
        else:
            self.win.trailers.genres[self.win.genre_id].movies[self.trailer].__update__()
        self.win.showTrailers( self.trailer )
        self.closeDialog()
        
    def deleteSavedTrailer( self ):
        saved_trailer = self.win.trailers.genres[self.win.genre_id].movies[self.trailer].saved
        dialog = xbmcgui.Dialog()
        if ( dialog.yesno( '%s?' % ( self._( 509 ), ), self._( 82 ), saved_trailer ) ):
            try:
                os.remove( saved_trailer )
            finally:
                try:
                    os.remove( '%s.conf' % ( saved_trailer, ) )
                finally:
                    try:
                        os.remove( '%s.tbn' % ( os.path.splitext( saved_trailer )[0], ) )
                    finally:
                        self.win.trailers.genres[self.win.genre_id].movies[self.trailer].saved = 'None'
                        self.win.showTrailers( self.trailer )
                        self.closeDialog()

    def closeDialog( self ):
        self.close()
        
    def onControl( self, control ):
        if ( control is self.controls['Context Menu Button2']['control'] ):
            self.toggleAsFavorite()
        elif ( control is self.controls['Context Menu Button3']['control'] ):
            self.toggleAsWatched()
        elif ( control is self.controls['Context Menu Button4']['control'] ):
            self.refreshInfo( False )
        elif ( control is self.controls['Context Menu Button5']['control'] ):
            self.refreshInfo( True )
        elif ( control is self.controls['Context Menu Button6']['control'] ):
            self.deleteSavedTrailer()
        
    def onAction( self, action ):
        control = self.getFocus()
        button_key = self.controller_action.get( action.getButtonCode(), 'n/a' )
        if ( button_key == 'B Button' or button_key == 'Remote Back Button' ):
            self.closeDialog()
        elif ( button_key == 'Back Button' or button_key == 'Remote Menu Button' ):
            self.closeDialog()
