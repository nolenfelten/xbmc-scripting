from xbmc_constants import *
import installer
import xbmc_skin_site as xss
import threading, time, os
import xbmcgui

from config import *
settings = Read()

class GUI( xbmcgui.Window ):
    def __init__( self ):
        self.setCoordinateResolution( 6 )
        self.Layout()

    def Layout( self ):
        global settings
        settings = Read()
        self.themepath = os.path.join ( ScriptPath, os.path.join( 'gfx', xss.sites[settings['site']][0] ) )

        self.in_fullView = False
        self.w = 720
        self.h = 576
        self.midx = self.w / 2
        self.midy = self.h / 2
        self.padding_top = 0
        self.padding_left = 0
        self.thumb_w = 322
        self.thumb_h = 241
        self.fontcolor = '0xff000000'

        # background
        self.bg = xbmcgui.ControlImage(
            0, 0,
            self.w, self.h,
            os.path.join( self.themepath, 'bg.png' )
        )
        self.padding_top += 150
        self.addControl( self.bg )

        # switcher button
        self.xbtn = xbmcgui.ControlImage(
            0, self.padding_top,
            28, 28,
            os.path.join( self.themepath, 'xbutton.png' )
        )
        self.padding_left += 28
        self.addControl( self.xbtn )
        self.switcher = xbmcgui.ControlLabel(
            self.padding_left, self.padding_top,
            100, 28,
            'Switch Site',
            'font14', self.fontcolor
        )
        self.switcher_x = self.padding_left
        self.switcher_y = self.padding_top
        self.padding_left += 100
        self.addControl( self.switcher )

        # fullview button
        self.ybtn = xbmcgui.ControlImage(
            self.padding_left, self.padding_top,
            28, 28,
            os.path.join( self.themepath, 'ybutton.png' )
        )
        self.padding_left += 28
        self.addControl( self.ybtn )
        self.fullview = xbmcgui.ControlLabel(
            self.padding_left, self.padding_top,
            200, 28,
            'Fullscreen Preview',
            'font14', self.fontcolor
        )
        self.switcher_x = self.padding_left
        self.switcher_y = self.padding_top
        self.padding_left += 200
        self.padding_top += 28
        self.addControl( self.fullview )

        # list
        self.list = xbmcgui.ControlList(
            0, self.padding_top,
            self.w / 2, self.h - self.padding_top,
            'font14', self.fontcolor,
            buttonFocusTexture = os.path.join( self.themepath, 'list_item_selected.png' )
        )
        self.addControl( self.list )
        self.list.reset()
        self.setFocus( self.list )

        # populate list
        try:
            exec 'selected_skinlist = self.%s_skinlist' % xss.sites[settings['site']][0]
        except:
            exec 'self.%s_skinlist = xss.Skins()' % xss.sites[settings['site']][0]
            exec 'selected_skinlist = self.%s_skinlist' % xss.sites[settings['site']][0]
        self.skins = selected_skinlist.items
        for skin in self.skins:
            listitem = xbmcgui.ListItem( skin.title )
            listitem.setLabel( skin.title )
            self.list.addItem( listitem )

        # preview
        pos = self.list.getSelectedPosition()
        if pos < 0:
            newthumb = 'empty_thumb.png'
        else:
            skin = self.skins[pos]
            newthumb = skin.getThumb( os.path.join( self.themepath, 'empty_thumb.png' ) )
        self.thumbnail = xbmcgui.ControlImage(
            self.w / 2 + 20, self.padding_top,
            self.thumb_w, self.thumb_h,
            os.path.join( self.themepath, newthumb )
        )
        self.addControl( self.thumbnail )

    def onControl( self, control ):
        if control == self.list:
            installer.install( self.skins[self.list.getSelectedPosition()].link )

    def onAction( self, action ):
        xbmcgui.Window.onAction( self, action )
        focus = self.getFocus()
        action_code = XBMC_Button( action.getId() )
        if action_code == 'X':
            self.switchView()
        if action_code == 'Y':
            self.fullscreenView()
        if focus.getId() == self.list.getId():
            if action_code == 'Up' or action_code == 'Down' or action_code == 'Right Shoulder' or action_code == 'Left Shoulder':
                time.sleep( 0.01 )
                self.displayThumbView()

    def displayThumbView( self ):
                skin = self.skins[self.list.getSelectedPosition()]
                newthumb = skin.getThumb( os.path.join( self.themepath, 'empty_thumb.png' ) )
                old_thumbnail = self.thumbnail
                if self.in_fullView:
                    self.thumbnail = xbmcgui.ControlImage(
                        0, 0,
                        self.w, self.h,
                        os.path.join( self.themepath, newthumb )
                    )
                else:
                    self.thumbnail = xbmcgui.ControlImage(
                        self.w / 2 + 20, self.padding_top,
                        self.thumb_w, self.thumb_h,
                        os.path.join( self.themepath, newthumb )
                    )
                self.addControl( self.thumbnail )
                self.removeControl( old_thumbnail )

    def switchView( self ):
        if settings['site'] >= xss.sites.keys()[-1]:
            settings.update( { 'site' : 0 } )
        else:
            settings.update( { 'site' : settings['site'] + 1 } )
        Save( settings )
        self.Layout()

    def fullscreenView( self ):
        # fullscreen preview
        self.in_fullView = not self.in_fullView
        self.displayThumbView()