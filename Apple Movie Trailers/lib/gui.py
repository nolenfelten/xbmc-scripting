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
#createProgressDialog( '%s xbmc' % ( _( 52 ), ) )
import xbmc
if 1:
#    updateProgressDialog( '%s sys' % ( _( 52 ), ) )
    import sys
#    updateProgressDialog( '%s os' % ( _( 52 ), ) )
    import os
#    updateProgressDialog( '%s traceback' % ( _( 52 ), ) )
    import traceback
#    updateProgressDialog( '%s trailers' % ( _( 52 ), ) )
    import trailers
#    updateProgressDialog( '%s threading' % ( _( 52 ), ) )
    import threading
#    updateProgressDialog( '%s guibuilder' % ( _( 52 ), ) )
    import guibuilder
#    updateProgressDialog( '%s guisettings' % ( _( 52 ), ) )
    import guisettings
#    updateProgressDialog( '%s amt_util' % ( _( 52 ), ) )
    import amt_util
#    updateProgressDialog( '%s cacheurl' % ( _( 52 ), ) )
    import cacheurl
#    updateProgressDialog( '%s shutil' % ( _( 52 ), ) )
    import shutil
#    try:
        #t = trailers.Trailers()
        #print 't = trailers.Trailers()'
    #except:
    #    try:
    #t = trailers.Trailers
    #print 't = trailers.Trailers'
    #    except:
    #        print 'neither'
    #        raise

#except:
    #print 'error importing'
    #closeProgessDialog()

class GUI( xbmcgui.Window ):
    
    def __init__( self ):
        self.cwd = os.path.dirname( sys.modules['default'].__file__ )
        self.debug = os.path.isfile( os.path.join( self.cwd, 'debug.txt' ))
        self.getSettings()
        self.skin = self.settings['skin']
        self.setupGUI()
        if ( not self.SUCCEEDED ): self.close()
        else:
            try:
                #closeProgessDialog()
                ## enable when ready
                self.controls['Search Button']['control'].setEnabled( False )
                self.setupConstants()
                self.trailers = trailers.Trailers
                if ( self.checkForDB() ):
                    self.getGenreCategories()
                    self.setStartupCategory()
                else:
                    dialog = xbmcgui.Dialog()
                    ok = dialog.ok( _( 0 ), _( 53), _( 54 ) )
            except:
                traceback.print_exc()
                self.debugWrite( 'init', False )
                self.exitScript()

    def checkForDB( self ):
        self.debugWrite( 'checkForDB', 2 )
        if ( os.path.isfile( os.path.join( self.cwd, 'data', 'AMT.pk' ) ) ): return True
        else: return False

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

    
    # dummy() and self.Timer are currently used for the Player() subclass so when an onPlayback* event occurs, 
    # it calls myPlayerChanged() immediately.
    def dummy( self ):
        self.debugWrite('dummy', 2)
        self.Timer = threading.Timer( 60*60*60, self.dummy,() )
        self.Timer.start()

    def editSettings( self ):
        self.debugWrite('editSettings', 2)
        settings = guisettings.GUI( skin=self.skin, language=_ )
        settings.doModal()
        del settings
        self.getSettings()
        self.setGenre( self.genre, self.genre_id )
        #self.getTrailerInfo( self.controls['Trailer List']['control'].getSelectedItem() )
        
    def exitScript( self ):
        self.debugWrite( 'exitScript', 2 )
        if ( self.Timer ): self.Timer.cancel()
        ##self.trailers.cleanup()
        self.close()
    
    def getGenreCategories( self ):
        self.debugWrite('getGenreCategories', 2)
        self.controls['Genre List']['control'].reset()
        for genre in self.trailers.genres[2:]:
            thumbnail = os.path.join( self.imagePath, '%s.tbn' % ( genre, ) )
            if ( not os.path.isfile( thumbnail ) ):
                thumbnail = os.path.join( self.imagePath, 'genre-thumbnail.tbn' )
            l = xbmcgui.ListItem( genre, '',  thumbnail)
            self.controls['Genre List']['control'].addItem( l )

    def getSettings( self ):
        self.debugWrite('getSettings', 2)
        self.settings = amt_util.getSettings()

    def getTrailer( self, choice ):
        self.debugWrite('getTrailer', 2)
        title = choice.getLabel()
        id = choice.getSelectedPosition()
        self.playTrailer( title, id )
    
    def getTrailerGenre( self, choice ):
        self.debugWrite('getTrailerGenre', 2)
        self.genre = choice.getLabel()
        self.genre_id = choice.getSelectedPosition() + 2
        self.showTrailers()
        self.setCategoryLabel()
        self.showControls( False )

    def getTrailerInfo( self, choice ):
        self.debugWrite('getTrailerInfo', 2)
        title = choice.getLabel()
        id = choice.getSelectedPosition()
        self.showTrailerInfo( title, id )
    
    # this function is used for skins like XBMC360 that have player information on screen
    def myPlayerChanged(self):
        self.debugWrite('myPlayerChanged', 2)
        self.controls['X Button On']['control'].setVisible( xbmc.getCondVisibility( self.controls['X Button On']['visible'] ) )
        self.controls['X Button Off']['control'].setVisible( xbmc.getCondVisibility( self.controls['X Button Off']['visible'] ) )
        self.controls['Full-Screen Visualisation Label']['control'].setVisible( xbmc.getCondVisibility( self.controls['Full-Screen Visualisation Label']['visible'] ) )
        self.controls['Full-Screen Video Label']['control'].setVisible( xbmc.getCondVisibility( self.controls['Full-Screen Video Label']['visible'] ) )
        ####trailers.genres[0].movie[2].trailers_urls[2] would equal 640w
        #####genres[0] is 'Exclusives', genres[1] is 'Newest', and genres[2:] is sorted alphabetically
        
    def playTrailer( self, title, id ):
        self.debugWrite('PlayTrailer', 2)
        trailer_urls = self.trailers.genres[self.genre_id].movie[id].trailer_urls
        print trailer_urls
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
            self.debugWrite( 'playTrailer', False, ['ERROR: Trying to play %s'], [( title )] )
    
    def saveThumbnail( self, filename ):
        self.debugWrite( 'saveThumbnail', 2 )
        try: 
            newfilename = '%s.tbn' % ( os.path.splitext( filename )[0], )
            if ( not os.path.isfile( newfilename ) ):
                shutil.copyfile(self.thumbnail, newfilename )
        except: pass

    def setCategoryLabel( self ):
        self.debugWrite('setCategoryLabel', 2)
        if ( self.genre == 'Newest' ):
            category = _(200)
        elif ( self.genre == 'Exclusives' ):
            category = _(201)
        elif ( self.genre == 'Genre' ):
            category = _(202)
        else:
            category = self.genre
        self.controls['Category Label']['control'].setLabel( category )
            
    def setGenre( self, genre, genre_id ):
        self.debugWrite('setGenre', 2)
        self.genre = genre
        self.genre_id = genre_id
        self.showScrollbar( False, 'Trailer List' )
        if ( genre != 'Genre' ): self.showTrailers()
        self.showControls( genre == 'Genre' )

    def setListNavigation( self, button ):
        self.debugWrite('setListNavigation', 2)
        self.controls['Trailer List']['control'].controlLeft( self.controls[button]['control'] )
#        self.controls['Trailer Plot']['control'].controlRight( self.controls[button]['control'] )
        self.controls['Trailer Cast']['control'].controlRight( self.controls[button]['control'] )
        
    def setSelection( self, pos ):
        self.debugWrite('setSelection', 2)
        self.controls['Trailer List']['control'].selectItem( pos )
        self.getTrailerInfo( self.controls['Trailer List']['control'].getSelectedItem() )

    def setStartupCategory( self ):
        self.debugWrite('setStartupCategory', 2)
        startup = amt_util.setStartupCategoryActual()
        self.setGenre( startup[self.settings['startup category']], self.settings['startup category id'] )
        self.setListNavigation( '%s Button' % ( startup[self.settings['startup category']], ) )
        #if ( startup[self.settings['startup category']] != 'Genre' ):
        #    self.getTrailerInfo( self.controls['Trailer List']['control'].getSelectedItem() )

    def setupConstants( self ):
        self.debugWrite('setupConstants', 2)
        self.display_cast = False
        self.dummy()
        self.MyPlayer = MyPlayer(xbmc.PLAYER_CORE_MPLAYER, function=self.myPlayerChanged)
        self.controllerAction = amt_util.setControllerAction()
        self.updateMethod = 0
        self.thumbnail = None
        self.genre = None
        self.genre_id = None
        
    def setupGUI(self):
        self.debugWrite('setupGUI', 2)
        skinPath = os.path.join( self.cwd, 'skins' )
        self.skinPath = os.path.join( skinPath, self.settings['skin'] )
        self.imagePath = os.path.join( self.skinPath, 'gfx' )
        res = self.getResolution()
        if ( res == 0 or res % 2 ): skin = 'skin_16x9.xml'
        else: skin = 'skin.xml'
        if ( not os.path.isfile( os.path.join( self.skinPath, skin ) ) ): skin = 'skin.xml'
        guibuilder.GUIBuilder( self, os.path.join( self.skinPath, skin ), self.imagePath, useDescAsKey=True, 
            title=_( 0 ), line1=__line1__, dlg=None, pct=0, useLocal=True, debug=False )
        #closeProgessDialog()
        if ( not self.SUCCEEDED ):
            dlg = xbmcgui.Dialog()
            dlg.ok(_( 0 ), _( 57 ), _( 58 ), os.path.join( self.skinPath, skin ) )

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
        

    def showTrailerInfo( self, title, id ):
        try:
        ####trailers.genres[0].movie[2].trailers_urls[2] would equal 640w
        #####genres[0] is 'Exclusives', genres[1] is 'Newest', and genres[2:] is sorted alphabetically

            #xbmcgui.lock()
            self.debugWrite('showTrailerInfo', 2)
            self.thumbnail = self.trailers.genres[self.genre_id].movie[id].thumbnail#get_trailer_info( self.genre, title )
            plot = self.trailers.genres[self.genre_id].movie[id].plot
            cast = self.trailers.genres[self.genre_id].movie[id].cast
            ## Test code ##
            cast = ['Angelina Jolee', 'Jessica Alba', 'Chuck Norris', 'Arnold Swarzenegger', 'Hillary Duff', 'William Shatner']
            # Trailer Thumbnail
            if ( not self.thumbnail ): self.thumbnail = os.path.join( self.imagePath, 'blank_poster.tbn' )
            self.controls['Trailer Thumbnail']['control'].setImage( self.thumbnail )
            # Trailer Title
            self.controls['Trailer Title']['control'].setLabel( title )
            # Trailer Description
            self.controls['Trailer Plot']['control'].reset()
            if ( plot ):
                self.controls['Trailer Plot']['control'].setText( plot )
            # Trailer Cast
            self.controls['Trailer Cast']['control'].reset()
            if ( cast ):
                for actor in cast:
                    thumbnail = os.path.join( self.imagePath, 'generic-actor.tbn' )
                    l = xbmcgui.ListItem( actor, '', thumbnail )
                    self.controls['Trailer Cast']['control'].addItem( l )
            self.setScrollbarIndicator('Trailer List')

        finally:
            pass#xbmcgui.unlock()

    def showTrailers( self ):
        try:
            self.debugWrite('showTrailers', 2)
            #xbmcgui.lock()
            self.controls['Trailer List']['control'].reset()
                    ####trailers.genres[0].movie[2].trailers_urls[2] would equal 640w
        #####genres[0] is 'Exclusives', genres[1] is 'Newest', and genres[2:] is sorted alphabetically

            titles = self.trailers.genres[self.genre_id].movies
            #if ( genre == 'Newest' ): titles = self.trailers.genres[self.genre_id]
            #elif ( genre == 'Exclusives' ): titles = self.trailers.get_exclusives_list()
            #else: titles = self.trailers.get_trailer_list( genre )
            for title in titles: # now fill the list control
                thumbnail = title.thumbnail#get_trailer_info( self.genre, title )
                plot = title.plot
                cast = title.cast
                if ( self.settings['thumbnail display'] == 2 ): thumbnail = ''
                elif ( self.settings['thumbnail display'] == 1 ): thumbnail = os.path.join( self.imagePath, 'generic-thumbnail.tbn' )
                l = xbmcgui.ListItem( title, '', thumbnail )
                self.controls['Trailer List']['control'].addItem( l )
            self.setSelection( 0 )
            self.calcScrollbarVisibilty()
        finally:
            pass#xbmcgui.unlock()
        
    def calcScrollbarVisibilty( self ):
        if ( self.controls['Trailer List']['special'] ):
            visible = ( self.controls['Trailer List']['control'].size() > self.controls['Trailer List']['special'] )
            self.showScrollbar( visible, 'Trailer List' )
        if ( self.controls['Trailer Cast']['special'] ):
            visible = (( self.controls['Trailer Cast']['control'].size() > self.controls['Trailer Cast']['special'] ))# and self.display_cast )
            self.showScrollbar( visible, 'Trailer Cast' )
        
    def setScrollbarIndicator( self, list_control ):
        if ( self.controls[list_control]['special'] ):
            offset = float( self.controls['%s Scrollbar Middle' % ( list_control, )]['height'] - self.controls['%s Scrollbar Position Indicator' % ( list_control, )]['height'] ) / float( self.controls[list_control]['control'].size() - 1 )
            posy = int( self.controls['%s Scrollbar Middle' % ( list_control, )]['posy'] + ( offset * self.controls[list_control]['control'].getSelectedPosition() ))
            self.controls['%s Scrollbar Position Indicator' % ( list_control, )]['control'].setPosition( self.controls['%s Scrollbar Position Indicator' % ( list_control, )]['posx'], posy )
    
    def showScrollbar( self, visible, list_control ):
        self.controls['%s Scrollbar Up Arrow' % ( list_control, )]['control'].setVisible( visible )
        self.controls['%s Scrollbar Middle' % ( list_control, )]['control'].setVisible( visible )
        self.controls['%s Scrollbar Down Arrow' % ( list_control, )]['control'].setVisible( visible )
        self.controls['%s Scrollbar Position Indicator' % ( list_control, )]['control'].setVisible( visible )
        
    def togglePlotCast( self ):
        self.debugWrite('togglePlotCast', 2)
        self.display_cast = not self.display_cast
        self.showPlotCastControls( False )
        if ( self.display_cast ): self.setFocus( self.controls['Plot Button']['control'] )
        else: self.setFocus( self.controls['Cast Button']['control'] )
        
    def updateDatabase( self ):
        self.debugWrite('updateDatabase', 2)
        if (self.updateMethod == 0 ):
            self.trailers.update_all()
            self.getGenreCategories()
            self.setGenre( self.genre, self.genre_id )

    def onControl( self, control ):
        self.debugWrite( 'onControl', 2 )
        try:
            if ( control is self.controls['Newest Button']['control'] ):
                self.setGenre( 'Newest', 1 )
            elif ( control is self.controls['Exclusives Button']['control'] ):
                self.setGenre( 'Exclusives', 0 )
            elif ( control is self.controls['Genre Button']['control'] ):
                self.setGenre( 'Genre', -1 )
            elif ( control is self.controls['Update Button']['control'] ):
                self.updateDatabase()
            elif ( control is self.controls['Settings Button']['control'] ):
                self.editSettings()
            elif ( control is self.controls['Plot Button']['control'] or control is self.controls['Cast Button']['control'] ):
                self.togglePlotCast()
            elif ( control is self.controls['Genre List']['control'] ):
                self.getTrailerGenre( control.getSelectedItem() )
            elif ( control is self.controls['Trailer List']['control'] ):
                self.getTrailer( control.getSelectedItem() )
        except: traceback.print_exc()

    def onAction( self, action ):
        try:
            buttonDesc = self.controllerAction.get( action.getButtonCode(), 'n/a' )
            if ( buttonDesc == 'Back Button' or buttonDesc == 'Remote Menu Button' ): self.exitScript()
            elif (buttonDesc == 'B Button' or buttonDesc == 'Remote Back Button' ):
                if ( self.genre != 'Newest' and self.genre != 'Exclusives' and self.genre != 'Genre'):
                    self.setGenre( 'Genre', -1 )
            else:
                control = self.getFocus()
                if ( control is self.controls['Trailer List']['control'] ):
                    self.getTrailerInfo( control.getSelectedItem() )
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
    
