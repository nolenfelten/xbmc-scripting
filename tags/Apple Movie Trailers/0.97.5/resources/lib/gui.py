"""
Main GUI for Apple Movie Trailers
"""

def createProgressDialog( __line2__, __line3__="" ):
    global dialog, pct
    pct = 0
    dialog = xbmcgui.DialogProgress()
    dialog.create( _( 0 ) )
    updateProgressDialog( __line2__, __line3__ )

def updateProgressDialog( __line2__, __line3__="" ):
    global dialog, pct
    pct += 10
    dialog.update( pct, _( 50 ), __line2__, __line3__ )

def closeProgessDialog():
    global dialog
    dialog.close()
    
import sys
import xbmcgui

_ = sys.modules[ "__main__" ].__language__
__scriptname__ = sys.modules[ "__main__" ].__scriptname__
__version__ = sys.modules[ "__main__" ].__version__

try:
    createProgressDialog( _( 51 ), "%s os" % ( _( 52 ), ))
    import os
    updateProgressDialog( _( 51 ), "%s xbmc" % ( _( 52 ), ))
    import xbmc
    updateProgressDialog( _( 51 ), "%s traceback" % ( _( 52 ), ))
    import traceback
    updateProgressDialog( _( 51 ), "%s threading" % ( _( 52 ), ))
    import threading
    updateProgressDialog( _( 51 ), "%s guibuilder" % ( _( 52 ), ))
    import guibuilder
    updateProgressDialog( _( 51 ), "%s context_menu" % ( _( 52 ), ))
    import context_menu
    import utilities
    updateProgressDialog( _( 51 ), "%s cacheurl" % ( _( 52 ), ))
    import cacheurl
    updateProgressDialog( _( 51 ), "%s shutil, datetime" % ( _( 52 ), ))
    import shutil
    import datetime
except:
    closeProgessDialog()
    traceback.print_exc()
    xbmcgui.Dialog().ok( _( 0 ), _( 81 ) )
    raise


class GUI( xbmcgui.Window ):
    def __init__( self ):
        try:
            ##self.Timer = None
            self.context_menu = None
            base_path = os.getcwd().replace( ";", "" )
            self.debug = os.path.isfile( os.path.join( base_path, "debug.txt" ))
            ##self.videoplayer_resolution = int( xbmc.executehttpapi( "getguisetting(0,videoplayer.displayresolution)" ).replace("<li>","") )
            self.getSettings()
            self.gui_loaded = self._load_gui( self.settings[ "skin" ] )
            if ( not self.gui_loaded ): raise
            else:
                updateProgressDialog( _( 67 ) )
                ## enable when ready
                self.controls["Search Button"]["control"].setEnabled( False )
                self.setupVariables()
                closeProgessDialog()
                self.setStartupChoices()
                self.setStartupCategory()
        except:
            closeProgessDialog()
            traceback.print_exc()
            self.gui_loaded = False
            self.exitScript()
                
    def getSettings( self ):
        self.settings = utilities.Settings().get_settings()
        ##if ( self.settings[ "videoplayer_displayresolution" ] != 10 ):
        ##    xbmc.executehttpapi( "SetGUISetting(0,videoplayer.displayresolution,%d)" % ( self.settings[ "videoplayer_displayresolution" ], ) )
        ##else:
        ##    xbmc.executehttpapi( "SetGUISetting(0,videoplayer.displayresolution,%d)" % ( self.videoplayer_resolution, ) )

    def _load_gui( self, skin ):
        updateProgressDialog( _( 55 ) )
        gb = guibuilder.GUIBuilder()
        gui_loaded, self.image_path = gb.create_gui( self, skin=skin, language=_ )
        #closeProgessDialog()
        #if ( not ok ):
        #    xbmcgui.Dialog().ok( _( 0 ), _( 57 ), _( 58 ), os.path.join( skin_path, xml_file ))
        return gui_loaded

    def setupVariables( self ):
        import trailers
        import database
        self.trailers = trailers.Trailers()
        self.query= database.Query()
        self.skin = self.settings[ "skin" ]
        self.context_menu = context_menu.GUI( skin=self.skin )
        self.flat_cache = ( unicode( "", "utf-8" ), "", )
        self.sql = ""
        self.params = None
        self.display_cast = False
        ##self.dummy()
        #self.MyPlayer = MyPlayer( xbmc.PLAYER_CORE_MPLAYER, function=self.myPlayerChanged )
        #self.controller_action = utilities.buttoncode_dict()
        self.update_method = 0
        self.list_control_pos = [ 0, 0, 0, 0 ]

    # dummy() and self.Timer are currently used for the Player() subclass so when an onPlayback* event occurs, 
    # it calls myPlayerChanged() immediately.
    ##def dummy( self ):
        ##self.Timer = threading.Timer( 60*60*60, self.dummy,() )
        ##self.Timer.start()

    ##def myPlayerChanged( self, event ):
    ##    pass
        #self.debugWrite("myPlayerChanged", 2)
        #if ( event == 0 and self.currently_playing_movie[1] >= 0 ):
        #    self.markAsWatched( self.currently_playing_movie[0] + 1, self.currently_playing_movie[1], self.currently_playing_movie[2] )
        #elif ( event == 2 ):
        #    self.currently_playing_movie = -1
        #    self.currently_playing_genre = -1
        
    def setStartupChoices( self ):
        self.sql_category = ""#"SELECT title, count, url, id, loaded FROM Genres ORDER BY title"
        self.params_category = None
        self.main_category = utilities.GENRES
        self.genres = self.trailers.categories
        self.current_display = [ [ utilities.GENRES , 0 ], [ 0, 1 ] ]
        self.setShortcutLabels()

    def setStartupCategory( self ):
        startup_button = "Shortcut1"
        if ( self.settings[ "startup_category_id" ] == self.settings[ "shortcut2" ] ): startup_button = "Shortcut2"
        elif ( self.settings[ "startup_category_id" ] == self.settings[ "shortcut3" ] ): startup_button = "Shortcut3"
        self.setControlNavigation( "%s Button" % ( startup_button, ) )
        self.setCategory( self.settings[ "startup_category_id" ], 1 )

    def setCategory( self, category_id = utilities.GENRES, list_category = 0 ):
        self.category_id = category_id
        self.list_category = list_category
        if ( list_category > 0 ):
            if ( category_id == utilities.FAVORITES ):
                sql = self.query[ "favorites" ]
                params = ( 1, )
            elif ( category_id == utilities.DOWNLOADED ):
                sql = self.query[ "downloaded" ]
                params = ( "", )
            elif ( list_category == 1 ):
                sql = self.query[ "movies_by_genre_id" ]
                params = ( self.genres[category_id].id, )
            elif ( list_category == 2 ):
                sql = self.query[ "movies_by_studio_name" ]
                params = ( self.trailers.categories[category_id].title.upper(), )
            elif ( list_category == 3 ):
                sql = self.query[ "movies_by_actor_name" ]
                names = self.actor.split( " " )[:2]
                if ( len( names ) == 1 ):
                    params = ( "%%%s%%" % ( names[0].upper(), ), )
                else:
                    params = ( "%%%s %s%%" % ( names[0].upper(), names[1].upper(), ), )
            self.current_display = [ self.current_display[ 0 ], [ category_id, list_category ] ]
            self.showTrailers( sql, params )
        else:
            self.main_category = category_id
            if ( category_id == utilities.GENRES ):
                sql = self.query[ "genre_category_list" ]
            elif ( category_id == utilities.STUDIOS ):
                sql = self.query[ "studio_category_list" ]
            elif ( category_id == utilities.ACTORS ):
                sql = self.query[ "actor_category_list" ]
            self.current_display = [ [ category_id, list_category ], self.current_display[ 1 ] ]
            self.showCategories( sql )
        self.showControls( self.category_id <= utilities.GENRES and self.category_id > utilities.FAVORITES )
        if ( self.category_id <= utilities.GENRES and self.category_id > utilities.FAVORITES ):
            if ( self.trailers.categories ): self.setFocus( self.controls[ "Category List" ][ "control" ] )
        else:
            if ( self.trailers.movies ): self.setFocus( self.controls[ "Trailer List" ][ "control" ] )
    
    def showCategories( self, sql, params=None, choice = 0, force_update = False ):
        try:
            #self.debugWrite("getGenreCategories", 2)
            xbmcgui.lock()
            if ( sql != self.sql_category or params != self.params_category or force_update ):
                self.list_control_pos[ self.list_category ] = choice
                self.trailers.getCategories( sql, params )
                self.sql_category = sql
                self.params_category = params
                self.controls[ "Category List" ][ "control" ].reset()
                if ( self.trailers.categories ):
                    for category in self.trailers.categories:
                        if ( self.category_id ) == utilities.GENRES: thumb_category = "genre"
                        elif ( self.category_id ) == utilities.STUDIOS: thumb_category = "studio"
                        else: thumb_category = "actor"
                        thumbnail = os.path.join( self.image_path, "%s.tbn" % ( category.title, ))
                        if ( not os.path.isfile( thumbnail )):
                            thumbnail = os.path.join( self.image_path, "generic-%s.tbn" % ( thumb_category, ) )
                        count = "(%d)" % ( category.count, )
                        self.controls[ "Category List" ][ "control" ].addItem( xbmcgui.ListItem( category.title, count, thumbnail, thumbnail ) )
                    ################
                    self.setSelection( "Category List", self.list_control_pos[ self.list_category ] )
                    #self.setSelection( "Trailer List", choice + ( choice == -1 ) )
        except: traceback.print_exc()
        xbmcgui.unlock()

    def showTrailers( self, sql, params=None, choice = 0, force_update = False ):
        try:
            if ( sql != self.sql or params != self.params or force_update ):
                self.list_control_pos[ self.list_category ] = choice
                self.trailers.getMovies( sql, params )
            else: choice = self.list_control_pos[ self.list_category ]
            xbmcgui.lock()
            self.sql = sql
            self.params = params
            self.controls[ "Trailer List" ][ "control" ].reset()
            if ( self.trailers.movies ):
                for movie in self.trailers.movies: # now fill the list control
                    if ( self.settings[ "thumbnail_display" ] == 0 ): 
                        if ( movie.watched ): thumbnail = movie.thumbnail_watched
                        else: thumbnail = movie.thumbnail
                    elif ( self.settings[ "thumbnail_display" ] == 1 ): thumbnail = os.path.join( self.image_path, "generic-trailer.tbn" )
                    else: thumbnail = ""
                    favorite = [ "", "*" ][ movie.favorite ]
                    favorite = [ favorite, "!" ][ not movie.trailer_urls ]
                    if ( movie.rating ): rating = "[%s]" % movie.rating
                    else: rating = ""
                    self.controls[ "Trailer List" ][ "control" ].addItem( xbmcgui.ListItem( "%s%s" % ( favorite, movie.title, ), rating, thumbnail, thumbnail ) )
                self.setSelection( "Trailer List", choice + ( choice == -1 ) )
            else: self.clearTrailerInfo()
        except:
            traceback.print_exc()
        xbmcgui.unlock()

    def calcScrollbarVisibilty( self, list_control ):
        if ( self.controls[list_control]["special"] ):
            if ( ( ( self.category_id >= 0 or self.category_id <= utilities.FAVORITES ) and list_control != "Category List" ) or 
                ( self.category_id <= utilities.GENRES and self.category_id > utilities.FAVORITES and list_control == "Category List" ) ):
                visible = ( self.controls[list_control]["control"].size() > self.getListControlItemsPerPage( list_control ) )
                if ( list_control == "Cast List" and not self.display_cast ):
                    visible = False
                self.showScrollbar( visible, list_control )
                ######self.setSelection( list_control )
            else: self.showScrollbar( False, list_control )

    def getListControlItemsPerPage( self, list_control ):
        height = self.controls[ list_control ][ "control" ].getItemHeight() + self.controls[ list_control ][ "control" ].getSpace()
        totalheight = self.controls[ list_control ][ "control" ].getHeight() - height
        items_per_page = int(float(totalheight) / float(height))
        return items_per_page
        
    def showScrollbar( self, visible, list_control ):
        try:
            self.controls["%s Scrollbar Position Indicator" % ( list_control, )]["control"].setVisible( visible )
            self.controls["%s Scrollbar Position Indicator" % ( list_control, )]["control"].setEnabled( visible )
        except: pass
            
    def setScrollbarIndicator( self, list_control ):
        try:
            if ( self.controls[list_control]["special"] ):
                if ( self.controls[list_control]["control"].size() > self.getListControlItemsPerPage( list_control ) ):
                    offset = float( self.controls["%s Scrollbar Middle" % ( list_control, )][ "control" ].getHeight() - self.controls["%s Scrollbar Position Indicator" % ( list_control, )][ "control" ].getHeight() ) / float( self.controls[list_control]["control"].size() - 1 )
                    posy = int( self.controls["%s Scrollbar Middle" % ( list_control, )][ "control" ].getPosition()[ 1 ] + ( offset * self.controls[list_control]["control"].getSelectedPosition() ) )
                    self.controls["%s Scrollbar Position Indicator" % ( list_control, )]["control"].setPosition( self.controls["%s Scrollbar Position Indicator" % ( list_control, )][ "control" ].getPosition()[ 0 ], posy )
        except: pass
        if ( list_control != "Cast List" ): self.list_control_pos[ self.list_category ] = self.controls[list_control]["control"].getSelectedPosition()
            
    def setSelection( self, list_control, pos = 0 ):
        #self.debugWrite("setSelection", 2)
        self.controls[list_control]["control"].selectItem( pos )
        #self.setFocus( self.controls[list_control]["control"] )
        if ( list_control == "Trailer List" ): self.showTrailerInfo()
        elif ( list_control == "Category List" ): choice = self.setCountLabel( "Category List" )
        self.setScrollbarIndicator( list_control )

    def pageIndicator( self, list_control, page ):
        #self.debugWrite("pageIndicator", 2)
        current_pos = self.controls[list_control]["control"].getSelectedPosition()
        total_items = self.controls[list_control]["control"].size()
        items_per_page = self.getListControlItemsPerPage( list_control )
        current_pos += page * items_per_page
        if ( current_pos < 0 ): current_pos = 0
        elif ( current_pos >= total_items ): current_pos = total_items - 1
        self.setSelection( list_control, current_pos )

    def setControlNavigation( self, button ):
        #self.debugWrite("setControlNavigation", 2)
        self.controls["Trailer List"]["control"].controlLeft( self.controls[button]["control"] )
        try:
            self.controls["Cast List Scrollbar Position Indicator"]["control"].controlRight( self.controls[button]["control"] )
        except:
            self.controls["Cast List"]["control"].controlRight( self.controls[button]["control"] )
            
        
    def showControls( self, category ):
        try:
            xbmcgui.lock()
            self.controls["Category List"]["control"].setVisible( category )
            self.controls["Category List"]["control"].setEnabled( category and self.trailers.categories != None )
            self.controls["Trailer List"]["control"].setVisible( not category )
            self.controls["Trailer List"]["control"].setEnabled( not category and self.trailers.movies != None )
            self.calcScrollbarVisibilty( "Trailer List" )
            self.calcScrollbarVisibilty( "Category List" )
            self.showPlotCastControls( category )
            self.setCategoryLabel()
        except: pass
        xbmcgui.unlock()
            
    def showPlotCastControls( self, category ):
        try:
            xbmcgui.lock()
            self.controls["Plot Button"]["control"].setVisible( self.display_cast and not category )
            self.controls["Plot Button"]["control"].setEnabled( self.display_cast and not category )
            self.controls["Cast Button"]["control"].setVisible( not self.display_cast and not category )
            self.controls["Cast Button"]["control"].setEnabled( not self.display_cast and not category )
            self.calcScrollbarVisibilty( "Cast List" )
        except: pass
        xbmcgui.unlock()
            
    def togglePlotCast( self ):
        #self.debugWrite("togglePlotCast", 2)
        self.display_cast = not self.display_cast
        self.showPlotCastControls( False )
        if ( self.display_cast ): self.setFocus( self.controls["Plot Button"]["control"] )
        else: self.setFocus( self.controls["Cast Button"]["control"] )

    def setCategoryLabel( self ):
        category= "oops"
        if ( self.category_id == utilities.GENRES ):
            category = _( 113 )
        elif ( self.category_id == utilities.STUDIOS ):
            category = _( 114 )
        elif ( self.category_id == utilities.ACTORS ):
            category = _( 115 )
        elif ( self.category_id == utilities.FAVORITES ):
            category = _( 152 )
        elif ( self.category_id == utilities.DOWNLOADED ):
            category = _( 153 )
        elif ( self.category_id >= 0 ):
            if ( self.list_category == 3 ):
                category = self.actor
            elif ( self.list_category == 2 ):
                category = self.trailers.categories[self.category_id].title
            elif ( self.list_category == 1 ):
                category = self.genres[self.category_id].title
        self.controls["Category Label"]["control"].setLabel( category )
            
    def setCountLabel( self, list_control ):
        pos = self.controls["%s" % list_control]["control"].getSelectedPosition()
        self.controls["%s Count Label" % list_control]["control"].setLabel( "%d of %d" % ( pos + 1, self.controls["%s" % list_control]["control"].size(), ))
        return pos
    
    def clearTrailerInfo( self ):
        self.controls["Trailer Poster"]["control"].setImage( "" )
        self.controls["Trailer Rating"]["control"].setImage( "" )
        self.controls["Trailer Title"]["control"].setLabel( "" )
        # Plot
        self.controls["Trailer Plot"]["control"].reset()
        self.controls["Trailer Plot"]["control"].setText( "" )
        # Cast
        self.controls["Cast List"]["control"].reset()
        self.controls["Trailer List Count Label"]["control"].setLabel( "" )
        self.showOverlays( -1 )
        
    def showTrailerInfo( self ):
        try:
            #self.debugWrite("showTrailerInfo", 2)
            xbmcgui.lock()
            trailer = self.setCountLabel( "Trailer List" )
            poster = self.trailers.movies[trailer].poster
            if ( not poster ): poster = os.path.join( self.image_path, "blank-poster.tbn" )
            self.controls["Trailer Poster"]["control"].setImage( poster )
            self.controls["Trailer Rating"]["control"].setImage( self.trailers.movies[trailer].rating_url )
            self.controls["Trailer Title"]["control"].setLabel( self.trailers.movies[trailer].title )
            # Plot
            self.controls["Trailer Plot"]["control"].reset()
            plot = self.trailers.movies[trailer].plot
            if ( plot ):
                self.controls["Trailer Plot"]["control"].setText( plot )
            else: self.controls["Trailer Plot"]["control"].setText( _( 400 ) )
            # Cast
            self.controls["Cast List"]["control"].reset()
            cast = self.trailers.movies[trailer].cast
            if ( cast ):
                self.cast_exists = True
                for actor in cast:
                    thumbnail = os.path.join( self.image_path, "generic-actor.tbn" )
                    self.controls["Cast List"]["control"].addItem( xbmcgui.ListItem( actor[ 0 ], "", thumbnail, thumbnail ) )
            else: 
                self.cast_exists = False
                self.controls["Cast List"]["control"].addItem( _( 401 ) )
            self.showPlotCastControls( False )
            #self.calcScrollbarVisibilty( "Cast List" )
            self.setScrollbarIndicator( "Trailer List" )
            self.setScrollbarIndicator( "Cast List" )
            self.showOverlays( trailer )
        except: pass
        xbmcgui.unlock()
        
    def showOverlays( self, trailer=-1 ):
        if ( trailer >= 0 ):
            posx, posy = self.controls["Trailer Favorite Overlay"][ "control" ].getPosition()
            favorite = self.trailers.movies[trailer].favorite
            posx = posx - ( favorite * self.controls["Trailer Favorite Overlay"][ "control" ].getWidth() )
            watched = self.trailers.movies[trailer].watched > 0
            self.controls["Trailer Watched Overlay"]["control"].setPosition( posx, posy )
            posx = posx - ( watched * self.controls["Trailer Watched Overlay"][ "control" ].getWidth() )
            saved = ( self.trailers.movies[trailer].saved != "" )
            self.controls["Trailer Saved Overlay"]["control"].setPosition( posx, posy )
        else:
            favorite = False
            watched = False
            saved = False
        self.controls["Trailer Favorite Overlay"]["control"].setVisible( favorite )
        self.controls["Trailer Watched Overlay"]["control"].setVisible( watched )
        self.controls["Trailer Saved Overlay"]["control"].setVisible( saved )

    def getTrailerGenre( self ):
        #self.debugWrite("getTrailerGenre", 2)
        genre = self.controls["Category List"]["control"].getSelectedPosition()
        if ( self.main_category == utilities.STUDIOS ): 
            list_category = 2
        elif ( self.main_category == utilities.ACTORS ): 
            list_category = 3
            self.actor = self.controls["Category List"]["control"].getSelectedItem().getLabel()
        else: list_category = 1
        self.setCategory( genre, list_category )

    def getActorChoice( self ):
        choice = self.controls["Cast List"]["control"].getSelectedPosition()
        self.actor = self.controls["Cast List"]["control"].getSelectedItem().getLabel()
        self.setCategory( choice, 3 )

    def playTrailer( self ):
        try:
            #self.debugWrite("PlayTrailer", 2)
            trailer = self.controls["Trailer List"]["control"].getSelectedPosition()
            trailer_urls = self.trailers.movies[trailer].trailer_urls
            if ( self.settings[ "trailer_quality" ] >= len( trailer_urls )):
                choice = len( trailer_urls ) - 1
            else:
                choice = self.settings[ "trailer_quality" ]
            if ( self.settings[ "mode" ] == 0 ):
                while ( "p.mov" in trailer_urls[ choice ] and choice != -1 ): choice -= 1
            #while ( "p.mov" in trailer_urls[ choice ] or choice == -1 ): choice -= 1
            url = trailer_urls[ choice ]
            #utilities.LOG( utilities.LOG_DEBUG, "%s (ver: %s) [core player=%d]", __scriptname__, __version__, core )
            utilities.LOG( utilities.LOG_DEBUG, "%s (ver: %s) [url=%s]", __scriptname__, __version__, url )

            if ( choice >= 0 ):
                filename = str( self.trailers.movies[ trailer ].saved )
                self.core = xbmc.PLAYER_CORE_DVDPLAYER
                if ( not os.path.isfile( filename ) ):
                    if ( self.settings[ "mode" ] == 0 ):
                        self.core = xbmc.PLAYER_CORE_MPLAYER
                        filename = url#trailer_urls[choice]
                    else:
                        #url = trailer_urls[choice]
                        ext = os.path.splitext( url )[ 1 ]
                        title = "%s%s" % (self.trailers.movies[trailer].title, ext, )
                        if ( self.settings[ "mode" ] == 1):
                            fetcher = cacheurl.HTTPProgressSave( save_title=title )
                            filename = str( fetcher.urlretrieve( url ) )
                            self.flat_cache = ( self.trailers.movies[trailer].title, filename, )
                        elif ( self.settings[ "mode" ] >= 2):
                            fetcher = cacheurl.HTTPProgressSave( self.settings[ "save_folder" ], title )
                            filename = str( fetcher.urlretrieve( url ) )
                            if ( filename ):
                                poster = self.trailers.movies[trailer].poster
                                if ( not poster ): poster = os.path.join( self.image_path, "blank-poster.tbn" )
                                self.saveThumbnail( filename, trailer, poster )
            else: filename = ""
            utilities.LOG( utilities.LOG_DEBUG, "%s (ver: %s) [%s]", __scriptname__, __version__, filename )
            if ( filename != "None" ):
                ##self.MyPlayer.play( filename )
                xbmc.Player( self.core ).play( filename )
                xbmc.sleep( 500 )
                self.markAsWatched( self.trailers.movies[ trailer ].watched + 1, trailer )
                #self.changed_trailers = False
        except: traceback.print_exc()

    def saveThumbnail( self, filename, trailer, poster ):
        #self.debugWrite( "saveThumbnail", 2 )
        try: 
            new_filename = "%s.tbn" % ( os.path.splitext( filename )[0], )
            if ( not os.path.isfile( new_filename ) ):
                shutil.copyfile( poster, new_filename )
            if ( self.trailers.movies[ trailer ].saved == "" ):
                success = self.trailers.updateRecord( "movies", ( "saved_location", ), ( filename, self.trailers.movies[ trailer ].idMovie, ), "idMovie" )
                if ( success ): self.trailers.movies[ trailer ].saved = filename
                #self.showTrailers( trailer )
        except: traceback.print_exc()
    
    def showContextMenu( self, list_control ):
        if ( self.context_menu.gui_loaded ):
            selection = self.controls[ list_control ]["control"].getSelectedPosition()
            x, y = self.controls[ list_control ][ "control" ].getPosition()
            w = self.controls[ list_control ]["control"].getWidth()
            h = self.controls[ list_control ]["control"].getHeight() - self.controls[ list_control ][ "control" ].getItemHeight()
            labels = ()
            functions = ()
            if ( list_control == "Trailer List" ):
                labels += ( _( 501 ), )
                functions += ( self.playTrailer, )
                labels += ( _( 502 + self.trailers.movies[ selection ].favorite ), )
                functions += ( self.toggleAsFavorite, )
                if ( self.trailers.movies[ selection ].watched ): watched_lbl = "  (%d)" % ( self.trailers.movies[ selection ].watched, )
                else: watched_lbl = ""
                labels += ( "%s" % ( _( 504 + ( self.trailers.movies[ selection ].watched > 0 ) ) + watched_lbl, ), )
                functions += ( self.toggleAsWatched, )
                labels += ( _( 506 ), )
                functions += ( self.refreshTrailerInfo, )
                if ( self.category_id >= 0 and self.list_category == 1 ):
                    labels += ( _( 512 ), )
                    functions += ( self.refreshCurrentGenre, )
                if ( self.trailers.movies[ selection ].saved ):
                    labels += ( _( 508 ), )
                    functions += ( self.deleteSavedTrailer, )
                elif ( self.trailers.movies[ selection ].title == self.flat_cache[ 0 ] ):
                    labels += ( _( 507 ), )
                    functions += ( self.saveCachedMovie, )
            elif ( list_control == "Category List" ):
                functions += ( self.getTrailerGenre, )
                if ( self.category_id == utilities.GENRES ):
                    labels += ( _( 511 ), )
                    labels += ( _( 512 ), )
                    functions += ( self.refreshGenre, )
                    labels += ( _( 513 ), )
                    functions += ( self.refreshAllGenres, )
                elif ( self.category_id ==  utilities.STUDIOS ):
                    labels += ( _( 521 ), )
                elif ( self.category_id ==  utilities.ACTORS ):
                    labels += ( _( 531 ), )
            elif ( list_control == "Cast List" ):
                    labels += ( _( 531 ), )
                    functions += ( self.getActorChoice, )
            if ( not self.trailers.complete ): 
                labels += ( _( 550 ), )
                functions += ( self.force_full_update, )
            self.context_menu.show_context_menu( area=( x, y, w, h, ), labels=labels )
            if ( self.context_menu.selection is not None ):
                functions[ self.context_menu.selection ]()

    def force_full_update( self ):
        self.trailers.fullUpdate()

    def markAsWatched( self, watched, trailer ):
        if ( watched ): date = datetime.date.today()
        else: date = ""
        success = self.trailers.updateRecord( "movies", ( "times_watched", "last_watched", ), ( watched, date, self.trailers.movies[ trailer ].idMovie, ), "idMovie" )
        if ( success ):
            self.trailers.movies[trailer].watched = watched
            self.showTrailers( self.sql, self.params, choice = trailer )

    def changeSettings( self ):
        import settings
        #self.debugWrite("changeSettings", 2)
        thumbnail_display = self.settings[ "thumbnail_display" ]
        settings = settings.GUI( skin=self.skin, genres=self.genres )
        if ( settings.gui_loaded ):
            settings.doModal()
            ok = False
            if ( settings.changed ):
                self.getSettings()
                if ( settings.restart ):
                    ok = xbmcgui.Dialog().yesno( __scriptname__, _( 240 ), "", _( 241 ), _( 256 ), _( 255 ) )
            del settings
            if ( not ok ):
                if ( thumbnail_display != self.settings[ "thumbnail_display" ] and self.category_id != utilities.GENRES and self.category_id != utilities.STUDIOS and self.category_id != utilities.ACTORS ):
                    trailer = self.controls[ "Trailer List" ][ "control" ].getSelectedPosition()
                    self.showTrailers( self.sql, self.params, choice = trailer )
                self.setShortcutLabels()
            else: self.exitScript( True )

    def setShortcutLabels( self ):
        if ( self.settings[ "shortcut1" ] == utilities.FAVORITES ):
            self.controls[ "Shortcut1 Button" ][ "control" ].setLabel( _( 152 ) )
        elif ( self.settings[ "shortcut1" ] == utilities.DOWNLOADED ):
            self.controls[ "Shortcut1 Button" ][ "control" ].setLabel( _( 153 ) )
        else:
            self.controls[ "Shortcut1 Button" ][ "control" ].setLabel( str( self.genres[ self.settings[ "shortcut1" ] ].title ) )
        if ( self.settings[ "shortcut2" ] == utilities.FAVORITES ):
            self.controls[ "Shortcut2 Button" ][ "control" ].setLabel( _( 152 ) )
        elif ( self.settings[ "shortcut2" ] == utilities.DOWNLOADED ):
            self.controls[ "Shortcut2 Button" ][ "control" ].setLabel( _( 153 ) )
        else:
            self.controls[ "Shortcut2 Button" ][ "control" ].setLabel( str( self.genres[ self.settings[ "shortcut2" ] ].title ) )
        if ( self.settings[ "shortcut3" ] == utilities.FAVORITES ):
            self.controls[ "Shortcut3 Button" ][ "control" ].setLabel( _( 152 ) )
        elif ( self.settings[ "shortcut3" ] == utilities.DOWNLOADED ):
            self.controls[ "Shortcut3 Button" ][ "control" ].setLabel( _( 153 ) )
        else:
            self.controls[ "Shortcut3 Button" ][ "control" ].setLabel( str( self.genres[ self.settings[ "shortcut3" ] ].title ) )

    def showCredits( self ):
        import credits
        cw = credits.GUI( skin=self.skin )
        if ( cw.gui_loaded ):
            cw.doModal()
        del cw

    def updateScript( self ):
        import update
        updt = update.Update( language=_ )
        del updt
        
    def toggleAsWatched( self ):
        trailer = self.setCountLabel( "Trailer List" )
        watched = not ( self.trailers.movies[ trailer ].watched > 0 )
        self.markAsWatched( watched, trailer )
  
    def toggleAsFavorite( self ):
        trailer = self.setCountLabel( "Trailer List" )
        favorite = not self.trailers.movies[ trailer ].favorite
        success = self.trailers.updateRecord( "movies", ( "favorite", ), ( favorite, self.trailers.movies[ trailer ].idMovie, ), "idMovie" )
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
    
    def refreshAllGenres( self ):
        self.sql = ""
        genres = range( len( self.genres ) )
        self.trailers.refreshGenre( genres )
        if ( self.category_id == utilities.GENRES ):
            sql = self.query[ "genre_category_list" ]
            genre = self.controls[ "Category List" ][ "control" ].getSelectedPosition()
            self.sql_category = ""
            self.showCategories( sql, choice=genre, force_update=True )
        
    def refreshGenre( self ):
        genre = self.controls[ "Category List" ][ "control" ].getSelectedPosition()
        self.sql_category = ""
        if ( self.current_display[ 1 ][ 0 ] == genre ):
            self.sql = ""
        self.trailers.refreshGenre( ( genre, ) )
        sql = self.query[ "genre_category_list" ]
        self.showCategories( sql, choice=genre, force_update=True )

    def refreshCurrentGenre( self ):
        trailer = self.setCountLabel( "Trailer List" )
        self.sql_category = ""
        self.trailers.refreshGenre( ( self.category_id, ) )
        self.showTrailers( self.sql, params=self.params, choice=trailer, force_update=True )

    def refreshTrailerInfo( self ):
        trailer = self.setCountLabel( "Trailer List" )
        self.controls[ "Trailer Poster" ][ "control" ].setImage( "" )
        self.controls[ "Trailer Rating" ][ "control" ].setImage( "" )
        self.trailers.refreshTrailerInfo( trailer )
        self.showTrailers( self.sql, params=self.params, choice=trailer, force_update=True )

    def saveCachedMovie( self ):
        try:
            trailer = self.setCountLabel( "Trailer List" )
            new_filename = os.path.join( self.settings[ "save_folder" ], os.path.split( self.flat_cache[ 1 ] )[ 1 ] )
            dialog = xbmcgui.DialogProgress()
            dialog.create( _( 56 ), "%s %s" % ( _( 1008 ), new_filename, ) )
            if ( not os.path.isfile( new_filename ) ):
                shutil.move( self.flat_cache[ 1 ], new_filename )
                shutil.move( "%s.conf" % self.flat_cache[ 1 ], "%s.conf" % new_filename )
                poster = self.trailers.movies[trailer].poster
                if ( not poster ): poster = os.path.join( self.image_path, "blank-poster.tbn" )
                self.saveThumbnail( new_filename, trailer, poster )
                self.showTrailerInfo()
            dialog.close()
        except:
            dialog.close()
            xbmcgui.Dialog().ok( _( 56 ), _( 90 ) )
            traceback.print_exc()
                
    def deleteSavedTrailer( self ):
        trailer = self.setCountLabel( "Trailer List" )
        saved_trailer = self.trailers.movies[ trailer ].saved
        if ( xbmcgui.Dialog().yesno( "%s?" % ( _( 509 ), ), _( 82 ), saved_trailer ) ):
            if ( os.path.isfile( saved_trailer ) ):
                os.remove( saved_trailer )
            if ( os.path.isfile( "%s.conf" % ( saved_trailer, ) ) ):
                os.remove( "%s.conf" % ( saved_trailer, ) )
            if ( os.path.isfile( "%s.tbn" % ( os.path.splitext( saved_trailer )[0], ) ) ):
                os.remove( "%s.tbn" % ( os.path.splitext( saved_trailer )[0], ) )
            success = self.trailers.updateRecord( "Movies", ( "saved_location", ), ( "", self.trailers.movies[ trailer ].idMovie, ), "idMovie" )
            if ( success ):
                self.trailers.movies[ trailer ].saved = ""
                if ( self.category_id == utilities.DOWNLOADED ): force_update = True
                else: force_update = False
                self.showTrailers( self.sql, self.params, choice = trailer, force_update = force_update )

    def exitScript( self, restart=False ):
        ##if ( self.Timer is not None ): self.Timer.cancel()
        if ( self.context_menu is not None ): del self.context_menu
        ##xbmc.executehttpapi( "SetGUISetting(0,videoplayer.displayresolution,%d)" % ( self.videoplayer_resolution, ) )
        self.close()
        if ( restart ): xbmc.executebuiltin( "XBMC.RunScript(%s)" % ( os.path.join( os.getcwd().replace( ";", "" ), "default.py" ), ) )
        """
    def setShortcut( self, shortcut ):
        if ( self.main_category == -1 ):
            self.sql_category = "SELECT title, count, url, id, loaded FROM Genres ORDER BY title"
            self.params_category = None
            self.main_category = -1
            #self.trailers.getCategories( self.sql_category, self.params_category )
            self.trailers.categories = self.genres
        self.setCategory( shortcut, 1 )
        """
    def onControl( self, control ):
        try:
            if ( control is self.controls["Shortcut1 Button"]["control"] ):
                #self.setShortcut( self.settings[ "shortcut1" ] )
                self.setCategory( self.settings[ "shortcut1" ], 1 )
            elif ( control is self.controls["Shortcut2 Button"]["control"] ):
                #self.setShortcut( self.settings[ "shortcut2" ] )
                self.setCategory( self.settings[ "shortcut2" ], 1 )
            elif ( control is self.controls["Shortcut3 Button"]["control"] ):
                self.setCategory( self.settings[ "shortcut3" ], 1 )
            elif ( control is self.controls["Genre Button"]["control"] ):
                self.setCategory( utilities.GENRES, 0 )
            elif ( control is self.controls["Studio Button"]["control"] ):
                self.setCategory( utilities.STUDIOS, 0 )
            elif ( control is self.controls["Actor Button"]["control"] ):
                self.setCategory( utilities.ACTORS, 0 )
            elif ( control is self.controls["Search Button"]["control"] ):
                pass#self.search
            elif ( control is self.controls["Settings Button"]["control"] ):
                self.changeSettings()
            elif ( control is self.controls["Plot Button"]["control"] or control is self.controls["Cast Button"]["control"] ):
                self.togglePlotCast()
            elif ( control is self.controls["Category List"]["control"] ):
                self.getTrailerGenre()
            elif ( control is self.controls["Trailer List"]["control"] ):
                self.playTrailer()
            elif ( control is self.controls["Cast List"]["control"] ):
                self.getActorChoice()
            else:
                try:
                    if ( control is self.controls[ "Optional Button" ][ "control" ] ):
                        exec self.controls[ "Optional Button" ][ "onclick" ]
                except: pass
        except: traceback.print_exc()
        
    def onAction( self, action ):
        try:
            if ( action.getButtonCode() in utilities.EXIT_SCRIPT ):
                self.exitScript()
            elif ( action.getButtonCode() in utilities.TOGGLE_DISPLAY ):
                self.setCategory( self.current_display[ self.list_category == 0 ][ 0 ], self.current_display[ self.list_category == 0 ][ 1 ] )
            else:
                #button_key = self.controller_action.get( action.getButtonCode(), "n/a" )
                control = self.getFocus()
                if ( control is self.controls["Trailer List"]["control"] ):
                    #if ( button_key == "Y" or button_key == "Remote 0" ):
                    #    pass#self.toggleAsFavorite()##change to queue
                    if ( action.getButtonCode() in utilities.CONTEXT_MENU ):
                        self.showContextMenu( "Trailer List" )
                    else:
                        self.showTrailerInfo()
                elif ( control is self.controls["Category List"]["control"] ):
                    if ( action.getButtonCode() in utilities.CONTEXT_MENU ):
                        self.showContextMenu( "Category List" )
                    else:
                        self.setScrollbarIndicator( "Category List" )
                        choice = self.setCountLabel( "Category List" )
                elif ( control is self.controls["Cast List"]["control"] ):
                    if ( action.getButtonCode() in utilities.CONTEXT_MENU ):
                        self.showContextMenu( "Cast List" )
                    else:
                        self.setScrollbarIndicator( "Cast List" )
                elif ( control is self.controls["Shortcut1 Button"]["control"] ):
                    self.setControlNavigation( "Shortcut1 Button" )
                elif ( control is self.controls["Shortcut2 Button"]["control"] ):
                    self.setControlNavigation( "Shortcut2 Button" )
                elif ( control is self.controls["Shortcut3 Button"]["control"] ):
                    self.setControlNavigation( "Shortcut3 Button" )
                elif ( control is self.controls["Genre Button"]["control"] ):
                    self.setControlNavigation( "Genre Button" )
                elif ( control is self.controls["Studio Button"]["control"] ):
                    self.setControlNavigation( "Studio Button" )
                elif ( control is self.controls["Actor Button"]["control"] ):
                    self.setControlNavigation( "Actor Button" )
                elif ( control is self.controls["Search Button"]["control"] ):
                    self.setControlNavigation( "Search Button" )
                elif ( control is self.controls["Settings Button"]["control"] ):
                    self.setControlNavigation( "Settings Button" )
                else:
                    try:
                        if ( control is self.controls["Trailer List Scrollbar Position Indicator"]["control"] ):
                            if ( action.getButtonCode() in utilities.MOVEMENT_UP ):
                                self.pageIndicator( "Trailer List", -1 )
                            elif ( action.getButtonCode() in utilities.MOVEMENT_DOWN ):
                                self.pageIndicator( "Trailer List", 1 )
                    except: pass
                    try:
                        if ( control is self.controls["Category List Scrollbar Position Indicator"]["control"] ):
                            if ( action.getButtonCode() in utilities.MOVEMENT_UP ):
                                self.pageIndicator( "Category List", -1 )
                                choice = self.setCountLabel( "Category List" )
                            elif ( action.getButtonCode() in utilities.MOVEMENT_DOWN ):
                                self.pageIndicator( "Category List", 1 )
                                choice = self.setCountLabel( "Category List" )
                    except: pass
                    try:
                        if ( control is self.controls["Cast List Scrollbar Position Indicator"]["control"] ):
                            if ( action.getButtonCode() in utilities.MOVEMENT_UP ):
                                self.pageIndicator( "Cast List", -1 )
                            elif ( action.getButtonCode() in utilities.MOVEMENT_DOWN ):
                                self.pageIndicator( "Cast List", 1 )
                    except: pass
                    try:
                        if ( control is self.controls[ "Optional Button" ][ "control" ] ):
                            self.setControlNavigation( "Optional Button" )
                    except: pass
        except: traceback.print_exc()
        
    def debugWrite( self, function, action, lines=[], values=[] ):
        if ( self.debug ):
            Action = ( "Failed", "Succeeded", "Started" )
            Highlight = ( "__", "__", "<<<<< ", "__", "__", " >>>>>" )
            xbmc.output( "%s%s%s : (%s)\n" % ( Highlight[action], function, Highlight[action + 3], Action[action] ) )
            try:
                for cnt, line in enumerate( lines ):
                    finished_line = "%s\n" % ( line, )
                    xbmc.output( finished_line % values[cnt] )
            except: traceback.print_exc()


## Thanks Thor918 for this class ##
#class MyPlayer( xbmc.Player ):
#    def  __init__( self, *args, **kwargs ):
#        xbmc.Player.__init__( self )
#        self.function = kwargs["function"]
#
#    def onPlayBackStopped( self ):
#        self.function( 0 )
#    
#    def onPlayBackEnded( self ):
#        self.function( 1 )
#    
#    def onPlayBackStarted( self ):
#        self.function( 2 )
