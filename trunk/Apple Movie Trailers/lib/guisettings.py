import xbmc, xbmcgui
import os, guibuilder, sys
import amt_util, default

class GUI( xbmcgui.WindowDialog ):
    def __init__( self, *args, **kwargs ):
        self.cwd = os.path.dirname( sys.modules['default'].__file__ )
        self.settings = amt_util.getSettings()
        self._ = kwargs['language']
        self.skin = kwargs['skin']
        self.setupGUI()
        if ( not self.SUCCEEDED ): self.close()
        else:
            self.setupConstants()
            self.setControlsValues()
            ##remove disabled when update script routine is done
            self.controls['Update Button']['control'].setEnabled( False )

    def setupGUI( self ):
        skinPath = os.path.join( self.cwd, 'skins' )
        self.skinPath = os.path.join( skinPath, self.skin )
        self.imagePath = os.path.join( self.skinPath, 'gfx' )
        res = self.getResolution()
        if ( res == 0 or res % 2 ): skin = 'settings_16x9.xml'
        else: skin = 'settings.xml'
        if ( not os.path.isfile( os.path.join( self.skinPath, skin ) ) ): skin = 'settings.xml'
        guibuilder.GUIBuilder( self, os.path.join( self.skinPath, skin ), self.imagePath, useDescAsKey=True, useLocal=True, fastMethod=True, debug=False )

    def setupConstants( self ):
        self.controllerAction = amt_util.setControllerAction()
        self.quality = amt_util.setQuality( self._ )
        self.mode = amt_util.setMode( self._ )
        self.startup = amt_util.setStartupCategory( self._ )
        self.thumbnail = amt_util.setThumbnailDisplay( self._ )
        
    def setControlsValues( self ):
        self.controls['Trailer Quality Button']['control'].setLabel( '%s: [%s]' % ( self._(300), self.quality[self.settings['trailer quality']], ) )
        self.controls['Mode Button']['control'].setLabel( '%s: [%s]' % ( self._(301), self.mode[self.settings['mode']], ) )
        self.controls['Save Folder Button']['control'].setLabel( '%s: [%s]' % ( self._(302), self.settings['save folder'], ) )
        self.controls['Save Folder Button']['control'].setEnabled( self.settings['mode'] == 2 )
        self.controls['Skin Button']['control'].setLabel( '%s: [%s]' % ( self._(303), self.settings['skin'], ) )
        self.controls['Startup Category Button']['control'].setLabel( '%s: [%s]' % ( self._(304), self.startup[self.settings['startup category']], ) )
        self.controls['Thumbnail Display Button']['control'].setLabel( '%s: [%s]' % ( self._(305), self.thumbnail[self.settings['thumbnail display']], ) )

    def saveSettings( self ):
        ret = amt_util.saveSettings( self.settings )
        if ( not ret ):
            dialog = xbmcgui.Dialog()
            ok = dialog.ok( self._(0), self._(55) )
        else:
            if ( self.skin != self.settings['skin']):
                dialog = xbmcgui.Dialog()
                ok = dialog.ok( self._(0), self._(56)  )
            self.closeDialog()

    def toggleTrailerQuality( self ):
        tq = self.settings['trailer quality'] + 1
        if ( tq > 2 ): tq = 0
        self.settings['trailer quality'] = tq
        #self.controls['Trailer Quality Button']['control'].setLabel( 'Trailer Quality: [%s]' % ( self.quality[tq], ) )
        self.setControlsValues()
      
    def toggleMode( self ):
        m = self.settings['mode'] + 1
        if ( m > 2 ): m = 0
        self.settings['mode'] = m
        #self.controls['Mode Button']['control'].setLabel( 'Mode: [%s]' % ( self.mode[m], ) )
        self.setControlsValues()

    def toggleStartupCategory( self ):
        c = self.settings['startup category'] + 1
        if ( c > 2 ): c = 0
        self.settings['startup category'] = c
        #self.controls['Startup Category Button'].setLabel( 'Startup Category: [%s]' % ( self.startup[c], ) )
        self.setControlsValues()
        
    def toggleThumbnailDisplay( self ):
        t = self.settings['thumbnail display'] + 1
        if ( t > 2 ): t = 0
        self.settings['thumbnail display'] = t
        #self.controls['Startup Category Button'].setLabel( 'Startup Category: [%s]' % ( self.startup[c], ) )
        self.setControlsValues()
    
    def browseForFolder( self ):
        dialog = xbmcgui.Dialog()
        folder = dialog.browse( 3, 'a save folder', 'files' )
        if ( folder ):
            self.settings['save folder'] = folder
            #self.controls['Save Folder Button']['control'].setLabel( 'Save Folder: [%s]' % ( folder, ) )
            self.setControlsValues()

    def chooseSkin( self ):
        skinPath = os.path.join( self.cwd, 'skins' )
        skins = os.listdir( skinPath )
        skins.sort()
        self.showPopup( 'choose your skin', skins )
        
    def getThumb( self, choice ):
        thumbnail = os.path.join( self.cwd, 'skins', choice.getLabel(), 'thumbnail.tbn' )
        if ( os.path.isfile( thumbnail ) ):
            self.controls['Popup Thumb']['control'].setImage( thumbnail )
        else:
            self.controls['Popup Thumb']['control'].setImage( '' )
        
    def hidePopup( self ):
        self.setPopupVisibility( False )
        self.setFocus( self.controls['Skin Button']['control'] )
    
    def showPopup( self, title, items ):
        self.controls['Popup Label']['control'].setLabel( title )
        self.controls['Popup List']['control'].reset()
        for item in items:
            if ( os.path.isfile( os.path.join( self.cwd, 'skins', item, 'skin.xml' ).replace( ';', '' ) ) and
                os.path.isfile( os.path.join( self.cwd, 'skins', item, 'settings.xml' ).replace( ';', '' ) ) ):
                if ( os.path.isfile( os.path.join( self.cwd, 'skins', item, 'warning.txt' ).replace( ';', '' ) ) ):
                    warning = '*'
                else: warning = ''
                self.controls['Popup List']['control'].addItem( '%s%s' % ( warning, item, ) )
        self.setPopupVisibility( True )
        self.setFocus( self.controls['Popup List']['control'] )
        
    def setPopupVisibility( self, visible ):
        self.controls['Popup Image']['control'].setVisible( visible )
        self.controls['Popup Label']['control'].setVisible( visible )
        self.controls['Popup Thumb']['control'].setVisible( visible )
        self.controls['Popup Warning Label']['control'].setVisible( visible )
        self.controls['Popup List']['control'].setVisible( visible )
        
    def setSkinSelection( self ):
        self.settings['skin'] = self.controls['Popup List']['control'].getSelectedItem().getLabel()
        #self.controls['Skin Button']['control'].setLabel( 'Skin: [%s]' % (self.settings['skin'], ) )
        self.setControlsValues()
        self.hidePopup()
    
    
    def setButtonNavigation( self, control ):
        pass
    #    self.controls['Ok Button']['control'].controlUp( control )
    #    self.controls['Cancel Button']['control'].controlUp( control )
    #    self.controls['Update Button']['control'].controlUp( control )
    #    self.controls['Credits Button']['control'].controlUp( control )
    #    self.controls['Ok Button']['control'].controlDown( control )
    #    self.controls['Cancel Button']['control'].controlDown( control )
    #    self.controls['Update Button']['control'].controlDown( control )
    #    self.controls['Credits Button']['control'].controlDown( control )

    def showCredits( self ):
        try:
            self.controls['Credits Label']['control'].setLabel( self._(0) )
            self.controls['Version Label']['control'].setLabel( '%s: %s' % ( self._(100), default.__version__, ) )
            self.controls['Team Credits Label']['control'].setLabel( self._(101) )
            self.controls['Team Credits List']['control'].reset()
            l = xbmcgui.ListItem( default.__credits_l1__, default.__credits_r1__ )
            self.controls['Team Credits List']['control'].addItem( l )
            l = xbmcgui.ListItem( default.__credits_l2__, default.__credits_r2__ )
            self.controls['Team Credits List']['control'].addItem( l )
            l = xbmcgui.ListItem( default.__credits_l3__, default.__credits_r3__ )
            self.controls['Team Credits List']['control'].addItem( l )

            self.controls['Additional Credits Label']['control'].setLabel( self._(102) )
            self.controls['Additional Credits List']['control'].reset()
            l = xbmcgui.ListItem( default.__acredits_l1__, default.__acredits_r1__ )
            self.controls['Additional Credits List']['control'].addItem( l )
            l = xbmcgui.ListItem( default.__acredits_l2__, default.__acredits_r2__ )
            self.controls['Additional Credits List']['control'].addItem( l )
            l = xbmcgui.ListItem( default.__acredits_l3__, default.__acredits_r3__ )
            self.controls['Additional Credits List']['control'].addItem( l )

            self.setCreditsVisibility( True )
            self.setFocus( self.controls['Skin Credits List']['control'] )
        except: print 'Credits Removed'
            
    def hideCredits( self ):
        self.setCreditsVisibility( False )
        self.setFocus( self.controls['Credits Button']['control'] )

    def setCreditsVisibility( self, visible ):
        try:
            self.controls['Credits Image']['control'].setVisible( visible )
            self.controls['Credits Label']['control'].setVisible( visible )
            self.controls['Version Label']['control'].setVisible( visible )
            self.controls['Team Credits Label']['control'].setVisible( visible )
            self.controls['Team Credits List']['control'].setVisible( visible )
            self.controls['Additional Credits Label']['control'].setVisible( visible )
            self.controls['Additional Credits List']['control'].setVisible( visible )
            self.controls['Skin Credits Label']['control'].setVisible( visible )
            self.controls['Skin Credits List']['control'].setVisible( visible )
        except: print 'Credits Removed'
            
    def closeDialog( self ):
        self.close()
        
    def onControl( self, control ):
        if ( control is self.controls['Cancel Button']['control'] ):
            self.closeDialog()
        elif ( control is self.controls['Ok Button']['control'] ):
            self.saveSettings()
        elif ( control is self.controls['Credits Button']['control'] ):
            self.showCredits()
        elif ( control is self.controls['Trailer Quality Button']['control'] ):
            self.toggleTrailerQuality()
        elif ( control is self.controls['Mode Button']['control'] ):
            self.toggleMode()
        elif ( control is self.controls['Save Folder Button']['control'] ):
            self.browseForFolder()
        elif ( control is self.controls['Skin Button']['control'] ):
            self.chooseSkin()
        elif ( control is self.controls['Startup Category Button']['control'] ):
            self.toggleStartupCategory()
        elif ( control is self.controls['Thumbnail Display Button']['control'] ):
            self.toggleThumbnailDisplay()
        elif ( control is self.controls['Popup List']['control'] ):
            self.setSkinSelection()
            
    def onAction( self, action ):
        control = self.getFocus()
        buttonDesc = self.controllerAction.get( action.getButtonCode(), 'n/a' )
        if ( buttonDesc == 'B Button' or buttonDesc == 'Remote Back Button' ):
            if ( control == self.controls['Popup List']['control'] ): self.hidePopup()
            elif ( control == self.controls['Skin Credits List']['control'] ): self.hideCredits()
            else: self.close()
        elif ( buttonDesc == 'Back Button' or buttonDesc == 'Remote Menu Button' ):
            if ( control == self.controls['Popup List']['control'] ): self.setSkinSelection()
            elif ( control == self.controls['Skin Credits List']['control'] ): self.hideCredits()
            else: self.saveSettings()
        elif ( control == self.controls['Popup List']['control'] ):
            self.getThumb( control.getSelectedItem() )
        #elif ( control != self.controls['Ok Button']['control'] and control != self.controls['Cancel Button']['control'] ):
        #    self.setButtonNavigation( control )
