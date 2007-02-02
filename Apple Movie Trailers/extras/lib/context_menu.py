import xbmc, xbmcgui
import os, guibuilder, sys
import amt_util, default

class GUI( xbmcgui.WindowDialog ):
    def __init__( self, *args, **kwargs ):
        try:
            self.cwd = os.path.dirname( sys.modules['default'].__file__ )
            self._ = kwargs['language']
            self.win = kwargs['win']
            self.list_control = kwargs['list_control']
            self.setupGUI()
            if ( not self.SUCCEEDED ): self.close()
            else:
                self.setupVariables()
                self.showContextMenu()
        except: 
            self.close()
                
    def setupVariables( self ):
        self.controller_action = amt_util.setControllerAction()
        self.list_item = self.win.controls[ self.list_control ][ 'control' ].getSelectedPosition()
        self.saved = self.win.trailers.movies[ self.list_item ].saved != ''
        
    def setupGUI( self ):
        if ( self.win.skin == 'Default' ): current_skin = xbmc.getSkinDir()
        else: current_skin = self.win.skin
        if ( not os.path.exists( os.path.join( self.cwd, 'extras', 'skins', current_skin ))): current_skin = 'default'
        skin_path = os.path.join( self.cwd, 'extras', 'skins', current_skin )
        image_path = os.path.join( skin_path, 'gfx' )
        if ( self.getResolution() == 0 or self.getResolution() % 2 ): xml_file = 'context_menu_16x9.xml'
        else: xml_file = 'context_menu.xml'
        if ( not os.path.isfile( os.path.join( skin_path, xml_file ))): xml_file = 'context_menu.xml'
        guibuilder.GUIBuilder( self, os.path.join( skin_path, xml_file ), image_path, useDescAsKey=True, useLocal=True, fastMethod=True, debug=False )

    def showContextMenu( self ):
        try:
            xbmcgui.lock()
            self.setButtonLabels()
            self.setMenuVisibility()
            self.setMenuPosition()
        finally:
            xbmcgui.unlock()
            
    def setButtonLabels( self ):
        if ( self.list_control == 'Trailer List' ):
            self.controls['Context Menu Button1']['control'].setLabel( self._( 510 ) )
            self.controls['Context Menu Button2']['control'].setLabel( self._( 502 + self.win.trailers.movies[self.list_item].favorite ) )
            watched = self.win.trailers.movies[self.list_item].watched
            if ( watched ): watched_lbl = '  (%d)' % ( watched, )
            else: watched_lbl = ''
            self.controls['Context Menu Button3']['control'].setLabel( '%s' % (self._( 504 + ( watched > 0 ) ) + watched_lbl, ) )
            self.controls['Context Menu Button4']['control'].setLabel( self._( 506 ) )
            self.controls['Context Menu Button5']['control'].setLabel( self._( 509 ) )
            #self.controls['Context Menu Button6']['control'].setLabel( self._( 510 ) )
        elif ( self.list_control == 'Category List' ):
            if ( self.win.category_id == amt_util.GENRES ):
                self.controls['Context Menu Button1']['control'].setLabel( self._( 511 ) )
                self.controls['Context Menu Button2']['control'].setLabel( self._( 507 ) )
            elif ( self.win.category_id ==  amt_util.STUDIOS ):
                self.controls['Context Menu Button1']['control'].setLabel( self._( 512 ) )
            elif ( self.win.category_id ==  amt_util.ACTORS ):
                self.controls['Context Menu Button1']['control'].setLabel( self._( 513 ) )
        elif ( self.list_control == 'Cast List' ):
                self.controls['Context Menu Button1']['control'].setLabel( self._( 513 ) )
    
    def setMenuPosition( self ):
        # calculate position
        bg_posx = self.controls['Context Menu Background Middle']['control'].getPosition()[0]
        button_posx = self.controls['Context Menu Button1'][ 'control' ].getPosition()[0]
        buttonx_offset = button_posx - bg_posx
        button_height = self.controls['Context Menu Button1'][ 'control' ].getHeight() + 2
        middle_height = ( self.buttons * button_height ) - 2
        try: top_height = self.controls['Context Menu Background Top']['control'].getHeight()
        except: top_height = 0
        try: bottom_height = self.controls['Context Menu Background Bottom']['control'].getHeight()
        except: bottom_height = 0
        menu_width = self.controls['Context Menu Background Middle']['control'].getWidth()
        menu_height = middle_height + top_height + bottom_height
        posx, posy = self.win.controls[ self.list_control ][ 'control' ].getPosition()
        list_height = self.win.controls[ self.list_control ][ 'control' ].getHeight()
        list_width = self.win.controls[ self.list_control ][ 'control' ].getWidth()
        menu_posx = int( float( list_width - menu_width ) / 2 ) + posx
        menu_posy = int( float( list_height - menu_height ) / 2 ) + posy
        button_width = self.controls['Context Menu Button1']['control'].getWidth()
        button_posx = menu_posx + buttonx_offset
        buttony_offset =int( float( bottom_height - top_height ) / 2 )
        # position menu
        self.controls['Context Menu Background Middle']['control'].setHeight( middle_height )
        try: self.controls['Context Menu Background Top']['control'].setPosition( menu_posx, menu_posy )
        except: pass
        self.controls['Context Menu Background Middle']['control'].setPosition( menu_posx, top_height + menu_posy - 1 )
        for button in range( 6 ):
            self.controls['Context Menu Button%d' % ( button + 1, ) ]['control'].setPosition( button_posx, top_height + ( button_height * button ) + menu_posy - buttony_offset )
        try: self.controls['Context Menu Background Bottom']['control'].setPosition( menu_posx, top_height + middle_height + menu_posy - 1 )
        except: pass
   
    def setMenuVisibility( self ):
        self.controls['Context Menu Button1']['control'].setVisible( True )
        self.controls['Context Menu Button1']['control'].setEnabled( True )
        visible = ( ( self.win.category_id == amt_util.GENRES and self.list_control == 'Category List' ) or self.list_control == 'Trailer List' )
        self.buttons = visible + 1
        self.controls['Context Menu Button2']['control'].setVisible( visible )
        self.controls['Context Menu Button2']['control'].setEnabled( visible )
        visible = ( self.list_control == 'Trailer List' )
        self.buttons += ( visible * 2 )
        self.controls['Context Menu Button3']['control'].setVisible( visible )
        self.controls['Context Menu Button3']['control'].setEnabled( visible )
        self.controls['Context Menu Button4']['control'].setVisible( visible )
        self.controls['Context Menu Button4']['control'].setEnabled( visible )
        visible = ( self.list_control == 'Trailer List' and self.saved )
        self.buttons += visible
        self.controls['Context Menu Button5']['control'].setVisible( visible )
        self.controls['Context Menu Button5']['control'].setEnabled( visible )
        self.controls['Context Menu Button6']['control'].setVisible( False )
        self.controls['Context Menu Button6']['control'].setEnabled( False )
        self.setFocus( self.controls['Context Menu Button1']['control'] )
        
    def closeDialog( self ):
        self.close()
        
    def onControl( self, control ):
        if ( control is self.controls['Context Menu Button1']['control'] ):
            if ( self.list_control == 'Trailer List' ):
                self.win.playTrailer()
            elif ( self.list_control == 'Category List' ):
                self.win.getTrailerGenre()
            elif ( self.list_control == 'Cast List' ):
                self.win.getActorChoice()
        elif ( control is self.controls['Context Menu Button2']['control'] ):
            if ( self.list_control == 'Trailer List' ):
                self.win.toggleAsFavorite()
            elif ( self.list_control == 'Category List' ):
                self.win.refreshInfo( True )
        elif ( control is self.controls['Context Menu Button3']['control'] ):
            if ( self.list_control == 'Trailer List' ):
                self.win.toggleAsWatched()
        elif ( control is self.controls['Context Menu Button4']['control'] ):
            if ( self.list_control == 'Trailer List' ):
                self.win.refreshInfo( False )
        elif ( control is self.controls['Context Menu Button5']['control'] ):
            if ( self.list_control == 'Trailer List' ):
                self.win.deleteSavedTrailer()
        #elif ( control is self.controls['Context Menu Button6']['control'] ):
        self.closeDialog()
        
    def onAction( self, action ):
        control = self.getFocus()
        button_key = self.controller_action.get( action.getButtonCode(), 'n/a' )
        if ( button_key == 'Keyboard Backspace Button' or button_key == 'B Button' or button_key == 'Remote Back Button' ):
            self.closeDialog()
        elif ( button_key == 'Keyboard ESC Button' or button_key == 'Back Button' or button_key == 'Remote Menu Button' ):
            self.closeDialog()
        elif ( button_key == 'Keyboard Menu Button' or button_key == 'Remote Title' or button_key == 'White Button' ):
            self.closeDialog()
