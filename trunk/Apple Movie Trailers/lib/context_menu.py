import xbmc, xbmcgui
import os, guibuilder, sys
import amt_util, default
#import trailers

class GUI( xbmcgui.WindowDialog ):
    def __init__( self, *args, **kwargs ):
        try:
            self.cwd = os.path.dirname( sys.modules['default'].__file__ )
            #self.getSettings()
            self._ = kwargs['language']
            #self.skin = kwargs['skin']
            self.win = kwargs['win']
            self.setupGUI()
            if ( not self.SUCCEEDED ): self.close()
            else:
                pass
                self.setupVariables()
                self.setButtons()
                #self.getGenreCategories()
                #self.setControlsValues()
                ##remove disabled when update script routine is done
                #self.controls['Update Button']['control'].setEnabled( False )
        except: 
            print 'FUCK CM'
            self.close()
                
    def setupVariables( self ):
        self.controller_action = amt_util.setControllerAction()
        #self.quality = amt_util.setQuality( self._ )
        #self.mode = amt_util.setMode( self._ )
        #self.startup = amt_util.setStartupCategory( self._ )
        #self.thumbnail = amt_util.setThumbnailDisplay( self._ )
        
 
    def setupGUI( self ):
        skin_path = os.path.join( self.cwd, 'skins' )
        self.skin_path = os.path.join( skin_path, self.win.skin )
        self.image_path = os.path.join( self.skin_path, 'gfx' )
        res = self.getResolution()
        if ( res == 0 or res % 2 ): skin = 'context_menu_16x9.xml'
        else: skin = 'context_menu.xml'
        if ( not os.path.isfile( os.path.join( self.skin_path, skin ) ) ): skin = 'context_menu.xml'
        guibuilder.GUIBuilder( self, os.path.join( self.skin_path, skin ), self.image_path, useDescAsKey=True, useLocal=True, fastMethod=True, debug=False )

    def setButtons( self ):
        trailer = self.win.controls['Trailer List']['control'].getSelectedPosition()
        self.controls['Context Menu Button1']['control'].setLabel( self._( 500 ) )
        self.controls['Context Menu Button2']['control'].setLabel( self._( 502 + self.win.trailers.genres[self.win.genre_id].movies[trailer].favorite ) )
        self.controls['Context Menu Button3']['control'].setLabel( self._( 504 + self.win.trailers.genres[self.win.genre_id].movies[trailer].watched ) )
        self.controls['Context Menu Button4']['control'].setLabel( self._( 506 + ( self.win.genre_id == -1 ) ) )
        self.controls['Context Menu Button5']['control'].setLabel( self._( 509 ) )
        self.controls['Context Menu Button5']['control'].setEnabled( self.win.trailers.genres[self.win.genre_id].movies[trailer].saved != 'None' )
        
    def toggleAsWatched( self ):
        trailer = self.win.controls['Trailer List']['control'].getSelectedPosition()
        self.win.trailers.genres[self.win.genre_id].movies[trailer].watched = not self.win.trailers.genres[self.win.genre_id].movies[trailer].watched
        self.win.showTrailers( trailer )
        self.closeDialog()
  
    def toggleAsFavorite( self ):
        trailer = self.win.controls['Trailer List']['control'].getSelectedPosition()
        self.win.trailers.genres[self.win.genre_id].movies[trailer].favorite = not self.win.trailers.genres[self.win.genre_id].movies[trailer].favorite
        self.win.showTrailers( trailer )
        self.closeDialog()

    def refreshInfo( self ):
        trailer = self.win.controls['Trailer List']['control'].getSelectedPosition()
        self.closeDialog()
        self.win.trailers.genres[self.win.genre_id].movies[trailer].__update__()
        self.win.showTrailers( trailer )
        
    def deleteSavedTrailer( self ):
        trailer = self.win.controls['Trailer List']['control'].getSelectedPosition()
        saved_trailer = self.win.trailers.genres[self.win.genre_id].movies[trailer].saved
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
                        self.win.trailers.genres[self.win.genre_id].movies[trailer].saved = 'None'
                        self.win.showTrailers( trailer )
                        self.closeDialog()

    def closeDialog( self ):
        self.close()
        
    def onControl( self, control ):
        if ( control is self.controls['Context Menu Button2']['control'] ):
            self.toggleAsFavorite()
        elif ( control is self.controls['Context Menu Button3']['control'] ):
            self.toggleAsWatched()
        elif ( control is self.controls['Context Menu Button4']['control'] ):
            self.refreshInfo()
        elif ( control is self.controls['Context Menu Button5']['control'] ):
            self.deleteSavedTrailer()
        
    def onAction( self, action ):
        control = self.getFocus()
        button_key = self.controller_action.get( action.getButtonCode(), 'n/a' )
        if ( button_key == 'B Button' or button_key == 'Remote Back Button' ):
            self.closeDialog()
        elif ( button_key == 'Back Button' or button_key == 'Remote Menu Button' ):
            self.closeDialog()
