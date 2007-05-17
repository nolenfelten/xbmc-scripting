"""
Main GUI for Apple Movie Trailers
"""

import sys
import xbmcgui

dialog = xbmcgui.DialogProgress()
def _progress_dialog( count=0, msg="" ):
    if ( count is None ):
        dialog.create( __scriptname__ )
    elif ( count > 0 ):
        percent = int( count * ( float( 100 ) / ( len( modules ) + 1 ) ) )
        dialog.update( percent, _( 50 ), _( 51 ), msg )
    else:
        dialog.close()
    
_ = sys.modules[ "__main__" ].__language__
__scriptname__ = sys.modules[ "__main__" ].__scriptname__
__version__ = sys.modules[ "__main__" ].__version__

try:
    _progress_dialog( None )
    modules = ( "os", "xbmc", "traceback", "utilities", "context_menu", "cacheurl", "shutil", "datetime", )
    for count, module in enumerate( modules ):
        _progress_dialog( count + 1, "%s %s" % ( _( 52 ), module, ) )
        exec "import %s" % module
except:
    traceback.print_exc()
    _progress_dialog( -1 )
    xbmcgui.Dialog().ok( __scriptname__, _( 81 ) )
    raise


class GUI( xbmcgui.WindowXML ):
    # control id's
    CONTROL_TITLE_LABEL = 20
    CONTROL_CATEGORY_LABEL = 30
    CONTROL_BUTTON_GROUP_START = 103
    CONTROL_BUTTON_GROUP_END = 109
    CONTROL_TRAILER_LIST_START = 50
    CONTROL_TRAILER_LIST_END = 59
    CONTROL_TRAILER_LIST_PAGE_START = 2050
    CONTROL_TRAILER_LIST_PAGE_END = 2059
    CONTROL_TRAILER_LIST_COUNT = 2150
    CONTROL_CATEGORY_LIST = 60
    CONTROL_CATEGORY_LIST_PAGE = 2060
    CONTROL_CATEGORY_LIST_COUNT = 2160
    CONTROL_CAST_LIST = 70
    CONTROL_CAST_LIST_PAGE = 2070
    CONTROL_CAST_BUTTON = 170
    CONTROL_PLOT_TEXTBOX = 75
    CONTROL_PLOT_BUTTON = 175
    CONTROL_TRAILER_POSTER = 201
    CONTROL_OVERLAY_RATING = 202
    CONTROL_OVERLAY_FAVORITE = 203
    CONTROL_OVERLAY_WATCHED = 204
    CONTROL_OVERLAY_SAVED = 205
    CONTROL_TRAILER_TITLE_LABEL = 206

    def __init__( self, *args, **kwargs ):
        xbmcgui.lock()
        self.startup = True
        ########self.videoplayer_resolution = int( xbmc.executehttpapi( "getguisetting(0,videoplayer.displayresolution)" ).replace("<li>","") )
        ##self.Timer = None
        self._get_settings()
        
    def onInit( self ):
        if ( self.startup ):
            self.startup = False
            ## remove when search is done ##
            self.getControl( 106 ).setEnabled( False )
            self._set_video_resolution()
            self._set_labels()
            xbmcgui.unlock()
            self._setup_variables()
            self._set_startup_choices()
            self._set_startup_category()

    def _set_labels( self ):
        try:
            self.getControl( self.CONTROL_TITLE_LABEL ).setLabel( __scriptname__ )
            self.getControl( self.CONTROL_CATEGORY_LABEL ).setLabel( "" )
            self.getControl( self.CONTROL_CATEGORY_LIST_COUNT ).setLabel( "" )
            for button_id in range( self.CONTROL_BUTTON_GROUP_START, self.CONTROL_BUTTON_GROUP_END + 1 ):
                self.getControl( button_id ).setLabel( _( button_id ) )
        except:
            pass

    def _get_settings( self ):
        self.settings = utilities.Settings().get_settings()

    def _set_video_resolution( self, default=False ):
        pass
        #if ( self.settings[ "videoplayer_displayresolution" ] != 10 and not default ):
        #    xbmc.executehttpapi( "SetGUISetting(0,videoplayer.displayresolution,%d)" % ( self.settings[ "videoplayer_displayresolution" ], ) )
        #else:
        #    xbmc.executehttpapi( "SetGUISetting(0,videoplayer.displayresolution,%d)" % ( self.videoplayer_resolution, ) )

    def _setup_variables( self ):
        import trailers
        import database
        self.trailers = trailers.Trailers()
        self.query= database.Query()
        self.skin = self.settings[ "skin" ]
        self.flat_cache = ( unicode( "", "utf-8" ), "", )
        self.sql = ""
        self.params = None
        self.display_cast = False
        ##self.dummy()
        ##self.MyPlayer = MyPlayer( xbmc.PLAYER_CORE_MPLAYER, function=self.myPlayerChanged )
        self.update_method = 0
        #self.list_control_pos = [ 0, 0, 0, 0 ]

    # dummy() and self.Timer are currently used for the Player() subclass so when an onPlayback* event occurs, 
    # it calls myPlayerChanged() immediately.
    ##def dummy( self ):
    ##    self.Timer = threading.Timer( 60*60*60, self.dummy,() )
    ##    self.Timer.start()

    ##def myPlayerChanged( self, event ):
    ##    pass
        #if ( event == 0 and self.currently_playing_movie[1] >= 0 ):
        #    self.markAsWatched( self.currently_playing_movie[0] + 1, self.currently_playing_movie[1], self.currently_playing_movie[2] )
        #elif ( event == 2 ):
        #    self.currently_playing_movie = -1
        #    self.currently_playing_genre = -1
        
    def _set_startup_choices( self ):
        self.sql_category = ""
        self.params_category = None
        self.main_category = utilities.GENRES
        self.genres = self.trailers.categories
        self.current_display = [ [ utilities.GENRES , 0 ], [ 0, 1 ] ]
        self.setShortcutLabels()

    def _set_startup_category( self ):
        startup_button = "Shortcut1"
        if ( self.settings[ "startup_category_id" ] == self.settings[ "shortcut2" ] ): startup_button = "Shortcut2"
        elif ( self.settings[ "startup_category_id" ] == self.settings[ "shortcut3" ] ): startup_button = "Shortcut3"
        self.setCategory( self.settings[ "startup_category_id" ], 1 )

    def setCategory( self, category_id=utilities.GENRES, list_category=0 ):
        self.category_id = category_id
        self.list_category = list_category
        if ( list_category > 0 ):
            if ( category_id == utilities.FAVORITES ):
                sql = self.query[ "favorites" ]
                params = ( 1, )
            elif ( category_id == utilities.DOWNLOADED ):
                sql = self.query[ "downloaded" ]
                params = ( "", )
            elif ( category_id == utilities.HD_TRAILERS ):
                sql = self.query[ "hd_trailers" ]
                params = ( "%p.mov%", )
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
            if ( self.trailers.categories ): self.setFocus( self.getControl( self.CONTROL_CATEGORY_LIST ) )
        else:
            if ( self.trailers.movies ): 
                #xbmc.sleep(20)
                self.setFocus( self.getControl( self.CONTROL_TRAILER_LIST_START ) )
    
    def showCategories( self, sql, params=None, choice=0, force_update=False ):
        xbmcgui.lock()
        try:
            if ( sql != self.sql_category or params != self.params_category or force_update ):
                #self.list_control_pos[ self.list_category ] = choice
                self.trailers.getCategories( sql, params )
                self.sql_category = sql
                self.params_category = params
                self.getControl( self.CONTROL_CATEGORY_LIST ).reset()
                if ( self.trailers.categories ):
                    thumbnail = "generic-%s.tbn" % ( ( "genre", "studio", "actor", )[ abs( self.category_id ) - 1 ], )
                    for category in self.trailers.categories:
                        count = "(%d)" % ( category.count, )
                        self.getControl( self.CONTROL_CATEGORY_LIST ).addItem( xbmcgui.ListItem( category.title, count, "%s.tbn" % category.title, thumbnail ) )
                    self._set_selection( self.CONTROL_CATEGORY_LIST, choice )#self.list_control_pos[ self.list_category ] )
        except: traceback.print_exc()
        xbmcgui.unlock()

    def showTrailers( self, sql, params=None, choice=0, force_update=False ):
        try:
            if ( sql != self.sql or params != self.params or force_update ):
                #self.list_control_pos[ self.list_category ] = choice
                if ( force_update != 2 ):
                    self.trailers.getMovies( sql, params )
                ##else:
                ##    choice = self.list_control_pos[ self.list_category ]
                xbmcgui.lock()
                self.sql = sql
                self.params = params
                self.clearList()
                print sql
                if ( self.trailers.movies ):
                    print "YUP movies found\n", sql
                    for movie in self.trailers.movies: # now fill the list control
                        #print movie.title
                        ## remove poster if can't use ListItem.Icon
                        poster = ( movie.poster, "blank-poster.tbn", )[ not movie.poster ]
                        thumbnail = ( ( movie.thumbnail, movie.thumbnail_watched )[ movie.watched and self.settings[ "fade_thumb" ] ], "generic-trailer.tbn", "", )[ self.settings[ "thumbnail_display" ] ]
                        #favorite = ( "", "*", )[ movie.favorite ]
                        urls = ( "", "!", )[ not movie.trailer_urls ]
                        rating = ( "[%s]" % movie.rating, "", )[ not movie.rating ]
                        list_item = xbmcgui.ListItem( "%s%s" % ( urls, movie.title, ), rating, poster, thumbnail )
                        list_item.select( movie.favorite )
                        self.addItem( list_item )
                    self._set_selection( self.CONTROL_TRAILER_LIST_START, choice + ( choice == -1 ) )
                else: self.clearTrailerInfo()
        except:
            traceback.print_exc()
        xbmcgui.unlock()

    def _set_selection( self, list_control, pos=0 ):
        ##self.controls[list_control]["control"].selectItem( pos )
        #self.setFocus( self.controls[list_control]["control"] )
        try:
            if ( list_control == self.CONTROL_TRAILER_LIST_START ): 
                self.setCurrentListPosition( pos )
                self.showTrailerInfo()
            elif ( list_control == self.CONTROL_CATEGORY_LIST ):
                choice = self._set_count_label( self.CONTROL_CATEGORY_LIST )
        except: traceback.print_exc()

    def showControls( self, category ):
        xbmcgui.lock()
        try:
            self.getControl( self.CONTROL_CATEGORY_LIST ).setVisible( category )
            self.getControl( self.CONTROL_CATEGORY_LIST ).setEnabled( category and self.trailers.categories is not None )
            self.showPlotCastControls( category )
            self.setCategoryLabel()
        except: traceback.print_exc()#pass
        xbmcgui.unlock()
            
    def showPlotCastControls( self, category ):
        xbmcgui.lock()
        self.getControl( self.CONTROL_PLOT_BUTTON ).setVisible( self.display_cast and not category )
        self.getControl( self.CONTROL_PLOT_BUTTON ).setEnabled( self.display_cast and not category )
        xbmcgui.unlock()
            
    def togglePlotCast( self ):
        self.display_cast = not self.display_cast
        self.showPlotCastControls( False )
        if ( self.display_cast ): self.setFocus( self.getControl( self.CONTROL_PLOT_BUTTON ) )
        else: self.setFocus( self.getControl( self.CONTROL_CAST_BUTTON ) )

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
        elif ( self.category_id == utilities.HD_TRAILERS ):
            category = _( 160 )
        elif ( self.category_id >= 0 ):
            if ( self.list_category == 3 ):
                category = self.actor
            elif ( self.list_category == 2 ):
                category = self.trailers.categories[ self.category_id ].title
            elif ( self.list_category == 1 ):
                category = self.genres[ self.category_id ].title
        self.getControl( self.CONTROL_CATEGORY_LABEL ).setLabel( category )
            
    def _set_count_label( self, list_control ):
        if ( list_control == self.CONTROL_TRAILER_LIST_START ):
            pos = self.getCurrentListPosition()
            self.getControl( self.CONTROL_TRAILER_LIST_COUNT ).setLabel( "%d of %d" % ( pos + 1, len( self.trailers.movies ), ) )
        else:
            pos = self.getControl( self.CONTROL_CATEGORY_LIST ).getSelectedPosition()
            self.getControl( self.CONTROL_CATEGORY_LIST_COUNT ).setLabel( "%d of %d" % ( pos + 1, self.getControl( self.CONTROL_CATEGORY_LIST ).size(), ) )
        #self.list_control_pos[ self.list_category ] = pos
        return pos
    
    def clearTrailerInfo( self ):
        #self.getControl( CONTROL_TRAILER_POSTER ).setImage( "" )
        self.getControl( self.CONTROL_OVERLAY_RATING ).setImage( "" )
        ##self.getControl( self.CONTROL_TRAILER_TITLE_LABEL ).setLabel( "" )
        # Plot
        self.getControl( self.CONTROL_PLOT_TEXTBOX ).reset()
        #self.getControl( self.CONTROL_PLOT_TEXTBOX ).setText( "" )
        # Cast
        self.getControl( self.CONTROL_CAST_LIST ).reset()
        self.getControl( self.CONTROL_TRAILER_LIST_COUNT ).setLabel( "" )
        self.showOverlays()
        
    def showTrailerInfo( self ):
        xbmcgui.lock()
        try:
            trailer = self._set_count_label( self.CONTROL_TRAILER_LIST_START )
            #hack until panel control is a native python control
            if ( trailer == -1 ): 
                self.setCurrentListPosition( len( self.trailers.movies ) - 1 )
                trailer = self._set_count_label( self.CONTROL_TRAILER_LIST_START )
            self.getControl( self.CONTROL_TRAILER_TITLE_LABEL ).setEnabled( not self.trailers.movies[ trailer ].favorite )
            ##poster = ( self.trailers.movies[ trailer ].poster, "blank-poster.tbn", )[ not self.trailers.movies[ trailer ].poster ]
            ##self.getControl( self.CONTROL_TRAILER_POSTER ).setImage( poster )
            self.getControl( self.CONTROL_OVERLAY_RATING ).setImage( self.trailers.movies[ trailer ].rating_url )
            ##self.getControl( self.CONTROL_TRAILER_TITLE_LABEL ).setLabel( self.trailers.movies[ trailer ].title )
            # Plot
            self.getControl( self.CONTROL_PLOT_TEXTBOX ).reset()
            self.getControl( self.CONTROL_PLOT_TEXTBOX ).setText( ( self.trailers.movies[ trailer ].plot, _( 400 ), )[ not self.trailers.movies[ trailer ].plot ] )
            # Cast
            self.getControl( self.CONTROL_CAST_LIST ).reset()
            cast = self.trailers.movies[ trailer ].cast
            if ( cast ):
                self.cast_exists = True
                thumbnail = "generic-actor.tbn"
                for actor in cast:
                    self.getControl( self.CONTROL_CAST_LIST ).addItem( xbmcgui.ListItem( actor[ 0 ], "", "%s.tbn" % actor, thumbnail ) )
            else: 
                self.cast_exists = False
                self.getControl( self.CONTROL_CAST_LIST ).addItem( _( 401 ) )
            self.showPlotCastControls( False )
            self.showOverlays( trailer )
        except: traceback.print_exc()#pass
        xbmcgui.unlock()
        
    def showOverlays( self, trailer=-1 ):
        self.getControl( self.CONTROL_OVERLAY_FAVORITE ).setVisible( self.trailers.movies[ trailer ].favorite * ( trailer != -1 ) )
        self.getControl( self.CONTROL_OVERLAY_WATCHED ).setVisible( self.trailers.movies[ trailer ].watched * ( trailer != -1 ) )
        self.getControl( self.CONTROL_OVERLAY_SAVED ).setVisible( ( self.trailers.movies[ trailer ].saved != "" ) * ( trailer != -1 ) )

    def getTrailerGenre( self ):
        genre = self.getControl( self.CONTROL_CATEGORY_LIST ).getSelectedPosition()
        if ( self.main_category == utilities.STUDIOS ): 
            list_category = 2
        elif ( self.main_category == utilities.ACTORS ): 
            list_category = 3
            self.actor = self.getControl( self.CONTROL_CATEGORY_LIST ).getSelectedItem().getLabel()
        else: list_category = 1
        self.setCategory( genre, list_category )

    def getActorChoice( self ):
        choice = self.getControl( self.CONTROL_CAST_LIST ).getSelectedPosition()
        self.actor = self.getControl( self.CONTROL_CAST_LIST ).getSelectedItem().getLabel()
        self.setCategory( choice, 3 )

    def playTrailer( self ):
        try:
            trailer = self.getCurrentListPosition()
            trailer_urls = self.trailers.movies[ trailer ].trailer_urls
            choice = ( self.settings[ "trailer_quality" ], len( trailer_urls ) - 1, )[ self.settings[ "trailer_quality" ] >= len( trailer_urls ) ]
            if ( self.settings[ "mode" ] == 0 or self.settings[ "trailer_quality" ] <= 2 ):
                while ( "p.mov" in trailer_urls[ choice ] and choice != -1 ): choice -= 1
            url = trailer_urls[ choice ]
            utilities.LOG( utilities.LOG_DEBUG, "%s (ver: %s) [choice=%d url=%s]", __scriptname__, __version__, choice, url )
            if ( choice >= 0 ):
                filename = str( self.trailers.movies[ trailer ].saved )
                self.core = xbmc.PLAYER_CORE_DVDPLAYER
                if ( not os.path.isfile( filename ) ):
                    if ( self.settings[ "mode" ] == 0 ):
                        self.core = xbmc.PLAYER_CORE_MPLAYER
                        filename = url
                    else:
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
                                poster = ( self.trailers.movies[ trailer ].poster, "blank-poster.tbn", )[ not self.trailers.movies[ trailer ].poster ]
                                self.saveThumbnail( filename, trailer, poster )
            else: filename = ""
            utilities.LOG( utilities.LOG_DEBUG, "%s (ver: %s) [%s -> %s]", __scriptname__, __version__, "GUI::playTrailer", filename )
            if ( filename and filename != "None" ):
                self.markAsWatched( self.trailers.movies[ trailer ].watched + 1, trailer )
                xbmc.Player( self.core ).play( filename )
        except: traceback.print_exc()

    def saveThumbnail( self, filename, trailer, poster ):
        try: 
            new_filename = "%s.tbn" % ( os.path.splitext( filename )[0], )
            if ( not os.path.isfile( new_filename ) ):
                shutil.copyfile( poster, new_filename )
            if ( self.trailers.movies[ trailer ].saved == "" ):
                success = self.trailers.updateRecord( "movies", ( "saved_location", ), ( filename, self.trailers.movies[ trailer ].idMovie, ), "idMovie" )
                if ( success ):
                    self.trailers.movies[ trailer ].saved = filename
                    ##self.showOverlays( trailer )
        except: traceback.print_exc()
    
    def showContextMenu( self ):
        if ( self.controlId == self.CONTROL_CATEGORY_LIST or self.controlId == self.CONTROL_CAST_LIST ):
            selection = self.getControl( self.controlId ).getSelectedPosition()
            controlId= self.controlId
        else:
            selection = self.getCurrentListPosition()
            controlId = self.CONTROL_TRAILER_LIST_START
        x, y = self.getControl( controlId ).getPosition()
        w = self.getControl( controlId ).getWidth()
        h = self.getControl( controlId ).getHeight() - self.getControl( controlId ).getItemHeight()
        labels = ()
        functions = ()
        if ( self.CONTROL_TRAILER_LIST_START <= controlId <= self.CONTROL_TRAILER_LIST_END ):
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
        elif ( controlId == self.CONTROL_CATEGORY_LIST ):
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
        elif ( controlId == self.CONTROL_CAST_LIST ):
                labels += ( _( 531 ), )
                functions += ( self.getActorChoice, )
        if ( not self.trailers.complete ): 
            labels += ( _( 550 ), )
            functions += ( self.force_full_update, )
        force_fallback = self.skin != "Default"
        cm = context_menu.GUI( "script-%s-context.xml" % ( __scriptname__.replace( " ", "_" ), ), utilities.BASE_RESOURCE_PATH, self.skin, force_fallback, area=( x, y, w, h, ), labels=labels )
        if ( cm.selection is not None ):
            functions[ cm.selection ]()
        del cm

    def force_full_update( self ):
        self.trailers.fullUpdate()

    def markAsWatched( self, watched, trailer ):
        date = ( datetime.date.today(), "", )[ not watched ]
        success = self.trailers.updateRecord( "movies", ( "times_watched", "last_watched", ), ( watched, date, self.trailers.movies[ trailer ].idMovie, ), "idMovie" )
        if ( success ):
            self.trailers.movies[ trailer ].watched = watched
            thumbnail = ( ( self.trailers.movies[ trailer ].thumbnail, self.trailers.movies[ trailer ].thumbnail_watched )[ self.trailers.movies[ trailer ].watched and self.settings[ "fade_thumb" ] ], "generic-trailer.tbn", "", )[ self.settings[ "thumbnail_display" ] ]
            self.setThumbnailImage( thumbnail )
            self.showOverlays( trailer )
        else:
            utilities.LOG( utilities.LOG_ERROR, "%s (ver: %s) [%s]", __scriptname__, __version__, "GUI::markAsWatched" )
            
    def changeSettings( self ):
        import settings
        force_fallback = self.skin != "Default"
        settings = settings.GUI( "script-%s-settings.xml" % ( __scriptname__.replace( " ", "_" ), ), utilities.BASE_RESOURCE_PATH, self.skin, force_fallback, skin=self.skin, genres=self.genres )
        settings.doModal()
        if ( settings.changed ):
            self._get_settings()
            ok = False
            if ( settings.restart ):
                ok = xbmcgui.Dialog().yesno( __scriptname__, _( 240 ), "", _( 241 ), _( 256 ), _( 255 ) )
            if ( not ok ):
                self.setShortcutLabels()
                if ( settings.refresh and self.category_id != utilities.GENRES and self.category_id != utilities.STUDIOS and self.category_id != utilities.ACTORS):
                    trailer = self.getCurrentListPosition()
                    self.showTrailers( self.sql, self.params, choice=trailer, force_update=2 )
                else: self.sql=""
            else: self.exitScript( True )
        del settings

    def setShortcutLabels( self ):
        if ( self.settings[ "shortcut1" ] == utilities.FAVORITES ):
            self.getControl( 100 ).setLabel( _( 152 ) )
        elif ( self.settings[ "shortcut1" ] == utilities.DOWNLOADED ):
            self.getControl( 100 ).setLabel( _( 153 ) )
        elif ( self.settings[ "shortcut1" ] == utilities.HD_TRAILERS ):
            self.getControl( 100 ).setLabel( _( 160 ) )
        else:
            self.getControl( 100 ).setLabel( str( self.genres[ self.settings[ "shortcut1" ] ].title ) )
        if ( self.settings[ "shortcut2" ] == utilities.FAVORITES ):
            self.getControl( 101 ).setLabel( _( 152 ) )
        elif ( self.settings[ "shortcut2" ] == utilities.DOWNLOADED ):
            self.getControl( 101 ).setLabel( _( 153 ) )
        elif ( self.settings[ "shortcut2" ] == utilities.HD_TRAILERS ):
            self.getControl( 101 ).setLabel( _( 160 ) )
        else:
            self.getControl( 101 ).setLabel( str( self.genres[ self.settings[ "shortcut2" ] ].title ) )
        if ( self.settings[ "shortcut3" ] == utilities.FAVORITES ):
            self.getControl( 102 ).setLabel( _( 152 ) )
        elif ( self.settings[ "shortcut3" ] == utilities.DOWNLOADED ):
            self.getControl( 102 ).setLabel( _( 153 ) )
        elif ( self.settings[ "shortcut3" ] == utilities.HD_TRAILERS ):
            self.getControl( 102 ).setLabel( _( 160 ) )
        else:
            self.getControl( 102 ).setLabel( str( self.genres[ self.settings[ "shortcut3" ] ].title ) )

    def showCredits( self ):
        """ shows a credit window """
        import credits
        force_fallback = self.skin != "Default"
        c = credits.GUI( "script-%s-credits.xml" % ( __scriptname__.replace( " ", "_" ), ), utilities.BASE_RESOURCE_PATH, self.skin, force_fallback )
        c.doModal()
        del c

    def updateScript( self ):
        import update
        updt = update.Update()
        del updt

    def toggleAsWatched( self ):
        trailer = self._set_count_label( self.CONTROL_TRAILER_LIST_START )
        watched = not ( self.trailers.movies[ trailer ].watched > 0 )
        print "toggleAsWatched", watched
        self.markAsWatched( watched, trailer )

    def toggleAsFavorite( self ):
        trailer = self._set_count_label( self.CONTROL_TRAILER_LIST_START )
        favorite = not self.trailers.movies[ trailer ].favorite
        success = self.trailers.updateRecord( "movies", ( "favorite", ), ( favorite, self.trailers.movies[ trailer ].idMovie, ), "idMovie" )
        if ( success ):
            self.trailers.movies[ trailer ].favorite = favorite
            self.select( favorite )
            if ( self.category_id == utilities.FAVORITES ):
                self.trailers.movies.pop( trailer )
                self.removeItem( trailer )
            if ( not len( self.trailers.movies ) ): self.clearTrailerInfo()
            else: self.showTrailerInfo()

    def refreshAllGenres( self ):
        self.sql = ""
        genres = range( len( self.genres ) )
        self.trailers.refreshGenre( genres )
        if ( self.category_id == utilities.GENRES ):
            sql = self.query[ "genre_category_list" ]
            genre = self.getControl( self.CONTROL_CATEGORY_LIST ).getSelectedPosition()
            self.sql_category = ""
            self.showCategories( sql, choice=genre, force_update=True )
        
    def refreshGenre( self ):
        genre = self.getControl( self.CONTROL_CATEGORY_LIST ).getSelectedPosition()
        if ( self.current_display[ 1 ][ 0 ] == genre ):
            self.sql = ""
        self.trailers.refreshGenre( ( genre, ) )
        count = "(%d)" % self.trailers.categories[ genre ].count
        self.getControl( self.CONTROL_CATEGORY_LIST ).getSelectedItem().setLabel2( count )

    def refreshCurrentGenre( self ):
        trailer = self._set_count_label( self.CONTROL_TRAILER_LIST_START )
        self.sql_category = ""
        self.trailers.refreshGenre( ( self.category_id, ) )
        self.showTrailers( self.sql, params=self.params, choice=trailer, force_update=True )

    def refreshTrailerInfo( self ):
        trailer = self._set_count_label( self.CONTROL_TRAILER_LIST_START )
        self.getControl( self.CONTROL_TRAILER_POSTER ).setImage( "" )
        self.getControl( self.CONTROL_OVERLAY_RATING ).setImage( "" )
        self.trailers.refreshTrailerInfo( trailer )
        self.showTrailers( self.sql, params=self.params, choice=trailer, force_update=True )

    def saveCachedMovie( self ):
        try:
            trailer = self._set_count_label( self.CONTROL_TRAILER_LIST_START )
            new_filename = os.path.join( self.settings[ "save_folder" ], os.path.split( self.flat_cache[ 1 ] )[ 1 ] )
            dialog = xbmcgui.DialogProgress()
            dialog.create( _( 56 ), "%s %s" % ( _( 1008 ), new_filename, ) )
            if ( not os.path.isfile( new_filename ) ):
                shutil.move( self.flat_cache[ 1 ], new_filename )
                shutil.move( "%s.conf" % self.flat_cache[ 1 ], "%s.conf" % new_filename )
                poster = ( self.trailers.movies[ trailer ].poster, "blank-poster.tbn", )[ not self.trailers.movies[ trailer ].poster ]
                self.saveThumbnail( new_filename, trailer, poster )
                self.showOverlays( trailer )
            dialog.close()
        except:
            dialog.close()
            xbmcgui.Dialog().ok( _( 56 ), _( 90 ) )
            traceback.print_exc()
                
    def deleteSavedTrailer( self ):
        trailer = self._set_count_label( self.CONTROL_TRAILER_LIST_START )
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
                if ( self.category_id == utilities.DOWNLOADED ):
                    self.trailers.movies.pop( trailer )
                    self.removeItem( trailer )
                if ( not len( self.trailers.movies ) ): self.clearTrailerInfo()
                else: self.showTrailerInfo()

    def exitScript( self, restart=False ):
        ##if ( self.Timer is not None ): self.Timer.cancel()
        self._set_video_resolution( True )
        self.close()
        if ( restart ): xbmc.executebuiltin( "XBMC.RunScript(%s)" % ( os.path.join( os.getcwd().replace( ";", "" ), "default.py" ), ) )

    def onClick( self, controlId ):
        try:
            if ( controlId == 100 ):
                self.setCategory( self.settings[ "shortcut1" ], 1 )
            elif ( controlId == 101 ):
                self.setCategory( self.settings[ "shortcut2" ], 1 )
            elif ( controlId == 102 ):
                self.setCategory( self.settings[ "shortcut3" ], 1 )
            elif ( controlId == 103 ):
                self.setCategory( utilities.GENRES, 0 )
            elif ( controlId == 104 ):
                self.setCategory( utilities.STUDIOS, 0 )
            elif ( controlId == 105 ):
                self.setCategory( utilities.ACTORS, 0 )
            elif ( controlId == 106 ):
                pass#self.search()
            elif ( controlId == 107 ):
                self.changeSettings()
            elif ( controlId == 108 ):
                self.showCredits()
            elif ( controlId == 109 ):
                self.updateScript()
            elif ( controlId in ( self.CONTROL_PLOT_BUTTON, self.CONTROL_CAST_BUTTON ) ):
                self.togglePlotCast()
            ##elif ( self.CONTROL_TRAILER_LIST_START <= controlId <= self.CONTROL_TRAILER_LIST_END ):
            ##    self.playTrailer()
            elif ( controlId == self.CONTROL_CATEGORY_LIST ):
                self.getTrailerGenre()
            elif ( controlId == self.CONTROL_CAST_LIST ):
                self.getActorChoice()
        except: traceback.print_exc()

    def onFocus( self, controlId ):
        #xbmc.sleep( 10 )
        self.controlId = controlId

    def onAction( self, action ):
        try:
            if ( action.getButtonCode() in utilities.EXIT_SCRIPT ):
                self.exitScript()
            elif ( action.getButtonCode() in utilities.TOGGLE_DISPLAY ):
                self.setCategory( self.current_display[ self.list_category == 0 ][ 0 ], self.current_display[ self.list_category == 0 ][ 1 ] )
            else:
                if ( self.CONTROL_TRAILER_LIST_START <= self.controlId <= self.CONTROL_TRAILER_LIST_END ):
                    if ( action.getButtonCode() in utilities.CONTEXT_MENU ):
                        self.showContextMenu()
                    elif ( action.getButtonCode() in utilities.SELECT_ITEM ):
                        self.playTrailer()
                    ###############################################################
                    elif ( action.getButtonCode() in utilities.MOVEMENT or action.getButtonCode() in ( 262, 263, ) ):
                        self.showTrailerInfo()
                    ###############################################################
                elif ( self.CONTROL_TRAILER_LIST_PAGE_START <= self.controlId <= self.CONTROL_TRAILER_LIST_PAGE_END ):
                    if ( action.getButtonCode() in utilities.MOVEMENT_UP or action.getButtonCode() in utilities.MOVEMENT_DOWN ):
                        self.showTrailerInfo()
                elif ( self.controlId == self.CONTROL_CATEGORY_LIST ):
                    if ( action.getButtonCode() in utilities.CONTEXT_MENU ):
                        self.showContextMenu()
                    #elif ( action.getButtonCode() in utilities.SELECT_ITEM ):
                    #    self.getTrailerGenre()
                    elif ( action.getButtonCode() in utilities.MOVEMENT_UP or action.getButtonCode() in utilities.MOVEMENT_DOWN ):
                        choice = self._set_count_label( self.CONTROL_CATEGORY_LIST )
                elif ( self.controlId == self.CONTROL_CATEGORY_LIST_PAGE ):
                    if ( action.getButtonCode() in utilities.MOVEMENT_UP or action.getButtonCode() in utilities.MOVEMENT_DOWN ):
                        self._set_count_label( self.CONTROL_CATEGORY_LIST )
                elif ( self.controlId == self.CONTROL_CAST_LIST ):
                    if ( action.getButtonCode() in utilities.CONTEXT_MENU ):
                        self.showContextMenu()
                    #elif ( action.getButtonCode() in utilities.SELECT_ITEM ):
                    #    self.getActorChoice()
        except:
            traceback.print_exc()

def main():
    _progress_dialog( len( modules ) + 1, _( 55 ) )
    settings = utilities.Settings().get_settings()
    force_fallback = settings[ "skin" ] != "Default"
    ui = GUI( "script-%s-main.xml" % ( __scriptname__.replace( " ", "_" ), ), utilities.BASE_RESOURCE_PATH, settings[ "skin" ], force_fallback )
    _progress_dialog( -1 )
    ui.doModal()
    del ui
main()

"""
## Thanks Thor918 for this class ##
class MyPlayer( xbmc.Player ):
    def  __init__( self, *args, **kwargs ):
        xbmc.Player.__init__( self )
        self.function = kwargs["function"]

    def onPlayBackStopped( self ):
        self.function( 0 )
    
    def onPlayBackEnded( self ):
        self.function( 1 )
    
    def onPlayBackStarted( self ):
        self.function( 2 )
"""