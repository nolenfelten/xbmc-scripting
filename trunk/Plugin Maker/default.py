"""
This script will creates a video plugin that lists a sepecific directory.
"""
# main imports
import os
import shutil
import xbmcgui

# Script constants
__scriptname__ = "Plugin Maker"
__author__ = "nuka1195"
__url__ = "http://code.google.com/p/xbmc-scripting/"
__svn_url__ = "http://xbmc-scripting.googlecode.com/svn/trunk/Plugin%20Maker"
__credits__ = "XBMC TEAM, freenode/#xbmc-scripting"
__version__ = "1.0"
__svn_revision__ = 0


class Main:
    def __init__( self ):
        # user selects plugin type
        plugin_type = 0##xbmcgui.Dialog().yesno( __scriptname__, "What type of plugin is this?", "", "", "Video", "Music" )
        # browse for the directory
        path = self.get_browse_dialog( heading="Browse for %s directory" % ( ( "video", "music", )[ plugin_type ], ) )
        if ( path ):
            self.create_plugin( path, ( "video", "music", )[ plugin_type ] )

    def get_browse_dialog( self, default="", heading="", dlg_type=0, shares="files", mask="", use_thumbs=False, treat_as_folder=False ):
        """ shows a browse dialog and returns a value
            - 0 : ShowAndGetDirectory
            - 1 : ShowAndGetFile
            - 2 : ShowAndGetImage
            - 3 : ShowAndGetWriteableDirectory
        """
        dialog = xbmcgui.Dialog()
        value = dialog.browse( dlg_type, heading, shares, mask, use_thumbs, treat_as_folder, default )
        return value

    def create_plugin( self, path, plugin_type ):
        plugin = os.path.join( os.getcwd().replace( ";", "" ), "plugin.py" )
        plugin_name = self.get_keyboard( default=os.path.basename( path[ : -1 ] ) + " plugin", heading="Enter plugin name" )
        plugin_path = os.path.join( "Q:\\plugins", plugin_type, plugin_name )
        if ( not os.path.isdir( plugin_path ) ):
            os.makedirs( plugin_path )
        try:
            # TODO: copy a generic thumb also or browse for thumb
            shutil.copy( plugin, os.path.join( plugin_path, "default.py" ) )
            shutil.copytree( os.path.join( os.getcwd().replace( ";", "" ), "resources" ), os.path.join( plugin_path, "resources" ) )
            ok = self.edit_path( os.path.join( plugin_path, "resources", "settings.xml" ), path, plugin_type )
            if ( not ok ): raise
        except:
            ok = xbmcgui.Dialog().ok( "__scriptname__", "Copying plugin to new plugin folder failed!" )

    def get_keyboard( self, default="", heading="", hidden=False ):
        """ shows a keyboard and returns a value """
        keyboard = xbmc.Keyboard( default, heading, hidden )
        keyboard.doModal()
        if ( keyboard.isConfirmed() ):
            return keyboard.getText()
        return default

    def edit_path( self, filepath, sourcepath, plugin_type ):
        try:
            ok = True
            text = """<?xml version="1.0" encoding="utf-8" standalone="yes"?>\n<settings>\n\t<setting id="path" type="folder" source="%s" label="30000" default="%s" />\n<setting id="content" type="enum" lvalues="30011|30012|30013" label="30010" default="%d" />\n</settings>""" % ( plugin_type, sourcepath, ( 0, 1, )[ plugin_type == "music" ], )
            # write new .py file
            file_object = open( filepath, "w" )
            file_object.write( text )
            file_object.close()
        except:
            ok = xbmcgui.Dialog().ok( "__scriptname__", "Creating settings.xml file failed!" )
        return ok


if ( __name__ == "__main__" ):
    Main()
