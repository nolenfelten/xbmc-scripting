import urllib
import cachedhttp_mod as cachedhttp
import xbmc, xbmcgui

import xbmc_skin_site as xss
from config import *
from debug import *

def download( url ):
    global settings
    settings = Read()
    fetcher = cachedhttp.CachedHTTPWithProgress()
    try:
        filepath = fetcher.urlretrieve( url )
    except:
        filepath = None
        debugPrint( error, url )
    return filepath

def install( url ):
    print url
    filepath = download( url )
    if filepath:
        ( installed, skinname ) = extract( settings['skinpath'], filepath )
        if installed:
            filename = urllib.unquote( os.path.split( filepath )[1] )
            xbmcgui.Dialog().ok( filename, skinname, 'Skin installed successfully!' )

def extract( extract_path, filepath ):
    try:
        filename = os.path.split( filepath )[1]
        filename_noext = urllib.unquote( os.path.splitext( filename )[0] )
        fileext = os.path.splitext( filename )[1]
        extract_path = os.path.join( extract_path, filename_noext )
        if ( fileext != '.zip' ) and ( fileext != '.rar' ):
            xbmcgui.Dialog().ok( filename, 'Not a ZIP or RAR file!', 'File format not supported.', 'Contact author to post a ZIP or RAR instead.' )
            return False, None
        if not xbmcgui.Dialog().yesno( filename, 'Use this directory?', extract_path ):
            return False, None
        if os.path.exists( extract_path ):
            if xbmcgui.Dialog().yesno( 'Overwrite?', 'Folder %s already exists.' % filename_noext, 'Overwrite files inside folder?' ) != True:
                return False, None
        else:
            os.mkdir( extract_path )
        xbmc.executebuiltin( 'XBMC.Extract(%s,%s)' % ( filepath, extract_path + os.sep ) )
        return True, filename_noext
    except:
        debugPrint(popup, "An error occurred while extracting.\nCorrupt file or not a properly formatted file.")
        debugPrint(error, "An error occurred while extracting: ")
        return False, None
