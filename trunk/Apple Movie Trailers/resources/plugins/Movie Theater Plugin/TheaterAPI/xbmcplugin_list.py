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
        from urllib import unquote
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
            fpaths += [ unquote( path ) ]
        return fpaths

    def _parse_argv( self ):
        # call _Info() with our formatted argv to create the self.args object
        exec "self.args = _Info(%s)" % ( sys.argv[ 2 ][ 1 : ].replace( "&", ", " ), )
        # backslashes cause issues when passed in the url
        self.args.path = [ self.args.path.replace( "[[BACKSLASH]]", "\\" ) ]

    def _get_items( self, path ):
        try:
            # smb share, database and local, need to retrieve the lists differently
            if ( self.settings[ "use_db" ] ):
                entries = self._get_videodb_list()
            else:
                entries = []
                for path in self.args.path:
                    if ( path.startswith( "smb://" ) ):
                        entries += self._get_smb_list( path )
                    else:
                        entries += self._get_local_list( path )
            # fill media list
            ok = self._fill_media_list( entries )
            # set content
            if ( ok ): xbmcplugin.setContent( handle=int( sys.argv[ 1 ] ), content="movies" )
        except:
            # oops print error message
            print sys.exc_info()[ 1 ]
            ok = False
        # send notification we're finished, successfully or unsuccessfully
        xbmcplugin.endOfDirectory( handle=int( sys.argv[ 1 ] ), succeeded=ok )

    def _get_videodb_list( self ):
        try:
            # TODO: change GLOB -> LIKE when and if sqLite get's updated with a fix
            from urllib import urlencode
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
            # our sql statement
            sql = """
                    SELECT path.strPath, files.strFileName, movie.c00, movie.c01, movie.c09, movie.c12, movie.c14, movie.c18 
                    FROM movie 
                    JOIN files ON files.idFile=movie.idFile 
                    JOIN path ON files.idPath=path.idPath 
                    %s
                    LIMIT 100 OFFSET %d
                    """
            # format our response, so it returns a valid python list of records
            xbmc.executehttpapi( "SetResponseFormat(OpenRecordSet,%s)" % ( urlencode( {"e": '[' } )[ 2 : ], ) )
            xbmc.executehttpapi( "SetResponseFormat(CloseRecordSet,%s)" % ( urlencode( {"e": ']' } )[ 2 : ], ) )
            xbmc.executehttpapi( "SetResponseFormat(OpenRecord,%s)" % ( urlencode( {"e": '(' } )[ 2 : ], ) )
            xbmc.executehttpapi( "SetResponseFormat(CloseRecord,%s)" % ( urlencode( {"e": '), ' } )[ 2 : ], ) )
            # we use [[TRIPLE_QUOTE]] for fields so as not to interfere with quoted strings
            xbmc.executehttpapi( "SetResponseFormat(OpenField,%s)" % ( urlencode( {"e": '[[TRIPLE_QUOTE]]' } )[ 2 : ], ) )
            xbmc.executehttpapi( "SetResponseFormat(CloseField,%s)" % ( urlencode( {"e": '[[TRIPLE_QUOTE]], ' } )[ 2 : ], ) )
            # query the database
            entries = []
            offset = 0
            records = ""
            while records != "[]":
                # create new sql based on our offset. (we limit the number of records returned each time to 100 for memory)
                new_sql = sql % ( rating_sql, offset, )
                # fetch the records
                records = xbmc.executehttpapi( "QueryVideoDatabase(%s)" % urlencode({"e": new_sql })[ 2 : ] )
                # if query was not successful, raise an error
                if ( "Error:" in records ): raise
                # eval response to a python list, replace \ with \\ or else eval will fail, same with handling quotes
                items = eval( records.replace( "\\", "\\\\" ).replace( '"', "[[QUOTE]]" ).replace( "[[TRIPLE_QUOTE]]", '"""' ) )
                # enumerate through our items list and add the info to our entries list
                for entry in items:
                    # TODO: fix a stacked path
                    # for stacked paths we do not concatenate the file and path
                    fpath = entry[ 0 ]
                    if ( not entry[ 0 ].startswith( "stack://" ) ):
                        fpath += entry[ 1 ]
                    # add video to our list
                    entries += [ ( unicode( fpath, "utf-8" ), unicode( entry[ 2 ].replace( "[[QUOTE]]", '"' ), "utf-8" ), False, entry[ 3 ].replace( "[[QUOTE]]", '"' ), entry[ 4 ], entry[ 5 ], entry[ 6 ], entry[ 7 ] ) ]
                offset += 100
        except:
            # oops print error message
            print sys.exc_info()[ 1 ]
        return entries

    def _get_smb_list( self, path ):
        try:
            entries = []
            # import the necessary modules
            from TheaterAPI import smb
            from TheaterAPI import nmb
            # split the path into useable parts
            share_string_list = path.split( "/" )
            # check for username/password in path
            username = password = ""
            if ( "@" in share_string_list[ 2 ] ):
                # this is the computers name
                remote_name = share_string_list[ 2 ].split( "@" )[ 1 ]
                # get the username/password
                login = share_string_list[ 2 ].split( "@" )[ 0 ]
                # username is the first parameter
                username = login.split( ":" )[ 0 ]
                # password is the second parameter if it exists
                if ( ":" in login ): password = login.split( ":" )[ 1 ]
            else:
                # this is the computers name
                remote_name = share_string_list[ 2 ]
                # default to Guest (May not work with all shares)
                username = "Guest"
            # we need the ip address of the computer
            remote_ip = nmb.NetBIOS().gethostbyname( remote_name )[ 0 ].get_ip()
            # this is the share name
            remote_share = share_string_list[ 3 ]
            # create our connection
            remote_conn = smb.SMB( remote_name, remote_ip )
            # if login is required, pass our username/password
            if ( remote_conn.is_login_required() ):
                remote_conn.login( username, password )
            # set our folder
            folder = "/".join( share_string_list[ 4 : ] ) + "/*"
            # get the paths list
            items = remote_conn.list_path( remote_share, folder )
            # enumerate through our items list and add the full name to our entries list
            for item in items:
                # we don't want the . or .. directory items
                if ( item.get_longname() and item.get_longname() != "." and item.get_longname() != ".." ):
                    # concatenate directory pairs
                    file_path = "%s/%s" % ( path, item.get_longname(), )
                    # get the item info
                    title, isVideo, isFolder = self._get_file_info( file_path )
                    # add our item to our entry list
                    if ( isVideo or isFolder ):
                        entries += [ ( file_path, title, isFolder, "", "", "", "", "" ) ]
        except:
            # oops print error message
            print sys.exc_info()[ 1 ]
        return entries

    def _get_local_list( self, path ):
        try:
            entries = []
            # get the paths list
            items = os.listdir( unicode( path, "utf-8" ) )
            # enumerate through our items list and add the full name to our entries list
            for item in items:
                # concatenate directory pairs
                file_path = "%s%s%s" % ( path, os.sep, item, )
                # get the item info
                title, isVideo, isFolder = self._get_file_info( file_path )
                # add our item to our entry list
                if ( isVideo or isFolder ):
                    entries += [ ( file_path, title, isFolder, "", "", "", "", "" ) ]
        except:
            # oops print error message
            print sys.exc_info()[ 1 ]
        return entries

    def _get_file_info( self, file_path ):
        try:
            # parse item for title
            title = os.path.splitext( os.path.basename( file_path ) )[ 0 ]
            # is this a folder?
            isFolder = os.path.isdir( self._fix_stacked_path( file_path ) )
            isVideo = False
            # if this is a file, check to see if it's a valid video file
            if ( not isFolder ):
                # get the files extension
                ext = os.path.splitext( file_path )[ 1 ].lower()
                # if it is a video file add it to our items list
                isVideo = ( ext and ext in self.VIDEO_EXT )
            return title, isVideo, isFolder
        except:
            return "", False, False

    def _fill_media_list( self, items ):
        try:
            ok = True
            # enumerate through the list of items and add the item to the media list
            for item in items:
                # create our url (backslashes cause issues when passed in the url)
                url = '%s?path="""%s"""&isFolder=%d' % ( sys.argv[ 0 ], item[ 0 ].replace( "\\", "[[BACKSLASH]]" ), item[ 2 ], )
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
                        date = datetime.datetime.fromtimestamp( os.path.getmtime( fpath ) ).strftime( "%d-%m-%Y" )
                        # get the size of the file
                        size = long( os.path.getsize( fpath ) )
                        # only need to add label and thumbnail, setInfo() and addSortMethod() takes care of label2
                        listitem=xbmcgui.ListItem( label=item[ 1 ], iconImage=icon, thumbnailImage=thumbnail )
                        # set an overlay if one is practical
                        overlay = ( xbmcgui.ICON_OVERLAY_NONE, xbmcgui.ICON_OVERLAY_RAR, xbmcgui.ICON_OVERLAY_ZIP, )[ item[ 0 ].endswith( ".rar" ) + ( 2 * item[ 0 ].endswith( ".zip" ) ) ]
                        ##TODO fix year and add other items
                        # add the different infolabels we want to sort by
                        listitem.setInfo( type="Video", infoLabels={ "Title": item[ 1 ], "Date": date, "Size": size, "Overlay": overlay, "Plot": item[ 3 ], "Plotoutline": item[ 3 ], "MPAA": item[ 5 ], "Genre": item[ 6 ], "Studio": item[ 7 ], "Year": 0 } )
                    except:
                        continue
                # add the item to the media list
                ok = xbmcplugin.addDirectoryItem( handle=int( sys.argv[ 1 ] ), url=url, listitem=listitem, isFolder=item[ 2 ], totalItems=len( items ) )
                # if user cancels, call raise to exit loop
                if ( not ok ): raise
        except:
            # user cancelled dialog or an error occurred
            print sys.exc_info()[ 1 ]
            ok = False
        # if successful and user did not cancel, add all the required sort methods
        if ( ok ):
            xbmcplugin.addSortMethod( handle=int( sys.argv[ 1 ] ), sortMethod=xbmcplugin.SORT_METHOD_LABEL )
            xbmcplugin.addSortMethod( handle=int( sys.argv[ 1 ] ), sortMethod=xbmcplugin.SORT_METHOD_DATE )
            xbmcplugin.addSortMethod( handle=int( sys.argv[ 1 ] ), sortMethod=xbmcplugin.SORT_METHOD_SIZE )
        return ok

    def _fix_stacked_path( self, path ):
        if ( path.startswith( "stack://" ) ):
            path = path[ 8 : ].split( " , " )[ 0 ]
        return path

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
            if ( not os.path.isfile( thumbnail ) ):
                thumbnail = ""
        return thumbnail
