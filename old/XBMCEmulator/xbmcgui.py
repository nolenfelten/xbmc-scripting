"""
    xbmcgui.py - emulator for Xbox Media Center
"""
import cStringIO, os, sys, thread, time, platform
from wxPython.wx import *
import wx.lib.evtmgr as em
import xbmc

sys.path += [ os.path.join( sys.prefix, 'Lib', 'site-packages', 'xbmc-emulator' ) ]
import emulator

__author__ = emulator.__author__
__credits__ = emulator.__credits__
__platform__ = emulator.__platform__
__date__ = ' '.join( '$Date: 2006-09-22 09:55:17 -0600 (Fri, 22 Sep 2006) $'.split()[1:4] )
__version__ = '%s R%s' % ( emulator.__version__, '$Rev: 40 $'.split()[1] )

# provided for backwards compatibility
Emulating = True

DEBUG = True
EMULATE_CONTROLLER = True    # This can be set to false once I bind keyboard input to controller signals.

UniqueID = 0

Action = emulator.Action

class Control:
    def __init__(self, type, x, y, width, height):
        self.ID = self._getUniqueID()
        self.type = type
        self.x = x
        self.y = y
        self.width = width
        self.height = height

    def _getUniqueID( self ):
        global UniqueID
        ID = UniqueID
        UniqueID += 1
        return ID

    def _show( self ):
        try:
            self.window.Show()
        except: pass

    def _makeFont( self, font ):
        try:
            fontsize = int( font[4:] )
            return wxFont( fontsize, wxROMAN, wxNORMAL, wxNORMAL )
        except:
            return wxNullFont

    def controlDown(self, Control):
        pass

    def controlLeft(self, Control):
        pass

    def controlRight(self, Control):
        pass

    def controlUp(self, Control):
        pass

    def getId(self):
        return self.ID

    def setEnabled( self, enabled ):  
        pass  

    def setHeight(self, height):
        pass

    def setNavigation( self, up, down, left, right ):
        pass

    def setPosition(self, x, y):
        pass

    def setVisible(self, isVisible):
        pass

    def setWidth(self, width):
        pass

class ControlButton(Control):
    """
        http://home.no.net/thor918/xbmc/xbmcgui.html#ControlButton
    """
    def __init__( self,
        x, y, width, height,
        label = '',
        focusTexture = None, noFocusTexture = None,
        textXOffset = 0, textYOffset = 0,
        alignment = 0, # investigate
        font = 'font13', # investigate
        textColor = '0xFFFFFFFF', # investigate
        disabledColor = '0xFFFFFFFF', # investigate
        angle = 0,
        shadowColor = None
    ):
        Control.__init__( self, self.__class__, x, y, width, height )
        self.window = wxButton( wxGetApp().getEmulatorWindow(), -1, label, wxPoint( x, y ), wxSize( width, height ) )

    def setDisabledColor( self, hexcolor ):
        pass

    def setLabel( self, label, font=None, textColor=None, disabledColor=None, shadowColor=None ):
        self.window.SetLabel( label )

class ControlCheckMark( Control ):
    """
        http://home.no.net/thor918/xbmc/xbmcgui.html#ControlCheckMark
    """
    def __init__( self,
        x, y, width, height,
        label = '',
        focusTexture = None, noFocusTexture = None,
        checkWidth = 0, checkHeight = 0,
        alignment = 0, # investigate
        font = 'font13', # investigate
        textColor = '0xFFFFFFFF', # investigate
        disabledColor = '0xFFFFFFFF' # investigate
    ):
        Control.__init__( self, self.__class__, x, y, width, height )
        self.window = wxCheckBox( wxGetApp().getEmulatorWindow(), -1, label, wxPoint( x, y ), wxSize( width, height ) )

    def getSelected( self ):
        return self.window.GetValue()

    def setDisabledColor( self, hexcolor ):
        pass

    def setLabel( self, label, font, textColor, disabledColor ):
        self.window.SetLabel( label )

    def setSelected( self, isOn ):
        self.window.SetValue( isOn )

class ControlFadeLabel(Control):
    """
        http://home.no.net/thor918/xbmc/xbmcgui.html#ControlFadeLabel
    """
    def __init__(self, x, y, width, height, font = 'font13', textColor = '0xffff3300', alignment = 0):
        Control.__init__( self, self.__class__, x, y, width, height )

    def addLabel(self, label):
        pass

    def reset(self):
        pass

class ControlImage(Control):
    """
        http://home.no.net/thor918/xbmc/xbmcgui.html#ControlImage
    """
    def __init__(self, x, y, width, height, filename = '', colorKey = '0xffff3300', aspectRatio = 0):
        Control.__init__( self, self.__class__, x, y, width, height )
        filename = os.path.join('q:\\skin\\Project Mayhem III\\media', filename)
        if (not os.path.isfile(filename)):
            self.image = wxEmptyBitmap( width, height )
        else:
            image = wxImage( filename )
            self.image = image.ConvertToBitmap()

        self.window = wxWindow( wxGetApp().getEmulatorWindow(), -1,
            wxPoint( x, y ), wxSize( width, height ), wxNO_BORDER )
        dc = wxClientDC( self.window )
        dc.DrawBitmap( self.image, 0, 0, True )
        em.eventManager.Register( self._OnPaint, EVT_PAINT, self.window )
        
        #pass

    def _OnPaint( self, event ):
        dc = wxPaintDC( self.window )
        dc.DrawBitmap( self.image, 0, 0, True )
        
    def setImage(self, filename, colorkey="ffffffff"):
        # load the new image  
        if not len( filename ):  
            self.image = wxEmptyBitmap( width, height )  
        image = wxImage( filename )  
        if not image.Ok():  
            self.image = wxEmptyBitmap( width, height )  
        else: self.image = image.ConvertToBitmap()  
        # manually redraw the image  
        self._OnPaint( None )  

    def setColorDiffuse( self, color ):
        pass

class ControlLabel(Control):
    """
        http://home.no.net/thor918/xbmc/xbmcgui.html#ControlLabel
    """
    def __init__(self,
        x, y, width, height,
        label = '',
        font = 'font13',
        textColor = '0xFFFF3300',
        disabledColor = '0xFFFF3300',
        alignment = 0,
        hasPath = False,
        angle = 0
    ):
        Control.__init__( self, self.__class__, x, y, width, height )
        self.window = wxStaticText( wxGetApp().getEmulatorWindow(), -1, label, wxPoint( x, y ) )

    def setLabel(self, label):
        self.window.SetLabel( label )

class ControlList(Control):
    """
        http://home.no.net/thor918/xbmc/xbmcgui.html#ControlList
    """
    def __init__(self,
        x, y, width, height,
        font = 'font13', textColor = '0xffffffff',
        buttonTexture = None, buttonFocusTexture = None,
        selectedColor = '0xffffffff',
        imageWidth = 16, imageHeight = 16, # investigate these
        itemTextXOffset = 0, itemTextYOffset = 0,
        itemHeight = 16, # investigate
        space = 2, #investigate
        alignmentY = 0 # investigate
    ):
        Control.__init__( self, self.__class__, x, y, width, height )
        self.window = wxListBox( wxGetApp().getEmulatorWindow(), -1, wxPoint( x, y ), wxSize( width, height ),
            style = wxLB_SINGLE )
        self.items = []

    def addItem(self, item):
        if item.__class__ != ListItem:
            item = ListItem( item )
        text = item.getLabel()
        if item.getLabel2():
            text += ' - ' + item.getLabel2()
        self.window.InsertItems( [ text ], self.window.GetCount() )
        self.items += [ item ]

    def getSelectedItem(self):
        pos = self.getSelectedPosition()
        if pos < 0: return None
        return self.items[pos]

    def getSelectedPosition(self):
        pos = self.window.GetSelection()
        if pos == wxNOT_FOUND: pos = -1
        return pos

    def getSpinControl(self):
        return None

    def reset(self):
        self.window.Clear()
        self.items = []

    def selectItem( self, item ):
        self.window.SetSelection( item )

    def setImageDimensions(self, width, height):
        pass

    def setItemHeight(self, height):
        pass

    def setPageControlVisible( self, isOn ):
        pass

    def setSpace(self, space):
        pass

class ControlTextBox(Control):
    """
        http://home.no.net/thor918/xbmc/xbmcgui.html#ControlTextBox
    """
    def __init__(self, x, y, width, height, font = 'font13', textColor = '0xffff3300'):
        Control.__init__( self, self.__class__, x, y, width, height )

    def getSpinControl(self):
        return None

    def reset(self):
        pass

    def setText(self, txt):
        pass

class Dialog:
    """
        http://home.no.net/thor918/xbmc/xbmcgui.html#Dialog
    """
    def browse( self, type, heading, shares, extra = '' ):  
        if type == 0:
            dialog = wxDirDialog( wxGetApp().getEmulatorWindow(), heading, style = wxDD_NEW_DIR_BUTTON )
        else:
            dialog = wxFileDialog( wxGetApp().getEmulatorWindow(), heading, style = wxOPEN )
        result = dialog.ShowModal()
        if result == wxID_OK:
            return dialog.GetPath()
        return ''

    def numeric( self, type, header ):  
        return ''  

    def ok(self, title, line1, line2 = '', line3 = '' ):
        lines = line1
        if len( line2 ): lines = lines + os.linesep + line2
        if len( line3 ): lines = lines + os.linesep + line3
        result = wxMessageDialog( wxGetApp().getEmulatorWindow(), lines, title, wxOK ).ShowModal()
        return True

    def select(self, title, li):
        dialog = wxSingleChoiceDialog( wxGetApp().getEmulatorWindow(), '', title, li )
        result = dialog.ShowModal()
        if result == wxID_OK:
            return dialog.GetSelection()
        return -1

    def yesno( self, title, line1, line2 = '', line3 = '' ):
        lines = line1
        if len( line2 ): lines = lines + os.linesep + line2
        if len( line3 ): lines = lines + os.linesep + line3
        result = wxMessageDialog( wxGetApp().getEmulatorWindow(), lines, title, wxYES_NO ).ShowModal()
        if result == wxID_YES: return True
        return False

class DialogProgress:
    """
        http://home.no.net/thor918/xbmc/xbmcgui.html#DialogProgress
    """
    def close( self ):
        self.window.Close()

    def create( self, heading, line1 = None, line2 = None, line3 = None ):
        lines = ''
        if line1: lines += line1
        if line2 and len( line2 ): lines = lines + os.linesep + line2
        if line3 and len( line3 ): lines = lines + os.linesep + line3

        self.window = wxDialog( wxGetApp().getEmulatorWindow(), -1, heading )
        self.text = wxStaticText( self.window, -1, lines )
        self.gauge = wxGauge( self.window, -1, 100,
            pos = wxPoint( 0, self.text.GetSizeTuple()[1] ),
            size = wxSize( self.text.GetSizeTuple()[0], 8 )
        )
        self.gauge.SetValue( 0 )
        self.window.Show()

    def iscanceled( self ):
        try:
            if not self.window: raise
        except:
            return True
        return False

    def update( self, percentage, line1 = None, line2 = None, line3 = None ):
        self.gauge.SetValue( percentage )

class ListItem:
    """
        http://home.no.net/thor918/xbmc/xbmcgui.html#ListItem
    """
    def __init__(self, label = None, label2 = None, iconImage = None, thumbnailImage = None):
        self.label = label
        self.label2 = label2

    def getLabel(self):
        return self.label

    def getLabel2(self):
        return self.label2

    def setIconImage( self, iconName ):
        pass

    def setLabel(self, text):
        self.label = text

    def setLabel2(self, text):
        self.label2 = text

    def setThumbnailImage( self, iconName ):
        pass

class Window:
    """
        http://home.no.net/thor918/xbmc/xbmcgui.html#Window
    """
    def __init__( self ):
        # some scripts call this specifically
        pass

    def addControl( self, control ):
        wxGetApp().controls += [ control ]
        control._show()

    def close(self):
        wxGetApp().Exit()

    def doModal( self ):
        wxGetApp().control_main_window = self
        wxGetApp().MainLoop()

    def getControl( self, controlId ):
        for control in wxGetApp().controls:
            if control == controlId: return control
        raise Exception

    def getFocus( self ):
        focus = wxGetApp().active_control
        if not focus:
            raise RuntimeError
        return focus

    def getHeight(self):
        return 480

    def getResolution( self ):
        return wxGetApp().resolution

    def getWidth(self):
        return 720

    def onAction(self, action):
        if action.getButtonCode() == 275:
            self.close()

    def removeControl(self, control):
        for ctrl in wxGetApp().controls:
            if ctrl == control:
                wxGetApp().controls.remove( ctrl )
                return
        raise RuntimeError

    def setCoordinateResolution( self, resolution ):
        matrix = {
            0: [ '1080i', ( 1920, 1080 ) ],
            1: [ '720p', ( 1280, 720 ) ],
            2: [ '480p 4:3', ( 720, 480 ) ],
            3: [ '480p 16:9', ( 720, 480 ) ],
            4: [ 'NTSC 4:3', ( 720, 480 ) ],
            5: [ 'NTSC 16:9', ( 720, 480 ) ],
            6: [ 'PAL 4:3', ( 720, 576 ) ],
            7: [ 'PAL 16:9', ( 720, 576 ) ],
            8: [ 'PAL60 4:3', ( 720, 480 ) ],
            9: [ 'PAL60 16:9', ( 720, 480 ) ],
        }
        app = wxGetApp()
        app.resolution = resolution
        width, height = matrix[resolution][1]
        app.window.SetSize( wxSize( width, height ) )
        app.window.Center()

    def setFocus( self, control ):
        wxGetApp().active_control = control

    def show( self ):
        pass

class WindowDialog( Window ):
    """
        http://home.no.net/thor918/xbmc/xbmcgui.html#WindowDialog
    """
    def __new__( *args ):
        return Window.__class__.__new__( *args )

def getCurrentWindowID():
    """
        http://home.no.net/thor918/xbmc/xbmcgui.html#-getCurrentWindowId
    """
    pass

def lock():
    """
        http://home.no.net/thor918/xbmc/xbmcgui.html#-lock
    """
    pass

def unlock():
    """
        http://home.no.net/thor918/xbmc/xbmcgui.html#-unlock
    """
    pass
