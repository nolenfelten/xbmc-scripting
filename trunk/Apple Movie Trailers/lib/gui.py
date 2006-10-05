'''
Main GUI for Apple Movie Trailers
'''

def createProgressDialog( __line3__ ):
    global dialog, pct
    pct = 0
    dialog = xbmcgui.DialogProgress()
    dialog.create( _( 0 ) )
    updateProgressDialog( __line3__ )

def updateProgressDialog( __line3__ ):
    global dialog, pct
    pct += 5
    dialog.update( pct, __line1__, __line2__, __line3__ )

def closeProgessDialog():
    global dialog
    dialog.close()
    
import xbmcgui, language
lang = language.Language()
_ = lang.string
__line1__       = _(50)
__line2__       = _(51)
createProgressDialog( '%s xbmc' % ( _( 52 ), ) )
import xbmc
try:
    updateProgressDialog( '%s sys' % ( _( 52 ), ) )
    import sys
    updateProgressDialog( '%s os' % ( _( 52 ), ) )
    import os
    updateProgressDialog( '%s traceback' % ( _( 52 ), ) )
    import traceback
    updateProgressDialog( '%s trailers' % ( _( 52 ), ) )
    import trailers
    updateProgressDialog( '%s threading' % ( _( 52 ), ) )
    import threading
    updateProgressDialog( '%s guibuilder' % ( _( 52 ), ) )
    import guibuilder
    updateProgressDialog( '%s guisettings' % ( _( 52 ), ) )
    import guisettings
    updateProgressDialog( '%s amt_util' % ( _( 52 ), ) )
    import amt_util
    updateProgressDialog( '%s cacheurl' % ( _( 52 ), ) )
    import cacheurl
    updateProgressDialog( '%s shutil' % ( _( 52 ), ) )
    import shutil
except:
    closeProgessDialog()
    dlg = xbmcgui.Dialog()
    ## check language 
    ##file All the required modules could not be found.
    ok = dlg.ok( _( 0 ), _( 53), _( 54 ) )

    
class GUI( xbmcgui.Window ):

    def __init__( self ):
        self.cwd = os.path.dirname( sys.modules['default'].__file__ )
        self.debug = os.path.isfile( os.path.join( self.cwd, 'debug.txt' ))
        self.getSettings()
        self.setupGUI()
        if ( not self.SUCCEEDED ): self.close()
        else:
            try:
                ## enable when ready
                self.controls['Search Button']['control'].setEnabled( False )
                self.setupVariables()
                #if ( self.checkForDB() ):
                self.getGenreCategories()
                self.setStartupCategory()
                #else:
                #    dialog = xbmcgui.Dialog()
                #    ok = dialog.ok( _( 0 ), _( 53), _( 54 ) )
            except:
                traceback.print_exc()
                self.debugWrite( 'init', False )
                self.SUCCEEDED = False
                self.exitScript()

    def getSettings( self ):
        self.debugWrite('getSettings', 2)
        self.settings = amt_util.getSettings()

    def setupGUI(self):
        self.debugWrite('setupGUI', 2)
        self.skinPath = os.path.join( self.cwd, 'skins', self.settings['skin'] )
        self.imagePath = os.path.join( self.skinPath, 'gfx' )
        if ( self.getResolution() == 0 or self.getResolution() % 2 ): skin = 'skin_16x9.xml'
        else: skin = 'skin.xml'
        if ( not os.path.isfile( os.path.join( self.skinPath, skin ) ) ): skin = 'skin.xml'
        guibuilder.GUIBuilder( self, os.path.join( self.skinPath, skin ), self.imagePath, useDescAsKey = True, 
            title = _( 0 ), line1 = __line1__, dlg = dialog, pct = pct, useLocal = True, debug = False )
        closeProgessDialog()
        if ( not self.SUCCEEDED ):
            dlg = xbmcgui.Dialog()
            dlg.ok( _( 0 ), _( 57 ), _( 58 ), os.path.join( self.skinPath, skin ))

    def setupVariables( self ):
        self.debugWrite('setupConstants', 2)
        self.trailers = trailers.Trailers()
        self.skin = self.settings['skin']
        self.display_cast = False
        self.dummy()
        self.MyPlayer = MyPlayer(xbmc.PLAYER_CORE_MPLAYER, function = self.myPlayerChanged)
        self.controllerAction = amt_util.setControllerAction()
        self.updateMethod = 0
        self.thumbnail = None
        #self.genre = None
        self.genre_id = None
        
    # dummy() and self.Timer are currently used for the Player() subclass so when an onPlayback* event occurs, 
    # it calls myPlayerChanged() immediately.
    def dummy( self ):
        self.debugWrite('dummy', 2)
        self.Timer = threading.Timer( 60*60*60, self.dummy,() )
        self.Timer.start()

    # this function is used for skins like XBMC360 that have player information on screen
    def myPlayerChanged(self):
        self.debugWrite('myPlayerChanged', 2)
        self.controls['X Button On']['control'].setVisible( xbmc.getCondVisibility( self.controls['X Button On']['visible'] ))
        self.controls['X Button Off']['control'].setVisible( xbmc.getCondVisibility( self.controls['X Button Off']['visible'] ))
        self.controls['Full-Screen Visualisation Label']['control'].setVisible( xbmc.getCondVisibility( self.controls['Full-Screen Visualisation Label']['visible'] ))
        self.controls['Full-Screen Video Label']['control'].setVisible( xbmc.getCondVisibility( self.controls['Full-Screen Video Label']['visible'] ))

    ## Remove if no DB used ##
    def checkForDB( self ):
        self.debugWrite( 'checkForDB', 2 )
        if ( os.path.isfile( os.path.join( self.cwd, 'data', 'AMT.pk' ))): return True
        else: return False

    def updateDatabase( self ):
        self.debugWrite('updateDatabase', 2)
        if (self.updateMethod == 0 ):
            self.trailers.update_all()
            self.getGenreCategories()
            self.setGenre( self.genre_id )
    
    def getGenreCategories( self ):
        self.debugWrite('getGenreCategories', 2)
        self.controls['Genre List']['control'].reset()
        for genre in self.trailers.genres[2:]:
            thumbnail = os.path.join( self.imagePath, '%s.tbn' % ( genre.title, ))
            if ( not os.path.isfile( thumbnail )):
                thumbnail = os.path.join( self.imagePath, 'generic-genre.tbn' )
            l = xbmcgui.ListItem( genre.title, '',  thumbnail )
            self.controls['Genre List']['control'].addItem( l )
            
    def showTrailers( self ):
        try:
            self.debugWrite('showTrailers', 2)
            xbmcgui.lock()
            self.controls['Trailer List']['control'].reset()
            for movie in self.trailers.genres[self.genre_id].movies: # now fill the list control
                if ( self.settings['thumbnail display'] == 2 ): thumbnail = ''
                elif ( self.settings['thumbnail display'] == 1 ): thumbnail = os.path.join( self.imagePath, 'generic-thumbnail.tbn' )
                else: thumbnail = movie.thumbnail
                l = xbmcgui.ListItem( movie.title, '', thumbnail )
                self.controls['Trailer List']['control'].addItem( l )
            self.setSelection( 0 )
            self.calcScrollbarVisibilty()
            self.calcCastScrollbarVisibilty()
        finally:
            xbmcgui.unlock()

    def calcScrollbarVisibilty( self ):
        if ( self.controls['Trailer List']['special'] ):
            visible = ( self.controls['Trailer List']['control'].size() > self.controls['Trailer List']['special'] )
            self.showScrollbar( visible, 'Trailer List' )
        
    def calcCastScrollbarVisibilty( self ):
        if ( self.controls['Trailer Cast']['special'] ):
            visible = (( self.controls['Trailer Cast']['control'].size() > self.controls['Trailer Cast']['special'] ) and self.display_cast )
            self.showScrollbar( visible, 'Trailer Cast' )
        
    def setScrollbarIndicator( self, list_control ):
        if ( self.controls[list_control]['special'] ):
            offset = float( self.controls['%s Scrollbar Middle' % ( list_control, )]['height'] - self.controls['%s Scrollbar Position Indicator' % ( list_control, )]['height'] ) / float( self.controls[list_control]['control'].size() - 1 )
            posy = int( self.controls['%s Scrollbar Middle' % ( list_control, )]['posy'] + ( offset * self.controls[list_control]['control'].getSelectedPosition() ))
            self.controls['%s Scrollbar Position Indicator' % ( list_control, )]['control'].setPosition( self.controls['%s Scrollbar Position Indicator' % ( list_control, )]['posx'], posy )

    def setSelection( self, pos ):
        self.debugWrite('setSelection', 2)
        self.controls['Trailer List']['control'].selectItem( pos )
        self.showTrailerInfo()
        
    def setStartupCategory( self ):
        self.debugWrite('setStartupCategory', 2)
        startup = amt_util.setStartupCategoryActual()
        self.setGenre( self.settings['startup category id'] )
        self.setListNavigation( '%s Button' % ( startup[self.settings['startup category']], ))

    def setGenre( self, genre_id ):
        self.debugWrite('setGenre', 2)
        self.genre_id = genre_id
        self.showScrollbar( False, 'Trailer List' )
        if ( genre_id != -1 ): self.showTrailers()
        self.showControls( genre_id == -1 )

    def showScrollbar( self, visible, list_control ):
        self.controls['%s Scrollbar Up Arrow' % ( list_control, )]['control'].setVisible( visible )
        self.controls['%s Scrollbar Middle' % ( list_control, )]['control'].setVisible( visible )
        self.controls['%s Scrollbar Down Arrow' % ( list_control, )]['control'].setVisible( visible )
        self.controls['%s Scrollbar Position Indicator' % ( list_control, )]['control'].setVisible( visible )
    
    def setListNavigation( self, button ):
        self.debugWrite('setListNavigation', 2)
        self.controls['Trailer List']['control'].controlLeft( self.controls[button]['control'] )
        self.controls['Trailer Cast']['control'].controlRight( self.controls[button]['control'] )
        
    def showControls( self, genre ):
        self.debugWrite('showControls', 2)
        self.controls['Genre List']['control'].setVisible( genre )
        self.controls['Genre List']['control'].setEnabled( genre )
        self.controls['Trailer List']['control'].setVisible( not genre )
        self.controls['Trailer List']['control'].setEnabled( not genre )
        self.controls['Trailer Backdrop']['control'].setVisible( not genre )
        self.controls['Trailer Thumbnail']['control'].setVisible( not genre )
        self.controls['Trailer Title']['control'].setVisible( not genre )
        self.showPlotCastControls( genre )
        self.setCategoryLabel()
        if ( genre ): self.setFocus(self.controls['Genre List']['control'] )
        else: self.setFocus(self.controls['Trailer List']['control'] )

    def showPlotCastControls( self, genre ):
        self.debugWrite('showPlotCastControls', 2)
        self.controls['Plot Button']['control'].setVisible( self.display_cast and not genre )
        self.controls['Plot Button']['control'].setEnabled( self.display_cast and not genre )
        self.controls['Cast Button']['control'].setVisible( not self.display_cast and not genre )
        self.controls['Cast Button']['control'].setEnabled( not self.display_cast and not genre )
        self.controls['Trailer Plot']['control'].setVisible( not self.display_cast and not genre )
        self.controls['Trailer Plot']['control'].setEnabled( not self.display_cast and not genre )
        self.controls['Trailer Cast']['control'].setVisible( self.display_cast and not genre )
        self.controls['Trailer Cast']['control'].setEnabled( self.display_cast and not genre )
        
    def togglePlotCast( self ):
        self.debugWrite('togglePlotCast', 2)
        self.display_cast = not self.display_cast
        self.showPlotCastControls( False )
        if ( self.display_cast ): self.setFocus( self.controls['Plot Button']['control'] )
        else: self.setFocus( self.controls['Cast Button']['control'] )
        self.calcCastScrollbarVisibilty()

    def setCategoryLabel( self ):
        self.debugWrite('setCategoryLabel', 2)
        if ( self.genre_id == 1 ):
            category = _(200)
        elif ( self.genre_id == 0 ):
            category = _(201)
        elif ( self.genre_id == -1 ):
            category = _(202)
        else:
            category = self.trailers.genres[self.genre_id].title
        self.controls['Category Label']['control'].setLabel( category )
            
    def showTrailerInfo( self ):
        try:
            self.debugWrite('showTrailerInfo', 2)
            xbmcgui.lock()
            trailer = self.controls['Trailer List']['control'].getSelectedPosition()
            self.thumbnail = self.trailers.genres[self.genre_id].movies[trailer].thumbnail
            if ( not self.thumbnail ): self.thumbnail = os.path.join( self.imagePath, 'blank_poster.tbn' )
            self.controls['Trailer Thumbnail']['control'].setImage( self.thumbnail )
            self.controls['Trailer Title']['control'].setLabel( self.trailers.genres[self.genre_id].movies[trailer].title )
            plot = self.trailers.genres[self.genre_id].movies[trailer].plot
            self.controls['Trailer Plot']['control'].reset()
            if ( plot ):
                self.controls['Trailer Plot']['control'].setText( plot )
            self.controls['Trailer Cast']['control'].reset()
            cast = self.trailers.genres[self.genre_id].movies[trailer].cast
            ## Test code ##
            cast = ['Angelina Jolee', 'Jessica Alba', 'Chuck Norris', 'Arnold Swarzenegger', 'Hillary Duff', 'William Shatner']
            if ( cast ):
                for actor in cast:
                    thumbnail = os.path.join( self.imagePath, 'generic-actor.tbn' )
                    l = xbmcgui.ListItem( actor, '', thumbnail )
                    self.controls['Trailer Cast']['control'].addItem( l )
            self.setScrollbarIndicator('Trailer List')

        finally:
            xbmcgui.unlock()

    def getTrailerGenre( self ):
        self.debugWrite('getTrailerGenre', 2)
        self.genre_id = self.controls['Genre List']['control'].getSelectedPosition() + 2
        self.showTrailers()
        self.setCategoryLabel()
        self.showControls( False )

    def playTrailer( self ):
        self.debugWrite('PlayTrailer', 2)
        trailer = self.controls['Trailer List']['control'].getSelectedPosition()
        trailer_urls = self.trailers.genres[self.genre_id].movies[trailer].trailer_urls
        if ( self.settings['trailer quality'] >= len( trailer_urls )):
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
            self.debugWrite( 'playTrailer', False, ['ERROR: Trying to play %s'], [( title )] )
    
    def saveThumbnail( self, filename ):
        self.debugWrite( 'saveThumbnail', 2 )
        try: 
            newfilename = '%s.tbn' % ( os.path.splitext( filename )[0], )
            if ( not os.path.isfile( newfilename ) ):
                shutil.copyfile(self.thumbnail, newfilename )
        except: pass
  
    def changeSettings( self ):
        self.debugWrite('changeSettings', 2)
        thumbnail_display = self.settings['thumbnail display']
        settings = guisettings.GUI( skin=self.skin, language=_ )
        settings.doModal()
        del settings
        self.getSettings()
        if ( thumbnail_display != self.settings['thumbnail display'] ):
            self.setGenre( self.genre_id )
        
    def exitScript( self ):
        self.debugWrite( 'exitScript', 2 )
        if ( self.Timer ): self.Timer.cancel()
        self.close()

    def onControl( self, control ):
        self.debugWrite( 'onControl', 2 )
        try:
            if ( control is self.controls['Newest Button']['control'] ):
                self.setGenre( 1 )
            elif ( control is self.controls['Exclusives Button']['control'] ):
                self.setGenre( 0 )
            elif ( control is self.controls['Genre Button']['control'] ):
                self.setGenre( -1 )
            elif ( control is self.controls['Update Button']['control'] ):
                self.updateDatabase()
            elif ( control is self.controls['Settings Button']['control'] ):
                self.changeSettings()
            elif ( control is self.controls['Plot Button']['control'] or control is self.controls['Cast Button']['control'] ):
                self.togglePlotCast()
            elif ( control is self.controls['Genre List']['control'] ):
                self.getTrailerGenre()
            elif ( control is self.controls['Trailer List']['control'] ):
                self.playTrailer()
        except: traceback.print_exc()

    def onAction( self, action ):
        try:
            buttonDesc = self.controllerAction.get( action.getButtonCode(), 'n/a' )
            if ( buttonDesc == 'Back Button' or buttonDesc == 'Remote Menu Button' ): self.exitScript()
            elif (buttonDesc == 'B Button' or buttonDesc == 'Remote Back Button' ):
                if ( self.genre_id >= 2):
                    self.setGenre( -1 )
            else:
                control = self.getFocus()
                if ( control is self.controls['Trailer List']['control'] ):
                    self.showTrailerInfo()
                elif ( control is self.controls['Trailer Cast']['control'] ):
                    self.setScrollbarIndicator( 'Trailer Cast' )
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

    def debugWrite( self, function, action, lines=[], values=[] ):
        if ( self.debug ):
            Action = ( 'Failed', 'Succeeded', 'Started' )
            Highlight = ( '__', '__', '<<<<< ', '__', '__', ' >>>>>' )
            xbmc.output( '%s%s%s : (%s)\n' % ( Highlight[action], function, Highlight[action + 3], Action[action] ) )
            try:
                for cnt, line in enumerate( lines ):
                    fLine = '%s\n' % ( line, )
                    xbmc.output( fLine % values[cnt] )
            except: pass



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
    







