import xbmc, xbmcgui
import os, sys
import guibuilder
import lyricsutil#, guibuilder
import traceback

class GUI( xbmcgui.WindowDialog ):
    def __init__( self, *args, **kwargs ):
        try:
            self._ = kwargs['language']
            self.setupGUI()
            if ( not self.SUCCEEDED ): self.close()
            else:
                self.setupVariables()
                self.getSettings()
                self.setupScrapers()
                self.setControlsValues()
        except:
            traceback.print_exc()
            self.close()
            
    def setupGUI( self ):
        cwd = sys.path[ 0 ]
        current_skin = xbmc.getSkinDir()
        if ( not os.path.exists( os.path.join( cwd, 'extras', 'skins', current_skin ))): current_skin = 'default'
        skin_path = os.path.join( cwd, 'extras', 'skins', current_skin )
        image_path = os.path.join( skin_path, 'gfx' )
        if ( self.getResolution() == 0 or self.getResolution() % 2 ): xml_file = 'settings_16x9.xml'
        else: xml_file = 'settings.xml'
        if ( not os.path.isfile( os.path.join( skin_path, xml_file ))): xml_file = 'settings.xml'
        guibuilder.GUIBuilder( self, os.path.join( skin_path, xml_file ), image_path, useDescAsKey=True, useLocal=True, fastMethod=True, debug=False )

    def setupVariables( self ):
        self.controller_action = lyricsutil.setControllerAction()
        
    def setupScrapers( self ):
        scrapers = []
        self.current_scraper = 0
        os.path.walk( os.path.join( sys.path[ 0 ], 'extras', 'scrapers' ), self.addDir, scrapers )
        self.scrapers = scrapers
        for cnt, scraper in enumerate( scrapers ):
            if ( scraper == self.settings.SCRAPER ):
                self.current_scraper = cnt
                break
        
    def addDir( self, scrapers, path, files ):
        tmp_scraper = os.path.split( path )[ 1 ]
        if ( tmp_scraper.lower() != 'scrapers' ):
            scrapers += [ tmp_scraper ]
            

    def getSettings( self ):
        self.settings = lyricsutil.Settings()
        self.SCRAPER = self.settings.SCRAPER
        #self.settings_start = lyricsutil.Settings()
        
    def setControlsValues( self ):
        #xbmcgui.lock()
        self.controls['Scraper Button Value']['control'].setLabel( '%s' % ( self.settings.SCRAPER, ) )
        self.controls['Save Lyrics Button Value']['control'].setLabel( '%s' % ( str( self.settings.SAVE_LYRICS, ) ) )
        self.controls['Save Folder Button']['control'].setEnabled( self.settings.SAVE_LYRICS )
        self.controls['Save Folder Button Value']['control'].setLabel( '%s' % ( self.settings.LYRICS_PATH, ) )
        self.controls['Save Folder Button Value']['control'].setEnabled( self.settings.SAVE_LYRICS  )
        #xbmcgui.lock()
    
    def toggleScraper( self ):
        self.current_scraper += 1
        if ( self.current_scraper == len( self.scrapers ) ): self.current_scraper = 0
        self.settings.SCRAPER = self.scrapers[ self.current_scraper ]
    
    def toggleSaveLyrics( self ):
        self.settings.SAVE_LYRICS = not self.settings.SAVE_LYRICS

    def browseForFolder( self ):
        dialog = xbmcgui.Dialog()
        folder = dialog.browse( 3, self._( 33 ), 'files' )
        if ( folder ):
            self.settings.LYRICS_PATH = folder
    
    def saveSettings( self ):
        ret = self.settings.saveSettings()
        if ( not ret ):
            ok = xbmcgui.Dialog().ok( self._( 0 ), self._( 12 ) )
        else:
            if ( self.SCRAPER != self.settings.SCRAPER):
                ok = xbmcgui.Dialog().ok( self._( 0 ), self._( 13 )  )
            self.closeDialog()

    def closeDialog( self ):
        self.close()
        
    def onControl( self, control ):
        if ( control is self.controls['Cancel Button']['control'] ):
            self.closeDialog()
        elif ( control is self.controls['Ok Button']['control'] ):
            self.saveSettings()
        #elif ( control is self.controls['Update Button']['control'] ):
        #    self.updateScript()
        #elif ( control is self.controls['Credits Button']['control'] ):
        #    self.showCredits()
        else:
            if ( control is self.controls['Scraper Button']['control'] ):
                self.toggleScraper()
            elif ( control is self.controls['Save Lyrics Button']['control'] ):
                self.toggleSaveLyrics()
            elif ( control is self.controls['Save Folder Button']['control'] ):
                self.browseForFolder()
            self.setControlsValues()
            
    def onAction( self, action ):
        control = self.getFocus()
        button_key = self.controller_action.get( action.getButtonCode(), 'n/a' )
        if ( button_key == 'Keyboard Backspace Button' or button_key == 'B Button' or button_key == 'Remote Back Button' ):
            self.closeDialog()
        elif ( button_key == 'Keyboard ESC Button' or button_key == 'Back Button' or button_key == 'Remote Menu Button' ):
            self.saveSettings()
