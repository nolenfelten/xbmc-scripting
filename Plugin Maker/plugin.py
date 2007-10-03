"""
    Plugin Maker: This plugin will create a directory listing of VIDEO_PATH and add videos.
"""

# main imports
import os
import sys
import xbmc
import xbmcgui
import xbmcplugin

import datetime

# plugin constants
__plugin__ = "Plugin Maker"
__author__ = "nuka1195"
__credits__ = "Team XBMC"
__version__ = "1.0"


class Main:
    # base paths
    BASE_CACHE_PATH = os.path.join( "P:\\", "Thumbnails", "Video" )
    # replaceable video path
    VIDEO_PATH = ###VIDEO_PATH###

    # add all video extensions wanted in lowercase
    VIDEO_EXT = ".m4v|.3gp|.nsv|.ts|.ty|.strm|.pls|.rm|.rmvb|.m3u|.ifo|.mov|.qt|.divx|.xvid|.bivx|.vob|.nrg|.img|.iso|.pva|.wmv|.asf|.asx|.ogm|.m2v|.avi|.bin|.dat|.mpg|.mpeg|.mp4|.mkv|.avc|.vp3|.svq3|.nuv|.viv|.dv|.fli|.flv|.rar|.001|.wpl|.zip|.vdr|.dvr-ms|.xsp"

    def __init__( self ):
        self.get_videos()

    def get_videos( self ):
        try:
            videos = []
            # get the video list by walking VIDEO_PATH recursively
            os.path.walk( self.VIDEO_PATH, self.add_video, videos )
            # fill media list
            ok = self._fill_media_list( videos )
        except:
            # oops print error message
            print sys.exc_info()[ 1 ]
            ok = False
        # send notification we're finished, successfully or unsuccessfully
        xbmcplugin.endOfDirectory( handle=int( sys.argv[ 1 ] ), succeeded=ok )

    def add_video( self, videos, path, files ):
        # enumerate through the list of files and check for a valid video file
        for file in files:
            # get the files extension
            ext = os.path.splitext( file )[ 1 ].lower()
            # if it is a video file add it to our videos list
            if ( ext and ext in self.VIDEO_EXT ):
                videos += [ os.path.join( path, file ) ]

    def _fill_media_list( self, videos ):
        try:
            ok = True
            # enumerate through the list of videos and add the item to the media list
            for video in videos:
                # call _get_thumbnail() for the path to the cached thumbnail
                thumbnail = self._get_thumbnail( video )
                title = os.path.splitext( os.path.basename( video ) )[ 0 ]
                date = datetime.datetime.fromtimestamp( os.path.getmtime( video ) ).strftime( "%d-%m-%Y" )
                size = os.path.getsize( video )
                # only need to add label and thumbnail, setInfo() and addSortMethod() takes care of label2
                listitem=xbmcgui.ListItem( label=title, thumbnailImage=thumbnail )
                # add the different infolabels we want to sort by
                listitem.setInfo( type="Video", infoLabels={ "Title": title, "Date": date, "Size": size } )
                # add the item to the media list
                ok = xbmcplugin.addDirectoryItem( handle=int( sys.argv[ 1 ] ), url=video, listitem=listitem, totalItems=len( videos ) )
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

    def _get_thumbnail( self, video ):
        # make the proper cache filename and path so duplicate caching is unnecessary
        filename = xbmc.getCacheThumbName( video )
        thumbnail = xbmc.translatePath( os.path.join( self.BASE_CACHE_PATH, filename[ 0 ], filename ) )
        # if the cached thumbnail does not exist create the thumbnail
        if ( not os.path.isfile( thumbnail ) ):
            # create filepath to a local tbn file
            thumbnail = os.path.splitext( video )[ 0 ] + ".tbn"
            # if there is no local tbn file use a default
            if ( not os.path.isfile( thumbnail ) ):
                thumbnail = "defaultVideoBig.png"
        return thumbnail


if ( __name__ == "__main__" ):
    Main()
