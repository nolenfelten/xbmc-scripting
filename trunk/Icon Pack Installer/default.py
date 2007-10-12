import sys
import os
import xbmcgui
import xbmc

from shutil import copyfile

from resources.language import Language

__scriptname__ = "Icon Pack Installer"
__author__ = "nuka1195"
__url__ = "http://code.google.com/p/xbmc-scripting/"
__svn_url__ = "http://xbmc-scripting.googlecode.com/svn/trunk/Thumbnail%20Pack%20Installer"
__credits__ = "XBMC TEAM, freenode/#xbmc-scripting"
__version__ = "1.0"


class Main:
    BASE_ICONPACK_PATH = xbmc.translatePath( os.path.join( os.getcwd().replace( ";", "" ), "resources", "thumbnails", "plugins" ) )
    _ = Language().localized

    def __init__( self ):
        pack = self.get_pack()
        if ( pack != self.BASE_ICONPACK_PATH ):
            self.install_pack( os.path.dirname( pack ) )

    def get_pack( self ):
        # get the thumbnail the user chooses
        return self.get_browse_dialog( default=self.BASE_ICONPACK_PATH, heading=self._( 100 ) )

    def install_pack( self, pack ):
        try:
            pDialog = xbmcgui.DialogProgress()
            pDialog.create( self._( 0 ) )
            pDialog.update( -1, self._( 101 ), self._( 102 ) )
            icons = os.listdir( pack )
            pack_type = "scripts"
            if ( "plugins" in pack ):
                pack_type = "plugins"
            for icon in icons:
                path, cached_thumbnail = self.get_path( pack_type, os.path.splitext( icon )[ 0 ] + "\\"  )
                if ( path is not None ):
                    # copy from path
                    icon_copy_path = xbmc.translatePath( os.path.join( pack, icon ) )
                    # default.tbn install path
                    icon_install_path = xbmc.translatePath( os.path.join( path, "default.tbn" ) )
                    # folder.jpg install path (probably not needed)
                    folderjpg_install_path = xbmc.translatePath( os.path.join( path, "folder.jpg" ) )
                    # cached thumb path (we delete the existing, so our plugin re-caches the new thumb)
                    cached_thumbnail_path = xbmc.translatePath( os.path.join( "Q:\\", "UserData", "Thumbnails", "Programs", cached_thumbnail ) )
                    # copy default.tbn
                    copyfile( icon_copy_path, icon_install_path )
                    # copy folder.jpg (probably not needed)
                    copyfile( icon_copy_path, folderjpg_install_path )
                    # delete our cached thumbnail
                    if ( os.path.isfile( cached_thumbnail_path ) ):
                        os.remove( cached_thumbnail_path )
            pDialog.close()
        except:
            pDialog.close()
            # oops notify user an error occurred
            ok = xbmcgui.Dialog().ok( self._( 0 ), self._( 200 ) )

    def get_path( self, pack_type, icon ):
        if ( pack_type == "scripts" ):
            path = xbmc.translatePath( os.path.join( "Q:\\", pack_type, icon ) )
            cached_thumbnail = xbmc.getCacheThumbName( os.path.join( path, "default.py" ) )
            if ( os.path.isdir( path ) ):
                return path, cached_thumbnail
        else:
            for source in ( "video", "music", "pictures", "programs", ):
                path = xbmc.translatePath( os.path.join( "Q:\\", pack_type, source, icon ) )
                cached_thumbnail = xbmc.getCacheThumbName( path )
                if ( os.path.isdir( path ) ):
                    return path, cached_thumbnail
        return None, None

    def get_browse_dialog( self, default="", heading="", dlg_type=2, shares="files", mask=".tbn", use_thumbs=True, treat_as_folder=False ):
        """ shows a browse dialog and returns a value
            - 0 : ShowAndGetDirectory
            - 1 : ShowAndGetFile
            - 2 : ShowAndGetImage
            - 3 : ShowAndGetWriteableDirectory
        """
        dialog = xbmcgui.Dialog()
        value = dialog.browse( dlg_type, heading, shares, mask, use_thumbs, treat_as_folder, default )
        return value

if ( __name__ == "__main__" ):
    Main()
