import xbmc, xbmcgui
import os, guibuilder


class settingsGUI( xbmcgui.WindowDialog ):
    def __init__( self ):
        self.getSettings()
        self.setupGUI()
        if ( not self.SUCCEEDED ): self.close()
        else: 
            self.setupConstants()
            self.setControlsValues()

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
        self.controllerAction = {
            216 : 'Remote Back Button',
            247 : 'Remote Menu Button',
            256 : 'A Button',
            257 : 'B Button',
            258 : 'X Button',
            259 : 'Y Button',
            260 : 'Black Button',
            261 : 'White Button',
            274 : 'Start Button',
            275 : 'Back Button',
            270 : 'DPad Up',
            271 : 'DPad Down',
            272 : 'DPad Left',
            273 : 'DPad Right'
        }
    
    def getSettings( self ):
        try:
            self.settings = {}
            f = open( os.path.join( os.getcwd(), 'data', 'settings.txt' ).replace( ';', '' ), 'r' )
            settings = f.read().split('|')
            f.close()
            self.settings['trailer quality'] = int( settings[0] )
            self.settings['mode'] = int( settings[1] )
            self.settings['skin'] = settings[2]
            self.settings['save folder'] = settings[3]
        except:
            self.settings = {'trailer quality' : 2, 'mode' : 0, 'skin' : 'default', 'save folder' : 'f:\\'}
        self.skin = self.settings['skin']
        
    def setControlsValues( self ):
        quality = ['Low', 'Medium', 'High']
        self.controls['Trailer Quality Button']['control'].setLabel( 'Trailer Quality: %s' % ( quality[self.settings['trailer quality']], ) )
        mode = ['Stream', 'Download', 'Download & Save']
        self.controls['Mode Button']['control'].setLabel( 'Mode: %s' % ( mode[self.settings['mode']], ) )
        self.controls['Save Folder Button']['control'].setLabel( 'Save Folder: %s' % ( self.settings['save folder'], ) )
        #self.controls['Save Folder Label']['control'].setLabel( self.settings['save folder'] )
        self.controls['Skin Button']['control'].setLabel( 'Skin: %s' % (self.settings['skin'], ) )

    def saveSettings( self ):
        try:
            f = open( os.path.join( os.getcwd(), 'data', 'settings.txt' ).replace( ';', '' ), 'w' )
            settings = '%d|%d|%s|%s' % ( self.settings['trailer quality'], self.settings['mode'], self.settings['skin'], self.settings['save folder'], )
            f.write(settings)
            f.close()
        except:
            dialog = xbmcgui.Dialog()
            ok = dialog.ok( 'Apple Movie Trailers', 'There was an error saving your settings.' )
            self.skin = None
        if ( self.skin and self.skin != self.settings['skin']):
            dialog = xbmcgui.Dialog()
            ok = dialog.ok( 'Apple Movie Trailers', "The skin change won't take affect until you restart." )
        self.closeDialog()

    def toggleTrailerQuality( self ):
        quality = ['Low', 'Medium', 'High']
        tq = self.settings['trailer quality'] + 1
        if ( tq > 2 ): tq = 0
        self.settings['trailer quality'] = tq
        self.controls['Trailer Quality Button']['control'].setLabel( 'Trailer Quality: %s' % ( quality[tq], ) )
      
    def toggleMode( self ):
        mode = ['Stream', 'Download', 'Download & Save']
        m = self.settings['mode'] + 1
        if ( m > 2 ): m = 0
        self.settings['mode'] = m
        self.controls['Mode Button']['control'].setLabel( 'Mode: %s' % ( mode[m], ) )

    def browseForFolder( self ):
        dialog = xbmcgui.Dialog()
        folder = dialog.browse( 0, 'a save folder', 'files' )
        if ( folder ):
            self.settings['save folder'] = folder
            self.controls['Save Folder Button']['control'].setLabel( 'Save Folder: %s' % ( folder, ) )
            
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
        elif ( control is self.controls['Popup List']['control'] ):
            self.settings['skin'] = self.controls['Popup List']['control'].getSelectedItem().getLabel()
            self.controls['Skin Button']['control'].setLabel( 'Skin: %s' % (self.settings['skin'], ) )
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
