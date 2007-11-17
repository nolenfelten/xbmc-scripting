"""
    Apple Movie Trailers: Module sownloads then plays trailers
"""

# TODO: remove this when dialog issue is resolved
import xbmc
# set our title
g_title = unicode( xbmc.getInfoLabel( "ListItem.Title" ), "utf-8" )
# set our studio (only works if the user is using the video library)
g_studio = unicode( xbmc.getInfoLabel( "ListItem.Studio" ), "utf-8" )
# set our genre (only works if the user is using the video library)
g_genre = unicode( xbmc.getInfoLabel( "ListItem.Genre" ), "utf-8" )
# set our rating (only works if the user is using the video library)
g_mpaa_rating = xbmc.getInfoLabel( "ListItem.MPAA" )
# set our thumbnail
g_thumbnail = xbmc.getInfoImage( "ListItem.Thumb" )
# set our plotoutline
g_plotoutline = xbmc.getInfoLabel( "ListItem.PlotOutline" )
# set our year
g_year = 0
if ( xbmc.getInfoLabel( "ListItem.Year" ) ):
    g_year = int( xbmc.getInfoLabel( "ListItem.Year" ) )

# create the progress dialog (we do it here so there is minimal delay with nothing displayed)
import xbmcgui
pDialog = xbmcgui.DialogProgress()
pDialog.create( g_title, "Downloading trailer" )

# main imports
import sys
import os
##import xbmc
import xbmcplugin

import urllib


class _Info:
    def __init__( self, *args, **kwargs ):
        self.__dict__.update( kwargs )


class Main:
    # base paths
    BASE_CACHE_PATH = os.path.join( "P:\\", "Thumbnails", "Video" )

    def __init__( self ):
        self._get_settings()
        # parse argv for our download url
        self._parse_argv()
        # download the video
        filepaths = self._download_video( self.args.download_url.replace( "stack://", "" ).split( " , " ) )
        # play the video
        self._play_video( filepaths )

    def _parse_argv( self ):
        # call _Info() with our formatted argv to create the self.args object
        exec "self.args = _Info(%s)" % ( sys.argv[ 2 ][ 1 : ].replace( "&", ", " ).replace( "\\u0027", "'" ).replace( "\\u0022", '"' ).replace( "\\u0026", "&" ), )

    def _get_settings( self ):
        self.settings = {}
        self.settings[ "mode" ] = int( xbmcplugin.getSetting( "mode" ) )
        self.settings[ "download_path" ] = xbmcplugin.getSetting( "download_path" )

    def _download_video( self, urls ):
        try:
            filepaths = []
            filepath = ""
            urls.sort()
            for count, url in enumerate( urls ):
                # TODO: rethink the replace
                # replace forward and back slashes, split at colon and replace leading and trailing apostrophes
                title = g_title#.replace( "/", "-" ).replace( "\\", "-" )
                # construct an xbox compatible filepath
                ext = os.path.splitext( url )[ 1 ]
                # we need to keep the end of the title if more than one trailer
                multiple = len( urls ) > 1
                # split and insert the trailer number if more than one
                filepath = "%s%s" % ( title, ( "", "_%d" % ( count + 1, ), )[ multiple ], )
                # folder to save to
                dirname = "Z:\\"
                if ( not self.settings[ "download_path" ].startswith( "smb://" ) ):
                    dirname = self.settings[ "download_path" ]
                # get a valid filepath
                filepath = self._make_legal_filepath( os.path.join( dirname, filepath + ext ), save_end=multiple )
                # if the file does not exist, download it
                if ( os.path.isfile( os.path.join( self.settings[ "download_path" ], os.path.basename( filepath ) ) ) ):
                    filepath = os.path.join( self.settings[ "download_path" ], os.path.basename( filepath ) )
                else:
                    if ( self.settings[ "mode" ] == 1 ):
                        filepath = "Z:\\AMT_Video_%d%s" % ( count, ext, )
                    # set our display message
                    self.msg = "Downloading trailer %d of %d" % ( count + 1, len( urls ), )
                    # fetch the video
                    urllib.urlretrieve( url, filepath, self._report_hook )
                    # make the conf file and copy to smb share if necessary
                    filepath = self._make_conf_file( filepath )
                filepaths += [ filepath ]
        except:
            if ( os.path.isfile( filepath ) ):
                os.remove( filepath )
            filepaths = []
            pDialog.close()
        return filepaths

    def _report_hook( self, count, blocksize, totalsize ):
        percent = int( float( count * blocksize * 100) / totalsize )
        pDialog.update( percent, self.msg )
        if ( pDialog.iscanceled() ): raise

    def _make_legal_filepath( self, path, compatible=False, extension=True, conf=True, save_end=False ):
        environment = os.environ.get( "OS", "xbox" )
        if ( environment == "win32" or environment == "xbox" ):
            path = path.replace( "\\", "/" )
        drive = os.path.splitdrive( path )[ 0 ]
        parts = os.path.splitdrive( path )[ 1 ].split( "/" )
        if ( not drive and parts[ 0 ].endswith( ":" ) and len( parts[ 0 ] ) == 2 and compatible ):
            drive = parts[ 0 ]
            parts[ 0 ] = ""
        if ( environment == "xbox" or environment == "win32" or compatible ):
            illegal_characters = """,*=|<>?;:"+"""
            length = ( 42 - ( conf * 5 ) )
            for count, part in enumerate( parts ):
                tmp_name = ""
                for char in part:
                    # if char's ord() value is > 127 or an illegal character remove it
                    if ( char in illegal_characters or ord( char ) > 127 ): char = ""
                    tmp_name += char
                if ( environment == "xbox" or compatible ):
                    if ( len( tmp_name ) > length ):
                        if ( count == len( parts ) - 1 and extension == True ):
                            filename = os.path.splitext( tmp_name )[ 0 ]
                            ext = os.path.splitext( tmp_name )[ 1 ]
                            if ( save_end ):
                                tmp_name = filename[ : 35 - len( ext ) ] + filename[ -2 : ]
                            else:
                                tmp_name = filename[ : 37 - len( ext ) ]
                            tmp_name = "%s%s" % ( tmp_name.strip(), ext )
                        else:
                            tmp_name = tmp_name[ : 42 ].strip()
                parts[ count ] = tmp_name
        filepath = drive + "/".join( parts )
        if ( environment == "win32" ):
            return filepath.encode( "utf-8" )
        else:
            return filepath

    def _make_conf_file( self, filepath ):
        try:
            new_filepath = filepath
            # create conf file for better MPlayer playback
            if ( not os.path.isfile( filepath + ".conf" ) ):
                f = open( filepath + ".conf" , "w" )
                f.write( "nocache=1" )
                f.close()
            # if save location is a samba share, copy the file
            if ( self.settings[ "download_path" ].startswith( "smb://" ) ):
                new_filepath = os.path.join( self.settings[ "download_path" ], os.path.basename( filepath ) )
                new_thumbpath = os.path.join( self.settings[ "download_path" ], os.path.splitext( os.path.basename( filepath ) )[ 0 ] + ".tbn" )
                xbmc.executehttpapi("FileCopy(%s,%s)" % ( filepath, new_filepath, ) )
                xbmc.executehttpapi("FileCopy(%s,%s)" % ( g_thumbnail, new_thumbpath, ) )
        except:
            # oops print error message
            print sys.exc_info()[ 1 ]
        return new_filepath


    def _play_video( self, filepaths ):
        if ( filepaths ):
            # call _get_thumbnail() for the path to the cached thumbnail
            thumbnail = g_thumbnail#self._get_thumbnail( sys.argv[ 0 ] + sys.argv[ 2 ] )
            # set the default icon
            icon = "DefaultVideo.png"
            # create our playlist
            playlist = xbmc.PlayList( xbmc.PLAYLIST_VIDEO )
            # clear any possible entries
            playlist.clear()
            # enumerate thru and add our item
            for count, filepath in enumerate( filepaths ):
                # only need to add label, icon and thumbnail, setInfo() and addSortMethod() takes care of label2
                listitem = xbmcgui.ListItem( g_title, iconImage=icon, thumbnailImage=thumbnail )
                # set the key information
                listitem.setInfo( "video", { "Title": "%s%s" % ( g_title, ( "", " %d" % ( count + 1, ) )[ len( filepaths ) > 1 ], ), "Genre": g_genre, "Studio": g_studio, "PlotOutline": g_plotoutline, "Year": g_year } )
                # add our item
                playlist.add( filepath, listitem )
            # we're finished
            pDialog.close()
            # play the playlist
            xbmc.Player().play( playlist )
