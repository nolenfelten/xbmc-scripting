# official python modules
import os, sys
# official xbmc modules
import xbmc, xbmcgui
# script modules
import codes

# script variables
common = sys.modules['common']
# language localization 'macro'
_ = common.localize

def get_keyboard( default = '', heading = '', hidden = False ):
    '''Shows a keyboard and returns a value'''
    keyboard = xbmc.Keyboard( default, heading, hidden )
    keyboard.doModal()
    if ( keyboard.isConfirmed() ):
        return keyboard.getText()
    return default

def get_numeric_dialog( default = '', heading = '', dlg_type = 3 ):
    '''
    Shows a numeric dialog and returns a value
        - 0 : ShowAndGetNumber		(default format: #)
        - 1 : ShowAndGetDate			(default format: DD/MM/YYYY)
        - 2 : ShowAndGetTime			(default format: HH:MM)
        - 3 : ShowAndGetIPAddress	(default format: #.#.#.#)
    '''
    dialog = xbmcgui.Dialog()
    value = dialog.numeric( type, heading, default )
    return value

def get_browse_dialog( default = '', heading = '', dlg_type = 1, shares = 'files', mask = '', use_thumbs = False, treat_as_folder = False ):
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

class BaseScriptWindow( xbmcgui.WindowXML ):
    def __init__( self, xmlFile = '', resourcePath = '', defaultName = 'Default', forceFallback = False ):
        '''
            At the time of this writing, the xbmcgui.WindowXML class does not
                follow python conventions in handling it's subclasses. The
                equivalent xbmcgui.WindowXML.__init__() method seems to be 
                evaluated prior to evaluating the code contained here, meaning
                that this BaseScriptWindow class can not modify the required
                arguments for it's invokation. Hopefully this will be fixed!

            For now, however, this means that the automatic generation of the
                xml filename and resource path here will not allow code that
                subclasses BaseScriptWindow to ignore passing these arguments.
                So, even though the arguments above show defaults of empty
                strings for xmlFile and resourcePath, all subclasses must pass
                a proper xml filename and the correct resource path:

                    BaseScriptWindow( xmlFile, resourcePath )

            The code to automatically generate these arguments has been left 
                here for demonstration purposes, and in the hopes that if 
                xbmcgui.WindowXML ever gets fixed, this code will already be
                here, and subclasses can use the intended syntax:

                    BaseScriptWindow()
        '''
        if not len( xmlFile ):
            xmlFile = 'script-%s-window.xml' % common.scriptname.replace( ' ', '_' )
        if not len( resourcePath ):
            resourcePath = common.resource_path
        if not hasattr( self, 'controls_map' ):
            self.controls_map = {
                # id: {
                #   'onClick': callback,
                #   'onFocus': callback,
                #   'label': str(),
                # },
            }
        xbmcgui.WindowXML.__init__( self, xmlFile, resourcePath, defaultName, forceFallback )
 
    def onInit( self ):
        '''
            sets each control to it's corresponding label from strings.xml
        '''
        for id, callbacks in self.controls_map.iteritems():
            try:
                callback = callbacks['label']
            except: callback = None
            if callback:
                # callback is a string or variable (see below) 
                #   for the label
                try:
                    # there may be data in strings.xml also
                    label = _( id, strict = True )
                except:
                    # nothing in strings.xml
                    label = ''
                try:
                    # try to use the data from strings.xml as a format for
                    #   assigning data from the callback variable
                    label = label % callback
                except:
                    # if that doesn't work, treat callback as a string and
                    #   concatenate to the data from strings.xml
                    label = label + callback
                self.getControl( id ).setLabel( label )
            else:
                self.getControl( id ).setLabel( _( id ) )
 
    def onAction( self, action ):
        for i in [ action.getId(), action.getButtonCode() ]:
            # this would work nicer here in standard python, but xbmc has 
            #   problems with it
            # if i in codes.EXIT_SCRIPT:
            for j in codes.EXIT_SCRIPT:
                if i == j:
                    self.close()
                    break

    def onClick( self, controlID ):
        for id, callbacks in self.controls_map.iteritems():
            if controlID == id:
                try:
                    callback = callbacks['onClick']
                except: callback = None
                if callback: callback()
 
    def onFocus( self, controlID ):
        for id, callbacks in self.controls_map.iteritems():
            if controlID == id:
                try:
                    callback = callbacks['onFocus']
                except: callback = None
                if callback: callback()
