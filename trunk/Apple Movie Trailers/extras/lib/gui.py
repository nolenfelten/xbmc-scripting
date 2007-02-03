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
    #updateProgressDialog( '%s guisettings' % ( _( 52 ), ))
    #import guisettings
    updateProgressDialog( '%s amt_util' % ( _( 52 ), ))
    import amt_util, context_menu
    updateProgressDialog( '%s cacheurl' % ( _( 52 ), ))
    import cacheurl
    updateProgressDialog( '%s shutil' % ( _( 52 ), ))
    import shutil, datetime, default


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
        if ( self.settings.skin == 'Default' ): current_skin = xbmc.getSkinDir()
        else: current_skin = self.settings.skin
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
        self.skin = self.settings.skin
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

    def setStartupChoices( self ):
        self.sql_category = ''#'SELECT title, count, url, id, loaded FROM Genres ORDER BY title'
        self.params_category = None
        self.main_category = amt_util.GENRES
        self.genres = self.trailers.categories
        self.setShortcutLabels()

    def setStartupCategory( self ):
        startup_button = 'Shortcut1'
        if ( self.settings.startup_category_id == self.settings.shortcut2 ): startup_button = 'Shortcut2'
        elif ( self.settings.startup_category_id == self.settings.shortcut3 ): startup_button = 'Shortcut3'
        self.setControlNavigation( '%s Button' % ( startup_button, ) )
        self.setCategory( self.settings.startup_category_id, 1 )

    def setCategory( self, category_id = amt_util.GENRES, list_category = 0 ):
        #print 'setcategory:', category_id, list_category, self.main_category
        self.category_id = category_id
        self.list_category = list_category
        #if ( category_id >= 0 or category_id <= amt_util.FAVORITES ):
        if ( list_category > 0 ):
            if ( category_id == amt_util.FAVORITES ):
                sql = 'SELECT * FROM Movies WHERE favorite = ? ORDER BY title'
                params = ( 1, )
            elif ( category_id == amt_util.DOWNLOADED ):
                sql = 'SELECT * FROM Movies WHERE saved_location != ? ORDER BY title'
                params = ( '', )
            elif ( list_category == 1 ):
                sql = 'SELECT * FROM Movies WHERE %s&genre > ? ORDER BY title' % ( self.genres[category_id].id, )
                params = ( 0, )
            elif ( list_category == 2 ):
                sql = 'SELECT * FROM Movies WHERE studio = ? ORDER BY title'
                params = ( self.trailers.categories[category_id].title, )
            elif ( list_category == 3 ):
                sql = 'SELECT * FROM Movies WHERE actors LIKE ? ORDER BY title'
                names = self.actor.split( ' ' )[:2]
                if ( len( names ) == 1 ):
                    params = ( '%%%s%%' % ( names[0], ), )
                else:
                    params = ( '%%%s %s%%' % ( names[0], names[1], ), )
            #elif ( list_category == 2 ):
            #    sql = 'SELECT * FROM Movies WHERE actors LIKE ? ORDER BY title'
            #    params = ( '%%%s%%' % ( self.controls['Cast List']['control'].getSelectedItem().getLabel(), ), )
            ##print sql
            self.showTrailers( sql, params )
        else:
            self.main_category = category_id
            if ( category_id == amt_util.GENRES ):
                sql = 'SELECT title, count, url, id, loaded FROM Genres ORDER BY title'
            elif ( category_id == amt_util.STUDIOS ):
                sql = 'SELECT title, count FROM Studios ORDER BY title'
            elif ( category_id == amt_util.ACTORS ):
                sql = 'SELECT name, count FROM Actors ORDER BY name'
            self.showCategories( sql )
        self.showControls( self.category_id <= amt_util.GENRES and self.category_id > amt_util.FAVORITES )
        if ( self.category_id <= amt_util.GENRES and self.category_id > amt_util.FAVORITES ):
            if ( self.trailers.categories ): self.setFocus( self.controls['Category List']['control'] )
        else:
            if ( self.trailers.movies ): self.setFocus( self.controls['Trailer List']['control'] )

    def showCategories( self, sql, params = None, choice = 0, force_update = False ):
        try:
            #self.debugWrite('getGenreCategories', 2)
            xbmcgui.lock()
            if ( sql != self.sql_category or params != self.params_category or force_update ):
                self.list_control_pos = 0
                self.trailers.getCategories( sql, params )
                self.sql_category = sql
                self.params_category = params
                self.controls['Category List']['control'].reset()
                if ( self.trailers.categories ):
                    for category in self.trailers.categories:
                        if ( self.category_id ) == amt_util.GENRES: thumb_category = 'genre'
                        elif ( self.category_id ) == amt_util.STUDIOS: thumb_category = 'studio'
                        else: thumb_category = 'actor'
                        thumbnail = os.path.join( self.image_path, '%s.tbn' % ( category.title, ))
                        if ( not os.path.isfile( thumbnail )):
                            thumbnail = os.path.join( self.image_path, 'generic-%s.tbn' % ( thumb_category, ) )
                        count = '(%d)' % ( category.count, )
                        self.controls['Category List']['control'].addItem( xbmcgui.ListItem( category.title, count, thumbnail, thumbnail ) )
                    ################
                    self.setSelection( 'Category List', self.list_control_pos )
                    #self.setSelection( 'Trailer List', choice + ( choice == -1 ) )
        except: pass #traceback.print_exc()
        xbmcgui.unlock()

    def showTrailers( self, sql, params = None, choice = 0, force_update = False ):
        try:
            if ( sql != self.sql or params != self.params or force_update ): self.trailers.getMovies( sql, params )
            xbmcgui.lock()
            self.sql = sql
            self.params = params
            self.controls['Trailer List']['control'].reset()
            if ( self.trailers.movies ):
                for movie in self.trailers.movies: # now fill the list control
                    if ( self.settings.thumbnail_display == 0 ): 
                        if ( movie.watched ): thumbnail = movie.thumbnail_watched
                        else: thumbnail = movie.thumbnail
                    elif ( self.settings.thumbnail_display == 1 ): thumbnail = os.path.join( self.image_path, 'generic-trailer.tbn' )
                    else: thumbnail = ''
                    favorite = [ '', '*' ][ movie.favorite ]
                    favorite = [ favorite, '!' ][ not movie.trailer_urls ]
                    if ( movie.rating ): rating = '[%s]' % movie.rating
                    else: rating = ''
                    self.controls['Trailer List']['control'].addItem( xbmcgui.ListItem( '%s%s' % ( favorite, movie.title, ), rating, thumbnail, thumbnail ) )
                self.setSelection( 'Trailer List', choice + ( choice == -1 ) )
            else: self.clearTrailerInfo()
        except:
            traceback.print_exc()
        xbmcgui.unlock()

    def calcScrollbarVisibilty( self, list_control ):
        if ( self.controls[list_control]['special'] ):
            if ( ( ( self.category_id >= 0 or self.category_id <= amt_util.FAVORITES ) and list_control != 'Category List' ) or 
                  ( self.category_id <= amt_util.GENRES and self.category_id > amt_util.FAVORITES and list_control == 'Category List' ) ):
                visible = ( self.controls[list_control]['control'].size() > self.controls[list_control]['special'] )
                visible2 = not visible
                if ( list_control == 'Cast List' and not self.display_cast ):
                    visible = False
                    visible2 = False
                self.showScrollbar( visible, visible2, list_control )
                ######self.setSelection( list_control )
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
        self.list_control_pos = self.controls[list_control]['control'].getSelectedPosition()
            
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
            self.controls['Category List']['control'].setEnabled( category and self.trailers.categories != None )
            self.controls['Category List Count Label']['control'].setVisible( category )
            try: self.controls['Trailer List Backdrop']['control'].setVisible( not category )
            except: pass
            self.controls['Trailer List']['control'].setVisible( not category )
            self.controls['Trailer List']['control'].setEnabled( not category and self.trailers.movies != None )
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
        category= 'oops'
        if ( self.category_id == amt_util.GENRES ):
            category = _( 219 )
        elif ( self.category_id == amt_util.STUDIOS ):
            category = _( 223 )
        elif ( self.category_id == amt_util.ACTORS ):
            category = _( 225 )
        elif ( self.category_id == amt_util.FAVORITES ):
            category = _( 217 )
        elif ( self.category_id == amt_util.DOWNLOADED ):
            category = _( 226 )
        elif ( self.category_id >= 0 ):
            if ( self.list_category == 3 ):
                category = self.actor
            elif ( self.list_category == 2 ):
                category = self.trailers.categories[self.category_id].title
            elif ( self.list_category == 1 ):
                category = self.genres[self.category_id].title
        self.controls['Category Label']['control'].setLabel( category )
            
    def setCountLabel( self, list_control ):
        pos = self.controls['%s' % list_control]['control'].getSelectedPosition()
        self.controls['%s Count Label' % list_control]['control'].setLabel( '%d of %d' % ( pos + 1, self.controls['%s' % list_control]['control'].size(), ))
        return pos
    
    def clearTrailerInfo( self ):
        self.controls['Trailer Poster']['control'].setImage( '' )
        self.controls['Trailer Rating']['control'].setImage( '' )
        self.controls['Trailer Title']['control'].setLabel( '' )
        # Plot
        self.controls['Trailer Plot']['control'].reset()
        self.controls['Trailer Plot']['control'].setText( '' )#_( 400 ) )
        # Cast
        self.controls['Cast List']['control'].reset()
        
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
            self.controls['Trailer Rating']['control'].setImage( self.trailers.movies[trailer].rating_url )
            self.controls['Trailer Title']['control'].setLabel( self.trailers.movies[trailer].title )
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
        except: pass
        xbmcgui.unlock()
        
    def showOverlays( self, trailer ):
        posx, posy = self.controls['Trailer Favorite Overlay'][ 'control' ].getPosition()# + self.coordinates[0]
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
        if ( self.main_category == amt_util.STUDIOS ): 
            list_category = 2
        elif ( self.main_category == amt_util.ACTORS ): 
            list_category = 3
            self.actor = self.controls['Category List']['control'].getSelectedItem().getLabel()
        else: list_category = 1
        self.setCategory( genre, list_category )

    def getActorChoice( self ):
        choice = self.controls['Cast List']['control'].getSelectedPosition()
        self.actor = self.controls['Cast List']['control'].getSelectedItem().getLabel()
        self.setCategory( choice, 3 )

    def playTrailer( self ):
        try:
            #self.debugWrite('PlayTrailer', 2)
            trailer = self.controls['Trailer List']['control'].getSelectedPosition()
            trailer_urls = self.trailers.movies[trailer].trailer_urls
            if ( self.settings.trailer_quality >= len( trailer_urls )):
                choice = len( trailer_urls ) - 1
            else:
                choice = self.settings.trailer_quality
            while ( 'p.mov' in trailer_urls[ choice ] or choice == -1 ): choice -= 1
            
            if ( choice >= 0 ):
                if ( self.settings.mode == 0 ):
                    filename = trailer_urls[choice]
                elif ( self.settings.mode == 1):
                    url = trailer_urls[choice]
                    fetcher = cacheurl.HTTPProgressSave()
                    filename = str( fetcher.urlretrieve( url ) )
                elif ( self.settings.mode == 2):
                    url = trailer_urls[choice]
                    ext = os.path.splitext( url )[ 1 ]
                    title = '%s%s' % (self.trailers.movies[trailer].title, ext, )
                    fetcher = cacheurl.HTTPProgressSave( self.settings.save_folder, title )
                    filename = str( fetcher.urlretrieve( url ) )
                    if ( filename ):
                        poster = self.trailers.movies[trailer].poster
                        if ( not poster ): poster = os.path.join( self.image_path, 'blank-poster.tbn' )
                        self.saveThumbnail( filename, trailer, poster, )
            else: filename = None
            if ( filename ):
                self.MyPlayer.play( filename )
                xbmc.sleep( 500 )
                self.markAsWatched( self.trailers.movies[ trailer ].watched + 1, self.trailers.movies[ trailer ].title, trailer )
                #self.changed_trailers = False
        except: traceback.print_exc()

    def saveThumbnail( self, filename, trailer, poster ):
        #self.debugWrite( 'saveThumbnail', 2 )
        try: 
            new_filename = '%s.tbn' % ( os.path.splitext( filename )[0], )
            if ( not os.path.isfile( new_filename ) ):
                shutil.copyfile( poster, new_filename )
            if ( self.trailers.movies[ trailer ].saved == '' ):
                success = self.trailers.updateRecord( 'Movies', ( 'saved_location', ), ( ( filename, self.trailers.movies[ trailer ].title, ), ), 'title' )
                if ( success ): self.trailers.movies[ trailer ].saved = filename
                #self.showTrailers( trailer )
        except: traceback.print_exc()
    
    def showContextMenu( self, list_control ):
        cm = context_menu.GUI( win=self, language=_, list_control=list_control )
        cm.doModal()
        del cm

    def markAsWatched( self, watched, trailer, index ):
        if ( watched ): date = datetime.date.today()
        else: date = ''
        success = self.trailers.updateRecord( 'Movies', ( 'times_watched', 'last_watched', ), ( ( watched, date, trailer, ), ), 'title' )
        if ( success ):
            self.trailers.movies[index].watched = watched
            self.showTrailers( self.sql, self.params, choice = index )
        
    def changeSettings( self ):
        import guisettings
        #self.debugWrite('changeSettings', 2)
        thumbnail_display = self.settings.thumbnail_display
        settings = guisettings.GUI( language=_ , genres=self.genres, skin=self.skin )
        settings.doModal()
        del settings
        self.getSettings()
        if ( thumbnail_display != self.settings.thumbnail_display and self.category_id != amt_util.GENRES and self.category_id != amt_util.STUDIOS and self.category_id != amt_util.ACTORS ):
            trailer = self.controls['Trailer List']['control'].getSelectedPosition()
            self.showTrailers( self.sql, self.params, choice = trailer )
        self.setShortcutLabels()
        
    def setShortcutLabels( self ):
        if ( self.settings.shortcut1 == amt_util.FAVORITES ):
            self.controls[ 'Shortcut1 Button' ][ 'control' ].setLabel( _( 217 ) )
        elif ( self.settings.shortcut1 == amt_util.DOWNLOADED ):
            self.controls[ 'Shortcut1 Button' ][ 'control' ].setLabel( _( 226 ) )
        else:
            self.controls[ 'Shortcut1 Button' ][ 'control' ].setLabel( str( self.genres[ self.settings.shortcut1 ].title ) )
        if ( self.settings.shortcut2 == amt_util.FAVORITES ):
            self.controls[ 'Shortcut2 Button' ][ 'control' ].setLabel( _( 217 ) )
        elif ( self.settings.shortcut2 == amt_util.DOWNLOADED ):
            self.controls[ 'Shortcut2 Button' ][ 'control' ].setLabel( _( 226 ) )
        else:
            self.controls[ 'Shortcut2 Button' ][ 'control' ].setLabel( str( self.genres[ self.settings.shortcut2 ].title ) )
        if ( self.settings.shortcut3 == amt_util.FAVORITES ):
            self.controls[ 'Shortcut3 Button' ][ 'control' ].setLabel( _( 217 ) )
        elif ( self.settings.shortcut3 == amt_util.DOWNLOADED ):
            self.controls[ 'Shortcut3 Button' ][ 'control' ].setLabel( _( 226 ) )
        else:
            self.controls[ 'Shortcut3 Button' ][ 'control' ].setLabel( str( self.genres[ self.settings.shortcut3 ].title ) )

    def showCredits( self ):
        import credits
        cw = credits.GUI( language=_, skin=self.skin )
        cw.doModal()
        del cw

    def updateScript( self ):
        import update
        updt = update.Update( language=_, script=default.__scriptname__, version=default.__version__ )
        del update
        
    def toggleAsWatched( self ):
        trailer = self.setCountLabel( 'Trailer List' )
        watched = not ( self.trailers.movies[ trailer ].watched > 0 )
        self.markAsWatched( watched, self.trailers.movies[ trailer ].title, trailer )
  
    def toggleAsFavorite( self ):
        trailer = self.setCountLabel( 'Trailer List' )
        favorite = not self.trailers.movies[ trailer ].favorite
        success = self.trailers.updateRecord( 'Movies', ( 'favorite', ), ( ( favorite, self.trailers.movies[ trailer ].title, ), ), 'title' )
        if ( success ):
            self.trailers.movies[ trailer ].favorite = favorite
            if ( self.category_id == amt_util.FAVORITES ):
                params = ( 1, )
                choice = trailer - 1 + ( trailer == 0 )
                force_update = True
            else: 
                params = self.params
                choice = trailer
                force_update = False
            self.showTrailers( self.sql, params = params, choice = choice, force_update = force_update )
    
    def refreshInfo( self, refresh_all ):
        xbmc.sleep(200)
        '''
        if ( refresh_all ):
            self.trailers.update_all( force_update = True )
        else:
            self.trailers.movies[self.list_item].__update__()
        self.showTrailers( self.sql, choice = self.list_item )
        '''
        
    def deleteSavedTrailer( self ):
        trailer = self.setCountLabel( 'Trailer List' )
        saved_trailer = self.trailers.movies[ trailer ].saved
        if ( xbmcgui.Dialog().yesno( '%s?' % ( _( 509 ), ), _( 82 ), saved_trailer ) ):
            if ( os.path.isfile( saved_trailer ) ):
                os.remove( saved_trailer )
            if ( os.path.isfile( '%s.conf' % ( saved_trailer, ) ) ):
                os.remove( '%s.conf' % ( saved_trailer, ) )
            if ( os.path.isfile( '%s.tbn' % ( os.path.splitext( saved_trailer )[0], ) ) ):
                os.remove( '%s.tbn' % ( os.path.splitext( saved_trailer )[0], ) )
            success = self.trailers.updateRecord( 'Movies', ( 'saved_location', ), ( ( '', self.trailers.movies[ trailer ].title, ), ), 'title' )
            if ( success ):
                self.trailers.movies[ trailer ].saved = ''
                if ( self.category_id == amt_util.DOWNLOADED ): force_update = True
                else: force_update = False
                self.showTrailers( self.sql, self.params, choice = trailer, force_update = force_update )

    def exitScript( self ):
        #self.debugWrite( 'exitScript', 2 )
        try:
            pass
        finally:
            if ( self.Timer ): self.Timer.cancel()
            self.close()

    def setShortcut( self, shortcut ):
        if ( self.main_category == -1 ):
            self.sql_category = 'SELECT title, count, url, id, loaded FROM Genres ORDER BY title'
            self.params_category = None
            self.main_category = -1
            #self.trailers.getCategories( self.sql_category, self.params_category )
            self.trailers.categories = self.genres
        self.setCategory( shortcut, 1 )

    def onControl( self, control ):
        try:
            if ( control is self.controls['Shortcut1 Button']['control'] ):
                #self.setShortcut( self.settings.shortcut1 )
                self.setCategory( self.settings.shortcut1, 1 )
            elif ( control is self.controls['Shortcut2 Button']['control'] ):
                #self.setShortcut( self.settings.shortcut2 )
                self.setCategory( self.settings.shortcut2, 1 )
            elif ( control is self.controls['Shortcut3 Button']['control'] ):
                self.setCategory( self.settings.shortcut3, 1 )
            elif ( control is self.controls['Genre Button']['control'] ):
                self.setCategory( amt_util.GENRES, 0 )
            elif ( control is self.controls['Studio Button']['control'] ):
                self.setCategory( amt_util.STUDIOS, 0 )
            elif ( control is self.controls['Actor Button']['control'] ):
                self.setCategory( amt_util.ACTORS, 0 )
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
                self.getActorChoice()
            else:
                try:
                    if ( control is self.controls[ 'Optional Button' ][ 'control' ] ):
                        exec self.controls[ 'Optional Button' ][ 'onclick' ]
                except: pass
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
                    #if ( self.main_category == -99 ): self.main_category = amt_util.ACTORS
                    self.setCategory( self.main_category, 0 )
                elif ( button_key == 'Keyboard Menu Button' or button_key == 'Remote Title' or button_key == 'White Button' ):
                    self.showContextMenu( 'Trailer List' )
                else:# ( button_key == 'n/a' or button_key == 'DPad Up' or button_key == 'Remote Up' or button_key == 'DPad Down' or button_key == 'Remote Down' ):
                    self.showTrailerInfo()
            elif ( control is self.controls['Trailer List Scrollbar Position Indicator']['control'] ):
                if ( button_key == 'Keyboard Up Arrow' or button_key == 'Remote Up' or button_key == 'DPad Up' ):
                    self.pageIndicator( 'Trailer List', -1 )
                elif ( button_key == 'Keyboard Down Arrow' or button_key == 'Remote Down' or button_key == 'DPad Down' ):
                    self.pageIndicator( 'Trailer List', 1 )
            elif ( control is self.controls['Category List']['control'] ):
                if ( button_key == 'Keyboard Menu Button' or button_key == 'Remote Title' or button_key == 'White Button' ):
                    self.showContextMenu( 'Category List' )
                else:
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
                if ( button_key == 'Keyboard Menu Button' or button_key == 'Remote Title' or button_key == 'White Button' ):
                    self.showContextMenu( 'Cast List' )
                else:
                    self.setScrollbarIndicator( 'Cast List' )
            elif ( control is self.controls['Cast List Scrollbar Position Indicator']['control'] ):
                if ( button_key == 'Keyboard Up Arrow' or button_key == 'Remote Up' or button_key == 'DPad Up' ):
                    self.pageIndicator( 'Cast List', -1 )
                elif ( button_key == 'Keyboard Down Arrow' or button_key == 'Remote Down' or button_key == 'DPad Down' ):
                    self.pageIndicator( 'Cast List', 1 )
            elif ( control is self.controls['Shortcut1 Button']['control'] ):
                self.setControlNavigation( 'Shortcut1 Button' )
            elif ( control is self.controls['Shortcut2 Button']['control'] ):
                self.setControlNavigation( 'Shortcut2 Button' )
            elif ( control is self.controls['Shortcut3 Button']['control'] ):
                self.setControlNavigation( 'Shortcut3 Button' )
            elif ( control is self.controls['Genre Button']['control'] ):
                self.setControlNavigation( 'Genre Button' )
            elif ( control is self.controls['Studio Button']['control'] ):
                self.setControlNavigation( 'Studio Button' )
            elif ( control is self.controls['Actor Button']['control'] ):
                self.setControlNavigation( 'Actor Button' )
            elif ( control is self.controls['Search Button']['control'] ):
                self.setControlNavigation( 'Search Button' )
            elif ( control is self.controls['Settings Button']['control'] ):
                self.setControlNavigation( 'Settings Button' )
            else:
                try:
                    if ( control is self.controls[ 'Optional Button' ][ 'control' ] ):
                        self.setControlNavigation( 'Optional Button' )
                except: pass
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
    







