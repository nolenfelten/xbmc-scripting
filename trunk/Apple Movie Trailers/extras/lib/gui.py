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
_ = language.Language().string

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
    updateProgressDialog( '%s threading' % ( _( 52 ), ))
    import threading
    updateProgressDialog( '%s guibuilder' % ( _( 52 ), ))
    import guibuilder
    updateProgressDialog( '%s guisettings' % ( _( 52 ), ))
    import guisettings
    updateProgressDialog( '%s amt_util' % ( _( 52 ), ))
    import amt_util, context_menu
    updateProgressDialog( '%s cacheurl' % ( _( 52 ), ))
    import cacheurl
    updateProgressDialog( '%s shutil' % ( _( 52 ), ))
    import shutil, datetime


except:
    closeProgessDialog()
    traceback.print_exc()
    xbmcgui.Dialog().ok( _( 0 ), _( 81 ) )
    raise
    
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
                self.setControlsDisabled()
                self.setupVariables()
                #if ( self.checkForDB() ):
                self.setStartupChoices()
                self.setStartupCategory()
                #else:
                #    xbmcgui.Dialog().ok( _( 0 ), _( 53), _( 54 ) )
            except:
                traceback.print_exc()
                self.SUCCEEDED = False
                self.exitScript()
                
    def setControlsDisabled( self ):
        try: self.controls['Category List Backdrop']['control'].setEnabled( False )
        except: pass
        try: self.controls['Trailer List Backdrop']['control'].setEnabled( False )
        except: pass
        try: self.controls['Cast List Backdrop']['control'].setEnabled( False )
        except: pass

    def getSettings( self ):
        self.settings = amt_util.Settings()

    def setupGUI( self ):
        current_skin = xbmc.getSkinDir()
        if ( not os.path.exists( os.path.join( self.cwd, 'extras', 'skins', current_skin ))): current_skin = 'default'
        skin_path = os.path.join( self.cwd, 'extras', 'skins', current_skin )
        self.image_path = os.path.join( skin_path, 'gfx' )
        if ( self.getResolution() == 0 or self.getResolution() % 2 ): xml_file = 'skin_16x9.xml'
        else: xml_file = 'skin.xml'
        if ( not os.path.isfile( os.path.join( skin_path, xml_file ))): xml_file = 'skin.xml'
        guibuilder.GUIBuilder( self, os.path.join( skin_path, xml_file ), self.image_path, useDescAsKey = True, 
            title = _( 0 ), line1 = __line1__, dlg = dialog, pct = pct, useLocal = True, debug = False )
        closeProgessDialog()
        if ( not self.SUCCEEDED ):
            xbmcgui.Dialog().ok( _( 0 ), _( 57 ), _( 58 ), os.path.join( skin_path, xml_file ))

    def setupVariables( self ):
        import trailers
        self.trailers = trailers.Trailers()
        #self.skin = self.settings.skin
        self.sql = None
        self.params = None
        self.display_cast = False
        self.dummy()
        self.MyPlayer = MyPlayer( xbmc.PLAYER_CORE_MPLAYER, function = self.myPlayerChanged )
        self.controller_action = amt_util.setControllerAction()
        self.update_method = 0
        
    # dummy() and self.Timer are currently used for the Player() subclass so when an onPlayback* event occurs, 
    # it calls myPlayerChanged() immediately.
    def dummy( self ):
        #self.debugWrite('dummy', 2)
        self.Timer = threading.Timer( 60*60*60, self.dummy,() )
        self.Timer.start()

    def myPlayerChanged( self, event ):
        #self.debugWrite('myPlayerChanged', 2)
        try:
            self.controls['X Button On']['control'].setVisible( xbmc.getCondVisibility( self.controls['X Button On']['visible'] ))
            self.controls['X Button Off']['control'].setVisible( xbmc.getCondVisibility( self.controls['X Button Off']['visible'] ))
            self.controls['Full-Screen Visualisation Label']['control'].setVisible( xbmc.getCondVisibility( self.controls['Full-Screen Visualisation Label']['visible'] ))
            self.controls['Full-Screen Video Label']['control'].setVisible( xbmc.getCondVisibility( self.controls['Full-Screen Video Label']['visible'] ))
        except: pass
        #if ( event == 0 and self.currently_playing_movie[1] >= 0 ):
        #    self.markAsWatched( self.currently_playing_movie[0] + 1, self.currently_playing_movie[1], self.currently_playing_movie[2] )
        #elif ( event == 2 ):
        #    self.currently_playing_movie = -1
        #    self.currently_playing_genre = -1

    ## Remove if no DB used ##
    def checkForDB( self ):
        #self.debugWrite( 'checkForDB', 2 )
        if ( os.path.isfile( os.path.join( self.cwd, 'data', 'AMT.pk' ))): return True
        else: return False

    def setStartupChoices( self ):
        self.sql_category = ''#SELECT title, count, url, id, loaded FROM Genres ORDER BY title'
        self.params_category = None
        self.main_category = -1
        self.genres = self.trailers.categories
        
    def setStartupCategory( self ):
        startup_button = 'Genre'
        if ( self.settings.startup_category_id == self.settings.category_newest ): startup_button = 'Newest'
        elif ( self.settings.startup_category_id == self.settings.category_exclusives ): startup_button = 'Exclusives'
        self.setControlNavigation( '%s Button' % ( startup_button, ) )
        self.setCategory( self.settings.startup_category_id )

    def setCategory( self, category_id = -1 ):
        self.category_id = category_id
        if ( category_id >= 0 or category_id <= -6 ):
            if ( category_id == -6 ):
                sql = 'SELECT * FROM Movies WHERE favorite=? ORDER BY title'
                params = ( 1, )
            elif ( category_id == -7 ):
                sql = 'SELECT * FROM "Movies" WHERE saved_location != ?'
                params = ( '', )
            elif ( self.main_category == -1 ):
                sql = 'SELECT * FROM Movies WHERE %s&genre>? ORDER BY title' % ( self.trailers.categories[category_id].id, )
                params = ( 0, )
            elif ( self.main_category == -2 ):
                sql = 'SELECT * FROM Movies WHERE studio=? ORDER BY title'
                params = ( self.trailers.categories[category_id].title, )
            elif ( self.main_category == -3 ):
                sql = 'SELECT * FROM Movies WHERE actors LIKE ? ORDER BY title'
                params = ( '%%%s%%' % ( self.trailers.categories[category_id].title, ), )
            elif ( self.main_category == -99 ):
                sql = 'SELECT * FROM Movies WHERE actors LIKE ? ORDER BY title'
                params = ( '%%%s%%' % ( self.controls['Cast List']['control'].getSelectedItem().getLabel(), ), )
            self.showTrailers( sql, params )
        else:
            if ( category_id == -1 ):
                sql = 'SELECT title, count, url, id, loaded FROM Genres ORDER BY title'
            elif ( category_id == -2 ):
                sql = 'SELECT title, count FROM Studios ORDER BY title'
            elif ( category_id == -3 ):
                sql = 'SELECT name, count FROM Actors ORDER BY name'
            self.main_category = category_id
            self.showCategories( sql )
        self.showControls( self.category_id <= -1 and self.category_id >= -5 )
        if ( self.category_id <= -1 and self.category_id >= -5 ): self.setFocus( self.controls['Category List']['control'] )
        else: self.setFocus( self.controls['Trailer List']['control'] )

    def showCategories( self, sql, params = None, choice = 0, force_update = False ):
        try:
            #self.debugWrite('getGenreCategories', 2)
            xbmcgui.lock()
            if ( sql != self.sql_category or params != self.params_category or force_update ):
                self.trailers.getCategories( sql, params )
                self.sql_category = sql
                self.params_category = params
                self.controls['Category List']['control'].reset()
                for category in self.trailers.categories:
                    if ( self.category_id ) == -1: thumb_category = 'genre'
                    elif ( self.category_id ) == -2: thumb_category = 'studio'
                    else: thumb_category = 'actor'
                    thumbnail = os.path.join( self.image_path, '%s.tbn' % ( category.title, ))
                    if ( not os.path.isfile( thumbnail )):
                        thumbnail = os.path.join( self.image_path, 'generic-%s.tbn' % ( thumb_category, ) )
                    count = '(%d)' % ( category.count, )
                    self.controls['Category List']['control'].addItem( xbmcgui.ListItem( category.title, count, thumbnail, thumbnail ) )
            xbmcgui.unlock()
        except:
            xbmcgui.unlock()
            traceback.print_exc()

    def showTrailers( self, sql, params = None, choice = 0, force_update = False ):
        try:
            xbmcgui.lock()
            if ( sql != self.sql or params != self.params or force_update ): self.trailers.getMovies( sql, params )
            self.sql = sql
            self.params = params
            self.controls['Trailer List']['control'].reset()
            for movie in self.trailers.movies: # now fill the list control
                if ( self.settings.thumbnail_display == 0 ): 
                    if ( movie.watched ): thumbnail = movie.thumbnail_watched
                    else: thumbnail = movie.thumbnail
                elif ( self.settings.thumbnail_display == 1 ): thumbnail = os.path.join( self.image_path, 'generic-trailer.tbn' )
                else: thumbnail = ''
                favorite = ['','*'][movie.favorite]
                if ( movie.rating ): rating = '[%s]' % movie.rating
                else: rating = ''
                self.controls['Trailer List']['control'].addItem( xbmcgui.ListItem( '%s%s' % ( favorite, movie.title, ), rating, thumbnail, thumbnail ) )
            xbmcgui.unlock()
            self.setSelection( 'Trailer List', choice + ( choice == -1 ) )
        except:
            traceback.print_exc()
            xbmcgui.unlock()

    def calcScrollbarVisibilty( self, list_control ):
        if ( self.controls[list_control]['special'] ):
            if ( ( ( self.category_id >= 0 or self.category_id <= -6 ) and list_control != 'Category List' ) or 
                  ( self.category_id <= -1 and self.category_id >= -5 and list_control == 'Category List' ) ):
                visible = ( self.controls[list_control]['control'].size() > self.controls[list_control]['special'] )
                visible2 = not visible
                if ( list_control == 'Cast List' and not self.display_cast ):
                    visible = False
                    visible2 = False
                self.showScrollbar( visible, visible2, list_control )
                self.setSelection( list_control )
            else: self.showScrollbar( False, False, list_control )

    def showScrollbar( self, visible, visible2, list_control ):
        try:
            self.controls['%s Scrollbar Up Arrow' % ( list_control, )]['control'].setVisible( visible or visible2 )
            self.controls['%s Scrollbar Middle' % ( list_control, )]['control'].setVisible( visible or visible2 )
            self.controls['%s Scrollbar Down Arrow' % ( list_control, )]['control'].setVisible( visible or visible2 )
            self.controls['%s Scrollbar Position Indicator' % ( list_control, )]['control'].setVisible( visible )
            self.controls['%s Scrollbar Position Indicator' % ( list_control, )]['control'].setEnabled( visible )
        except: pass
            
    def setScrollbarIndicator( self, list_control ):
        try:
            if ( self.controls[list_control]['special'] ):
                if ( self.controls[list_control]['control'].size() > int( self.controls[list_control]['special'] ) ):
                    offset = float( self.controls['%s Scrollbar Middle' % ( list_control, )][ 'control' ].getHeight() - self.controls['%s Scrollbar Position Indicator' % ( list_control, )][ 'control' ].getHeight() ) / float( self.controls[list_control]['control'].size() - 1 )
                    posy = int( self.controls['%s Scrollbar Middle' % ( list_control, )][ 'control' ].getPosition()[ 1 ] + ( offset * self.controls[list_control]['control'].getSelectedPosition() ) )
                    self.controls['%s Scrollbar Position Indicator' % ( list_control, )]['control'].setPosition( self.controls['%s Scrollbar Position Indicator' % ( list_control, )][ 'control' ].getPosition()[ 0 ], posy )
        except: pass
            
    def setSelection( self, list_control, pos = 0 ):
        #self.debugWrite('setSelection', 2)
        self.controls[list_control]['control'].selectItem( pos )
        #self.setFocus( self.controls[list_control]['control'] )
        if ( list_control == 'Trailer List' ): self.showTrailerInfo()
        elif ( list_control == 'Category List' ): choice = self.setCountLabel( 'Category List' )
        self.setScrollbarIndicator( list_control )

    def pageIndicator( self, list_control, page ):
        #self.debugWrite('pageIndicator', 2)
        current_pos = self.controls[list_control]['control'].getSelectedPosition()
        total_items = self.controls[list_control]['control'].size()
        items_per_page = self.controls[list_control]['special']
        current_pos += page * items_per_page
        if ( current_pos < 0 ): current_pos = 0
        elif ( current_pos >= total_items ): current_pos = total_items - 1
        self.setSelection( list_control, current_pos )

    def setControlNavigation( self, button ):
        #self.debugWrite('setControlNavigation', 2)
        self.controls['Trailer List']['control'].controlLeft( self.controls[button]['control'] )
        try:
            self.controls['Cast List Scrollbar Position Indicator']['control'].controlRight( self.controls[button]['control'] )
        except:
            self.controls['Cast List']['control'].controlRight( self.controls[button]['control'] )
            
        
    def showControls( self, category ):
        try:
            xbmcgui.lock()
            try: self.controls['Category List Backdrop']['control'].setVisible( category )
            except: pass
            self.controls['Category List']['control'].setVisible( category )
            self.controls['Category List']['control'].setEnabled( category )
            self.controls['Category List Count Label']['control'].setVisible( category )
            try: self.controls['Trailer List Backdrop']['control'].setVisible( not category )
            except: pass
            self.controls['Trailer List']['control'].setVisible( not category )
            self.controls['Trailer List']['control'].setEnabled( not category )
            self.controls['Trailer List Count Label']['control'].setVisible( not category )
            self.controls['Poster Backdrop']['control'].setVisible( not category )
            self.controls['Trailer Poster']['control'].setVisible( not category )
            self.controls['Trailer Rating']['control'].setVisible( not category )
            self.controls['Trailer Title']['control'].setVisible( not category )
            if ( category ):
                self.controls['Trailer Favorite Overlay']['control'].setVisible( False )
                self.controls['Trailer Watched Overlay']['control'].setVisible( False )
                self.controls['Trailer Saved Overlay']['control'].setVisible( False )
            self.calcScrollbarVisibilty( 'Trailer List' )
            self.calcScrollbarVisibilty( 'Category List' )
            self.showPlotCastControls( category )
            self.setCategoryLabel()
        finally:
            xbmcgui.unlock()
            
    def showPlotCastControls( self, category ):
        try:
            xbmcgui.lock()
            try: self.controls['Cast List Backdrop']['control'].setVisible( self.display_cast and not category )
            except: pass
            self.controls['Plot Button']['control'].setVisible( self.display_cast and not category )
            self.controls['Plot Button']['control'].setEnabled( self.display_cast and not category )
            self.controls['Cast Button']['control'].setVisible( not self.display_cast and not category )
            self.controls['Cast Button']['control'].setEnabled( not self.display_cast and not category )
            self.controls['Trailer Plot']['control'].setVisible( not self.display_cast and not category )
            self.controls['Trailer Plot']['control'].setEnabled( not self.display_cast and not category )
            self.controls['Cast List']['control'].setVisible( self.display_cast and not category )
            self.controls['Cast List']['control'].setEnabled( self.display_cast and not category and self.cast_exists )
            self.calcScrollbarVisibilty( 'Cast List' )
        finally:
            xbmcgui.unlock()
            
    def togglePlotCast( self ):
        #self.debugWrite('togglePlotCast', 2)
        self.display_cast = not self.display_cast
        self.showPlotCastControls( False )
        if ( self.display_cast ): self.setFocus( self.controls['Plot Button']['control'] )
        else: self.setFocus( self.controls['Cast Button']['control'] )

    def setCategoryLabel( self ):
        #self.debugWrite('setCategoryLabel', 2)
        if ( self.category_id == self.settings.category_newest and self.main_category == -1 ):
            category = _( 200 )
        elif ( self.category_id == self.settings.category_exclusives and self.main_category == -1 ):
            category = _( 201 )
        elif ( self.category_id == -1 ):
            category = _( 219 )
        elif ( self.category_id == -2 ):
            category = _( 223 )
        elif ( self.category_id == -3 ):
            category = _( 225 )
        elif ( self.category_id == -6 ):
            category = _( 217 )
        elif ( self.category_id == -7 ):
            category = _( 226 )
        elif ( self.category_id >= 0 and self.main_category == -99 ):
            category = self.actor
        elif ( self.category_id >= 0 ):
            category = self.trailers.categories[self.category_id].title
        self.controls['Category Label']['control'].setLabel( category )
            
    def setCountLabel( self, list_control ):
        pos = self.controls['%s' % list_control]['control'].getSelectedPosition()
        self.controls['%s Count Label' % list_control]['control'].setLabel( '%d of %d' % ( pos + 1, self.controls['%s' % list_control]['control'].size(), ))
        return pos
    
    def showTrailerInfo( self ):
        try:
            #self.debugWrite('showTrailerInfo', 2)
            xbmcgui.lock()
            #trailer = self.controls['Trailer List']['control'].getSelectedPosition()
            #self.controls['Trailer Count Label']['control'].setLabel( '%d of %d' % ( trailer + 1, self.controls['Trailer List']['control'].size(), ))
            trailer = self.setCountLabel( 'Trailer List' )
            poster = self.trailers.movies[trailer].poster
            if ( not poster ): poster = os.path.join( self.image_path, 'blank-poster.tbn' )
            self.controls['Trailer Poster']['control'].setImage( poster )
            #rating = self.trailers.movies[trailer].rating_url
            self.controls['Trailer Rating']['control'].setImage( self.trailers.movies[trailer].rating_url )
            self.controls['Trailer Title']['control'].setLabel( self.trailers.movies[trailer].title )
            #print 'showTrailerInfo: %s' % self.trailers.genres[self.category_id].movies[trailer].title
            # Plot
            self.controls['Trailer Plot']['control'].reset()
            plot = self.trailers.movies[trailer].plot
            if ( plot ):
                self.controls['Trailer Plot']['control'].setText( plot )
            else: self.controls['Trailer Plot']['control'].setText( _( 400 ) )
            # Cast
            self.controls['Cast List']['control'].reset()
            cast = self.trailers.movies[trailer].cast
            if ( cast ):
                self.cast_exists = True
                for actor in cast:
                    thumbnail = os.path.join( self.image_path, 'generic-actor.tbn' )
                    self.controls['Cast List']['control'].addItem( xbmcgui.ListItem( actor, '', thumbnail, thumbnail ) )
            else: 
                self.cast_exists = False
                self.controls['Cast List']['control'].addItem( _( 401 ) )
            self.showPlotCastControls( False )
            #self.calcScrollbarVisibilty( 'Cast List' )
            self.setScrollbarIndicator( 'Trailer List' )
            self.showOverlays( trailer )
        finally:
            xbmcgui.unlock()
        
    def showOverlays( self, trailer ):
        posx, posy = self.controls['Trailer Favorite Overlay'][ 'control' ].getPosition()# + self.coordinates[0]
        #posy = self.controls['Trailer Favorite Overlay'][ 'control' ].getPosition()[ 1 ]# + self.coordinates[1]
        favorite = self.trailers.movies[trailer].favorite
        self.controls['Trailer Favorite Overlay']['control'].setVisible( favorite )
        posx = posx - ( favorite * self.controls['Trailer Favorite Overlay'][ 'control' ].getWidth() )
        watched = self.trailers.movies[trailer].watched > 0
        self.controls['Trailer Watched Overlay']['control'].setPosition( posx, posy )
        self.controls['Trailer Watched Overlay']['control'].setVisible( watched )
        posx = posx - ( watched * self.controls['Trailer Watched Overlay'][ 'control' ].getWidth() )
        saved = ( self.trailers.movies[trailer].saved != '' )
        self.controls['Trailer Saved Overlay']['control'].setPosition( posx, posy )
        self.controls['Trailer Saved Overlay']['control'].setVisible( saved )

    def getTrailerGenre( self ):
        #self.debugWrite('getTrailerGenre', 2)
        genre = self.controls['Category List']['control'].getSelectedPosition()
        self.setCategory( genre )

    def getActorChoice( self ):
        choice = self.controls['Cast List']['control'].getSelectedPosition()
        self.actor = self.controls['Cast List']['control'].getSelectedItem().getLabel()
        self.setCategory( choice )

    def playTrailer( self ):
        try:
            #self.debugWrite('PlayTrailer', 2)
            trailer = self.controls['Trailer List']['control'].getSelectedPosition()
            trailer_urls = self.trailers.movies[trailer].trailer_urls
            if ( self.settings.trailer_quality >= len( trailer_urls )):
                choice = len( trailer_urls ) - 1
            else:
                choice = self.settings.trailer_quality
            if ( 'p.mov' in trailer_urls[choice] ): choice -= 1
            if ( self.settings.mode == 0 ):
                filename = trailer_urls[choice]
            elif ( self.settings.mode == 1):
                url = trailer_urls[choice]
                fetcher = cacheurl.HTTPProgressSave()
                filename = str( fetcher.urlretrieve( url ) )
            elif ( self.settings.mode == 2):
                url = trailer_urls[choice]
                ext = os.path.splitext( url )[1]
                title = '%s%s' % (self.trailers.movies[trailer].title, ext, )
                fetcher = cacheurl.HTTPProgressSave( self.settings.save_folder, title )
                filename = str( fetcher.urlretrieve( url ) )
                if ( filename ):
                    poster = self.trailers.movies[trailer].poster
                    if ( not poster ): poster = os.path.join( self.image_path, 'blank-poster.tbn' )
                    self.saveThumbnail( filename, trailer, poster, )
            if ( filename ):
                self.MyPlayer.play( filename)
                xbmc.sleep(500)
                self.markAsWatched( self.trailers.movies[trailer].watched + 1, self.trailers.movies[trailer].title, trailer )
                #self.changed_trailers = False
        except: traceback.print_exc()

    def saveThumbnail( self, filename, trailer, poster ):
        #self.debugWrite( 'saveThumbnail', 2 )
        try: 
            new_filename = '%s.tbn' % ( os.path.splitext( filename )[0], )
            if ( not os.path.isfile( new_filename ) ):
                shutil.copyfile( poster, new_filename )
            if ( self.trailers.movies[trailer].saved == '' ):
                success = self.trailers.updateRecord( ( 'saved_location', ), 'Movies', ( filename, ), key_value = self.trailers.movies[trailer].title)
                if ( success ): self.trailers.movies[trailer].saved = filename
                #self.showTrailers( trailer )
        except: traceback.print_exc()
    
    def showContextMenu( self ):
        cm = context_menu.GUI( win = self, language=_ )
        cm.doModal()
        del cm

    def addToPlaylist( self ):
        pass
        
    def markAsWatched( self, watched, trailer, index ):
        if ( watched ): date = datetime.date.today()
        else: date = ''
        success = self.trailers.updateRecord( ( 'times_watched', 'last_watched', ), 'Movies', ( watched, date, ), key_value = trailer )
        if ( success ):
            self.trailers.movies[index].watched = watched
            self.showTrailers( self.sql, self.params, choice = index )
        
    def changeSettings( self ):
        #self.debugWrite('changeSettings', 2)
        thumbnail_display = self.settings.thumbnail_display
        settings = guisettings.GUI( language=_ , genres=self.genres )
        settings.doModal()
        del settings
        self.getSettings()
        if ( thumbnail_display != self.settings.thumbnail_display and self.category_id != -1 ):
            trailer = self.controls['Trailer List']['control'].getSelectedPosition()
            self.showTrailers( self.sql, self.params, choice = trailer )
    
    def exitScript( self ):
        #self.debugWrite( 'exitScript', 2 )
        try:
            pass
        finally:
            if ( self.Timer ): self.Timer.cancel()
            self.close()

    def setShortcut( self, shortcut ):
        if ( self.main_category != -1 ):
            #print 'NOPE'
            self.sql_category = 'SELECT title, count, url, id, loaded FROM Genres ORDER BY title'
            self.params_category = None
            self.main_category = -1
            #self.trailers.getCategories( self.sql_category, self.params_category )
            self.trailers.categories = self.genres
        #print self.trailers.categories[shortcut].title
        #print self.trailers.categories[shortcut].id
        self.setCategory( shortcut )

    def onControl( self, control ):
        try:
            if ( control is self.controls['Newest Button']['control'] ):
                self.setShortcut( self.settings.category_newest )
            elif ( control is self.controls['Exclusives Button']['control'] ):
                self.setShortcut( self.settings.category_exclusives )
            elif ( control is self.controls['Genre Button']['control'] ):
                self.setCategory( -1 )
            elif ( control is self.controls['Studio Button']['control'] ):
                self.setCategory( -2 )
            elif ( control is self.controls['Actor Button']['control'] ):
                self.setCategory( -3 )
            elif ( control is self.controls['Downloaded Button']['control'] ):
                self.setCategory( -7 )
            elif ( control is self.controls['Favorites Button']['control'] ):
                self.setCategory( -6 )
            elif ( control is self.controls['Search Button']['control'] ):
                pass#self.search
            elif ( control is self.controls['Settings Button']['control'] ):
                self.changeSettings()
            elif ( control is self.controls['Plot Button']['control'] or control is self.controls['Cast Button']['control'] ):
                self.togglePlotCast()
            elif ( control is self.controls['Category List']['control'] ):
                self.getTrailerGenre()
            elif ( control is self.controls['Trailer List']['control'] ):
                self.playTrailer()
            elif ( control is self.controls['Cast List']['control'] ):
                self.main_category = -99
                self.getActorChoice()
        except: traceback.print_exc()
        
    def onAction( self, action ):
        try:
            button_key = self.controller_action.get( action.getButtonCode(), 'n/a' )
            control = self.getFocus()
            if ( button_key == 'Keyboard ESC Button' or button_key == 'Back Button' or button_key == 'Remote Menu Button' ):
                self.exitScript()
            elif ( control is self.controls['Trailer List']['control'] ):
                if ( button_key == 'Y' or button_key == 'Remote 0' ):
                    pass#self.toggleAsFavorite()##change to queue
                elif ( button_key == 'Keyboard Backspace Button' or button_key == 'B Button' or button_key == 'Remote Back Button' ):
                    if ( self.main_category == -99 ): self.main_category = -3
                    self.setCategory( self.main_category )
                elif ( button_key == 'Keyboard Menu Button' or button_key == 'Remote Title' or button_key == 'White Button' ):
                    self.showContextMenu()
                else:# ( button_key == 'n/a' or button_key == 'DPad Up' or button_key == 'Remote Up' or button_key == 'DPad Down' or button_key == 'Remote Down' ):
                    self.showTrailerInfo()
            elif ( control is self.controls['Trailer List Scrollbar Position Indicator']['control'] ):
                if ( button_key == 'Keyboard Up Arrow' or button_key == 'Remote Up' or button_key == 'DPad Up' ):
                    self.pageIndicator( 'Trailer List', -1 )
                elif ( button_key == 'Keyboard Down Arrow' or button_key == 'Remote Down' or button_key == 'DPad Down' ):
                    self.pageIndicator( 'Trailer List', 1 )
            elif ( control is self.controls['Category List']['control'] ):
                self.setScrollbarIndicator( 'Category List' )
                choice = self.setCountLabel( 'Category List' )
            elif ( control is self.controls['Category List Scrollbar Position Indicator']['control'] ):
                if ( button_key == 'Keyboard Up Arrow' or button_key == 'Remote Up' or button_key == 'DPad Up' ):
                    self.pageIndicator( 'Category List', -1 )
                    choice = self.setCountLabel( 'Category List' )
                elif ( button_key == 'Keyboard Down Arrow' or button_key == 'Remote Down' or button_key == 'DPad Down' ):
                    self.pageIndicator( 'Category List', 1 )
                    choice = self.setCountLabel( 'Category List' )
            elif ( control is self.controls['Cast List']['control'] ):
                self.setScrollbarIndicator( 'Cast List' )
            elif ( control is self.controls['Cast List Scrollbar Position Indicator']['control'] ):
                if ( button_key == 'Keyboard Up Arrow' or button_key == 'Remote Up' or button_key == 'DPad Up' ):
                    self.pageIndicator( 'Cast List', -1 )
                elif ( button_key == 'Keyboard Down Arrow' or button_key == 'Remote Down' or button_key == 'DPad Down' ):
                    self.pageIndicator( 'Cast List', 1 )
            elif ( control is self.controls['Newest Button']['control'] ):
                self.setControlNavigation( 'Newest Button' )
            elif ( control is self.controls['Exclusives Button']['control'] ):
                self.setControlNavigation( 'Exclusives Button' )
            elif ( control is self.controls['Genre Button']['control'] ):
                self.setControlNavigation( 'Genre Button' )
            elif ( control is self.controls['Studio Button']['control'] ):
                self.setControlNavigation( 'Studio Button' )
            elif ( control is self.controls['Favorites Button']['control'] ):
                self.setControlNavigation( 'Favorites Button' )
            elif ( control is self.controls['Actor Button']['control'] ):
                self.setControlNavigation( 'Actor Button' )
            elif ( control is self.controls['Search Button']['control'] ):
                self.setControlNavigation( 'Search Button' )
            elif ( control is self.controls['Settings Button']['control'] ):
                self.setControlNavigation( 'Settings Button' )
            elif ( control is self.controls['Downloaded Button']['control'] ):
                self.setControlNavigation( 'Downloaded Button' )
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
            except: traceback.print_exc()



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
    







