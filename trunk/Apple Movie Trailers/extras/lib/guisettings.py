import xbmc, xbmcgui
import os, guibuilder, sys
import amt_util, default

class GUI( xbmcgui.WindowDialog ):
    def __init__( self, *args, **kwargs ):
        self.cwd = os.path.dirname( sys.modules['default'].__file__ )
        self.getSettings()
        self._ = kwargs['language']
        self.skin = kwargs['skin']
        self.setupGUI()
        if ( not self.SUCCEEDED ): self.close()
        else:
            self.setStartupCategories( kwargs['genres'] )
            self.setupVariables()
            self.setControlsValues()

    def setupGUI( self ):
        current_skin = xbmc.getSkinDir()
        if ( not os.path.exists( os.path.join( self.cwd, 'extras', 'skins', current_skin ) ) ): current_skin = 'default'
        skin_path = os.path.join( self.cwd, 'extras', 'skins', current_skin )
        image_path = os.path.join( skin_path, 'gfx' )
        if ( self.getResolution() == 0 or self.getResolution() % 2 ): xml_file = 'settings_16x9.xml'
        else: xml_file = 'settings.xml'
        if ( not os.path.isfile( os.path.join( skin_path, xml_file ) ) ): xml_file = 'settings.xml'
        guibuilder.GUIBuilder( self, os.path.join( skin_path, xml_file ), image_path, useDescAsKey=True, useLocal=True, fastMethod=True, debug=False )

    def setStartupCategories( self, genres ):
        self.startup_categories = []
        self.startup_category = [ 0, 0, 0, 0]
        for count, genre in enumerate( genres ):
            self.startup_categories.append( ( str( genre.title ), count ) )
        self.startup_categories.append( ( self._( 217 ), -6 ) )
        self.startup_categories.append( ( self._( 226 ), -7 ) )
        for count, item in enumerate( self.startup_categories ):
            if ( self.settings.startup_category_id == item[ 1 ] ):
                self.startup_category[ 0 ] = count
            if ( self.settings.shortcut1 == item[ 1 ] ):
                self.startup_category[ 1 ] = count
            if ( self.settings.shortcut2 == item[ 1 ] ):
                self.startup_category[ 2 ] = count
            if ( self.settings.shortcut3 == item[ 1 ] ):
                self.startup_category[ 3 ] = count

    def setupVariables( self ):
        self.controls['Version Label']['control'].setLabel( '%s: %s' % ( self._(100), default.__version__, ) )
        self.controller_action = amt_util.setControllerAction()
        self.quality = amt_util.setQuality( self._ )
        self.mode = amt_util.setMode( self._ )
        self.thumbnail = amt_util.setThumbnailDisplay( self._ )
        self.current_setting_control = None
        ##self.getGenreCategories()
        
    def setControlsValues( self ):
        xbmcgui.lock()
        self.controls['Skin Button Value']['control'].setLabel( '%s' % ( self.settings.skin, ) )
        self.controls['Trailer Quality Button Value']['control'].setLabel( '%s' % ( self.quality[self.settings.trailer_quality], ) )
        self.controls['Mode Button Value']['control'].setLabel( '%s' % ( self.mode[self.settings.mode], ) )
        self.controls['Save Folder Button']['control'].setEnabled( self.settings.mode == 2 )
        self.controls['Save Folder Button Value']['control'].setLabel( '%s' % ( self.settings.save_folder, ) )
        self.controls['Save Folder Button Value']['control'].setEnabled( self.settings.mode == 2 )
        self.controls['Thumbnail Display Button Value']['control'].setLabel( '%s' % ( self.thumbnail[self.settings.thumbnail_display], ) )
        self.controls['Startup Category Button Value']['control'].setLabel( '%s' % ( self.startup_categories[self.startup_category[0]][0], ) )
        self.controls['Shortcut1 Button Value']['control'].setLabel( '%s' % ( self.startup_categories[self.startup_category[1]][0], ) )
        self.controls['Shortcut2 Button Value']['control'].setLabel( '%s' % ( self.startup_categories[self.startup_category[2]][0], ) )
        self.controls['Shortcut3 Button Value']['control'].setLabel( '%s' % ( self.startup_categories[self.startup_category[3]][0], ) )
        xbmcgui.unlock()
        
    def getSettings( self ):
        self.settings = amt_util.Settings()
        self.settings_start = amt_util.Settings()
        
    def saveSettings( self ):
        ret = self.settings.saveSettings()
        if ( not ret ):
            dialog = xbmcgui.Dialog()
            ok = dialog.ok( self._(0), self._(55) )
        else:
            if ( self.skin != self.settings.skin):
                dialog = xbmcgui.Dialog()
                ok = dialog.ok( self._(0), self._(56)  )
            self.closeDialog()

    def browseForFolder( self ):
        dialog = xbmcgui.Dialog()
        folder = dialog.browse( 3, 'a save folder', 'files' )
        if ( folder ):
            self.settings.save_folder = folder
            self.setControlsValues()

    def getThumb( self, choice ):
        thumbnail = os.path.join( self.cwd, 'extras', 'skins', choice.getLabel().replace( '*','' ), 'thumbnail.tbn' )
        if ( os.path.isfile( thumbnail ) ):
            self.controls['Popup Thumb']['control'].setImage( thumbnail )
        else:
            self.controls['Popup Thumb']['control'].setImage( '' )
        self.controls['Popup Warning Label']['control'].setVisible( choice.getLabel()[0] == '*' )
    
    def chooseSkin( self ):
        xbmcgui.lock()
        skin_path = os.path.join( self.cwd, 'extras', 'skins' )
        skins = os.listdir( skin_path )
        skins.sort()
        pos = 0
        self.controls['Popup List']['control'].reset()
        for count, item in enumerate( skins ):
            if ( os.path.isfile( os.path.join( self.cwd, 'extras', 'skins', item, 'skin.xml' )) and
                os.path.isfile( os.path.join( self.cwd, 'extras', 'skins', item, 'settings.xml' )) and
                os.path.isfile( os.path.join( self.cwd, 'extras', 'skins', item, 'credits.xml' )) and
                os.path.isfile( os.path.join( self.cwd, 'extras', 'skins', item, 'context_menu.xml' ))):
                if ( os.path.isfile( os.path.join( self.cwd, 'extras', 'skins', item, 'warning.txt' ))):
                    warning = '*'
                else: warning = ''
                self.controls['Popup List']['control'].addItem( '%s%s' % ( warning, item, ) )
                if ( item.lower() == self.settings.skin.lower() ): pos = count - 1
        self.controls['Popup List']['control'].selectItem( pos  )
        self.getThumb( self.controls['Popup List']['control'].getSelectedItem() )
        self.showPopup( 'choose your skin', True )
        xbmcgui.unlock()

    def chooseTrailerQuality( self ):
        xbmcgui.lock()
        self.controls['Popup List2']['control'].reset()
        for item in self.quality:
            self.controls['Popup List2']['control'].addItem( item ) 
        self.controls['Popup List2']['control'].selectItem( self.settings.trailer_quality )
        self.showPopup( 'choose trailer quality', False, True )
        xbmcgui.unlock()

    def chooseMode( self ):
        xbmcgui.lock()
        self.controls['Popup List2']['control'].reset()
        for item in self.mode:
            self.controls['Popup List2']['control'].addItem( item ) 
        self.controls['Popup List2']['control'].selectItem( self.settings.mode )
        self.showPopup( 'choose streaming mode', False, True )
        xbmcgui.unlock()

    def chooseThumbnailDisplay( self ):
        #xbmcgui.lock()
        self.controls['Popup List2']['control'].reset()
        for item in self.thumbnail:
            self.controls['Popup List2']['control'].addItem( item ) 
        self.showPopup( 'choose thumbnail display mode', False, True )
        self.controls['Popup List2']['control'].selectItem( self.settings.thumbnail_display )
        #xbmcgui.unlock()

    def chooseCategory( self, category ):
        #xbmcgui.lock()
        self.controls['Popup List2']['control'].reset()
        for item in self.startup_categories:
            self.controls['Popup List2']['control'].addItem( str( item[ 0 ] ) )
        self.controls['Popup List2']['control'].selectItem( self.startup_category[ category ] )
        self.showPopup( 'choose category', False, True )
        #xbmcgui.unlock()

    def showPopup( self, title, thumb_visible=False, list_visible=False ):
        self.controls['Popup Label']['control'].setLabel( title )
        self.setPopupVisibility( True, thumb_visible, list_visible )
        if ( thumb_visible ):
            self.setFocus( self.controls['Popup List']['control'] )
        else:
            self.setFocus( self.controls['Popup List2']['control'] )
            
    def hidePopup( self ):
        self.setPopupVisibility()
        self.setFocus( self.current_setting_control )

    def setPopupVisibility( self, visible=False, visible2=False, visible3=False ):
        #self.setPopupBGVisibility( visible )
        try: self.controls['Popup Image Top']['control'].setVisible( visible )
        except: pass
        try: self.controls['Popup Image Middle']['control'].setVisible( visible )
        except: pass
        try: self.controls['Popup Image Bottom']['control'].setVisible( visible )
        except: pass
        self.controls['Popup Label']['control'].setVisible( visible )
        self.controls['Popup Thumb']['control'].setVisible( visible2 )
        self.controls['Popup Warning Label']['control'].setVisible( visible2 )
        self.controls['Popup List']['control'].setVisible( visible2 )
        self.controls['Popup List2']['control'].setVisible( visible3 )
        
    def setSkinSelection( self ):
        self.settings.skin = self.controls['Popup List']['control'].getSelectedItem().getLabel().replace( '*', '' )
        self.setControlsValues()
        self.hidePopup()
    
    def setTrailerQuality( self ):
        self.settings.trailer_quality = self.controls['Popup List2']['control'].getSelectedPosition()
        self.setControlsValues()
        self.hidePopup()
    
    def setMode( self ):
        self.settings.mode = self.controls['Popup List2']['control'].getSelectedPosition()
        self.setControlsValues()
        self.hidePopup()
    
    def setThumbnailDisplay( self ):
        self.settings.thumbnail_display = self.controls['Popup List2']['control'].getSelectedPosition()
        self.setControlsValues()
        self.hidePopup()

    def setCategory( self, category ):
        item = self.controls['Popup List2']['control'].getSelectedPosition()
        self.startup_category[ category ] = item
        if ( category == 0 ):
            self.settings.startup_category_id = self.startup_categories[ item ][1]
        elif ( category == 1 ):
            self.settings.shortcut1 = self.startup_categories[ item ][1]
        elif ( category == 2 ):
            self.settings.shortcut2 = self.startup_categories[ item ][1]
        elif ( category == 3 ):
            self.settings.shortcut3 = self.startup_categories[ item ][1]
        self.setControlsValues()
        self.hidePopup()

    def setSelectionList2( self ):
        if ( self.current_setting_control == self.controls['Trailer Quality Button']['control'] ):
            self.setTrailerQuality()
        elif ( self.current_setting_control == self.controls['Mode Button']['control'] ):
            self.setMode()
        elif ( self.current_setting_control == self.controls['Thumbnail Display Button']['control'] ):
            self.setThumbnailDisplay()
        elif ( self.current_setting_control == self.controls['Startup Category Button']['control'] ):
            self.setCategory( 0 )
        elif ( self.current_setting_control == self.controls['Shortcut1 Button']['control'] ):
            self.setCategory( 1 )
        elif ( self.current_setting_control == self.controls['Shortcut2 Button']['control'] ):
            self.setCategory( 2 )
        elif ( self.current_setting_control == self.controls['Shortcut3 Button']['control'] ):
            self.setCategory( 3 )

    def setButtonNavigation( self, control ):
        pass
        '''
        self.controls['Ok Button']['control'].controlRight( control )
        self.controls['Cancel Button']['control'].controlRight( control )
        self.controls['Update Button']['control'].controlRight( control )
        self.controls['Credits Button']['control'].controlRight( control )
        self.controls['Ok Button']['control'].controlLeft( control )
        self.controls['Cancel Button']['control'].controlLeft( control )
        self.controls['Update Button']['control'].controlLeft( control )
        self.controls['Credits Button']['control'].controlLeft( control )
        '''

    def showCredits( self ):
        import credits
        cw = credits.GUI( language=self._ )
        cw.doModal()
        del cw

    def updateScript( self ):
        import update
        updt = update.Update( language = self._, script = default.__scriptname__, version = default.__version__ )
        del update
        
    def closeDialog( self ):
        self.close()

    def onControl( self, control ):
        if ( control is self.controls['Cancel Button']['control'] ):
            self.closeDialog()
        elif ( control is self.controls['Ok Button']['control'] ):
            self.saveSettings()
        elif ( control is self.controls['Update Button']['control'] ):
            self.updateScript()
        elif ( control is self.controls['Credits Button']['control'] ):
            self.showCredits()
        elif ( control is self.controls['Skin Button']['control'] ):
            self.current_setting_control = control
            self.chooseSkin()
        elif ( control is self.controls['Trailer Quality Button']['control'] ):
            self.current_setting_control = control
            self.chooseTrailerQuality()
        elif ( control is self.controls['Mode Button']['control'] ):
            self.current_setting_control = control
            self.chooseMode()
        elif ( control is self.controls['Save Folder Button']['control'] ):
            self.browseForFolder()
        elif ( control is self.controls['Thumbnail Display Button']['control'] ):
            self.current_setting_control = control
            self.chooseThumbnailDisplay()
        elif ( control is self.controls['Startup Category Button']['control'] ):
            self.current_setting_control = control
            self.chooseCategory( 0 )
        elif ( control is self.controls['Shortcut1 Button']['control'] ):
            self.current_setting_control = control
            self.chooseCategory( 1 )
        elif ( control is self.controls['Shortcut2 Button']['control'] ):
            self.current_setting_control = control
            self.chooseCategory( 2 )
        elif ( control is self.controls['Shortcut3 Button']['control'] ):
            self.current_setting_control = control
            self.chooseCategory( 3 )
        elif ( control is self.controls['Popup List']['control'] ): self.setSkinSelection()
        elif ( control is self.controls['Popup List2']['control'] ): self.setSelectionList2()
                
    def onAction( self, action ):
        control = self.getFocus()
        button_key = self.controller_action.get( action.getButtonCode(), 'n/a' )
        if ( button_key == 'Keyboard Backspace Button' or button_key == 'B Button' or button_key == 'Remote Back Button' ):
            if ( control == self.controls['Popup List']['control'] ): self.hidePopup()
            elif ( control == self.controls['Popup List2']['control'] ): self.hidePopup()
            else: self.closeDialog()
        elif ( button_key == 'Keyboard ESC Button' or button_key == 'Back Button' or button_key == 'Remote Menu Button' ):
            if ( control is self.controls['Popup List']['control'] ): self.setSkinSelection()
            elif ( control is self.controls['Popup List2']['control'] ): self.setSelectionList2()
            else: self.saveSettings()
        elif ( control == self.controls['Popup List']['control'] ):
            self.getThumb( control.getSelectedItem() )
        #elif ( control != self.controls['Ok Button']['control'] and control != self.controls['Cancel Button']['control'] and
        #    control != self.controls['Update Button']['control'] and control != self.controls['Credits Button']['control'] and
        #    control != self.controls['Popup List']['control']):
        #    self.setButtonNavigation( control )
