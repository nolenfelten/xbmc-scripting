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
__svn_revision__ = sys.modules[ "__main__" ].__svn_revision__

try:
    _progress_dialog( None )
    modules = ( "os", "xbmc", "utilities", "trailers", "database", "context_menu", "cacheurl", "datetime", )
    for count, module in enumerate( modules ):
        _progress_dialog( count + 1, "%s %s" % ( _( 52 ), module, ) )
        if ( module == "utilities" ):
            exec "from %s import *" % module
        else:
            exec "import %s" % module
except:
    print sys.exc_info()[ 1 ]
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
    CONTROL_TRAILER_LIST_PAGE_GROUP_START = 2550
    CONTROL_TRAILER_LIST_PAGE_GROUP_END = 2579
    CONTROL_TRAILER_LIST_COUNT = 2150
    CONTROL_CATEGORY_LIST = 60
    CONTROL_CATEGORY_LIST_PAGE = 2060
    CONTROL_CATEGORY_LIST_COUNT = 2160
    CONTROL_CATEGORY_LIST_PAGE_GROUP = ( 2650, 2660, 2661, )
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
    CONTROL_TRAILER_LIST_GROUP = 3000
    CONTROL_CATEGORY_LIST_GROUP = 4000
    
    def __init__( self, *args, **kwargs ):
        xbmcgui.lock()
        self.startup = True
        ##Enable once we figure out why it crashes sometimes#################################
        ##self.videoplayer_resolution = int( xbmc.executehttpapi( "getguisetting(0,videoplayer.displayresolution)" ).replace("<li>","") )
        ######################################################################
        ##self.Timer = None
        self._get_settings()
        self._get_showtimes_scraper()
        self._get_custom_sql()
        
    def onInit( self ):
        if ( self.startup ):
            self.startup = False
            self.getControl( self.CONTROL_CATEGORY_LIST_GROUP ).setVisible( False )
            self.getControl( self.CONTROL_TRAILER_LIST_GROUP ).setVisible( False )
            self._set_labels()
            xbmcgui.unlock()
            self._setup_variables()
            self._set_startup_choices()
            self._set_startup_category()
            if ( INSTALL_PLUGIN ):
                install_plugin()
                install_plugin( 1 )

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
        self.settings = Settings().get_settings()

    def _get_showtimes_scraper( self ):
        sys.path.append( os.path.join( BASE_RESOURCE_PATH, "showtimes_scrapers", self.settings[ "showtimes_scraper" ] ) )

    def _get_custom_sql( self ):
        self.search_sql = get_custom_sql()

    def _set_video_resolution( self, default=False ):
        """
        if ( self.settings[ "videoplayer_displayresolution" ] != 10 and not default ):
            # set the videoplayers resolution to AMT setting
            xbmc.executehttpapi( "SetGUISetting(0,videoplayer.displayresolution,%d)" % ( self.settings[ "videoplayer_displayresolution" ], ) )
        else:
            # set the videoplayers resolution back to XBMC setting
            xbmc.executehttpapi( "SetGUISetting(0,videoplayer.displayresolution,%d)" % ( self.videoplayer_resolution, ) )
        """
        pass

    def _setup_variables( self ):
        self.trailers = trailers.Trailers()
        self.query= database.Query()
        self.skin = self.settings[ "skin" ]
        self.flat_cache = ()
        self.sql = ""
        self.params = None
        self.display_cast = False
        ##self.dummy()
        ##self.MyPlayer = MyPlayer( xbmc.PLAYER_CORE_MPLAYER, function=self.myPlayerChanged )
        self.update_method = 0
        #self.list_control_pos = [ 0, 0, 0, 0 ]
        self.search_keywords = ""

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
        self.main_category = GENRES
        self.genres = self.trailers.categories
        self.current_display = [ [ GENRES , 0 ], [ 0, 1 ] ]
        self.setShortcutLabels()

    def _set_startup_category( self ):
        startup_button = "Shortcut1"
        if ( self.settings[ "startup_category_id" ] == self.settings[ "shortcut2" ] ): startup_button = "Shortcut2"
        elif ( self.settings[ "startup_category_id" ] == self.settings[ "shortcut3" ] ): startup_button = "Shortcut3"
        self.setCategory( self.settings[ "startup_category_id" ], 1 )

    def setCategory( self, category_id=GENRES, list_category=0 ):
        self.category_id = category_id
        self.list_category = list_category
        if ( list_category > 0 ):
            if ( category_id == FAVORITES ):
                sql = self.query[ "favorites" ]
                params = ( 1, )
            elif ( category_id == DOWNLOADED ):
                sql = self.query[ "downloaded" ]
                params = ( "", )
            elif ( category_id == HD_TRAILERS ):
                sql = self.query[ "hd_trailers" ]
                params = ( "%p.mov%", )
            elif ( category_id == NO_TRAILER_URLS ):
                sql = self.query[ "no_trailer_urls" ]
                params = ( "[]", )
            elif ( category_id == WATCHED ):
                sql = self.query[ "watched" ]
                params = ( 0, )
            elif ( category_id == RECENTLY_ADDED ):
                sql = self.query[ "recently_added" ]
                params = None
            elif ( category_id == CUSTOM_SEARCH ):
                sql = self.search_sql
                params = None
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
                    params = ( "%%%s%%" % ( names[0], ), )
                else:
                    params = ( "%%%s %s%%" % ( names[0], names[1], ), )
            self.current_display = [ self.current_display[ 0 ], [ category_id, list_category ] ]
            self.showTrailers( sql, params )
        else:
            self.main_category = category_id
            if ( category_id == GENRES ):
                sql = self.query[ "genre_category_list" ]
            elif ( category_id == STUDIOS ):
                sql = self.query[ "studio_category_list" ]
            elif ( category_id == ACTORS ):
                sql = self.query[ "actor_category_list" ]
            self.current_display = [ [ category_id, list_category ], self.current_display[ 1 ] ]
            self.showCategories( sql )
        self.showControls( self.category_id <= GENRES and self.category_id > FAVORITES )
    
    def showCategories( self, sql, params=None, choice=0, force_update=False ):
        try:
            if ( sql != self.sql_category or params != self.params_category or force_update ):
                #self.list_control_pos[ self.list_category ] = choice
                self.trailers.getCategories( sql, params )
                xbmcgui.lock()
                self.sql_category = sql
                self.params_category = params
                self.getControl( self.CONTROL_CATEGORY_LIST ).reset()
                if ( len( self.trailers.categories ) ):
                    for category in self.trailers.categories:
                        if ( self.main_category == GENRES ):
                            title = category.title.replace( "Newest", _( 150 ) ).replace( "Exclusives", _( 151 ) )
                        else:
                            title = category.title
                        thumbnail = "amt-generic-%s%s.png" % ( ( "genre", "studio", "actor", )[ abs( self.category_id ) - 1 ], ( "-i", "", )[ category.completed ], )
                        if ( self.main_category == ACTORS ):
                            actor_path = xbmc.translatePath( os.path.join( "P:\\", "Thumbnails", "Video", xbmc.getCacheThumbName( "actor" + category.title )[ 0 ], xbmc.getCacheThumbName( "actor" + category.title ) ) )
                            thumbnail = ( thumbnail, actor_path, )[ os.path.isfile( actor_path ) ]
                        count = "(%d)" % ( category.count, )
                        list_item = xbmcgui.ListItem( title, count, thumbnail, thumbnail )
                        list_item.select( not category.completed )
                        self.getControl( self.CONTROL_CATEGORY_LIST ).addItem( list_item )
                    self._set_selection( self.CONTROL_CATEGORY_LIST, choice )#self.list_control_pos[ self.list_category ] )
        except:
            LOG( LOG_ERROR, "%s (rev: %s) GUI::showCategories [%s]", __scriptname__, __svn_revision__, sys.exc_info()[ 1 ], )
        xbmcgui.unlock()

    def showTrailers( self, sql, params=None, choice=0, force_update=False ):
        try:
            if ( sql != self.sql or params != self.params or force_update ):
                #self.list_control_pos[ self.list_category ] = choice
                if ( force_update != 2 ):
                    updated = self.trailers.getMovies( sql, params )
                    if ( updated ):
                        self.sql_category = ""
                ##else:
                ##    choice = self.list_control_pos[ self.list_category ]
                xbmcgui.lock()
                self.sql = sql
                self.params = params
                self.clearList()
                if ( self.trailers.movies ):
                    for movie in self.trailers.movies: # now fill the list control
                        thumbnail, poster = self._get_thumbnail( movie )
                        total_trailers = ( "", " (x%d)" % len( movie.trailer_urls ), )[ len( movie.trailer_urls ) > 1 ]
                        urls = ( "(%s)", "%%s%s" % total_trailers, )[ len( movie.trailer_urls ) > 0 ]
                        #rating = ( "[%s]" % movie.rating, "", )[ not movie.rating ]
                        list_item = xbmcgui.ListItem( urls % ( movie.title, ), movie.rating, poster, thumbnail )
                        list_item.select( movie.favorite )
                        plot = ( movie.plot, _( 400 ), )[ not movie.plot ]
                        overlay = ( xbmcgui.ICON_OVERLAY_NONE, xbmcgui.ICON_OVERLAY_HD, )[ "720p.mov" in repr( movie.trailer_urls ) or "1080p.mov" in repr( movie.trailer_urls ) ]
                        list_item.setInfo( "video", { "Title": movie.title, "Overlay": overlay, "Plot": plot, "MPAARating": movie.rating } )
                        self.addItem( list_item )
                    self._set_selection( self.CONTROL_TRAILER_LIST_START, choice + ( choice == -1 ) )
                else: self.clearTrailerInfo()
        except:
            LOG( LOG_ERROR, "%s (rev: %s) GUI::showTrailers [%s]", __scriptname__, __svn_revision__, sys.exc_info()[ 1 ], )
        xbmcgui.unlock()

    def _get_thumbnail( self, movie ):
        poster = ( movie.poster, "amt-blank-poster.png", )[ not movie.poster ]
        if ( not movie.poster and self.settings[ "thumbnail_display" ] == 0 ):
            thumbnail = poster
        else:
            thumbnail = ( ( movie.thumbnail, movie.thumbnail_watched )[ movie.watched and self.settings[ "fade_thumb" ] ], "amt-generic-trailer%s.png" % ( ( "", "-w", )[ movie.watched > 0 ], ), "", )[ self.settings[ "thumbnail_display" ] ]
        return thumbnail, poster
        

    def _set_selection( self, list_control, pos=0 ):
        if ( list_control == self.CONTROL_TRAILER_LIST_START ): 
            self.setCurrentListPosition( pos )
            self.showTrailerInfo()
        elif ( list_control == self.CONTROL_CATEGORY_LIST ):
            self.getControl( self.CONTROL_CATEGORY_LIST ).selectItem( pos )
            choice = self._set_count_label( self.CONTROL_CATEGORY_LIST )

    def showControls( self, category ):
        xbmcgui.lock()
        self.getControl( self.CONTROL_CATEGORY_LIST_GROUP ).setVisible( category )
        self.getControl( self.CONTROL_TRAILER_LIST_GROUP ).setVisible( not category )
        self.setCategoryLabel()
        xbmcgui.unlock()
        self.showPlotCastControls( category )
        self.setFocus( self.getControl( ( self.CONTROL_CATEGORY_LIST_GROUP, self.CONTROL_TRAILER_LIST_GROUP, )[ not category ] ) )
            
    def showPlotCastControls( self, category ):
        xbmcgui.lock()
        self.getControl( self.CONTROL_PLOT_BUTTON ).setVisible( self.display_cast and not category )
        self.getControl( self.CONTROL_CAST_BUTTON ).setVisible( not self.display_cast and not category )
        xbmcgui.unlock()
            
    def togglePlotCast( self ):
        self.display_cast = not self.display_cast
        self.showPlotCastControls( False )
        if ( self.display_cast ): self.setFocus( self.getControl( self.CONTROL_PLOT_BUTTON ) )
        else: self.setFocus( self.getControl( self.CONTROL_CAST_BUTTON ) )

    def setCategoryLabel( self ):
        category= u""
        if ( self.category_id == GENRES ):
            category = _( 113 )
        elif ( self.category_id == STUDIOS ):
            category = _( 114 )
        elif ( self.category_id == ACTORS ):
            category = _( 115 )
        elif ( self.category_id == FAVORITES ):
            category = _( 152 )
        elif ( self.category_id == DOWNLOADED ):
            category = _( 153 )
        elif ( self.category_id == HD_TRAILERS ):
            category = _( 160 )
        elif ( self.category_id == NO_TRAILER_URLS ):
            category = _( 161 )
        elif ( self.category_id == CUSTOM_SEARCH ):
            category = _( 162 )
        elif ( self.category_id == WATCHED ):
            category = _( 163 )
        elif ( self.category_id == RECENTLY_ADDED ):
            category = _( 164 )
        elif ( self.category_id >= 0 ):
            if ( self.list_category == 3 ):
                category = self.actor
            elif ( self.list_category == 2 ):
                category = self.trailers.categories[ self.category_id ].title
            elif ( self.list_category == 1 ):
                category = self.genres[ self.category_id ].title.replace( "Newest", _( 150 ) ).replace( "Exclusives", _( 151 ) )
        self.getControl( self.CONTROL_CATEGORY_LABEL ).setLabel( category.encode( "utf-8" ) )

    def _set_count_label( self, list_control ):
        separator = ( _( 96 ) )
        if ( list_control == self.CONTROL_TRAILER_LIST_START ):
            pos = self.getCurrentListPosition()
            self.getControl( self.CONTROL_TRAILER_LIST_COUNT ).setLabel( "%d %s %d" % ( pos + 1, separator, len( self.trailers.movies ), ) )
        else:
            pos = self.getControl( self.CONTROL_CATEGORY_LIST ).getSelectedPosition()
            self.getControl( self.CONTROL_CATEGORY_LIST_COUNT ).setLabel( "%d %s %d" % ( pos + 1, separator, len( self.trailers.categories ), ) )#self.getControl( self.CONTROL_CATEGORY_LIST ).size()
        return pos
    
    def clearTrailerInfo( self ):
        self.getControl( self.CONTROL_OVERLAY_RATING ).setImage( "" )
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
            self.getControl( self.CONTROL_OVERLAY_RATING ).setImage( self.trailers.movies[ trailer ].rating_url )
            # Cast
            self.getControl( self.CONTROL_CAST_LIST ).reset()
            self.cast_exists = ( len( self.trailers.movies[ trailer ].cast ) > 0 )
            thumbnail = "amt-generic-%sactor.png" % ( "no", "" )[ self.trailers.movies[ trailer ].cast != [] ]
            if ( self.cast_exists ):
                for actor in self.trailers.movies[ trailer ].cast:
                    actor_path = xbmc.translatePath( os.path.join( "P:\\", "Thumbnails", "Video", xbmc.getCacheThumbName( "actor" + actor[ 0 ] )[ 0 ], xbmc.getCacheThumbName( "actor" + actor[ 0 ] ) ) )
                    actor_thumbnail = ( thumbnail, actor_path, )[ os.path.isfile( actor_path ) ]
                    actual_icon = ( "", actor_thumbnail, )[ actor_thumbnail != thumbnail ]
                    self.getControl( self.CONTROL_CAST_LIST ).addItem( xbmcgui.ListItem( actor[ 0 ], "", actual_icon, actor_thumbnail ) )
            else: 
                self.getControl( self.CONTROL_CAST_LIST ).addItem( xbmcgui.ListItem( _( 401 ), "", "", thumbnail ) )
            self.showPlotCastControls( False )
            self.showOverlays( trailer )
        except:
            LOG( LOG_ERROR, "%s (rev: %s) GUI::showTrailerInfo [%s]", __scriptname__, __svn_revision__, sys.exc_info()[ 1 ], )
        xbmcgui.unlock()

    def showOverlays( self, trailer=-1 ):
        if ( trailer != -1 ):
            self.getControl( self.CONTROL_OVERLAY_FAVORITE ).setVisible( self.trailers.movies[ trailer ].favorite )
            self.getControl( self.CONTROL_OVERLAY_WATCHED ).setVisible( self.trailers.movies[ trailer ].watched )
            self.getControl( self.CONTROL_OVERLAY_SAVED ).setVisible( self.trailers.movies[ trailer ].saved != [] )
        else:
            self.getControl( self.CONTROL_OVERLAY_FAVORITE ).setVisible( False )
            self.getControl( self.CONTROL_OVERLAY_WATCHED ).setVisible( False )
            self.getControl( self.CONTROL_OVERLAY_SAVED ).setVisible( False )
            
    def getTrailerGenre( self ):
        genre = self.getControl( self.CONTROL_CATEGORY_LIST ).getSelectedPosition()
        if ( self.main_category == STUDIOS ): 
            list_category = 2
        elif ( self.main_category == ACTORS ): 
            list_category = 3
            self.actor = self.getControl( self.CONTROL_CATEGORY_LIST ).getSelectedItem().getLabel()
        else: list_category = 1
        self.setCategory( genre, list_category )

    def getActorChoice( self ):
        choice = self.getControl( self.CONTROL_CAST_LIST ).getSelectedPosition()
        self.actor = self.getControl( self.CONTROL_CAST_LIST ).getSelectedItem().getLabel()
        self.setCategory( choice, 3 )

    def _get_trailer_url( self, title, trailer_urls ):
        items = ()
        urls = []
        for trailers in trailer_urls:
            # get intial choice
            choice = ( self.settings[ "trailer_quality" ], len( trailers ) - 1, )[ self.settings[ "trailer_quality" ] >= len( trailers ) ]
            # if quality is non progressive
            if ( self.settings[ "trailer_quality" ] <= 2 ):
                # select the correct non progressive trailer
                while ( trailers[ choice ].endswith( "p.mov" ) and choice != -1 ): choice -= 1
            # quality is progressive
            else:
                # select the proper progressive quality
                quality = ( "480p", "720p", "1080p", )[ self.settings[ "trailer_quality" ] - 3 ]
                # select the correct progressive trailer
                while ( quality not in trailers[ choice ] and trailers[ choice ].endswith( "p.mov" ) and choice != -1 ): choice -= 1
            # if we have a valid choice add the url to our list
            if ( choice >= 0 ):
                urls += [ trailers[ choice ] ]
        # if there are selections we and there is more than one trailer, let user choose
        if len( urls ):
            trailer = 0
            if ( len( urls ) > 1 ):
                # sort the urls, hopefully they will then be in the order of release
                urls.sort()
                # let the user choose
                trailer = self._get_trailer( title, urls )
            # if the user did not cancel the dialog
            if ( trailer is not None ):
                # if play all was selected, get the filepath for each url
                if ( trailer == len( urls ) ):
                    for c, url in enumerate( urls ):
                        t = self.get_filepath( "%s%s" % ( title, os.path.splitext( url )[ 1 ], ), c + 1, len( urls ) > 1 )
                        items += ( ( t, url, c + 1 ), )
                else:
                    # we only want the trailer selected
                    t = self.get_filepath( "%s%s" % ( title, os.path.splitext( urls[ trailer ] )[ 1 ], ), trailer + 1, len( urls ) > 1 )
                    items = ( ( t, urls[ trailer ], trailer + 1 ), )
        return items

    def get_filepath( self, title, count, multiple ):
        # add our trailer number if there is more than one trailer
        filepath = "%s%s%s" % ( os.path.splitext( title )[ 0 ], ( "", "_%d" % ( count, ), )[ multiple ], os.path.splitext( title )[ 1 ], )
        # now make it legal
        filepath = make_legal_filepath( filepath, save_end=multiple )
        return filepath

    def _get_trailer( self, title, urls ):
        # if Auto play all trailers, return the play all selection
        if ( self.settings[ "auto_play_all" ] ):
            return len( urls )
        import chooser
        force_fallback = self.skin != "Default"
        choices = [ "%s %d%s" % ( _( 99 ), c + 1, ( "", " - [HD]", )[ "720p.mov" in url or "1080p.mov" in url ] ) for c, url in enumerate( urls ) ]
        choices += [ _( 39 ) ]
        ch = chooser.GUI( "script-%s-chooser.xml" % ( __scriptname__.replace( " ", "_" ), ), BASE_RESOURCE_PATH, self.skin, force_fallback, choices=choices, original=-1, selection=0, list_control=1, title=title )
        selection = ch.selection
        del ch
        return selection

    def playTrailer( self ):
        try:
            trailer = self.getCurrentListPosition()
            if ( len( self.trailers.movies[ trailer ].trailer_urls ) ):
                items = self._get_trailer_url( self.trailers.movies[ trailer ].title, self.trailers.movies[ trailer ].trailer_urls )
                if ( items ):
                    playlist = xbmc.PlayList( xbmc.PLAYLIST_VIDEO )
                    playlist.clear()
                    for count, ( title, url, selected ) in enumerate( items ):
                        LOG( LOG_DEBUG, "%s (rev: %s) [url=%s]", __scriptname__, __svn_revision__, repr( url ) )
                        filename = None
                        for saved in self.trailers.movies[ trailer ].saved:
                            if ( title in saved[ 0 ] ):
                                filename = saved[ 0 ]
                                self.core = saved[ 1 ]
                                break
                        if ( filename is None or not os.path.isfile( filename ) ):
                            if ( url.endswith( "p.mov" ) ):
                                self.core = xbmc.PLAYER_CORE_DVDPLAYER
                            else:
                                self.core = xbmc.PLAYER_CORE_MPLAYER
                            if ( self.settings[ "mode" ] == 0 ):
                                filename = url
                            else:
                                if ( self.settings[ "mode" ] == 1 ):
                                    if ( not self.check_cache( self.trailers.movies[ trailer ].title ) ):
                                        self.flat_cache = ()
                                    fetcher = cacheurl.HTTPProgressSave( save_title=title, clear_cache_folder=not self.flat_cache )
                                    filename = fetcher.urlretrieve( url )
                                    if ( filename and not self.check_cache( filename, 1 ) ):
                                        self.flat_cache += ( ( self.trailers.movies[ trailer ].title, filename, ), )
                                elif ( self.settings[ "mode" ] >= 2 ):
                                    fetcher = cacheurl.HTTPProgressSave( self.settings[ "save_folder" ], title )
                                    filename = fetcher.urlretrieve( url )
                                    if ( filename is not None ):
                                        poster = ( self.trailers.movies[ trailer ].poster, "amt-blank-poster.png", )[ not self.trailers.movies[ trailer ].poster ]
                                        self.saveThumbnail( filename, trailer, poster )
                        if ( filename is not None ):
                            listitem = xbmcgui.ListItem( self.trailers.movies[ trailer ].title, thumbnailImage=self.trailers.movies[ trailer ].poster )
                            if ( len( items ) > 1 ): s = count + 1
                            else: s = selected
                            t = "%s%s" % ( self.trailers.movies[ trailer ].title, ( "", " (%s %d)" % ( _( 99 ), s, ), )[ len( self.trailers.movies[ trailer ].trailer_urls ) > 1 ] )
                            listitem.setInfo( "video", { "Title": t, "Studio": self.trailers.movies[ trailer ].studio, "Genre": self.getControl( self.CONTROL_CATEGORY_LABEL ).getLabel() } )
                            LOG( LOG_DEBUG, "%s (rev: %s) [%s -> %s]", __scriptname__, __svn_revision__, "GUI::playTrailer", filename )
                            playlist.add( filename, listitem )
                    if ( len( playlist ) ):
                        self.markAsWatched( self.trailers.movies[ trailer ].watched + 1, trailer )
                        self._set_video_resolution()
                        ##xbmc.Player( self.core ).play( playlist )
                        xbmc.Player().play( playlist )
        except:
            LOG( LOG_ERROR, "%s (rev: %s) GUI::playTrailer [%s]", __scriptname__, __svn_revision__, sys.exc_info()[ 1 ], )

    def check_cache( self, title, pos=0 ):
        exists = False
        for item in self.flat_cache:
            if ( title == item[ pos ] ):
                exists = True
                break
        return exists

    def saveThumbnail( self, filename, trailer, poster ):
        try: 
            new_filename = "%s.tbn" % ( os.path.splitext( filename )[0], )
            if ( not os.path.isfile( new_filename ) ):
                xbmc.executehttpapi("FileCopy(%s,%s)" % ( poster, new_filename, ) )
            if ( not self.check_cache( filename, 1 ) ):# not in repr( self.trailers.movies[ trailer ].saved ) ):
                self.trailers.movies[ trailer ].saved += [ ( filename, self.core, ) ]
                success = self.trailers.updateRecord( "movies", ( "saved", ), ( repr( self.trailers.movies[ trailer ].saved ), self.trailers.movies[ trailer ].idMovie, ), "idMovie" )
                #if ( success ):
                #    self.trailers.movies[ trailer ].saved = filename
                #    ##self.showOverlays( trailer )
        except:
            LOG( LOG_ERROR, "%s (rev: %s) GUI::saveThumbnail [%s]", __scriptname__, __svn_revision__, sys.exc_info()[ 1 ], )

    def showContextMenu( self ):
        if ( self.controlId == self.CONTROL_CATEGORY_LIST or self.controlId == self.CONTROL_CAST_LIST ):
            selection = self.getControl( self.controlId ).getSelectedPosition()
            controlId= self.controlId
        else:
            selection = self.getCurrentListPosition()
            controlId = self.CONTROL_TRAILER_LIST_START
        x, y = self.getControl( controlId ).getPosition()
        w = self.getControl( controlId ).getWidth()
        h = self.getControl( controlId ).getHeight()# - self.getControl( controlId ).getItemHeight()
        labels = ()
        functions = ()
        if ( self.CONTROL_TRAILER_LIST_START <= controlId <= self.CONTROL_TRAILER_LIST_END ):
            if ( len( self.trailers.movies[ selection ].trailer_urls ) ):
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
            if ( self.category_id == NO_TRAILER_URLS ):
                labels += ( _( 507 ), )
                functions += ( self.refreshAllTrailersInfo, )
            if ( self.category_id >= 0 and self.list_category == 1 ):
                labels += ( _( 512 ), )
                functions += ( self.refreshCurrentGenre, )
            if ( self.trailers.movies[ selection ].saved != [] ):
                labels += ( _( 509 ), )
                functions += ( self.deleteSavedTrailer, )
            elif ( self.check_cache( self.trailers.movies[ selection ].title ) ):
                labels += ( _( 508 ), )
                functions += ( self.saveCachedMovie, )
            labels += ( _( 510 ), )
            functions += ( self.get_showtimes, )
        elif ( controlId == self.CONTROL_CATEGORY_LIST ):
            functions += ( self.getTrailerGenre, )
            if ( self.category_id == GENRES ):
                labels += ( _( 511 ), )
                labels += ( _( 512 ), )
                functions += ( self.refreshGenre, )
                labels += ( _( 513 ), )
                functions += ( self.refreshAllGenres, )
            elif ( self.category_id ==  STUDIOS ):
                labels += ( _( 521 ), )
            elif ( self.category_id ==  ACTORS ):
                labels += ( _( 531 ), )
        elif ( controlId == self.CONTROL_CAST_LIST and self.cast_exists ):
                labels += ( _( 531 ), )
                functions += ( self.getActorChoice, )
        if ( not self.trailers.complete ): 
            labels += ( _( 550 ), )
            functions += ( self.force_full_update, )
        force_fallback = self.skin != "Default"
        cm = context_menu.GUI( "script-%s-context.xml" % ( __scriptname__.replace( " ", "_" ), ), BASE_RESOURCE_PATH, self.skin, force_fallback, area=( x, y, w, h, ), labels=labels )
        if ( cm.selection is not None ):
            functions[ cm.selection ]()
        del cm

    def force_full_update( self ):
        updated = self.trailers.fullUpdate()
        if ( self.list_category > 0 ):
            self.sql_category = ""
            trailer = self.getCurrentListPosition()
            self.showTrailers( self.sql, self.params, choice=trailer, force_update=2 )
        else:
            self.sql = ""
            if ( self.main_category == GENRES ):
                genre = self.getControl( self.CONTROL_CATEGORY_LIST ).getSelectedPosition()
                self.showCategories( self.sql_category, choice=genre, force_update=True )

    def markAsWatched( self, watched, trailer ):
        date = ( datetime.date.today(), "", )[ not watched ]
        success = self.trailers.updateRecord( "movies", ( "times_watched", "last_watched", ), ( watched, date, self.trailers.movies[ trailer ].idMovie, ), "idMovie" )
        if ( success ):
            self.trailers.movies[ trailer ].watched = watched
            thumbnail, poster = self._get_thumbnail( self.trailers.movies[ trailer ] )
            self.getListItem( trailer ).setThumbnailImage( thumbnail )
            self.showOverlays( trailer )
        else:
            LOG( LOG_ERROR, "%s (rev: %s) [%s]", __scriptname__, __svn_revision__, "GUI::markAsWatched" )

    def perform_search( self ):
        self.search_sql = ""
        if ( self.settings[ "use_simple_search" ] ):
            keyword = get_keyboard( default=self.search_keywords, heading= _( 95 ) )
            xbmc.sleep(10)
            if ( keyword ):
                keywords = keyword.split()
                self.search_keywords = keyword
                where = ""
                compare = False
                # this may be faster than regex, but not as accurate
                #where += "(LIKE '%% %s %%' OR title LIKE '%% %s.%%' OR title LIKE '%% %s,%%' OR title LIKE '%% %s:%%' OR title LIKE '%% %s!%%' OR title LIKE '%% %s-%%' OR title LIKE '%% %s?%%' OR title LIKE '%s %%' OR title LIKE '%s.%%' OR title LIKE '%s,%%' OR title LIKE '%s:%%' OR title LIKE '%s!%%' OR title LIKE '%s-%%' OR title LIKE '%s?%%' OR title LIKE '%% %s' OR title LIKE '%s' OR title LIKE '%%(%s' OR title LIKE '%% %s)' OR " % ( ( word, ) * 18 )
                pattern = ( "LIKE '%%%s%%'", "regexp('\\b%s\\b')", )[ self.settings[ "match_whole_words" ] ]
                for word in keywords:
                    if ( word.upper() == "AND" or word.upper() == "OR" ):
                        where += " %s " % word.upper()
                        compare = False
                        continue
                    elif ( word.upper() == "NOT" ):
                        where += "NOT "
                        continue
                    elif ( compare ):
                        where += " AND "
                        compare = False
                    where += "(title %s OR " % ( pattern % ( word, ), )
                    where += "plot %s OR " % ( pattern % ( word, ), )
                    where += "actor %s OR " % ( pattern % ( word, ), )
                    where += "studio %s OR " % ( pattern % ( word, ), )
                    where += "genre %s)" % ( pattern % ( word, ), )
                    compare = True
                self.search_sql = self.query[ "simple_search" ] % ( where, )
        else:
            import search
            force_fallback = self.skin != "Default"
            s = search.GUI( "script-%s-search.xml" % ( __scriptname__.replace( " ", "_" ), ), BASE_RESOURCE_PATH, self.skin, force_fallback )
            s.doModal()
            if ( s.query ):
                self.search_sql = s.query
            del s
        if ( self.search_sql ):
            self.setCategory( CUSTOM_SEARCH, 1 )

    def changeSettings( self ):
        import settings
        force_fallback = self.skin != "Default"
        settings = settings.GUI( "script-%s-settings.xml" % ( __scriptname__.replace( " ", "_" ), ), BASE_RESOURCE_PATH, self.skin, force_fallback, skin=self.skin, genres=self.genres )
        settings.doModal()
        if ( settings.changed ):
            self._get_settings()
            ok = False
            if ( settings.restart ):
                ok = xbmcgui.Dialog().yesno( __scriptname__, _( 240 ), "", _( 241 ), _( 271 ), _( 270 ) )
            if ( not ok ):
                self.setShortcutLabels()
                if ( settings.refresh and self.category_id not in ( GENRES, STUDIOS, ACTORS, ) ):
                    self._set_labels()
                    self.sql_category = ""
                    trailer = self.getCurrentListPosition()
                    self.showTrailers( self.sql, self.params, choice=trailer, force_update=2 )
                elif ( settings.refresh ):
                    self._set_labels()
                    self.sql = ""
                    genre = self.getControl( self.CONTROL_CATEGORY_LIST ).getSelectedPosition()
                    self.showCategories( self.sql_category, self.params_category, choice=genre, force_update=2 )
                #else: self.sql=""
            else: self.exitScript( True )
        del settings

    def setShortcutLabels( self ):
        for s in range( 3 ):
            if ( self.settings[ "shortcut%d" % ( s + 1, ) ] == FAVORITES ):
                self.getControl( 100 + s ).setLabel( _( 152 ) )
            elif ( self.settings[ "shortcut%d" % ( s + 1, ) ] == DOWNLOADED ):
                self.getControl( 100 + s ).setLabel( _( 153 ) )
            elif ( self.settings[ "shortcut%d" % ( s + 1, ) ] == HD_TRAILERS ):
                self.getControl( 100 + s ).setLabel( _( 160 ) )
            elif ( self.settings[ "shortcut%d" % ( s + 1, ) ] == NO_TRAILER_URLS ):
                self.getControl( 100 + s ).setLabel( _( 161 ) )
            elif ( self.settings[ "shortcut%d" % ( s + 1, ) ] == CUSTOM_SEARCH ):
                self.getControl( 100 + s ).setLabel( _( 162 ) )
            elif ( self.settings[ "shortcut%d" % ( s + 1, ) ] == WATCHED ):
                self.getControl( 100 + s ).setLabel( _( 163 ) )
            elif ( self.settings[ "shortcut%d" % ( s + 1, ) ] == RECENTLY_ADDED ):
                self.getControl( 100 + s ).setLabel( _( 164 ) )
            else:
                self.getControl( 100 + s ).setLabel( self.genres[ self.settings[ "shortcut%d" % ( s + 1, ) ] ].title.replace( "Newest", _( 150 ) ).replace( "Exclusives", _( 151 ) ) )

    def showCredits( self ):
        """ shows a credit window """
        import credits
        force_fallback = self.skin != "Default"
        c = credits.GUI( "script-%s-credits.xml" % ( __scriptname__.replace( " ", "_" ), ), BASE_RESOURCE_PATH, self.skin, force_fallback )
        c.doModal()
        del c

    def updateScript( self ):
        import update
        updt = update.Update()
        del updt

    def toggleAsWatched( self ):
        trailer = self._set_count_label( self.CONTROL_TRAILER_LIST_START )
        watched = not ( self.trailers.movies[ trailer ].watched > 0 )
        self.markAsWatched( watched, trailer )

    def toggleAsFavorite( self ):
        trailer = self._set_count_label( self.CONTROL_TRAILER_LIST_START )
        favorite = not self.trailers.movies[ trailer ].favorite
        success = self.trailers.updateRecord( "movies", ( "favorite", ), ( favorite, self.trailers.movies[ trailer ].idMovie, ), "idMovie" )
        if ( success ):
            self.trailers.movies[ trailer ].favorite = favorite
            self.getListItem( trailer ).select( favorite )
            if ( self.category_id == FAVORITES ):
                self.trailers.movies.pop( trailer )
                self.removeItem( trailer )
            if ( not len( self.trailers.movies ) ): self.clearTrailerInfo()
            else: self.showTrailerInfo()

    def refreshAllGenres( self ):
        self.sql = ""
        genres = range( len( self.genres ) )
        self.trailers.refreshGenre( genres )
        if ( self.category_id == GENRES ):
            sql = self.query[ "genre_category_list" ]
            genre = self.getControl( self.CONTROL_CATEGORY_LIST ).getSelectedPosition()
            self.sql_category = ""
            self.showCategories( sql, choice=genre, force_update=True )
        
    def refreshGenre( self ):
        genre = self.getControl( self.CONTROL_CATEGORY_LIST ).getSelectedPosition()
        if ( self.current_display[ 1 ][ 0 ] == genre ):
            self.sql = ""
        self.trailers.refreshGenre( ( genre, ) )
        self.sql_category = ""
        sql = self.query[ "genre_category_list" ]
        self.showCategories( sql, choice=genre, force_update=True )
        #count = "(%d)" % self.trailers.categories[ genre ].count
        #self.getControl( self.CONTROL_CATEGORY_LIST ).getSelectedItem().setLabel2( count )

    def refreshCurrentGenre( self ):
        trailer = self._set_count_label( self.CONTROL_TRAILER_LIST_START )
        self.sql_category = ""
        self.trailers.refreshGenre( ( self.category_id, ) )
        self.showTrailers( self.sql, params=self.params, choice=trailer, force_update=True )

    def refreshTrailerInfo( self ):
        trailer = self._set_count_label( self.CONTROL_TRAILER_LIST_START )
        #self.getControl( self.CONTROL_TRAILER_POSTER ).setImage( "" )
        self.getControl( self.CONTROL_OVERLAY_RATING ).setImage( "" )
        self.trailers.refreshTrailerInfo( ( trailer, ) )
        self.showTrailers( self.sql, params=self.params, choice=trailer, force_update=True )

    def refreshAllTrailersInfo( self ):
        ##### add a progress dialog
        trailer = self._set_count_label( self.CONTROL_TRAILER_LIST_START )
        self.getControl( self.CONTROL_OVERLAY_RATING ).setImage( "" )
        trailers = range( len( self.trailers.movies ) )
        self.trailers.refreshTrailerInfo( trailers )
        self.showTrailers( self.sql, params=self.params, choice=trailer, force_update=True )

    def saveCachedMovie( self ):
        try:
            dialog = xbmcgui.DialogProgress()
            dialog.create( _( 56 ) )
            trailer = self._set_count_label( self.CONTROL_TRAILER_LIST_START )
            environment = os.environ.get( "OS", "xbox" )
            dirname = self.settings[ "save_folder" ]
            if ( environment == "xbox" or environment == "win32" ):
                dirname = dirname.replace( "\\", "/" )
            for count, filename in enumerate( self.flat_cache ):
                percent = int( ( count + 1 ) * ( float( 100 ) / len( self.flat_cache ) ) )
                new_filename = "%s%s" % ( dirname, os.path.basename( filename[ 1 ] ), )
                dialog.update( percent, "%s %s" % ( _( 1008 ), new_filename, ) )
                if ( not os.path.isfile( new_filename ) ):
                    xbmc.executehttpapi("FileCopy(%s,%s)" % ( filename[ 1 ], new_filename, ) )
                    if ( not new_filename.startswith( "smb://" ) ):
                        xbmc.executehttpapi("FileCopy(%s.conf,%s.conf)" % ( filename[ 1 ], new_filename, ) )
                    poster = ( self.trailers.movies[ trailer ].poster, "amt-blank-poster.png", )[ not self.trailers.movies[ trailer ].poster ]
                    self.saveThumbnail( new_filename, trailer, poster )
            self.showOverlays( trailer )
            dialog.close()
        except:
            LOG( LOG_ERROR, "%s (rev: %s) GUI::saveCachedMovie [%s]", __scriptname__, __svn_revision__, sys.exc_info()[ 1 ], )
            dialog.close()
            xbmcgui.Dialog().ok( _( 56 ), _( 90 ) )
                
    def deleteSavedTrailer( self ):
        trailer = self._set_count_label( self.CONTROL_TRAILER_LIST_START )
        if ( xbmcgui.Dialog().yesno( "%s?" % ( _( 509 ), ), _( 82 ), self.trailers.movies[ trailer ].title ) ):
            for saved in self.trailers.movies[ trailer ].saved:
                if ( os.path.isfile( saved[ 0 ] ) ):
                    os.remove( saved[ 0 ] )
                if ( os.path.isfile( "%s.conf" % ( saved[ 0 ], ) ) ):
                    os.remove( "%s.conf" % ( saved[ 0 ], ) )
                if ( os.path.isfile( "%s.tbn" % ( os.path.splitext( saved[ 0 ] )[ 0 ], ) ) ):
                    os.remove( "%s.tbn" % ( os.path.splitext( saved[ 0 ] )[ 0 ], ) )
                success = self.trailers.updateRecord( "Movies", ( "saved", ), ( "[]", self.trailers.movies[ trailer ].idMovie, ), "idMovie" )
                if ( success ):
                    self.trailers.movies[ trailer ].saved = []
                    if ( self.category_id == DOWNLOADED ):
                        self.trailers.movies.pop( trailer )
                        self.removeItem( trailer )
                    if ( not len( self.trailers.movies ) ): self.clearTrailerInfo()
                    else: self.showTrailerInfo()

    def get_showtimes( self ):
        trailer = self._set_count_label( self.CONTROL_TRAILER_LIST_START )
        import showtimes
        force_fallback = self.skin != "Default"
        s = showtimes.GUI( "script-%s-showtimes.xml" % ( __scriptname__.replace( " ", "_" ), ), BASE_RESOURCE_PATH, self.skin, force_fallback, title=self.trailers.movies[ trailer ].title, location=self.settings[ "showtimes_local" ] )
        s.doModal()
        del s

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
                self.setCategory( GENRES, 0 )
            elif ( controlId == 104 ):
                self.setCategory( STUDIOS, 0 )
            elif ( controlId == 105 ):
                self.setCategory( ACTORS, 0 )
            elif ( controlId == 106 ):
                self.perform_search()
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
            elif ( controlId == self.CONTROL_CAST_LIST and self.cast_exists ):
                self.getActorChoice()
        except:
            LOG( LOG_ERROR, "%s (rev: %s) GUI::onClick [%s]", __scriptname__, __svn_revision__, sys.exc_info()[ 1 ], )


    def onFocus( self, controlId ):
        #xbmc.sleep( 10 )
        if ( controlId == self.CONTROL_TRAILER_LIST_GROUP ):
            self.controlId = self.CONTROL_TRAILER_LIST_START
        elif ( controlId == self.CONTROL_CATEGORY_LIST_GROUP ):
            self.controlId = self.CONTROL_CATEGORY_LIST
        else:
            self.controlId = controlId

    def onAction( self, action ):
        try:
            if ( action.getButtonCode() in EXIT_SCRIPT ):
                self.exitScript()
            elif ( action.getButtonCode() in TOGGLE_DISPLAY ):
                self.setCategory( self.current_display[ self.list_category == 0 ][ 0 ], self.current_display[ self.list_category == 0 ][ 1 ] )
            else:
                if ( self.CONTROL_TRAILER_LIST_START <= self.controlId <= self.CONTROL_TRAILER_LIST_END ):
                    if ( action.getButtonCode() in CONTEXT_MENU ):
                        self.showContextMenu()
                    elif ( action.getButtonCode() in SELECT_ITEM ):
                        self.playTrailer()
                    ###############################################################
                    elif ( action.getButtonCode() in MOVEMENT + ( 262, 263, ) ):
                        self.showTrailerInfo()
                    ###############################################################
                elif ( self.CONTROL_TRAILER_LIST_PAGE_START <= self.controlId <= self.CONTROL_TRAILER_LIST_PAGE_END ):
                    if ( action.getButtonCode() in MOVEMENT ):
                        self.showTrailerInfo()
                elif ( self.controlId == self.CONTROL_CATEGORY_LIST ):
                    if ( action.getButtonCode() in CONTEXT_MENU ):
                        self.showContextMenu()
                    #elif ( action.getButtonCode() in SELECT_ITEM ):
                    #    self.getTrailerGenre()
                    elif ( action.getButtonCode() in MOVEMENT_UP + MOVEMENT_DOWN ):
                        choice = self._set_count_label( self.CONTROL_CATEGORY_LIST )
                elif ( self.controlId == self.CONTROL_CATEGORY_LIST_PAGE ):
                    if ( action.getButtonCode() in MOVEMENT_UP + MOVEMENT_DOWN ):
                        self._set_count_label( self.CONTROL_CATEGORY_LIST )
                elif ( self.controlId == self.CONTROL_CAST_LIST ):
                    if ( action.getButtonCode() in CONTEXT_MENU ):
                        self.showContextMenu()
                elif ( ( self.CONTROL_TRAILER_LIST_PAGE_GROUP_START <= self.controlId <= self.CONTROL_TRAILER_LIST_PAGE_GROUP_END ) and action.getButtonCode() in SELECT_ITEM ):
                    self.showTrailerInfo()
                elif ( self.controlId in self.CONTROL_CATEGORY_LIST_PAGE_GROUP and action.getButtonCode() in SELECT_ITEM ):
                    self._set_count_label( self.CONTROL_CATEGORY_LIST )
                    #elif ( action.getButtonCode() in SELECT_ITEM ):
                    #    self.getActorChoice()
        except:
            LOG( LOG_ERROR, "%s (rev: %s) GUI::onAction [%s]", __scriptname__, __svn_revision__, sys.exc_info()[ 1 ], )

def main():
    _progress_dialog( len( modules ) + 1, _( 55 ) )
    settings = Settings().get_settings()
    force_fallback = settings[ "skin" ] != "Default"
    ui = GUI( "script-%s-main.xml" % ( __scriptname__.replace( " ", "_" ), ), BASE_RESOURCE_PATH, settings[ "skin" ], force_fallback )
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