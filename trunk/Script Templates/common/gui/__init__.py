# official python modules
import os, sys
# official xbmc modules
import xbmc, xbmcgui
# script modules
import codes, dialog

# script variables
common = sys.modules['common']
# language localization 'macro'
_ = common.localize

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
                # get the control object for this id
                control = self.getControl( id )
                try:
                    # see if there is a label set in the code
                    #   callback is a string or variable (see below) 
                    #   for the label
                    callback = callbacks['label']
                except: callback = None
                if callback:
                    try:
                        # there may be data in strings.xml also, check with
                        #   a strict (error throwing) lookup
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
                else:
                    # no label information was set in the code, so use the 
                    #   strings.xml lookup alone
                    label = _( id )
                if hasattr( control, 'setLabel' ):
                    # make sure that this control can even accept a label!
                    control.setLabel( label )
                # explicitly delete the control object for the next loop pass
                del control
            except:
                # something horrible occurred
                import traceback
                print '-' * 79
                print 'error setting label for', id
                traceback.print_exc()
 
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
