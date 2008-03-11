# official python modules
import sys
# official xbmc modules
import xbmc, xbmcgui
# script modules
import base, dialog

# script variables
common = sys.modules['common']

def keyboard( default = '', heading = '', hidden = False ):
    '''Shows a keyboard and returns a value'''
    keyboard = xbmc.Keyboard( default, heading, hidden )
    keyboard.doModal()
    if ( keyboard.isConfirmed() ):
        return keyboard.getText()
    return default

def numeric( default = '', heading = '', dlg_type = 3 ):
    '''
    Shows a numeric dialog and returns a value
        - 0 : ShowAndGetNumber        (default format: #)
        - 1 : ShowAndGetDate          (default format: DD/MM/YYYY)
        - 2 : ShowAndGetTime          (default format: HH:MM)
        - 3 : ShowAndGetIPAddress     (default format: #.#.#.#)
    '''
    dialog = xbmcgui.Dialog()
    value = dialog.numeric( type, heading, default )
    return value

def browse( default = '', heading = '', dlg_type = 1, shares = 'files', mask = '', use_thumbs = False, treat_as_folder = False ):
    '''
    Shows a browse dialog and returns a value
        - 0 : ShowAndGetDirectory
        - 1 : ShowAndGetFile
        - 2 : ShowAndGetImage
        - 3 : ShowAndGetWriteableDirectory
    '''
    dialog = xbmcgui.Dialog()
    value = dialog.browse( dlg_type, heading, shares, mask, use_thumbs, treat_as_folder, default )
    return value

class popupmenu:
    '''
        Shows a popup dialog with the specified list items automatically added.
    '''
    def __init__( self, menuItems, xmlFile = '', resourcePath = '', defaultName = 'Default', forceFallback = False ):
        if not len( xmlFile ):
            xmlFile = 'script-%s-popupmenu.xml' % common.scriptname.replace( ' ', '_' )
        if not len( resourcePath ):
            resourcePath = common.resource_path
        self.controls_map = menuItems
        self.window = base.__internal_base_classPopupMenu__( xmlFile, resourcePath, defaultName, forceFallback, parentClass = self )
        self.window.doModal()

    def close( self ):
        self.window.close()
