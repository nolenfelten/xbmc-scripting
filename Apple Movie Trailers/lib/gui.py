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
__line1__ = _(50)
__line2__ = _(51)
try:
    createProgressDialog( '%s xbmc' % ( _( 52 ), ))
    import xbmc
    updateProgressDialog( '%s sys' % ( _( 52 ), ))
    import sys
    updateProgressDialog( '%s os' % ( _( 52 ), ))
    import os
    updateProgressDialog( '%s traceback' % ( _( 52 ), ))
    import traceback
    updateProgressDialog( '%s trailers' % ( _( 52 ), ))
    import trailers
    updateProgressDialog( '%s threading' % ( _( 52 ), ))
    import threading
    updateProgressDialog( '%s guibuilder' % ( _( 52 ), ))
    import guibuilder
    updateProgressDialog( '%s guisettings' % ( _( 52 ), ))
    import guisettings
    updateProgressDialog( '%s amt_util' % ( _( 52 ), ))
    import amt_util
    updateProgressDialog( '%s cacheurl' % ( _( 52 ), ))
    import cacheurl
    updateProgressDialog( '%s shutil' % ( _( 52 ), ))
    import shutil
except:
    closeProgessDialog()
    dlg = xbmcgui.Dialog()
    ok = dlg.ok( _( 0 ), _( 81 ) )

    
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
        self.settings = amt_util.Settings()

    def setupGUI(self):
        self.debugWrite('setupGUI', 2)
        self.skin_path = os.path.join( self.cwd, 'skins', self.settings.skin )
        self.image_path = os.path.join( self.skin_path, 'gfx' )
        if ( self.getResolution() == 0 or self.getResolution() % 2 ): skin = 'skin_16x9.xml'
        else: skin = 'skin.xml'
        if ( not os.path.isfile( os.path.join( self.skin_path, skin ) ) ): skin = 'skin.xml'
        guibuilder.GUIBuilder( self, os.path.join( self.skin_path, skin ), self.image_path, useDescAsKey = True, 
            title = _( 0 ), line1 = __line1__, dlg = dialog, pct = pct, useLocal = True, debug = False )
        closeProgessDialog()
        if ( not self.SUCCEEDED ):
            dlg = xbmcgui.Dialog()
            dlg.ok( _( 0 ), _( 57 ), _( 58 ), os.path.join( self.skin_path, skin ))

    def setupVariables( self ):
        self.debugWrite('setupConstants', 2)
        self.trailers = trailers.Trailers()
        self.skin = self.settings.skin
        self.display_cast = False
        self.dummy()
        self.MyPlayer = MyPlayer(xbmc.PLAYER_CORE_MPLAYER, function = self.myPlayerChanged)
        self.controller_action = amt_util.setControllerAction()
        self.update_method = 0
        self.poster = None
        self.genre_id = None
        self.currently_playing_movie = -1
        self.currently_playing_genre = -1
        self.context_menu = False
        
    # dummy() and self.Timer are currently used for the Player() subclass so when an onPlayback* event occurs, 
    # it calls myPlayerChanged() immediately.
    def dummy( self ):
        self.debugWrite('dummy', 2)
        self.Timer = threading.Timer( 60*60*60, self.dummy,() )
        self.Timer.start()

    # this function is used for skins like XBMC360 that have player information on screen
    def myPlayerChanged( self, event ):
        self.debugWrite('myPlayerChanged', 2)
        self.controls['X Button On']['control'].setVisible( xbmc.getCondVisibility( self.controls['X Button On']['visible'] ))
        self.controls['X Button Off']['control'].setVisible( xbmc.getCondVisibility( self.controls['X Button Off']['visible'] ))
        self.controls['Full-Screen Visualisation Label']['control'].setVisible( xbmc.getCondVisibility( self.controls['Full-Screen Visualisation Label']['visible'] ))
        self.controls['Full-Screen Video Label']['control'].setVisible( xbmc.getCondVisibility( self.controls['Full-Screen Video Label']['visible'] ))
        if ( event == 1 and self.currently_playing_movie >= 0 ):
            self.markAsWatched( True, self.currently_playing_movie, self.currently_playing_genre_id )
        #elif ( event == 2 ):
        #    self.currently_playing_movie = -1
        #    self.currently_playing_genre_id = -1

    ## Remove if no DB used ##
    def checkForDB( self ):
        self.debugWrite( 'checkForDB', 2 )
        if ( os.path.isfile( os.path.join( self.cwd, 'data', 'AMT.pk' ))): return True
        else: return False

    def updateDatabase( self ):
        self.debugWrite('updateDatabase', 2)
        if (self.update_method == 0 ):
            self.trailers.update_all()
            self.getGenreCategories()
            self.setGenre( self.genre_id )
    
    def getGenreCategories( self ):
        self.debugWrite('getGenreCategories', 2)
        self.controls['Genre List']['control'].reset()
        for genre in self.trailers.genres[2:]:
            thumbnail = os.path.join( self.image_path, '%s.tbn' % ( genre.title, ))
            if ( not os.path.isfile( thumbnail )):
                thumbnail = os.path.join( self.image_path, 'generic-genre.tbn' )
            l = xbmcgui.ListItem( genre.title, '',  thumbnail )
            self.controls['Genre List']['control'].addItem( l )
            
    def showTrailers( self, choice = 0 ):
        try:
            self.debugWrite('showTrailers', 2)
            xbmcgui.lock()
            self.controls['Trailer List']['control'].reset()
            #movie_quality = 'LMH'
            for movie in self.trailers.genres[self.genre_id].movies: # now fill the list control
                if ( self.settings.thumbnail_display == 1 ): thumbnail = os.path.join( self.image_path, 'generic-trailer.tbn' )
                elif ( self.settings.thumbnail_display == 0 ): thumbnail = movie.thumbnail
                else: thumbnail = ''
                #choices = movie_quality[:len( movie.trailer_urls )]
                if ( movie.favorite ): favorite = '*'
                else: favorite = ''
                l = xbmcgui.ListItem( '%s%s' % ( favorite, movie.title, ), '', thumbnail )
                self.controls['Trailer List']['control'].addItem( l )
            self.setSelection( 'Trailer List', choice )
            self.calcScrollbarVisibilty('Trailer List')
            #self.calcScrollbarVisibilty('Trailer Cast')
        finally:
            xbmcgui.unlock()

    def calcScrollbarVisibilty( self, list_control ):
        if ( self.controls[list_control]['special'] ):
            visible = ( self.controls[list_control]['control'].size() > self.controls[list_control]['special'] )
            if ( list_control == 'Trailer Cast' and visible ): visible = (self.display_cast and self.genre_id != -1 )
            self.showScrollbar( visible, list_control )
        
    def setScrollbarIndicator( self, list_control ):
        if ( self.controls[list_control]['special'] ):
            offset = float( self.controls['%s Scrollbar Middle' % ( list_control, )]['height'] - self.controls['%s Scrollbar Position Indicator' % ( list_control, )]['height'] ) / float( self.controls[list_control]['control'].size() - 1 )
            posy = int( self.controls['%s Scrollbar Middle' % ( list_control, )]['posy'] + ( offset * self.controls[list_control]['control'].getSelectedPosition() ))
            self.controls['%s Scrollbar Position Indicator' % ( list_control, )]['control'].setPosition( self.controls['%s Scrollbar Position Indicator' % ( list_control, )]['posx'], posy )

    def setSelection( self, list_control, pos ):
        self.debugWrite('setSelection', 2)
        self.controls[list_control]['control'].selectItem( pos )
        if ( list_control == 'Trailer List' ): self.showTrailerInfo()
        else: self.setScrollbarIndicator( list_control )

    def pageIndicator( self, list_control, page ):
        self.debugWrite('pageIndicator', 2)
        current_pos = self.controls[list_control]['control'].getSelectedPosition()
        total_items = self.controls[list_control]['control'].size()
        items_per_page = self.controls[list_control]['special']
        current_pos += page * items_per_page
        if ( current_pos < 0 ): current_pos = 0
        elif ( current_pos >= total_items ): current_pos = total_items - 1
        self.setSelection( list_control, current_pos )

    def setStartupCategory( self ):
        self.debugWrite('setStartupCategory', 2)
        startup = amt_util.setStartupCategoryActual()
        self.setGenre( self.settings.startup_category_id )
        self.setControlNavigation( '%s Button' % ( startup[self.settings.startup_category], ))

    def setGenre( self, genre_id ):
        self.debugWrite('setGenre', 2)
        self.genre_id = genre_id
        self.showScrollbar( False, 'Trailer List' )
        self.showControls( genre_id == -1 )
        if ( genre_id != -1 ): self.showTrailers()

    def showScrollbar( self, visible, list_control ):
        self.controls['%s Scrollbar Up Arrow' % ( list_control, )]['control'].setVisible( visible )
        self.controls['%s Scrollbar Middle' % ( list_control, )]['control'].setVisible( visible )
        self.controls['%s Scrollbar Down Arrow' % ( list_control, )]['control'].setVisible( visible )
        self.controls['%s Scrollbar Position Indicator' % ( list_control, )]['control'].setVisible( visible )
    
    def setControlNavigation( self, button ):
        self.debugWrite('setControlNavigation', 2)
        self.controls['Trailer List']['control'].controlLeft( self.controls[button]['control'] )
        self.controls['Trailer Cast Scrollbar Position Indicator']['control'].controlRight( self.controls[button]['control'] )
        
    def showControls( self, genre ):
        self.debugWrite('showControls', 2)
        self.controls['Genre List']['control'].setVisible( genre )
        self.controls['Genre List']['control'].setEnabled( genre )
        self.controls['Trailer List']['control'].setVisible( not genre )
        self.controls['Trailer List']['control'].setEnabled( not genre )
        self.controls['Trailer Backdrop']['control'].setVisible( not genre )
        self.controls['Trailer Poster']['control'].setVisible( not genre )
        self.controls['Trailer Watched Overlay']['control'].setVisible( not genre )
        self.controls['Trailer Favorite Overlay']['control'].setVisible( not genre )
        self.controls['Trailer Title']['control'].setVisible( not genre )
        self.showPlotCastControls( genre )
        self.setCategoryLabel()
        if ( genre ): self.setFocus( self.controls['Genre List']['control'] )
        else: self.setFocus( self.controls['Trailer List']['control'] )

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
        self.calcScrollbarVisibilty('Trailer Cast')

    def togglePlotCast( self ):
        self.debugWrite('togglePlotCast', 2)
        self.display_cast = not self.display_cast
        self.showPlotCastControls( False )
        if ( self.display_cast ): self.setFocus( self.controls['Plot Button']['control'] )
        else: self.setFocus( self.controls['Cast Button']['control'] )
        self.calcScrollbarVisibilty('Trailer Cast')

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
            self.poster = self.trailers.genres[self.genre_id].movies[trailer].poster
            if ( self.poster == '' ): self.poster = os.path.join( self.image_path, 'blank_poster.tbn' )
            self.controls['Trailer Poster']['control'].setImage( self.poster )
            self.controls['Trailer Title']['control'].setLabel( self.trailers.genres[self.genre_id].movies[trailer].title )
            self.controls['Trailer Watched Overlay']['control'].setVisible( self.trailers.genres[self.genre_id].movies[trailer].watched )
            self.controls['Trailer Favorite Overlay']['control'].setVisible( self.trailers.genres[self.genre_id].movies[trailer].favorite )
            plot = self.trailers.genres[self.genre_id].movies[trailer].plot
            self.controls['Trailer Plot']['control'].reset()
            if ( plot ):
                self.controls['Trailer Plot']['control'].setText( plot )
            self.controls['Trailer Cast']['control'].reset()
            cast = self.trailers.genres[self.genre_id].movies[trailer].cast
            ## Test code ##
            #cast = ['Angelina Jolee', 'Jessica Alba', 'Chuck Norris', 'Arnold Swarzenegger', 'Hillary Duff', 'William Shatner']
            if ( cast ):
                for actor in cast:
                    thumbnail = os.path.join( self.image_path, 'generic-actor.tbn' )
                    l = xbmcgui.ListItem( actor, '', thumbnail )
                    self.controls['Trailer Cast']['control'].addItem( l )
            self.setScrollbarIndicator('Trailer List')
            self.setSelection( 'Trailer Cast', 0 )

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
        if ( self.settings.trailer_quality >= len( trailer_urls )):
            choice = len( trailer_urls ) - 1
        else:
            choice = self.settings.trailer_quality
        try:
            if ( self.settings.mode == 0 ):
                filename = trailer_urls[choice].replace( '//', '/' ).replace( '/', '//', 1 )
            elif ( self.settings.mode == 1):
                url = trailer_urls[choice].replace( '//', '/' ).replace( '/', '//', 1 )
                fetcher = cacheurl.HTTPProgressSave()
                filename = fetcher.urlretrieve( url )
            elif ( self.settings.mode == 2):
                url = trailer_urls[choice].replace( '//', '/' ).replace( '/', '//', 1 )
                fetcher = cacheurl.HTTPProgressSave( self.settings.save_folder )
                filename = fetcher.urlretrieve( url )
                if ( filename ): self.saveThumbnail( filename )
            if ( filename ): 
                self.MyPlayer.play( filename )
                self.currently_playing_movie = trailer
                self.currently_playing_genre_id = self.genre_id
        except:
            self.debugWrite( 'playTrailer', False, ['ERROR: Trying to play trailer'], [()] )
    
    def saveThumbnail( self, filename ):
        self.debugWrite( 'saveThumbnail', 2 )
        try: 
            new_filename = '%s.tbn' % ( os.path.splitext( filename )[0], )
            if ( not os.path.isfile( new_filename ) ):
                shutil.copyfile( self.poster, new_filename )
        except: pass
    
    def toggleContextMenu( self ):
        self.debugWrite('toggleContextMenu', 2)
        self.context_menu = not self.context_menu
        if ( self.context_menu ):
            trailer = self.controls['Trailer List']['control'].getSelectedPosition()
            self.controls['Context Menu Queue Button']['control'].setLabel( _( 500 ) )
            self.controls['Context Menu Favorite Button']['control'].setLabel( _( 502 + self.trailers.genres[self.genre_id].movies[trailer].favorite ) )
            self.controls['Context Menu Watched Button']['control'].setLabel( _( 504 + self.trailers.genres[self.genre_id].movies[trailer].watched ) )
            self.controls['Context Menu Refresh Button']['control'].setLabel( _( 506 ) )
            self.showContextMenu( True )
            self.setFocus( self.controls['Context Menu Queue Button']['control'] )
        else:
            self.showContextMenu( False )
            self.setFocus( self.controls['Trailer List']['control'] )
            
    def showContextMenu( self, visible ):
        self.controls['Context Menu Background']['control'].setVisible( visible )
        self.controls['Context Menu Queue Button']['control'].setVisible( visible )
        self.controls['Context Menu Favorite Button']['control'].setVisible( visible )
        self.controls['Context Menu Watched Button']['control'].setVisible( visible )
        self.controls['Context Menu Refresh Button']['control'].setVisible( visible )

    def toggleAsWatched( self ):
        trailer = self.controls['Trailer List']['control'].getSelectedPosition()
        watched = not self.trailers.genres[self.genre_id].movies[trailer].watched
        self.markAsWatched( watched, trailer, self.genre_id )
        if ( self.context_menu ): self.toggleContextMenu()
        
    def markAsWatched( self, watched, trailer, genre_id ):
        self.trailers.genres[genre_id].movies[trailer].watched = watched
        if ( genre_id == self.genre_id ):
            self.showTrailers( trailer )
  
    def toggleAsFavorite( self ):
        trailer = self.controls['Trailer List']['control'].getSelectedPosition()
        self.trailers.genres[self.genre_id].movies[trailer].favorite = not self.trailers.genres[self.genre_id].movies[trailer].favorite
        self.showTrailers( trailer )
        if ( self.context_menu ): self.toggleContextMenu()
  
    def changeSettings( self ):
        self.debugWrite('changeSettings', 2)
        thumbnail_display = self.settings.thumbnail_display
        settings = guisettings.GUI( skin=self.skin, language=_ )
        settings.doModal()
        del settings
        self.getSettings()
        if ( thumbnail_display != self.settings.thumbnail_display ):
            self.setGenre( self.genre_id )
        
    def exitScript( self ):
        self.debugWrite( 'exitScript', 2 )
        try:
            self.trailers.saveDatabase()
        finally:
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
            elif ( control is self.controls['Context Menu Favorite Button']['control'] ):
                self.toggleAsFavorite()
            elif ( control is self.controls['Context Menu Watched Button']['control'] ):
                self.toggleAsWatched()
        except: traceback.print_exc()

    def onAction( self, action ):
        try:
            button_key = self.controller_action.get( action.getButtonCode(), 'n/a' )
            control = self.getFocus()
            if ( button_key == 'Back Button' or button_key == 'Remote Menu Button' ):
                if ( self.context_menu ): self.toggleContextMenu()
                else: self.exitScript()
            elif (button_key == 'B Button' or button_key == 'Remote Back Button' ):
                if ( self.context_menu ): self.toggleContextMenu()
                elif ( self.genre_id >= 2):
                    self.setGenre( -1 )
            elif ( button_key == 'Remote Title' or button_key == 'White Button' ):
                if ( control is self.controls['Trailer List']['control'] or self.context_menu ):
                    self.toggleContextMenu()
            elif ( control is self.controls['Trailer List']['control'] ):
                if ( button_key == 'Y' or button_key == 'Remote 0' ):
                    self.toggleAsFavorite()##change to queue
                else:
                    self.showTrailerInfo()
            elif ( control is self.controls['Trailer List Scrollbar Position Indicator']['control'] ):
                if ( button_key == 'Remote Up' or button_key == 'DPad Up' ):
                    self.pageIndicator( 'Trailer List', -1 )
                elif ( button_key == 'Remote Down' or button_key == 'DPad Down' ):
                    self.pageIndicator( 'Trailer List', 1 )
            elif ( control is self.controls['Trailer Cast']['control'] ):
                self.setScrollbarIndicator( 'Trailer Cast' )
            elif ( control is self.controls['Trailer Cast Scrollbar Position Indicator']['control'] ):
                if ( button_key == 'Remote Up' or button_key == 'DPad Up' ):
                    self.pageIndicator( 'Trailer Cast', -1 )
                elif ( button_key == 'Remote Down' or button_key == 'DPad Down' ):
                    self.pageIndicator( 'Trailer Cast', 1 )
            elif ( control is self.controls['Exclusives Button']['control'] ):
                self.setControlNavigation( 'Exclusives Button' )
            elif ( control is self.controls['Newest Button']['control'] ):
                self.setControlNavigation( 'Newest Button' )
            elif ( control is self.controls['Genre Button']['control'] ):
                self.setControlNavigation( 'Genre Button' )
            elif ( control is self.controls['Search Button']['control'] ):
                self.setControlNavigation( 'Search Button' )
            elif ( control is self.controls['Settings Button']['control'] ):
                self.setControlNavigation( 'Settings Button' )
            elif ( control is self.controls['Update Button']['control'] ):
                self.setControlNavigation( 'Update Button' )
        except: traceback.print_exc()

    def debugWrite( self, function, action, lines=[], values=[] ):
        if ( self.debug ):
            Action = ( 'Failed', 'Succeeded', 'Started' )
            Highlight = ( '__', '__', '<<<<< ', '__', '__', ' >>>>>' )
            xbmc.output( '%s%s%s : (%s)\n' % ( Highlight[action], function, Highlight[action + 3], Action[action] ) )
            try:
                for cnt, line in enumerate( lines ):
                    finished_line = '%s\n' % ( line, )
                    xbmc.output( finished_line % values[cnt] )
            except: pass



## Thanks Thor918 for this class ##
class MyPlayer( xbmc.Player ):
    def  __init__( self, *args, **kwargs ):
        if ( kwargs.has_key( 'function' )): 
            self.function = kwargs['function']
            xbmc.Player.__init__( self )
    
    def onPlayBackStopped( self ):
        self.function( 0 )
    
    def onPlayBackEnded( self ):
        self.function( 1 )
    
    def onPlayBackStarted( self ):
        self.function( 2 )
    







