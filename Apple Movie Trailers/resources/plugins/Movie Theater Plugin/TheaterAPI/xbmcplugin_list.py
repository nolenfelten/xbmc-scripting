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
    BASE_CACHE_PATH = os.path.join( "P:\\", "Thumbnails", "Video" )
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
                self.get_settings()
                self.get_items( self.args.path )
            else:
                self._parse_argv()
                if ( self.args.isFolder ):
                    self.get_items( self.args.path )

    def _launch_script( self ):
        # no database was found so notify XBMC we're finished
        xbmcplugin.endOfDirectory( handle=int( sys.argv[ 1 ] ), succeeded=False )
        # ask to run script to create the database
        if ( os.path.isfile( xbmc.translatePath( os.path.join( "Q:\\", "scripts", sys.modules[ "__main__" ].__script__, "default.py" ) ) ) ):
            if ( xbmcgui.Dialog().yesno( sys.modules[ "__main__" ].__plugin__, "Database not found!", "Would you like to run the main script?" ) ):
                xbmc.executebuiltin( "XBMC.RunScript(%s)" % ( xbmc.translatePath( os.path.join( "Q:\\", "scripts", sys.modules[ "__main__" ].__script__, "default.py" ) ), ) )
        else:
            ok = xbmcgui.Dialog().ok( sys.modules[ "__main__" ].__plugin__, "Database not found!", "You need to install and run the main script.", sys.modules[ "__main__" ].__svn_url__ )

    def get_settings( self ):
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

    def get_items( self, path ):
        try:
            # if this is a smb share, we need to retrieve the list differently
            if ( path.startswith( "smb://" ) ):
                entries = self.get_smb_list( path )
            else:
                entries = os.listdir( path )
            # get the item list by
            items = self.get_directory( path, entries )
            # fill media list
            ok = self._fill_media_list( items )
        except:
            # oops print error message
            print sys.exc_info()[ 1 ]
            ok = False
        # send notification we're finished, successfully or unsuccessfully
        xbmcplugin.endOfDirectory( handle=int( sys.argv[ 1 ] ), succeeded=ok )

    def get_smb_list( self, path ):
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
            if ( item.get_longname() != "." and item.get_longname() != ".." ):
                entries += [ item.get_longname() ]
        return entries

    def get_directory( self, path, entries ):
        items = []
        # enumerate through our entries list and check for a valid video file or folder
        for entry in entries:
            # create the file path
            if ( path.startswith( "smb://" ) ): sep = "/"
            else: sep = os.sep
            file_path = "%s%s%s" % ( path, sep, entry, )
            # is this a folder?
            isFolder = os.path.isdir( file_path )
            # if this is a file, check to see if it's a valid video file
            if ( not isFolder ):
                # get the files extension
                ext = os.path.splitext( entry )[ 1 ].lower()
                # if it is a video file add it to our items list
                if ( ext and ext in self.VIDEO_EXT ):
                    items += [ ( file_path, isFolder, ) ]
            else:
                # it must be a folder
                items += [ ( file_path, isFolder, ) ]
        return items

    def _fill_media_list( self, items ):
        try:
            ok = True
            # enumerate through the list of items and add the item to the media list
            for item in items:
                # create our url (backslashes cause issues when passed in the url)
                url = '%s?path="""%s"""&isFolder=%d&username="""%s"""&password="""%s"""&trailer_intro_path="""%s"""&movie_intro_path="""%s"""&number_trailers=%d&rating="""%s"""&only_hd=%d&quality="""%s"""' % ( sys.argv[ 0 ], item[ 0 ].replace( "\\", "[[BACKSLASH]]" ), item[ 1 ], self.args.username, self.args.password, self.args.trailer_intro_path.replace( "\\", "[[BACKSLASH]]" ), self.args.movie_intro_path.replace( "\\", "[[BACKSLASH]]" ), self.args.number_trailers, self.args.rating, self.args.only_hd, self.args.quality, )
                if ( item[ 1 ] ):
                    # parse item for title
                    title = os.path.basename( item[ 0 ] )
                    # if a folder.jpg exists use that for our thumbnail
                    #thumbnail = os.path.join( item[ 0 ], "%s.jpg" % ( title, ) )
                    #if ( not os.path.isfile( thumbnail ) ):
                    thumbnail = "DefaultFolderBig.png"
                    # only need to add label and thumbnail, setInfo() and addSortMethod() takes care of label2
                    listitem=xbmcgui.ListItem( label=title, thumbnailImage=thumbnail )
                    # add the different infolabels we want to sort by
                    listitem.setInfo( type="Video", infoLabels={ "Title": title + " (%s)" % ( xbmc.getLocalizedString( 20334 ), ) } )
                else:
                    # call _get_thumbnail() for the path to the cached thumbnail
                    thumbnail = self._get_thumbnail( item[ 0 ] )
                    # parse item for title
                    title = os.path.splitext( os.path.basename( item[ 0 ] ) )[ 0 ]
                    # get the date of the file
                    date = datetime.datetime.fromtimestamp( os.path.getmtime( item[ 0 ] ) ).strftime( "%d-%m-%Y" )
                    # get the size of the file
                    size = long( os.path.getsize( item[ 0 ] ) )
                    # only need to add label and thumbnail, setInfo() and addSortMethod() takes care of label2
                    listitem=xbmcgui.ListItem( label=title, thumbnailImage=thumbnail )
                    # set an overlay if one is practical
                    overlay = ( xbmcgui.ICON_OVERLAY_NONE, xbmcgui.ICON_OVERLAY_RAR, xbmcgui.ICON_OVERLAY_ZIP, )[ item[ 0 ].endswith( ".rar" ) + ( 2 * item[ 0 ].endswith( ".zip" ) ) ]
                    # add the different infolabels we want to sort by
                    listitem.setInfo( type="Video", infoLabels={ "Title": title, "Date": date, "Size": size, "Overlay": overlay } )
                # add the item to the media list
                ok = xbmcplugin.addDirectoryItem( handle=int( sys.argv[ 1 ] ), url=url, listitem=listitem, isFolder=item[ 1 ], totalItems=len( items ) )
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
                thumbnail = "defaultVideoBig.png"
        return thumbnail


if ( __name__ == "__main__" ):
    Main()
