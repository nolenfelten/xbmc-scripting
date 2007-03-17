'''
Main GUI for Apple Movie Trailers
'''

import xbmc, xbmcgui, traceback, guibase
from guibase import _

class GUI( guibase.GUI ):

    def __init__( self ):
        try:
            custom_imports = [ 'context_menu', 'cacheurl', 'utilities' ]
            guibase.GUI.__init__( self, custom_imports )
            for name in self.imported.keys():
                globals().update( { name: self.imported[name] } )
            ## enable when ready
            self.controls['Search Button']['control'].setEnabled( False )
            #self.setControlsDisabled()
            self.setStartupChoices()
            self.setStartupCategory()
        except:
            traceback.print_exc()
            self.exitScript()
        '''
    def setControlsDisabled( self ):
        try: self.controls['Category List Backdrop']['control'].setEnabled( False )
        except: pass
        try: self.controls['Trailer List Backdrop']['control'].setEnabled( False )
        except: pass
        try: self.controls['Cast List Backdrop']['control'].setEnabled( False )
        except: pass
        '''
        
    def setupVariables( self ):
        guibase.GUI.setupVariables( self )
        import trailers, database
        self.trailers = trailers.Trailers()
        self.query= database.Query()
        self.sql = None
        self.params = None
        self.display_cast = False
        self.dummy()
        self.MyPlayer = MyPlayer( xbmc.PLAYER_CORE_MPLAYER, function=self.myPlayerChanged )
        self.update_method = 0
        self.list_control_pos = [ 0, 0, 0, 0 ]

    # dummy() and self.Timer are currently used for the Player() subclass so when an onPlayback* event occurs, 
    # it calls myPlayerChanged() immediately.
    def dummy( self ):
        import threading
        #self.debugWrite('dummy', 2)
        self.Timer = threading.Timer( 60*60*60, self.dummy,() )
        self.Timer.start()

    def myPlayerChanged( self, event ):
        pass
        #self.debugWrite('myPlayerChanged', 2)
        #if ( event == 0 and self.currently_playing_movie[1] >= 0 ):
        #    self.markAsWatched( self.currently_playing_movie[0] + 1, self.currently_playing_movie[1], self.currently_playing_movie[2] )
        #elif ( event == 2 ):
        #    self.currently_playing_movie = -1
        #    self.currently_playing_genre = -1
        
    def setStartupChoices( self ):
        self.sql_category = ''#'SELECT title, count, url, id, loaded FROM Genres ORDER BY title'
        self.params_category = None
        self.main_category = utilities.GENRES
        self.genres = self.trailers.categories
        self.current_display = [ [ utilities.GENRES , 0 ], [ 0, 1 ] ]
        self.setShortcutLabels()

    def setStartupCategory( self ):
        startup_button = 'Shortcut1'
        if ( self.settings[ "startup_category_id" ] == self.settings[ "shortcut2" ] ): startup_button = 'Shortcut2'
        elif ( self.settings[ "startup_category_id" ] == self.settings[ "shortcut3" ] ): startup_button = 'Shortcut3'
        self.setControlNavigation( '%s Button' % ( startup_button, ) )
        self.setCategory( self.settings[ "startup_category_id" ], 1 )

    def setCategory( self, category_id = None, list_category = 0 ):
        # slight change to allow for the dynamic importing in guibase
        if category_id == None:
            category_id = utilities.GENRES
        self.category_id = category_id
        self.list_category = list_category
        if ( list_category > 0 ):
            if ( category_id == utilities.FAVORITES ):
                sql = self.query[ 'favorites' ]#'SELECT * FROM Movies WHERE favorite = ? ORDER BY title'
                params = ( 1, )
            elif ( category_id == utilities.DOWNLOADED ):
                sql = self.query[ 'downloaded' ]#'SELECT * FROM Movies WHERE saved_location != ? ORDER BY title'
                params = ( '', )
            elif ( list_category == 1 ):
                sql = self.query[ 'movies_by_genre_id' ]
                params = ( self.genres[category_id].id, )
            elif ( list_category == 2 ):
                sql = self.query[ 'movies_by_studio_name' ]#'SELECT * FROM Movies WHERE upper(studio) = ? ORDER BY title'
                params = ( self.trailers.categories[category_id].title.upper(), )
            elif ( list_category == 3 ):
                sql = self.query[ 'movies_by_actor_name' ]#'SELECT * FROM Movies WHERE upper(actors) LIKE ? ORDER BY title'
                names = self.actor.split( ' ' )[:2]
                if ( len( names ) == 1 ):
                    params = ( '%%%s%%' % ( names[0].upper(), ), )
                else:
                    params = ( '%%%s %s%%' % ( names[0].upper(), names[1].upper(), ), )
            self.current_display = [ self.current_display[ 0 ], [ category_id, list_category ] ]
            self.showTrailers( sql, params )
        else:
            self.main_category = category_id
            if ( category_id == utilities.GENRES ):
                sql = self.query[ 'genre_category_list' ]#'SELECT title, count, url, id, loaded FROM Genres ORDER BY title'
            elif ( category_id == utilities.STUDIOS ):
                sql = self.query[ 'studio_category_list' ]#"SELECT * FROM Studios ORDER BY title"
            elif ( category_id == utilities.ACTORS ):
                sql = self.query[ 'actor_category_list' ]#'SELECT * FROM Actors ORDER BY name'
            self.current_display = [ [ category_id, list_category ], self.current_display[ 1 ] ]
            self.showCategories( sql )
        self.showControls( self.category_id <= utilities.GENRES and self.category_id > utilities.FAVORITES )
        if ( self.category_id <= utilities.GENRES and self.category_id > utilities.FAVORITES ):
            if ( self.trailers.categories ): self.setFocus( self.controls['Category List']['control'] )
        else:
            if ( self.trailers.movies ): self.setFocus( self.controls['Trailer List']['control'] )

    def showCategories( self, sql, params = False, choice = 0, force_update = False ):
        try:
            #self.debugWrite('getGenreCategories', 2)
            xbmcgui.lock()
            if ( sql != self.sql_category or params != self.params_category or force_update ):
                self.list_control_pos[ self.list_category ] = 0
                self.trailers.getCategories( sql, params )
                self.sql_category = sql
                self.params_category = params
                self.controls['Category List']['control'].reset()
                if ( self.trailers.categories ):
                    for category in self.trailers.categories:
                        if ( self.category_id ) == utilities.GENRES: thumb_category = 'genre'
                        elif ( self.category_id ) == utilities.STUDIOS: thumb_category = 'studio'
                        else: thumb_category = 'actor'
                        thumbnail = os.path.join( self.image_path, '%s.tbn' % ( category.title, ))
                        if ( not os.path.isfile( thumbnail )):
                            thumbnail = os.path.join( self.image_path, 'generic-%s.tbn' % ( thumb_category, ) )
                        count = '(%d)' % ( category.count, )
                        self.controls['Category List']['control'].addItem( xbmcgui.ListItem( category.title, count, thumbnail, thumbnail ) )
                    ################
                    self.setSelection( 'Category List', self.list_control_pos[ self.list_category ] )
                    #self.setSelection( 'Trailer List', choice + ( choice == -1 ) )
        except: traceback.print_exc()
        xbmcgui.unlock()

    def showTrailers( self, sql, params = None, choice = 0, force_update = False ):
        try:
            if ( sql != self.sql or params != self.params or force_update ):
                self.list_control_pos[ self.list_category ]  = choice
                self.trailers.getMovies( sql, params )
            else: choice = self.list_control_pos[ self.list_category ]
            xbmcgui.lock()
            self.sql = sql
            self.params = params
            self.controls['Trailer List']['control'].reset()
            if ( self.trailers.movies ):
                for movie in self.trailers.movies: # now fill the list control
                    if ( self.settings[ "thumbnail_display" ] == 0 ): 
                        if ( movie.watched ): thumbnail = movie.thumbnail_watched
                        else: thumbnail = movie.thumbnail
                    elif ( self.settings[ "thumbnail_display" ] == 1 ): thumbnail = os.path.join( self.image_path, 'generic-trailer.tbn' )
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
            if ( ( ( self.category_id >= 0 or self.category_id <= utilities.FAVORITES ) and list_control != 'Category List' ) or 
                ( self.category_id <= utilities.GENRES and self.category_id > utilities.FAVORITES and list_control == 'Category List' ) ):
                visible = ( self.controls[list_control]['control'].size() > self.getListControlItemsPerPage( list_control ) )
                if ( list_control == 'Cast List' and not self.display_cast ):
                    visible = False
                self.showScrollbar( visible, list_control )
                ######self.setSelection( list_control )
            else: self.showScrollbar( False, list_control )

    def getListControlItemsPerPage( self, list_control ):
        height = self.controls[ list_control ][ 'control' ].getItemHeight() + self.controls[ list_control ][ 'control' ].getSpace()
        totalheight = self.controls[ list_control ][ 'control' ].getHeight() - height
        items_per_page = int(float(totalheight) / float(height))
        return items_per_page
        
    def showScrollbar( self, visible, list_control ):
        try:
            self.controls['%s Scrollbar Position Indicator' % ( list_control, )]['control'].setVisible( visible )
            self.controls['%s Scrollbar Position Indicator' % ( list_control, )]['control'].setEnabled( visible )
        except: pass
            
    def setScrollbarIndicator( self, list_control ):
        try:
            if ( self.controls[list_control]['special'] ):
                if ( self.controls[list_control]['control'].size() > self.getListControlItemsPerPage( list_control ) ):
                    offset = float( self.controls['%s Scrollbar Middle' % ( list_control, )][ 'control' ].getHeight() - self.controls['%s Scrollbar Position Indicator' % ( list_control, )][ 'control' ].getHeight() ) / float( self.controls[list_control]['control'].size() - 1 )
                    posy = int( self.controls['%s Scrollbar Middle' % ( list_control, )][ 'control' ].getPosition()[ 1 ] + ( offset * self.controls[list_control]['control'].getSelectedPosition() ) )
                    self.controls['%s Scrollbar Position Indicator' % ( list_control, )]['control'].setPosition( self.controls['%s Scrollbar Position Indicator' % ( list_control, )][ 'control' ].getPosition()[ 0 ], posy )
        except: pass
        if ( list_control != 'Cast List' ): self.list_control_pos[ self.list_category ] = self.controls[list_control]['control'].getSelectedPosition()
            
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
        items_per_page = self.getListControlItemsPerPage( list_control )
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
            self.controls['Category List']['control'].setVisible( category )
            self.controls['Category List']['control'].setEnabled( category and self.trailers.categories != None )
            self.controls['Trailer List']['control'].setVisible( not category )
            self.controls['Trailer List']['control'].setEnabled( not category and self.trailers.movies != None )
            self.calcScrollbarVisibilty( 'Trailer List' )
            self.calcScrollbarVisibilty( 'Category List' )
            self.showPlotCastControls( category )
            self.setCategoryLabel()
        except: pass
        xbmcgui.unlock()
            
    def showPlotCastControls( self, category ):
        try:
            xbmcgui.lock()
            self.controls['Plot Button']['control'].setVisible( self.display_cast and not category )
            self.controls['Plot Button']['control'].setEnabled( self.display_cast and not category )
            self.controls['Cast Button']['control'].setVisible( not self.display_cast and not category )
            self.controls['Cast Button']['control'].setEnabled( not self.display_cast and not category )
            self.calcScrollbarVisibilty( 'Cast List' )
        except: pass
        xbmcgui.unlock()
            
    def togglePlotCast( self ):
        #self.debugWrite('togglePlotCast', 2)
        self.display_cast = not self.display_cast
        self.showPlotCastControls( False )
        if ( self.display_cast ): self.setFocus( self.controls['Plot Button']['control'] )
        else: self.setFocus( self.controls['Cast Button']['control'] )

    def setCategoryLabel( self ):
        category= 'oops'
        if ( self.category_id == utilities.GENRES ):
            category = _( 219 )
        elif ( self.category_id == utilities.STUDIOS ):
            category = _( 223 )
        elif ( self.category_id == utilities.ACTORS ):
            category = _( 225 )
        elif ( self.category_id == utilities.FAVORITES ):
            category = _( 217 )
        elif ( self.category_id == utilities.DOWNLOADED ):
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
        self.controls['Trailer List Count Label']['control'].setLabel( '' )
        
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
                    self.controls['Cast List']['control'].addItem( xbmcgui.ListItem( actor[ 0 ], '', thumbnail, thumbnail ) )
            else: 
                self.cast_exists = False
                self.controls['Cast List']['control'].addItem( _( 401 ) )
            self.showPlotCastControls( False )
            #self.calcScrollbarVisibilty( 'Cast List' )
            self.setScrollbarIndicator( 'Trailer List' )
            self.setScrollbarIndicator( 'Cast List' )
            self.showOverlays( trailer )
        except: pass
        xbmcgui.unlock()
        
    def showOverlays( self, trailer ):
        posx, posy = self.controls['Trailer Favorite Overlay'][ 'control' ].getPosition()
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
        if ( self.main_category == utilities.STUDIOS ): 
            list_category = 2
        elif ( self.main_category == utilities.ACTORS ): 
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
            if ( self.settings[ "trailer_quality" ] >= len( trailer_urls )):
                choice = len( trailer_urls ) - 1
            else:
                choice = self.settings[ "trailer_quality" ]
            while ( 'p.mov' in trailer_urls[ choice ] or choice == -1 ): choice -= 1
            
            if ( choice >= 0 ):
                if ( self.settings[ "mode" ] == 0 ):
                    filename = trailer_urls[choice]
                elif ( self.settings[ "mode" ] == 1):
                    url = trailer_urls[choice]
                    fetcher = cacheurl.HTTPProgressSave()
                    filename = str( fetcher.urlretrieve( url ) )
                elif ( self.settings[ "mode" ] >= 2):
                    url = trailer_urls[choice]
                    ext = os.path.splitext( url )[ 1 ]
                    title = '%s%s' % (self.trailers.movies[trailer].title, ext, )
                    fetcher = cacheurl.HTTPProgressSave( self.settings[ "save_folder" ], title )
                    filename = str( fetcher.urlretrieve( url ) )
                    if ( filename ):
                        poster = self.trailers.movies[trailer].poster
                        if ( not poster ): poster = os.path.join( self.image_path, 'blank-poster.tbn' )
                        self.saveThumbnail( filename, trailer, poster )
            else: filename = None
            if ( filename ):
                self.MyPlayer.play( filename )
                xbmc.sleep( 500 )
                self.markAsWatched( self.trailers.movies[ trailer ].watched + 1, trailer )
                #self.changed_trailers = False
        except: traceback.print_exc()

    def saveThumbnail( self, filename, trailer, poster ):
        #self.debugWrite( 'saveThumbnail', 2 )
        try: 
            new_filename = '%s.tbn' % ( os.path.splitext( filename )[0], )
            if ( not os.path.isfile( new_filename ) ):
                shutil.copyfile( poster, new_filename )
            if ( self.trailers.movies[ trailer ].saved == '' ):
                success = self.trailers.updateRecord( 'movies', ( 'saved_location', ), ( filename, self.trailers.movies[ trailer ].idMovie, ), 'idMovie' )
                if ( success ): self.trailers.movies[ trailer ].saved = filename
                #self.showTrailers( trailer )
        except: traceback.print_exc()
    
    def showContextMenu( self, list_control ):
        cm = context_menu.GUI( win=self, language=_, list_control=list_control )
        if ( cm.gui_loaded ):
            cm.doModal()
        del cm

    def force_full_update( self ):
        categories = self.trailers.categories
        self.trailers.categories = self.genres
        #self.setCategory( shortcut, 1 )
        self.trailers.fullUpdate()
        self.trailers.categories = categories

    def markAsWatched( self, watched, trailer ):
        if ( watched ): date = datetime.date.today()
        else: date = ''
        success = self.trailers.updateRecord( 'movies', ( 'times_watched', 'last_watched', ), ( watched, date, self.trailers.movies[ trailer ].idMovie, ), 'idMovie' )
        if ( success ):
            self.trailers.movies[trailer].watched = watched
            self.showTrailers( self.sql, self.params, choice = trailer )

    def changeSettings( self ):
        import settings
        #self.debugWrite("changeSettings", 2)
        thumbnail_display = self.settings[ "thumbnail_display" ]
        settings = settings.GUI( language=_ , genres=self.genres, skin=self.skin )
        if ( settings.gui_loaded ):
            settings.doModal()
            ok = False
            if ( settings.changed ):
                self.getSettings()
                if ( settings.restart ):
                    ok = xbmcgui.Dialog().yesno( __scriptname__, _( 240 ), "", _( 241 ) % ( __scriptname__, ), _( 256 ), _( 255 ) )
            del settings
            if ( not ok ):
                if ( thumbnail_display != self.settings[ "thumbnail_display" ] and self.category_id != utilities.GENRES and self.category_id != utilities.STUDIOS and self.category_id != utilities.ACTORS ):
                    trailer = self.controls[ "Trailer List" ][ "control" ].getSelectedPosition()
                    self.showTrailers( self.sql, self.params, choice = trailer )
                self.setShortcutLabels()
            else: self.exitScript( True )

    def setShortcutLabels( self ):
        if ( self.settings[ "shortcut1" ] == utilities.FAVORITES ):
            self.controls[ 'Shortcut1 Button' ][ 'control' ].setLabel( _( 217 ) )
        elif ( self.settings[ "shortcut1" ] == utilities.DOWNLOADED ):
            self.controls[ 'Shortcut1 Button' ][ 'control' ].setLabel( _( 226 ) )
        else:
            self.controls[ 'Shortcut1 Button' ][ 'control' ].setLabel( str( self.genres[ self.settings[ "shortcut1" ] ].title ) )
        if ( self.settings[ "shortcut2" ] == utilities.FAVORITES ):
            self.controls[ 'Shortcut2 Button' ][ 'control' ].setLabel( _( 217 ) )
        elif ( self.settings[ "shortcut2" ] == utilities.DOWNLOADED ):
            self.controls[ 'Shortcut2 Button' ][ 'control' ].setLabel( _( 226 ) )
        else:
            self.controls[ 'Shortcut2 Button' ][ 'control' ].setLabel( str( self.genres[ self.settings[ "shortcut2" ] ].title ) )
        if ( self.settings[ "shortcut3" ] == utilities.FAVORITES ):
            self.controls[ 'Shortcut3 Button' ][ 'control' ].setLabel( _( 217 ) )
        elif ( self.settings[ "shortcut3" ] == utilities.DOWNLOADED ):
            self.controls[ 'Shortcut3 Button' ][ 'control' ].setLabel( _( 226 ) )
        else:
            self.controls[ 'Shortcut3 Button' ][ 'control' ].setLabel( str( self.genres[ self.settings[ "shortcut3" ] ].title ) )

    def showCredits( self ):
        import credits
        cw = credits.GUI( language=_, skin=self.skin )
        if ( cw.gui_loaded ):
            cw.doModal()
        del cw

    def toggleAsWatched( self ):
        trailer = self.setCountLabel( 'Trailer List' )
        watched = not ( self.trailers.movies[ trailer ].watched > 0 )
        self.markAsWatched( watched, trailer )
  
    def toggleAsFavorite( self ):
        trailer = self.setCountLabel( 'Trailer List' )
        favorite = not self.trailers.movies[ trailer ].favorite
        success = self.trailers.updateRecord( 'movies', ( 'favorite', ), ( favorite, self.trailers.movies[ trailer ].idMovie, ), 'idMovie' )
        if ( success ):
            self.trailers.movies[ trailer ].favorite = favorite
            if ( self.category_id == utilities.FAVORITES ):
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
            success = self.trailers.updateRecord( 'Movies', ( 'saved_location', ), ( '', self.trailers.movies[ trailer ].idMovie, ), 'idMovie' )
            if ( success ):
                self.trailers.movies[ trailer ].saved = ''
                if ( self.category_id == utilities.DOWNLOADED ): force_update = True
                else: force_update = False
                self.showTrailers( self.sql, self.params, choice = trailer, force_update = force_update )

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
                #self.setShortcut( self.settings[ "shortcut1" ] )
                self.setCategory( self.settings[ "shortcut1" ], 1 )
            elif ( control is self.controls['Shortcut2 Button']['control'] ):
                #self.setShortcut( self.settings[ "shortcut2" ] )
                self.setCategory( self.settings[ "shortcut2" ], 1 )
            elif ( control is self.controls['Shortcut3 Button']['control'] ):
                self.setCategory( self.settings[ "shortcut3" ], 1 )
            elif ( control is self.controls['Genre Button']['control'] ):
                self.setCategory( utilities.GENRES, 0 )
            elif ( control is self.controls['Studio Button']['control'] ):
                self.setCategory( utilities.STUDIOS, 0 )
            elif ( control is self.controls['Actor Button']['control'] ):
                self.setCategory( utilities.ACTORS, 0 )
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
        guibase.GUI.onAction( self, action )
        try:
            button_key = self.controller_action.get( action.getButtonCode(), 'n/a' )
            control = self.getFocus()
            if ( button_key == 'Keyboard Backspace Button' or button_key == 'B Button' or button_key == 'Remote Back Button' ):
                self.setCategory( self.current_display[ self.list_category == 0 ][ 0 ], self.current_display[ self.list_category == 0 ][ 1 ] )
            elif ( control is self.controls['Trailer List']['control'] ):
                if ( button_key == 'Y' or button_key == 'Remote 0' ):
                    pass#self.toggleAsFavorite()##change to queue
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



## Thanks Thor918 for this class ##
class MyPlayer( xbmc.Player ):
    def  __init__( self, *args, **kwargs ):
        xbmc.Player.__init__( self )
        self.function = kwargs['function']

    def onPlayBackStopped( self ):
        self.function( 0 )
    
    def onPlayBackEnded( self ):
        self.function( 1 )
    
    def onPlayBackStarted( self ):
        self.function( 2 )
    







