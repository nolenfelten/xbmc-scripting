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
        if ( self.settings.startup_category_id == -6 ):
            self.startup_category[ 0 ] = len( self.startup_categories ) -2
        elif ( self.settings.startup_category_id == -7 ):
            self.startup_category[ 0 ] = len( self.startup_categories ) -1
        else:
            self.startup_category[ 0 ] = self.settings.startup_category_id
        if ( self.settings.shortcut1 == -6 ):
            self.startup_category[ 1 ] = len( self.startup_categories ) -2
        elif ( self.settings.shortcut1 == -7 ):
            self.startup_category[ 1 ] = len( self.startup_categories ) -1
        else:
            self.startup_category[ 1 ] = self.settings.shortcut1
        if ( self.settings.shortcut2 == -6 ):
            self.startup_category[ 2 ] = len( self.startup_categories ) -2
        elif ( self.settings.shortcut2 == -7 ):
            self.startup_category[ 2 ] = len( self.startup_categories ) -1
        else:
            self.startup_category[ 2 ] = self.settings.shortcut2
        if ( self.settings.shortcut3 == -6 ):
            self.startup_category[ 3 ] = len( self.startup_categories ) -2
        elif ( self.settings.shortcut3 == -7 ):
            self.startup_category[ 3 ] = len( self.startup_categories ) -1
        else:
            self.startup_category[ 3 ] = self.settings.shortcut3
        
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
        self.controls['Startup Category Button Value']['control'].setLabel( '%s' % ( self.startup_categories[self.startup_category[0]][0], ) )
        self.controls['Thumbnail Display Button Value']['control'].setLabel( '%s' % ( self.thumbnail[self.settings.thumbnail_display], ) )
        self.controls['Shortcut1 Button Value']['control'].setLabel( '%s' % ( self.startup_categories[self.startup_category[1]][0], ) )
        self.controls['Shortcut2 Button Value']['control'].setLabel( '%s' % ( self.startup_categories[self.startup_category[2]][0], ) )
        self.controls['Shortcut3 Button Value']['control'].setLabel( '%s' % ( self.startup_categories[self.startup_category[3]][0], ) )
        '''settings_changed = ( 
            self.settings.trailer_quality != self.settings_start.trailer_quality or
            self.settings.mode != self.settings_start.mode or
            self.settings.skin != self.settings_start.skin or
            self.settings.save_folder != self.settings_start.save_folder or
            self.settings.thumbnail_display != self.settings_start.thumbnail_display or
            self.settings.startup_category_id != self.settings_start.startup_category_id or
            self.settings.shortcut1 != self.settings_start.shortcut1 or
            self.settings.shortcut2 != self.settings_start.shortcut2 or
            self.settings.shortcut3 != self.settings_start.shortcut3
            )
        self.controls['Ok Button'][ 'control' ].setEnabled( settings_changed )
        '''
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

    def toggleTrailerQuality( self ):
        tq = self.settings.trailer_quality + 1
        if ( tq > 2 ): tq = 0
        self.settings.trailer_quality = tq
        self.setControlsValues()
      
    def toggleMode( self ):
        m = self.settings.mode + 1
        if ( m > 2 ): m = 0
        self.settings.mode = m
        self.setControlsValues()

    def toggleCategory( self, category ):
        self.startup_category[ category ] += 1
        if ( self.startup_category[ category ] == len( self.startup_categories ) ): self.startup_category[ category ] = 0
        self.setControlsValues()
        if ( self.startup_category[ category ] == ( len( self.startup_categories ) - 1 ) ):
            if ( category == 0 ): self.settings.startup_category_id = -7
            elif ( category == 1 ): self.settings.shortcut1 = -7
            elif ( category == 2 ): self.settings.shortcut2 = -7
            elif ( category == 3 ): self.settings.shortcut3 = -7
        elif ( self.startup_category[ category ] == ( len( self.startup_categories ) - 2 ) ):
            if ( category == 0 ): self.settings.startup_category_id = -6
            elif ( category == 1 ): self.settings.shortcut1 = -6
            elif ( category == 2 ): self.settings.shortcut2 = -6
            elif ( category == 3 ): self.settings.shortcut3 = -6
        else: 
            if ( category == 0 ): self.settings.startup_category_id = self.startup_category[ category ]
            elif ( category == 1 ): self.settings.shortcut1 = self.startup_category[ category ]
            elif ( category == 2 ): self.settings.shortcut2 = self.startup_category[ category ]
            elif ( category == 3 ): self.settings.shortcut3 = self.startup_category[ category ]
        
    def toggleThumbnailDisplay( self ):
        t = self.settings.thumbnail_display + 1
        if ( t > 2 ): t = 0
        self.settings.thumbnail_display = t
        self.setControlsValues()
    
    def browseForFolder( self ):
        dialog = xbmcgui.Dialog()
        folder = dialog.browse( 3, 'a save folder', 'files' )
        if ( folder ):
            self.settings.save_folder = folder
            self.setControlsValues()

    def chooseSkin( self ):
        skin_path = os.path.join( self.cwd, 'extras', 'skins' )
        skins = os.listdir( skin_path )
        skins.sort()
        self.showPopup( 'choose your skin' )
        self.fillListSkins( skins )
        
    def getThumb( self, choice ):
        thumbnail = os.path.join( self.cwd, 'extras', 'skins', choice.getLabel().replace( '*','' ), 'thumbnail.tbn' )
        if ( os.path.isfile( thumbnail ) ):
            self.controls['Popup Thumb']['control'].setImage( thumbnail )
        else:
            self.controls['Popup Thumb']['control'].setImage( '' )
        self.controls['Popup Warning Label']['control'].setVisible( choice.getLabel()[0] == '*' )

    def hidePopup( self ):
        xbmcgui.lock()
        self.setPopupVisibility( False, False )
        self.setFocus( self.current_setting_control )
        xbmcgui.unlock()
        
    def showPopup( self, title ):
        #xbmcgui.lock()
        self.controls['Popup Label']['control'].setLabel( title )
        self.controls['Popup List']['control'].reset()
    
    def fillListSkins( self, items ):
        #xbmcgui.lock()
        for item in items:
            if ( os.path.isfile( os.path.join( self.cwd, 'extras', 'skins', item, 'skin.xml' )) and
                os.path.isfile( os.path.join( self.cwd, 'extras', 'skins', item, 'settings.xml' )) and
                os.path.isfile( os.path.join( self.cwd, 'extras', 'skins', item, 'credits.xml' )) and
                os.path.isfile( os.path.join( self.cwd, 'extras', 'skins', item, 'context_menu.xml' ))):
                if ( os.path.isfile( os.path.join( self.cwd, 'extras', 'skins', item, 'warning.txt' ))):
                    warning = '*'
                else: warning = ''
                self.controls['Popup List']['control'].addItem( xbmcgui.ListItem( '%s%s' % ( warning, item, ), '', '', '' ) )
        self.setPopupVisibility( True, True )
        self.setFocus( self.controls['Popup List']['control'] )
        #xbmcgui.unlock()

    #def setPopupBGVisibility( self, visible ):
    #    try: self.controls['Popup Image Top']['control'].setVisible( visible )
    #    except: pass
    #    try: self.controls['Popup Image Middle']['control'].setVisible( visible )
    #    except: pass
    #    try: self.controls['Popup Image Bottom']['control'].setVisible( visible )
    #    except: pass

    def setPopupVisibility( self, visible=False, visible2=False ):
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
        self.controls['Popup List']['control'].setVisible( visible )
        
    def setSkinSelection( self ):
        self.settings.skin = self.controls['Popup List']['control'].getSelectedItem().getLabel().replace( '*', '' )
        self.setControlsValues()
        self.hidePopup()
    
    
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
        elif ( control is self.controls['Trailer Quality Button']['control'] ):
            self.toggleTrailerQuality()
        elif ( control is self.controls['Mode Button']['control'] ):
            self.toggleMode()
        elif ( control is self.controls['Save Folder Button']['control'] ):
            self.browseForFolder()
        elif ( control is self.controls['Skin Button']['control'] ):
            self.current_setting_control = control
            self.chooseSkin()
        elif ( control is self.controls['Startup Category Button']['control'] ):
            self.toggleCategory( 0 )
        elif ( control is self.controls['Thumbnail Display Button']['control'] ):
            self.toggleThumbnailDisplay()
        elif ( control is self.controls['Shortcut1 Button']['control'] ):
            self.toggleCategory( 1 )
        elif ( control is self.controls['Shortcut2 Button']['control'] ):
            self.toggleCategory( 2 )
        elif ( control is self.controls['Shortcut3 Button']['control'] ):
            self.toggleCategory( 3 )
        elif ( control is self.controls['Popup List']['control'] ):
            self.setSkinSelection()
            
    def onAction( self, action ):
        control = self.getFocus()
        button_key = self.controller_action.get( action.getButtonCode(), 'n/a' )
        if ( button_key == 'Keyboard Backspace Button' or button_key == 'B Button' or button_key == 'Remote Back Button' ):
            if ( control == self.controls['Popup List']['control'] ): self.hidePopup()
            else: self.closeDialog()
        elif ( button_key == 'Keyboard ESC Button' or button_key == 'Back Button' or button_key == 'Remote Menu Button' ):
            if ( control == self.controls['Popup List']['control'] ): self.setSkinSelection()
            else: self.saveSettings()
        elif ( control == self.controls['Popup List']['control'] and self.current_setting_control == self.controls['Skin Button']['control'] ):
            self.getThumb( control.getSelectedItem() )
        #elif ( control != self.controls['Ok Button']['control'] and control != self.controls['Cancel Button']['control'] and
        #    control != self.controls['Update Button']['control'] and control != self.controls['Credits Button']['control'] and
        #    control != self.controls['Popup List']['control']):
        #    self.setButtonNavigation( control )
