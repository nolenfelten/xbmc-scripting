'''
Main GUI for Apple Movie Trailers
'''
__line1__       = 'Setting up script:'
__line2__       = 'Importing modules & initializing...'

def createProgressDialog( __line3__ ):
    global dialog, pct
    pct = 0
    dialog = xbmcgui.DialogProgress()
    dialog.create( default.__scriptname__ )
    updateProgressDialog( __line3__ )

def updateProgressDialog( __line3__ ):
    global dialog, pct
    pct += 5
    dialog.update( pct, __line1__, __line2__, __line3__ )

def closeProgessDialog():
    global dialog
    dialog.close()
    
import xbmcgui, default
createProgressDialog( 'modules: xbmcgui, default' )

updateProgressDialog( 'modules: xbmc, sys, os, traceback' )
import xbmc, sys, os, traceback

updateProgressDialog( 'modules: trailers' )
import trailers

updateProgressDialog( 'modules: threading, language' )
import threading, language

updateProgressDialog( 'modules: guibuilder, guisettings' )
import guibuilder, guisettings

updateProgressDialog( 'modules: amt_util, cacheurl, shutil' )
import amt_util, cacheurl, shutil


class GUI( xbmcgui.Window ):
    def __init__( self ):
        self.getSettings()
        self.skin = self.settings['skin']
        self.setupGUI()
        if ( not self.SUCCEEDED ): self.close()
        else:
            try:
                closeProgessDialog()
                ## enable when ready
                self.controls['Search Button']['control'].setEnabled( False )
                self.setupConstants()
                self.trailers = trailers.Trailers()
                if ( self.checkForDB() ):
                    self.getGenreCategories()
                    self.setStartupCategory()
                else:
                    dialog = xbmcgui.Dialog()
                    ok = dialog.ok(default.__scriptname__, 'No database found!', 'You must Update all genre and movie information.')
            except: 
                xbmc.output('Error at script start')
                self.exitScript()
                
    def setupGUI(self):
        skinPath = os.path.join( os.getcwd(), 'skins' ).replace( ';', '' ) # workaround apparent xbmc bug - os.getcwd() returns an extraneous semicolon (;) at the end of the path
        self.skinPath = os.path.join( skinPath, self.settings['skin'] )
        self.imagePath = os.path.join( self.skinPath, 'gfx' )
        res = self.getResolution()
        if ( res == 0 or res % 2 ): skin = 'skin_16x9.xml'
        else: skin = 'skin.xml'
        if ( not os.path.isfile( os.path.join( self.skinPath, skin ) ) ): skin = 'skin.xml'
        guibuilder.GUIBuilder( self, os.path.join( self.skinPath, skin ), self.imagePath, useDescAsKey=True, title=default.__scriptname__, line1=__line1__, dlg=dialog, pct=pct, useLocal=True, debug=False )

    def getSettings( self ):
        self.settings = amt_util.getSettings()

    def checkForDB( self ):
        if ( os.path.isfile( os.path.join( os.getcwd(), 'data', 'AMT.pk' ).replace( ';', '' ) ) ): return True
        else: return False

    def setStartupCategory( self ):
        startup = amt_util.setStartupCategory()
        self.setGenre( startup[self.settings['startup category']] )
        self.setListNavigation( '%s Button' % ( startup[self.settings['startup category']], ) )
        if ( startup[self.settings['startup category']] != 'Genre' ):
            self.getTrailerInfo( self.controls['Trailer List']['control'].getSelectedItem() )
            
    def setupConstants( self ):
        self.dummy()
        self.MyPlayer = MyPlayer(xbmc.PLAYER_CORE_MPLAYER, function=self.myPlayerChanged)
        self.controllerAction = amt_util.setControllerAction()
        self.updateMethod = 0
        self.thumbnail = None
        self.genre = None
        
    # dummy() and self.Timer are currently used for the Player() subclass so when an onPlayback* event occurs, 
    #it calls myPlayerChanged() immediately.
    def dummy( self ):
        self.Timer = threading.Timer(60*60*60, self.dummy,() )
        self.Timer.start()
    
    # this function is used for skins like XBMC360 that have player information on screen
    def myPlayerChanged(self):
        self.controls['X Button On']['control'].setVisible( xbmc.getCondVisibility( self.controls['X Button On']['visible'] ) )
        self.controls['X Button Off']['control'].setVisible( xbmc.getCondVisibility( self.controls['X Button Off']['visible'] ) )
        self.controls['Full-Screen Visualisation Label']['control'].setVisible( xbmc.getCondVisibility( self.controls['Full-Screen Visualisation Label']['visible'] ) )
        self.controls['Full-Screen Video Label']['control'].setVisible( xbmc.getCondVisibility( self.controls['Full-Screen Video Label']['visible'] ) )
        
    def playTrailer( self, title ):
        trailer_urls = self.trailers.get_video_list( self.genre, title )
        if ( self.settings['trailer quality'] >= len( trailer_urls ) ):
            choice = len( trailer_urls ) - 1
        else:
            choice = self.settings['trailer quality']
        try:
            if ( self.settings['mode'] == 0 ):
                filename = trailer_urls[choice].replace( '//', '/' ).replace( '/', '//', 1 )
            elif ( self.settings['mode'] == 1):
                url = trailer_urls[choice].replace( '//', '/' ).replace( '/', '//', 1 )
                fetcher = cacheurl.HTTPProgressSave()
                filename = fetcher.urlretrieve( url )
            elif ( self.settings['mode'] == 2):
                url = trailer_urls[choice].replace( '//', '/' ).replace( '/', '//', 1 )
                fetcher = cacheurl.HTTPProgressSave( self.settings['save folder'] )
                filename = fetcher.urlretrieve( url )
                if ( filename ): self.saveThumbnail( filename )
            if ( filename ): self.MyPlayer.play( filename )
        except:
            xbmc.output('ERROR: playing %s' % ( title, ) )
            
    def saveThumbnail( self, filename ):
        try: 
            newfilename = '%s.tbn' % ( os.path.splitext( filename )[0], )
            if ( not os.path.isfile( newfilename ) ):
                shutil.copyfile(self.thumbnail, newfilename )
        except: pass

    def showTrailerInfo( self, title ):
        self.thumbnail, description = self.trailers.get_trailer_info( self.genre, title )
        # Trailer Thumbnail
        if ( not self.thumbnail ): self.thumbnail = os.path.join( self.imagePath, 'blank_poster.tbn' )
        self.controls['Trailer Thumbnail']['control'].setImage( self.thumbnail )
        # Trailer Title
        self.controls['Trailer Title']['control'].setLabel( title )
        # Trailer Description
        self.controls['Trailer Info']['control'].reset()
        if description:
            self.controls['Trailer Info']['control'].setText( description )

    def showTrailers( self, genre ):
        self.controls['Trailer List']['control'].reset()
        if ( genre == 'Newest' ): titles = self.trailers.get_newest_list()
        elif ( genre == 'Exclusives' ): titles = self.trailers.get_exclusives_list()
        else: titles = self.trailers.get_trailer_list( genre )
        for title in titles: # now fill the list control
            thumbnail, description = self.trailers.get_trailer_info( genre, title )
            if ( self.settings['thumbnail display'] == 2 ): thumbnail = ''
            elif ( self.settings['thumbnail display'] == 1 ): thumbnail = os.path.join( self.imagePath, 'generic-thumbnail.tbn' )
            l = xbmcgui.ListItem( title, '', thumbnail )
            self.controls['Trailer List']['control'].addItem( l )
            
    def updateDatabase( self ):
        if (self.updateMethod == 0 ):
            self.trailers.update_all()
            #self.getGenreCategories()
            #self.showTrailers( self.genre )
            self.setGenre( self. genre )
            
    def getGenreCategories( self ):
        self.controls['Genre List']['control'].reset()
        for genre in self.trailers.get_genre_list():
            thumbnail = os.path.join( self.imagePath, '%s.tbn' % ( genre, ) )
            if ( not os.path.isfile( thumbnail ) ):
                thumbnail = os.path.join( self.imagePath, 'genre-thumbnail.tbn' )
            l = xbmcgui.ListItem( genre, '',  thumbnail)
            self.controls['Genre List']['control'].addItem( l )

    def exitScript(self):
        if ( self.Timer ): self.Timer.cancel()
        self.trailers.cleanup()
        self.close()
    
    def showList( self, Genre ):
        self.controls['Genre List']['control'].setVisible( Genre )
        self.controls['Genre List']['control'].setEnabled( Genre )
        self.controls['Trailer List']['control'].setVisible( not Genre )
        self.controls['Trailer List']['control'].setEnabled( not Genre )
        ## until initial visibilty is solved just hardcode them
        #self.controls['Trailer Thumbnail']['control'].setVisible(xbmc.getCondVisibility( self.controls['Trailer Thumbnail']['visible'] ) )
        #self.controls['Trailer Title']['control'].setVisible(xbmc.getCondVisibility( self.controls['Trailer Title']['visible'] ) )
        #self.controls['Trailer Info']['control'].setVisible(xbmc.getCondVisibility( self.controls['Trailer Info']['visible'] ) )
        self.controls['Trailer Backdrop']['control'].setVisible( not Genre )
        self.controls['Trailer Thumbnail']['control'].setVisible( not Genre )
        self.controls['Trailer Title']['control'].setVisible( not Genre )
        self.controls['Trailer Info']['control'].setVisible( not Genre )
        self.controls['Trailer Info']['control'].setEnabled( not Genre )
        self.setCategoryLabel( self.genre )
        if ( Genre ): self.setFocus(self.controls['Genre List']['control'] )
        else: self.setFocus(self.controls['Trailer List']['control'] )
        
    def setGenre( self, genre ):
        self.genre = genre
        if ( genre != 'Genre' ): self.showTrailers( genre )
        self.showList( genre == 'Genre' )

    def setCategoryLabel( self, category ):
        self.controls['Category Label']['control'].setLabel( category )
            
    def setListNavigation( self, button ):
        self.controls['Trailer List']['control'].controlLeft( self.controls[button]['control'] )
        self.controls['Trailer Info']['control'].controlRight( self.controls[button]['control'] )
        
    def getTrailerInfo( self, choice ):
        title = choice.getLabel()
        self.showTrailerInfo( title )
    
    def getTrailer( self, choice ):
        title = choice.getLabel()
        self.playTrailer( title )
        
    def getTrailerGenre( self, choice ):
        self.genre = choice.getLabel()
        self.showTrailers( self.genre )
        self.setCategoryLabel( self.genre )
        self.showList( False )
    
    def changeSettings( self ):
        settings = guisettings.GUI( skin=self.skin )
        settings.doModal()
        del settings
        self.getSettings()
        #self.getGenreCategories()
        self.setGenre( self.genre )

    def onControl( self, control ):
        try:
            if ( control is self.controls['Newest Button']['control'] ):
                self.setGenre( 'Newest' )
            elif ( control is self.controls['Exclusives Button']['control'] ):
                self.setGenre( 'Exclusives' )
            elif ( control is self.controls['Genre Button']['control'] ):
                self.setGenre( 'Genre' )
            elif ( control is self.controls['Update Button']['control'] ):
                self.updateDatabase()
            elif ( control is self.controls['Settings Button']['control'] ):
                self.changeSettings()
                #settings = guisettings.GUI()
                #settings.doModal()
                #del settings
                #self.getSettings()
                #self.getGenreCategories()
                #self.setStartupCategory()
            elif ( control is self.controls['Genre List']['control'] ):
                self.getTrailerGenre( control.getSelectedItem() )
            elif ( control is self.controls['Trailer List']['control'] ):
                self.getTrailer( control.getSelectedItem() )
        except: traceback.print_exc()
            
    def onAction( self, action ):
        try:
            buttonDesc = self.controllerAction.get(action.getButtonCode(), 'n/a')
            if ( buttonDesc == 'Back Button' or buttonDesc == 'Remote Menu Button' ): self.exitScript()
            elif (buttonDesc == 'B Button' or buttonDesc == 'Remote Back Button' ):
                if ( self.genre != 'Newest' and self.genre != 'Exclusives' and self.genre != 'Genre'):
                    self.setGenre( 'Genre' )
            else:
                control = self.getFocus()
                if ( control is self.controls['Trailer List']['control'] ):
                    self.getTrailerInfo( control.getSelectedItem() )
                elif ( control is self.controls['Exclusives Button']['control'] ):
                    self.setListNavigation('Exclusives Button')
                elif ( control is self.controls['Newest Button']['control'] ):
                    self.setListNavigation('Newest Button')
                elif ( control is self.controls['Genre Button']['control'] ):
                    self.setListNavigation('Genre Button')
                elif ( control is self.controls['Search Button']['control'] ):
                    self.setListNavigation('Search Button')
                elif ( control is self.controls['Settings Button']['control'] ):
                    self.setListNavigation('Settings Button')
                elif ( control is self.controls['Update Button']['control'] ):
                    self.setListNavigation('Update Button')
        except: traceback.print_exc()



## Thanks Thor918 for this class ##
class MyPlayer(xbmc.Player):
    def  __init__(self, *args, **kwargs):
        if (kwargs.has_key('function')): 
            self.function = kwargs['function']
            xbmc.Player.__init__(self)
    
    def onPlayBackStopped(self):
        self.function()
    
    def onPlayBackEnded(self):
        self.function()
    
    def onPlayBackStarted(self):
        self.function()
    
