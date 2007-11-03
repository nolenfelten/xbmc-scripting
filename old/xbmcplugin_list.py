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
import traceback

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
            # if this is the first time in, get the settings
            if ( not sys.argv[ 2 ] ):
                self._get_settings()
            else:
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
        try:
            f = open( os.path.join( os.getcwd().replace( ";", "" ), "settings.xml" ), "r" )
            data = f.read()
            f.close()
            import re
            arg_string = ""
            items = re.findall( '<setting (.*?)>(.*?)</setting>', data, re.IGNORECASE )
            for item in items:
                name = re.findall( 'name=\"([^\"]*)\"', item[ 0 ], re.IGNORECASE )
                stype = re.findall( 'type=\"([^\"]*)\"', item[ 0 ], re.IGNORECASE )
                if ( stype[ 0 ] == "bool" or stype[ 0 ] == "select int" ):
                    fstr = '%s=%s,'
                else:
                    fstr = '%s="""%s""",'
                arg_string += fstr % ( name[ 0 ], item[ 1 ], )
            exec "self.args = _Info(%s)" % ( arg_string[ : -1 ], )
        except:
            # oops print error message
            print sys.exc_info()[ 1 ]

    def _parse_argv( self ):
        # call _Info() with our formatted argv to create the self.args object
        exec "self.args = _Info(%s)" % ( sys.argv[ 2 ][ 1 : ].replace( "&", ", " ), )
        # backslashes cause issues when passed in the url
        self.args.path = self.args.path.replace( "[[BACKSLASH]]", "\\" )
        self.args.trailer_intro_path = self.args.trailer_intro_path.replace( "[[BACKSLASH]]", "\\" )
        self.args.movie_intro_path = self.args.movie_intro_path.replace( "[[BACKSLASH]]", "\\" )
        self.args.movie_end_path = self.args.movie_end_path.replace( "[[BACKSLASH]]", "\\" )

    def _get_items( self, path ):
        try:
            # smb share, database and local, need to retrieve the lists differently
            if ( self.args.use_db ):
                entries = self._get_videodb_list( path )
            elif ( path.startswith( "smb://" ) ):
                entries = self._get_smb_list( path )
            else:
                entries = self._get_local_list( path )
            # fill media list
            ok = self._fill_media_list( entries )
        except:
            # oops print error message
            print sys.exc_info()[ 1 ]
            ok = False
        # send notification we're finished, successfully or unsuccessfully
        xbmcplugin.endOfDirectory( handle=int( sys.argv[ 1 ] ), succeeded=ok )

    def _get_videodb_list( self, path ):
        try:
            from urllib import urlencode
            # if the user has a certain path, set it
            path_sql = ""
            if ( path ):
                path_sql = "WHERE path.strPath LIKE '%s%%%%' " % path
            rating_sql = ""
            mpaa_ratings = [ "G", "PG", "PG-13", "R", "NC-17" ]
            # if the user set a valid rating and limit query add all up to the selection
            if ( self.args.limit_query and self.args.rating in mpaa_ratings ):
                if ( path_sql ): rating_sql = "AND ("
                else: rating_sql = "WHERE ("
                # enumerate through mpaa ratings and add the selected ones to our sql statement
                for rating in mpaa_ratings:
                    rating_sql += "movie.c12 LIKE '%%%% %s %%%%' OR " % ( rating, )
                    # if we found the users choice, we're finished
                    if ( rating == self.args.rating ): break
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
                    %s
                    """ % ( path_sql, rating_sql, )
            # format our response, so it returns a valid python list of records
            xbmc.executehttpapi( "SetResponseFormat(OpenRecordSet,%s)" % ( urlencode( {"e": '[' } )[ 2 : ], ) )
            xbmc.executehttpapi( "SetResponseFormat(CloseRecordSet,%s)" % ( urlencode( {"e": ']' } )[ 2 : ], ) )
            xbmc.executehttpapi( "SetResponseFormat(OpenRecord,%s)" % ( urlencode( {"e": '(' } )[ 2 : ], ) )
            xbmc.executehttpapi( "SetResponseFormat(CloseRecord,%s)" % ( urlencode( {"e": '), ' } )[ 2 : ], ) )
            xbmc.executehttpapi( "SetResponseFormat(OpenField,%s)" % ( urlencode( {"e": '"""' } )[ 2 : ], ) )
            xbmc.executehttpapi( "SetResponseFormat(CloseField,%s)" % ( urlencode( {"e": '""", ' } )[ 2 : ], ) )
            # query the database
            records = xbmc.executehttpapi( "QueryVideoDatabase(%s)" % urlencode({"e": sql })[ 2 : ] )
            entries = []
            # if query was successful, set our entries list
            if ( "Error:" not in records ):
                print records
                # eval response to a python list, replace \ with \\ or else eval will fail
                items = eval( records.replace( "\\", "\\\\" ) )
                # enumerate through our items list and add the info to our entries list
                for entry in items:
                    entries += [ ( entry[ 0 ] + entry[ 1 ], entry[ 2 ], False, entry[ 3 ], entry[ 4 ], entry[ 5 ], entry[ 6 ], entry[ 7 ] ) ]
        except:
            # oops print error message
            print sys.exc_info()[ 1 ]
        return entries

    def _get_smb_list( self, path ):
        entries = []
        # import the necessary modules
        from TheaterAPI import smb
        from TheaterAPI import nmb
        # split the path into useable parts
        share_string_list = path.split( "/" )
        # this is the computers name
        remote_name = share_string_list[ 2 ]
        # we need the ip address of the computer
        remote_ip = nmb.NetBIOS().gethostbyname( remote_name )[ 0 ].get_ip()
        # this is the share name
        remote_share = share_string_list[ 3 ]
        # create our connection
        remote_conn = smb.SMB( remote_name, remote_ip )
        # if login is required, pass our username/password
        if ( remote_conn.is_login_required() ):
            remote_conn.login( self.args.username, self.args.password )
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
        return entries

    def _get_local_list( self, path ):
        entries = []
        # get the paths list
        items = os.listdir( path )
        # enumerate through our items list and add the full name to our entries list
        for item in items:
            # concatenate directory pairs
            file_path = "%s%s%s" % ( path, os.sep, item, )
            # get the item info
            title, isVideo, isFolder = self._get_file_info( file_path )
            # add our item to our entry list
            if ( isVideo or isFolder ):
                entries += [ ( file_path, title, isFolder, "", "", "", "", "" ) ]
        return entries

    def _get_file_info( self, file_path ):
        # parse item for title
        title = os.path.splitext( os.path.basename( file_path ) )[ 0 ]
        # is this a folder?
        isFolder = os.path.isdir( file_path )
        isVideo = False
        # if this is a file, check to see if it's a valid video file
        if ( not isFolder ):
            # get the files extension
            ext = os.path.splitext( file_path )[ 1 ].lower()
            # if it is a video file add it to our items list
            isVideo = ( ext and ext in self.VIDEO_EXT )
        return title, isVideo, isFolder

    def _fill_media_list( self, items ):
        try:
            ok = True
            # enumerate through the list of items and add the item to the media list
            for item in items:
                # create our url (backslashes cause issues when passed in the url)
                url = '%s?path="""%s"""&isFolder=%d&username="""%s"""&password="""%s"""&trailer_intro_path="""%s"""&movie_intro_path="""%s"""&number_trailers=%d&rating="""%s"""&only_hd=%d&quality="""%s"""&use_db=%d&limit_query=%d&movie_end_path="""%s"""' % ( sys.argv[ 0 ], item[ 0 ].replace( "\\", "[[BACKSLASH]]" ), item[ 2 ], self.args.username, self.args.password, self.args.trailer_intro_path.replace( "\\", "[[BACKSLASH]]" ), self.args.movie_intro_path.replace( "\\", "[[BACKSLASH]]" ), self.args.number_trailers, self.args.rating, self.args.only_hd, self.args.quality, self.args.use_db, self.args.limit_query, self.args.movie_end_path, )
                if ( item[ 2 ] ):
                    # if a folder.jpg exists use that for our thumbnail
                    #thumbnail = os.path.join( item[ 0 ], "%s.jpg" % ( title, ) )
                    #if ( not os.path.isfile( thumbnail ) ):
                    icon = "DefaultFolder.png"
                    # only need to add label and icon, setInfo() and addSortMethod() takes care of label2
                    listitem=xbmcgui.ListItem( label=item[ 1 ], iconImage=icon )
                    # add the different infolabels we want to sort by
                    listitem.setInfo( type="Video", infoLabels={ "Title": item[ 1 ] + " (%s)" % ( xbmc.getLocalizedString( 20334 ), ) } )
                else:
                    # call _get_thumbnail() for the path to the cached thumbnail
                    thumbnail = self._get_thumbnail( item[ 0 ] )
                    # set the default icon
                    icon = "DefaultVideo.png"
                    # get the date of the file
                    date = datetime.datetime.fromtimestamp( os.path.getmtime( item[ 0 ] ) ).strftime( "%d-%m-%Y" )
                    # get the size of the file
                    size = long( os.path.getsize( item[ 0 ] ) )
                    # only need to add label and thumbnail, setInfo() and addSortMethod() takes care of label2
                    listitem=xbmcgui.ListItem( label=item[ 1 ], iconImage=icon, thumbnailImage=thumbnail )
                    # set an overlay if one is practical
                    overlay = ( xbmcgui.ICON_OVERLAY_NONE, xbmcgui.ICON_OVERLAY_RAR, xbmcgui.ICON_OVERLAY_ZIP, )[ item[ 0 ].endswith( ".rar" ) + ( 2 * item[ 0 ].endswith( ".zip" ) ) ]
                    # add the different infolabels we want to sort by
                    listitem.setInfo( type="Video", infoLabels={ "Title": item[ 1 ], "Date": date, "Size": size, "Overlay": overlay, "Plot": item[ 3 ], "MPAA": item[ 5 ], "Genre": item[ 6 ], "Studio": item[ 7 ] } )
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

    def _get_thumbnail( self, item ):
        # make the proper cache filename and path so duplicate caching is unnecessary
        filename = xbmc.getCacheThumbName( item )
        thumbnail = xbmc.translatePath( os.path.join( self.BASE_CACHE_PATH, filename[ 0 ], filename ) )
        # if the cached thumbnail does not exist create the thumbnail
        if ( not os.path.isfile( thumbnail ) ):
            # create filepath to a local tbn file
            thumbnail = os.path.splitext( item )[ 0 ] + ".tbn"
            # if there is no local tbn file use a default
            if ( not os.path.isfile( thumbnail ) ):
                thumbnail = ""
        return thumbnail
