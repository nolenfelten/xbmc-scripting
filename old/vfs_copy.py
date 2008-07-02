import xbmc
import xbmcgui
import os
import shutil

def get_browse_dialog( default="", heading="", dlg_type=1, shares="files", mask="", use_thumbs=False, treat_as_folder=True ):
    """ shows a browse dialog and returns a value
        - 0 : ShowAndGetDirectory
        - 1 : ShowAndGetFile
        - 2 : ShowAndGetImage
        - 3 : ShowAndGetWriteableDirectory
    """
    dialog = xbmcgui.Dialog()
    value = dialog.browse( dlg_type, heading, shares, mask, use_thumbs, treat_as_folder, default )
    return value

file = get_browse_dialog( heading="File to copy" )
path = get_browse_dialog( heading="Copy to", dlg_type=3 )
shutil.copyfile( file, os.path.join( path, os.path.basename( file ) ) )
print os.listdir( path )