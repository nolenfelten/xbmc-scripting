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
        self.saved = self.win.trailers.movies[self.trailer].saved != ''
        
    def setupGUI( self ):
        if ( self.win.skin == 'Default' ): current_skin = xbmc.getSkinDir()
        else: current_skin = self.win.skin
        if ( not os.path.exists( os.path.join( self.cwd, 'extras', 'skins', current_skin ))): current_skin = 'default'
        skin_path = os.path.join( self.cwd, 'extras', 'skins', current_skin )
        image_path = os.path.join( skin_path, 'gfx' )
        if ( self.getResolution() == 0 or self.getResolution() % 2 ): xml_file = 'context_16x9.xml'
        else: xml_file = 'context.xml'
        if ( not os.path.isfile( os.path.join( skin_path, xml_file ))): xml_file = 'context.xml'
        guibuilder.GUIBuilder( self, os.path.join( skin_path, xml_file ), image_path, useDescAsKey=True, useLocal=True, fastMethod=True, debug=False )

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
        self.controls['Context Menu Button2']['control'].setLabel( self._( 502 + self.win.trailers.movies[self.trailer].favorite ) )
        watched = self.win.trailers.movies[self.trailer].watched
        if ( watched ): watched_lbl = '  (%d)' % ( watched, )
        else: watched_lbl = ''
        self.controls['Context Menu Button3']['control'].setLabel( '%s' % (self._( 504 + ( watched > 0 ) ) + watched_lbl, ) )
        self.controls['Context Menu Button4']['control'].setLabel( self._( 506 ) )
        self.controls['Context Menu Button5']['control'].setLabel( self._( 507 ) )
        self.controls['Context Menu Button6']['control'].setLabel( self._( 509 ) )
    
    def setMenuPosition( self ):
        button_height = self.controls['Context Menu Button1'][ 'control' ].getHeight()#['height'] + 2
        height = ( 5 + self.saved ) * self.controls['Context Menu Button1'][ 'control' ].getHeight()#['height']
        #height -=  ( button_height * ( not self.saved ) )
        self.controls['Context Menu Background Middle']['control'].setHeight( height )
        
        x = self.controls['Context Menu Background Bottom'][ 'control' ].getPosition()[ 0 ] #+ self.coordinates[ 0 ]
        y = self.controls['Context Menu Background Middle'][ 'control' ].getPosition()[ 1 ] + height #+ self.coordinates[ 1 ]
        self.controls['Context Menu Background Bottom']['control'].setPosition( x, y )
    
    def setMenuVisibility( self ):
        self.controls['Context Menu Button6']['control'].setVisible( self.saved )
        self.controls['Context Menu Button6']['control'].setEnabled( self.saved )
        self.setFocus( self.controls['Context Menu Button1']['control'] )
        
    def toggleAsWatched( self ):
        watched = not ( self.win.trailers.movies[self.trailer].watched > 0 )
        self.win.markAsWatched( watched, self.win.trailers.movies[self.trailer].title, self.trailer )
        self.closeDialog()
  
    def toggleAsFavorite( self ):
        favorite = not self.win.trailers.movies[self.trailer].favorite
        success = self.win.trailers.updateRecord( ( 'favorite', ), 'Movies', ( favorite, ), key_value = self.win.trailers.movies[self.trailer].title )
        if ( success ):
            self.win.trailers.movies[self.trailer].favorite = favorite
            if ( self.win.category_id == -3 ):
                params = ( 1, )
                choice = self.trailer - 1 + ( self.trailer == 0 )
                force_update = True
            else: 
                params = self.win.params
                choice = self.trailer
                force_update = False
            self.win.showTrailers( self.win.sql, params = params, choice = choice, force_update = force_update )
        self.closeDialog()
    
    def refreshInfo( self, refresh_all ):
        self.closeDialog()
        '''
        if ( refresh_all ):
            self.win.trailers.update_all( force_update = True )
        else:
            self.win.trailers.movies[self.trailer].__update__()
        self.win.showTrailers( self.win.sql, choice = self.trailer )
        '''
        
    def deleteSavedTrailer( self ):
        saved_trailer = self.win.trailers.movies[self.trailer].saved
        if ( xbmcgui.Dialog().yesno( '%s?' % ( self._( 509 ), ), self._( 82 ), saved_trailer ) ):
            if ( os.path.isfile( saved_trailer ) ):
                os.remove( saved_trailer )
            if ( os.path.isfile( '%s.conf' % ( saved_trailer, ) ) ):
                os.remove( '%s.conf' % ( saved_trailer, ) )
            if ( os.path.isfile( '%s.tbn' % ( os.path.splitext( saved_trailer )[0], ) ) ):
                os.remove( '%s.tbn' % ( os.path.splitext( saved_trailer )[0], ) )
            success = self.win.trailers.updateRecord( ( 'saved_location', ), 'Movies', ( '', ), key_value = self.win.trailers.movies[self.trailer].title )
            if ( success ):
                self.win.trailers.movies[self.trailer].saved = ''
                if ( self.win.category_id == -7 ): force_update = True
                else: force_update = False
                self.win.showTrailers( self.win.sql, self.win.params, choice = self.trailer, force_update = force_update )
            self.closeDialog()

    def closeDialog( self ):
        self.close()
        
    def onControl( self, control ):
        if ( control is self.controls['Context Menu Button1']['control'] ):
            pass#self.addPlaylist()
        elif ( control is self.controls['Context Menu Button2']['control'] ):
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
        if ( button_key == 'Keyboard Backspace Button' or button_key == 'B Button' or button_key == 'Remote Back Button' ):
            self.closeDialog()
        elif ( button_key == 'Keyboard ESC Button' or button_key == 'Back Button' or button_key == 'Remote Menu Button' ):
            self.closeDialog()
        elif ( button_key == 'Keyboard Menu Button' or button_key == 'Remote Title' or button_key == 'White Button' ):
            self.closeDialog()
