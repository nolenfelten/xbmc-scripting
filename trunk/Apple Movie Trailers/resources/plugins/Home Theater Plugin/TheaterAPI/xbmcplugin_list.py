"""
    Movie Theater: Module creates a directory listing of videos and folders.
"""

# main imports
import os
import sys
import xbmc
import xbmcgui
import xbmcplugin

import datetime
from urllib import quote_plus, unquote_plus


class _Info:
    def __init__( self, *args, **kwargs ):
        self.__dict__.update( kwargs )


class Main:
    # base paths
    BASE_CACHE_PATH = os.path.join( "P:\\Thumbnails", "Video" )
    BASE_DATABASE_PATH = sys.modules[ "__main__" ].BASE_DATABASE_PATH
    # add all video extensions wanted in lowercase
    VIDEO_EXT = ".m4v|.3gp|.nsv|.ts|.ty|.strm|.pls|.rm|.rmvb|.m3u|.ifo|.mov|.qt|.divx|.xvid|.bivx|.vob|.nrg|.img|.iso|.pva|.wmv|.asf|.asx|.ogm|.m2v|.avi|.bin|.dat|.mpg|.mpeg|.mp4|.mkv|.avc|.vp3|.svq3|.nuv|.viv|.dv|.fli|.flv|.rar|.001|.wpl|.zip|.vdr|.dvr-ms|.xsp"

    def __init__( self ):
        # if no database was found we need to run the script to create it.
        if ( not os.path.isfile( os.path.join( self.BASE_DATABASE_PATH, "AMT.db" ) ) ):
            self._launch_script()
        else:
            self._get_settings()
            if ( sys.argv[ 2 ] ):
                self._parse_argv()
            self._get_items( self.args.path )

    def _launch_script( self ):
        # no database was found so notify XBMC we're finished
        xbmcplugin.endOfDirectory( handle=int( sys.argv[ 1 ] ), succeeded=False )
        # ask to run script to create the database
        if ( os.path.isfile( xbmc.translatePath( os.path.join( "Q:\\scripts", sys.modules[ "__main__" ].__script__, "default.py" ) ) ) ):
            if ( xbmcgui.Dialog().yesno( sys.modules[ "__main__" ].__plugin__, "Database not found!", "Would you like to run the main script?" ) ):
                xbmc.executebuiltin( "XBMC.RunScript(%s)" % ( xbmc.translatePath( os.path.join( "Q:\\scripts", sys.modules[ "__main__" ].__script__, "default.py" ) ), ) )
        else:
            ok = xbmcgui.Dialog().ok( sys.modules[ "__main__" ].__plugin__, "Database not found!", "You need to install and run the main script.", sys.modules[ "__main__" ].__svn_url__ )

    def _get_settings( self ):
        self.settings = {}
        self.settings[ "path" ] = self._get_path_list( xbmcplugin.getSetting( "path" ) )
        self.settings[ "use_db" ] = xbmcplugin.getSetting( "use_db" ) == "true"
        self.settings[ "limit_query" ] = xbmcplugin.getSetting( "limit_query" ) == "true"
        self.settings[ "rating" ] = int( xbmcplugin.getSetting( "rating" ) )
        # we need to set self.args.path
        self.args = _Info( path=self.settings[ "path" ] )

    def _get_path_list( self, paths ):
        # we do not want the slash at end
        if ( paths.endswith( "\\" ) or paths.endswith( "/" ) ):
            paths = paths[ : -1 ]
        # if this is not a multipath return it as a list
        if ( not paths.startswith( "multipath://" ) ): return [ paths ]
        # we need to parse out the separate paths in a multipath share
        fpaths = []
        # multipaths are separated by a forward slash(why not a pipe)
        path_list = paths[ 12 : ].split( "/" )
        # enumerate thru our path list and unquote the url
        for path in path_list:
        # we do not want the slash at end
            if ( path.endswith( "\\" ) or path.endswith( "/" ) ):
                path = path[ : -1 ]
            # add our path
            fpaths += [ unquote_plus( path ) ]
        return fpaths

    def _parse_argv( self ):
        # call _Info() with our formatted argv to create the self.args object
        exec "self.args = _Info(%s)" % ( sys.argv[ 2 ][ 1 : ].replace( "&", ", " ), )
        # backslashes cause issues when passed in the url
        self.args.path = [ self.args.path.replace( "[[BACKSLASH]]", "\\" ) ]

    def _get_items( self, path ):
        try:
            # smb share and local retrieve the lists differently than database
            if ( self.settings[ "use_db" ] ):
                ok = self._get_videodb_list()
            else:
                ok = self._get_list()
            # if successful and user did not cancel, add all the required sort methods and set the content
            if ( ok ):
                xbmcplugin.addSortMethod( handle=int( sys.argv[ 1 ] ), sortMethod=xbmcplugin.SORT_METHOD_LABEL )
                xbmcplugin.addSortMethod( handle=int( sys.argv[ 1 ] ), sortMethod=xbmcplugin.SORT_METHOD_DATE )
                xbmcplugin.addSortMethod( handle=int( sys.argv[ 1 ] ), sortMethod=xbmcplugin.SORT_METHOD_SIZE )
                # set content
                xbmcplugin.setContent( handle=int( sys.argv[ 1 ] ), content="movies" )
        except:
            # oops print error message
            print sys.exc_info()[ 1 ]
            ok = False
        # send notification we're finished, successfully or unsuccessfully
        xbmcplugin.endOfDirectory( handle=int( sys.argv[ 1 ] ), succeeded=ok )

    def _get_videodb_list( self ):
        try:
            ok = True
            # TODO: change GLOB -> LIKE when and if sqLite get's updated with a fix
            rating_sql = ""
            mpaa_ratings = [ "G", "PG", "PG-13", "R", "NC-17" ]
            # if the user set a valid rating and limit query add all up to the selection
            if ( self.settings[ "limit_query" ] and self.settings[ "rating" ] < len( mpaa_ratings ) ):
                user_rating = mpaa_ratings[ self.settings[ "rating" ] ]
                rating_sql = "WHERE ("
                # enumerate through mpaa ratings and add the selected ones to our sql statement
                for rating in mpaa_ratings:
                    rating_sql += "movie.c12 GLOB '* %s *' OR " % ( rating, )
                    # if we found the users choice, we're finished
                    if ( rating == user_rating ): break
                # fix the sql statement
                rating_sql = rating_sql[ : -4 ] + ") "
            # TODO: add pagination (ORDER BY movie.c00 LIMIT %d OFFSET %d)
            # our sql statement movie.c00, movie.c01, movie.c09, movie.c12, movie.c14, movie.c18 
            sql = "SELECT path.strPath, files.strFileName, movie.* FROM movie JOIN files ON files.idFile=movie.idFile JOIN path ON files.idPath=path.idPath %sLIMIT 50 OFFSET %d;"
            cast_sql = "SELECT actors.strActor, actorlinkmovie.strRole FROM actorlinkmovie JOIN actors ON actors.idActor=actorlinkmovie.idActor WHERE actorlinkmovie.idMovie=%s;"
            # TODO: determine why 'u[[TRIPLE_QUOTE]]' as an OpenField response does not work as a unicode qualifier
            # format our response, so it returns a valid python list of records
            xbmc.executehttpapi( "SetResponseFormat(OpenRecordSet,%s)" % ( quote_plus( '[' ), ) )
            xbmc.executehttpapi( "SetResponseFormat(CloseRecordSet,%s)" % ( quote_plus( ']' ), ) )
            xbmc.executehttpapi( "SetResponseFormat(OpenRecord,%s)" % ( quote_plus( '(' ), ) )
            xbmc.executehttpapi( "SetResponseFormat(CloseRecord,%s)" % ( quote_plus( '), ' ), ) )
            # we use [[TRIPLE_QUOTE]] for fields so as not to interfere with quoted strings
            xbmc.executehttpapi( "SetResponseFormat(OpenField,%s)" % ( quote_plus( '[[TRIPLE_QUOTE]]' ), ) )
            xbmc.executehttpapi( "SetResponseFormat(CloseField,%s)" % ( quote_plus( '[[TRIPLE_QUOTE]], ' ), ) )
            # query the database
            items = []
            offset = 0
            records = ""
            while records != "[]":
                # create new sql based on our offset. (we limit the number of records returned each time to 100 for memory)
                new_sql = sql % ( rating_sql, offset, )
                # fetch the records
                records = xbmc.executehttpapi( "QueryVideoDatabase(%s)" % quote_plus( new_sql ), )
                # eval response to a python list, replace \ with \\ or else eval will fail, same with handling quotes
                items += eval( records.replace( "\\", "\\\\" ).replace( '"', "[[QUOTE]]" ).replace( "[[TRIPLE_QUOTE]]", '"""' ) )
                # increment our record offset
                offset += 50
            # enumerate through our items list and add the info to our media list
            for item in items:
                # fetch the cast
                records = xbmc.executehttpapi( "QueryVideoDatabase(%s)" % quote_plus( cast_sql % ( item[ 2 ], ) ), )
                # our final actor/role list
                actors = []
                # eval response to a python list, replace \ with \\ or else eval will fail, same with handling quotes
                try:
                    cast = eval( records.replace( "\\", "\\\\" ).replace( '"', "[[QUOTE]]" ).replace( "[[TRIPLE_QUOTE]]", '"""' ) )
                    # we enumerate through and convert actors/roles to a unicode object
                    # we have to do this because adding a 'u' to OpenField response does not work
                    for actor in cast:
                        actors += [ ( unicode( actor[ 0 ], "utf-8" ), unicode( actor[ 1 ], "utf-8" ), ) ]
                except:
                    pass
                # TODO: fix a stacked path
                # for stacked paths we do not concatenate the file and path(maybe we do?)
                fpath = item[ 0 ]
                if ( not item[ 0 ].startswith( "stack://" ) ):
                    fpath += item[ 1 ]
                # add video to our list
                ok = self._add_item( ( unicode( fpath, "utf-8" ), unicode( item[ 3 ].replace( "[[QUOTE]]", '"' ), "utf-8" ), False, unicode( item[ 4 ].replace( "[[QUOTE]]", '"' ), "utf-8" ), unicode( item[ 5 ].replace( "[[QUOTE]]", '"' ), "utf-8" ), unicode( item[ 6 ].replace( "[[QUOTE]]", '"' ), "utf-8" ), item[ 7 ], item[ 8 ], unicode( item[ 9 ], "utf-8" ), item[ 10 ], item[ 11 ], item[ 12 ], item[ 13 ], item[ 14 ], item[ 15 ], item[ 16 ], item[ 17 ], unicode( item[ 18 ], "utf-8" ), item[ 19 ], item[ 20 ], unicode( item[ 21 ], "utf-8" ), actors ), len( items ) )
                if ( not ok ): raise
        except:
            #oops print error message
            ok = False
            print sys.exc_info()[ 1 ]
        return ok

    def _get_list( self ):
        items = []
        for path in self.args.path:
            items += self._get_file_list( path )
        return self._fill_media_list( items )

    def _get_file_list( self, path ):
        #    if ( os.path.supports_unicode_filenames or os.environ.get( "OS", "n/a" ) == "win32"  or os.environ.get( "OS", "n/a" ) == "xbox" ):
        try:
            items = []
            # get the directory listing
            entries = xbmc.executehttpapi( "GetDirectory(%s)" % ( path, ) ).split( "\n" )
            # enumerate through our items list and add the full name to our entries list
            for entry in entries:
                # fix path
                entry = entry.replace( "<li>", "" )
                if ( entry.endswith( "/" ) or entry.endswith( "\\" ) ):
                    entry = entry[ : -1 ]
                file_path = unicode( entry, "utf-8" )
                # get the item info
                title, isVideo, isFolder = self._get_file_info( file_path )
                # add our item to our entry list
                if ( isVideo or isFolder ):
                    items += [ ( file_path, title, isFolder, "", "", "", "", "0", "", "0", "", "", "", "", "", "", "", "", "", "", "", [], ) ]
        except:
            # oops print error message
            print sys.exc_info()[ 1 ]
        return items
        
    def _get_file_info( self, file_path ):
        try:
            # parse item for title
            title = os.path.splitext( os.path.basename( file_path ) )[ 0 ]
            # is this a folder?
            isFolder = os.path.isdir( self._fix_stacked_path( file_path ) )
            # default isVideo to false
            isVideo = False
            # if this is a file, check to see if it's a valid video file
            if ( not isFolder ):
                # get the files extension
                ext = os.path.splitext( file_path )[ 1 ].lower()
                # if it is a video file add it to our items list
                isVideo = ( ext and ext in self.VIDEO_EXT )
            return title, isVideo, isFolder
        except:
            # oops print error message
            print repr( file_path )
            print sys.exc_info()[ 1 ]
            return "", False, False

    def _fill_media_list( self, items ):
        try:
            ok = True
            for item in items:
                ok = self._add_item( item, len( items ) )
                if ( not ok ): raise
        except:
            ok = False
        return ok

    def _add_item( self, item, total ):
        ok = True
        add = True
        # call this hack for rar files, strict rules apply to the naming of the video inside
        url_path = self._fix_rar_path( item[ 0 ] )
        # create our url
        url = '%s?path="%s"&isFolder=%d' % ( sys.argv[ 0 ], url_path, item[ 2 ], )
        if ( item[ 2 ] ):
            # if a folder.jpg exists use that for our thumbnail
            #thumbnail = os.path.join( item[ 0 ], "%s.jpg" % ( title, ) )
            #if ( not os.path.isfile( thumbnail ) ): thumbnail = ""
            icon = "DefaultFolder.png"
            # only need to add label and icon, setInfo() and addSortMethod() takes care of label2
            listitem=xbmcgui.ListItem( label=item[ 1 ], iconImage=icon )
            # add the different infolabels we want to sort by
            listitem.setInfo( type="Video", infoLabels={ "Title": item[ 1 ] + " (%s)" % ( xbmc.getLocalizedString( 20334 ), ) } )
        else:
            fpath = self._fix_stacked_path( item[ 0 ] )
            # call _get_thumbnail() for the path to the cached thumbnail
            thumbnail = self._get_thumbnail( fpath )
            # set the default icon
            icon = "DefaultVideo.png"
            try:
                # get the date of the file
                date = datetime.datetime.fromtimestamp( os.path.getmtime( fpath.encode( "utf-8" ) ) ).strftime( "%d-%m-%Y" )
                # get the size of the file
                size = long( os.path.getsize( fpath.encode( "utf-8" ) ) )
                # only need to add label and thumbnail, setInfo() and addSortMethod() takes care of label2
                listitem=xbmcgui.ListItem( label=item[ 1 ], iconImage=icon, thumbnailImage=thumbnail.encode( "utf-8" ) )
                # set an overlay if one is practical
                overlay = ( xbmcgui.ICON_OVERLAY_NONE, xbmcgui.ICON_OVERLAY_RAR, xbmcgui.ICON_OVERLAY_ZIP, )[ item[ 0 ].endswith( ".rar" ) + ( 2 * item[ 0 ].endswith( ".zip" ) ) ]
                # add the different infolabels we want to sort by
                listitem.setInfo( type="Video", infoLabels={ "Title": item[ 1 ], "Date": date, "Size": size, "Overlay": overlay, "Plot": item[ 3 ], "Plotoutline": item[ 4 ], "TagLine": item[ 5 ], "Rating": float( item[ 7 ] ), "Writer": item[ 8 ], "Year": int( item[ 9 ] ), "Runtime": item[ 13 ], "MPAA": item[ 14 ], "Genre": item[ 16 ], "Director": item[ 17 ], "Studio": item[ 18 ], "Cast": item[ 21 ] } )
            except:
                # oops print error message
                add = False
                print repr( item[ 1 ] )
                print sys.exc_info()[ 1 ]
        if ( add ):
            # add the item to the media list
            ok = xbmcplugin.addDirectoryItem( handle=int( sys.argv[ 1 ] ), url=url, listitem=listitem, isFolder=item[ 2 ], totalItems=total )
        return ok

    def _fix_stacked_path( self, path ):
        if ( path.startswith( "stack://" ) ):
            path = path[ 8 : ].split( " , " )[ 0 ]
        return path

    def _fix_rar_path( self, path ):
        # TODO: find a way to list rar's as a directory
        # if it's not a rar file, return it with the backslash fix
        if ( not path.endswith( ".rar" ) ): return path.replace( "\\", "[[BACKSLASH]]" )
        # we split the basename off and use that for the video's filename with an .avi extension
        rar_video_name = os.path.splitext( os.path.basename( path ) )[ 0 ] + ".avi"
        # rar paths need to be quoted, including ._-
        url_path = quote_plus( path ).replace( ".", "%2e").replace( "-", "%2d").replace( "_", "%5f")
        # append the path with our filename
        filepath = "rar://%s/%s" % ( url_path, rar_video_name, )
        # return the filename with the backslash fix
        return filepath.replace( "\\", "[[BACKSLASH]]" )

    def _get_thumbnail( self, path ):
        fpath = path
        # if this is a smb path, we need to eliminate username/password
        if ( path.startswith( "smb://" ) and "@" in path ):
            # split the path into useable parts
            share_string_list = path.split( "/" )
            # strip username/password
            share_string_list[ 2 ] = share_string_list[ 2 ].split( "@" )[ 1 ]
            # concatenate the list back together
            fpath = "/".join( share_string_list )
        # make the proper cache filename and path so duplicate caching is unnecessary
        filename = xbmc.getCacheThumbName( fpath )
        thumbnail = xbmc.translatePath( os.path.join( self.BASE_CACHE_PATH, filename[ 0 ], filename ) )
        # if the cached thumbnail does not exist check for a tbn file
        if ( not os.path.isfile( thumbnail ) ):
            # create filepath to a local tbn file
            thumbnail = os.path.splitext( path )[ 0 ] + ".tbn"
            # if there is no local tbn file leave blank
            if ( not os.path.isfile( thumbnail.encode( "utf-8" ) ) ):
                thumbnail = ""
        return thumbnail
