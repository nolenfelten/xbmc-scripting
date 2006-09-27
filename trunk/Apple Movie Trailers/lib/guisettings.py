import xbmc, xbmcgui
import os, guibuilder
import amt_util

class GUI( xbmcgui.WindowDialog ):
    def __init__( self ):
        self.settings = amt_util.getSettings()
        self.setupGUI()
        if ( not self.SUCCEEDED ): self.close()
        else:
            self.skin = self.settings['skin']
            self.setupConstants()
            self.setControlsValues()
            ##remove disabled when update script routine is done
            self.controls['Update Button']['control'].setEnabled( False )

    def setupGUI(self):
        skinPath = os.path.join( os.getcwd(), 'skins' ).replace( ';', '' ) # workaround apparent xbmc bug - os.getcwd() returns an extraneous semicolon (;) at the end of the path
        self.skinPath = os.path.join( skinPath, self.settings['skin'] )
        self.imagePath = os.path.join( self.skinPath, 'gfx' )
        res = self.getResolution()
        if ( res == 0 or res % 2 ): skin = 'settings_wide.xml'
        else: skin = 'settings.xml'
        if ( not os.path.isfile( os.path.join( self.skinPath, skin ) ) ): skin = 'settings.xml'
        guibuilder.GUIBuilder( self, os.path.join( self.skinPath, skin ), self.imagePath, useDescAsKey=True, fastMethod=True, debug=False )

    def setupConstants( self ):
        self.controllerAction = amt_util.setControllerAction()
        self.quality = amt_util.setQuality()
        self.mode = amt_util.setMode()
        self.startup = amt_util.setStartupCategory()
        self.thumbnail = amt_util.setThumbnailDisplay()
        
    def setControlsValues( self ):
        self.controls['Trailer Quality Button']['control'].setLabel( 'Trailer Quality: [%s]' % ( self.quality[self.settings['trailer quality']], ) )
        self.controls['Mode Button']['control'].setLabel( 'Mode: [%s]' % ( self.mode[self.settings['mode']], ) )
        self.controls['Save Folder Button']['control'].setLabel( 'Save Folder: [%s]' % ( self.settings['save folder'], ) )
        self.controls['Skin Button']['control'].setLabel( 'Skin: [%s]' % ( self.settings['skin'], ) )
        self.controls['Startup Category Button']['control'].setLabel( 'Startup Category: [%s]' % ( self.startup[self.settings['startup category']], ) )
        self.controls['Thumbnail Display Button']['control'].setLabel( 'Thumbnail Display: [%s]' % ( self.thumbnail[self.settings['thumbnail display']], ) )
        
    def saveSettings( self ):
        ret = amt_util.saveSettings( self.settings )
        if ( not ret ):
            dialog = xbmcgui.Dialog()
            ok = dialog.ok( 'Apple Movie Trailers', 'There was an error saving your settings.' )
        else:
            if ( self.skin != self.settings['skin']):
                dialog = xbmcgui.Dialog()
                ok = dialog.ok( 'Apple Movie Trailers', "The skin change won't take affect until you restart." )
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
        folder = dialog.browse( 0, 'a save folder', 'files' )
        if ( folder ):
            self.settings['save folder'] = folder
            #self.controls['Save Folder Button']['control'].setLabel( 'Save Folder: [%s]' % ( folder, ) )
            self.setControlsValues()

    def chooseSkin( self ):
        skinPath = os.path.join( os.getcwd(), 'skins' ).replace( ';', '' ) # workaround apparent xbmc bug - os.getcwd() returns an extraneous semicolon (;) at the end of the path
        self.showPopup( 'choose your skin', os.listdir( skinPath ) )
        
    def getThumb( self, choice ):
        thumbnail = os.path.join( os.getcwd(), 'skins', choice.getLabel(), 'thumbnail.tbn' ).replace( ';', '' ) # workaround apparent xbmc bug - os.getcwd() returns an extraneous semicolon (;) at the end of the path
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
            if ( os.path.isfile( os.path.join( os.getcwd(), 'skins', item, 'skin.xml' ).replace( ';', '' ) ) ):
                self.controls['Popup List']['control'].addItem( item )
        self.setPopupVisibility( True )
        self.setFocus( self.controls['Popup List']['control'] )
        
    def setPopupVisibility( self, visible ):
        self.controls['Popup Image']['control'].setVisible( visible )
        self.controls['Popup Thumb']['control'].setVisible( visible )
        self.controls['Popup Label']['control'].setVisible( visible )
        self.controls['Popup List']['control'].setVisible( visible )
    
    def setButtonNavigation( self, control ):
        self.controls['Ok Button']['control'].controlLeft( control )
        self.controls['Cancel Button']['control'].controlRight( control )
        
    def closeDialog( self ):
        self.close()
        
    def onControl( self, control ):
        if ( control is self.controls['Cancel Button']['control'] ):
            self.closeDialog()
        elif ( control is self.controls['Ok Button']['control'] ):
            self.saveSettings()
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
            self.settings['skin'] = self.controls['Popup List']['control'].getSelectedItem().getLabel()
            #self.controls['Skin Button']['control'].setLabel( 'Skin: [%s]' % (self.settings['skin'], ) )
            self.setControlsValues()
            self.hidePopup()
            
    def onAction( self, action ):
        control = self.getFocus()
        buttonDesc = self.controllerAction.get(action.getButtonCode(), 'n/a')
        if ( buttonDesc == 'Back Button' or buttonDesc == 'Remote Menu Button' or 
            buttonDesc == 'B Button' or buttonDesc == 'Remote Back Button'):
            if ( control == self.controls['Popup List']['control']): self.hidePopup()
            else: self.close()
        elif ( control == self.controls['Popup List']['control'] ):
            self.getThumb( control.getSelectedItem() )
        elif ( control != self.controls['Ok Button']['control'] and control != self.controls['Cancel Button']['control'] ):
            self.setButtonNavigation( control )
