import os, sys, platform

from wxPython.wx import *
import wx.lib.evtmgr as em

__author__ = 'XBMC Emulator Team (https://opensvn.csie.org/traccgi/XBMCEmulator)'
__credits__ = 'XBMC TEAM and alexpoet/bitplane'
__platform__ = platform.platform( terse = True )
__version__ = '0.4'

class Action:
    """
        http://home.no.net/thor918/xbmc/xbmcgui.html#Action
    """
    def __init__( self, __button_name__ = None ):
        self.__button_name__ = __button_name__
        self.codes = {
            # name: [ button_code, id ]
            'A': [ 256, 7 ], 
            'B': [ 257, 9 ],
            'X': [ 258, 18 ],
            'Y': [ 259, 34 ],
            'Start': [ 274, 122 ],
            'Back': [ 275, 10 ],
            'Black': [ 260, 0 ],
            'White': [ 261, 117 ],
            'Dpad Up': [ 270, 3 ],
            'Dpad Down': [ 271, 4 ],
            'Dpad Left': [ 272, 1 ],
            'Dpad Right': [ 273, 2 ],
        }
    def __eq__( self, id ):  
        return id == self.codes[self.__button_name__][1]
    def __ge__( self, id ):  
        return id >= self.codes[self.__button_name__][1]
    def __gt__( self, id ):  
        return id > self.codes[self.__button_name__][1]
    def __le__( self, id ):  
        return id <= self.codes[self.__button_name__][1]
    def __lt__( self, id ):  
        return id < self.codes[self.__button_name__][1]
    def __ne__( self, id ):  
        return id != self.codes[self.__button_name__][1]
    def getButtonCode( self ):
        return self.codes[self.__button_name__][0]
    def getId( self ):  
        return self.codes[self.__button_name__][1]

def GetBitmap( filename, scale = 1 ):
    image = wxImage( os.path.join( emulator_path, 'images', filename ) )
    image = image.Scale( image.GetWidth() / scale, image.GetHeight() / scale )
    return image.ConvertToBitmap()

def GetScaledRegion( x, y, width, height, scale = 1 ):
    return wxRegion( x / scale, y / scale, width / scale, height / scale )

class __Controller_Buttons__( dict ):
    def __init__( self, scale = 1 ):
        self.scale = scale

    def add( self, code, name, x, y, width, height ):
        self.update(
            { 
                # code: [ name, region on controller, highlighted ]
                code: [ name, GetScaledRegion( x, y, width, height, self.scale ), False ] 
            } 
        )

    def map_images( self, controller_normal, controller_highlight ):
        # add the image for each button to the dict
        # code: [ name, rect position on controller, image, image_highlight ]
        for each in self.keys():
            rect = self[each][1].GetBox()
            image = controller_normal.GetSubBitmap( rect )
            image_highlight = controller_highlight.GetSubBitmap( rect )
            self[each] += [ image, image_highlight ]

class __Emulate_Controller__( wxPanel ):
    def __init__( self, parent ):
        self.scale = 2

        self.controller_image = GetBitmap( 'Emulator-controller.png', self.scale )
        self.controller_image_highlight = GetBitmap( 'Emulator-controller-HL.png', self.scale )

        wxPanel.__init__( self, parent, -1, size = self.controller_image.GetSize() )

        self.buttons = __Controller_Buttons__( self.scale )
        self.buttons.add( 256, 'A', 453, 185, 46, 46 )
        self.buttons.add( 257, 'B', 494, 145, 46, 46 )
        self.buttons.add( 258, 'X', 411, 146, 46, 46 )
        self.buttons.add( 259, 'Y', 452, 105, 46, 46 )
        self.buttons.add( 260, 'Black', 506, 222, 30, 30 )
        self.buttons.add( 261, 'White', 472, 256, 30, 30 )
        self.buttons.add( 270, 'Dpad Up', 185, 203, 34, 34 )
        self.buttons.add( 271, 'Dpad Down', 185, 264, 34, 34 )
        self.buttons.add( 272, 'Dpad Left', 150, 235, 34, 34 )
        self.buttons.add( 273, 'Dpad Right', 215, 235, 34, 34 )
        self.buttons.add( 274, 'Start', 86, 244, 34, 34 )
        self.buttons.add( 275, 'Back', 53, 214, 34, 34 )
        self.buttons.map_images( self.controller_image, self.controller_image_highlight )

        em.eventManager.Register( self._OnPaint, EVT_PAINT, self )
        em.eventManager.Register( self._OnMouseMove, EVT_MOTION, self )
        em.eventManager.Register( self._OnMouseClick, EVT_LEFT_UP, self )

    def _OnPaint( self, event ):
        dc = wxPaintDC( self )
        dc.BeginDrawing()
        dc.DrawBitmap( self.controller_image, 0, 0, True )
        for each in self.buttons:
            code = each
            name, region, highlighted, image, image_highlight = self.buttons[each]
            rect = region.GetBox()
            if highlighted:
                paint_image = image_highlight
            else:
                paint_image = image
            dc.DrawBitmap( paint_image, rect.x, rect.y, True )
        dc.EndDrawing()

    def _OnMouseMove( self, event ):
        for each in self.buttons:
            code = each
            name, region, highlighted, image, image_highlight = self.buttons[each]
            rect = region.GetBox()
            mouse_pos = event.GetPosition()
            highlight = region.ContainsPoint( mouse_pos )
            if highlight != highlighted: 
                self.buttons[each][2] = region.ContainsPoint( mouse_pos )
                self.RefreshRect( rect )

    def _OnMouseClick( self, event ):
        for each in self.buttons:
            code = each
            name, region, highlighted, image, image_highlight = self.buttons[each]
            rect = region.GetBox()
            mouse_pos = event.GetPosition()
            if region.ContainsPoint( mouse_pos ):
                wxGetApp().control_main_window.onAction( Action( name ) )

class __Emulator__( wxApp ):
    def __init__( self ):
        wxApp.__init__( self )
        self.window = None
        self.control_main_window = None
        self.controls = []
        self.active_control = None
        self.resolution = 6

    def Show( self, state ):
        if not self.window:
            # main emulator window
            self.window = wxFrame( None, -1, 'XBMC Emulator', style = wxCAPTION, size = wxSize( 720, 576 ) )
            self.SetTopWindow( self.window )
            self.window.Center()
            self.window.Show()

            # controller window
            self.controller = wxFrame( None, -1, 'Controller', style = wxCAPTION, pos = wxPoint( 0, 0 ) )
            self.controllerWindow = __Emulate_Controller__( self.controller )
            self.controller.Fit()

            self.SetTopWindow( self.controller )
            self.controller.Show()

    def getEmulatorWindow( self ):
        return self.window

    def getControllerWindow( self ):
        return self.controller

if not wxGetApp():
    emulator_path = os.path.join( sys.prefix, 'Lib', 'site-packages', 'xbmc-emulator' )
    app = __Emulator__()
    app.MainLoop()
    app.Show( True )
    print '--> XBMC Emulator %s initialized <--' % __version__

