# official python modules
import os
# official xbmc modules
import xbmcgui
# script modules
import language, codes

# script variables
__scriptname__ = os.path.split( os.getcwd()[:-1] )[-1].replace( '_', ' ' )
RESPATH = os.path.join( os.getcwd()[:-1], 'resources' )
_ = language.Language().localized

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
            xmlFile = 'script-%s-window.xml' % __scriptname__.replace( ' ', '_' )
        if not len( resourcePath ):
            resourcePath = RESPATH
        if not hasattr( self, 'controls_map' ):
            self.controls_map = {
                # id: {
                #   'onClick': callback,
                #   'onFocus': callback,
                # },
            }
        xbmcgui.WindowXML.__init__( self, xmlFile, resourcePath, defaultName, forceFallback )
 
    def onInit( self ):
        '''
            sets each control to it's corresponding label from strings.xml
        '''
        for id in self.controls_map.keys():
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
