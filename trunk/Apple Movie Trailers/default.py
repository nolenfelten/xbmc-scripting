import sys, os, traceback

sys.path.append( os.path.join( os.getcwd().replace( ";", "" ), 'resources', 'lib' ) )

import gui

__scriptname__ = 'Apple Movie Trailers'
__author__ = 'Apple Movie Trailers (AMT) Team'
__url__ = 'http://code.google.com/p/xbmc-scripting/'
__credits__ = 'XBMC TEAM, freenode/#xbmc-scripting'
__version__ = 'pre-0.97.1'

__credits_l1__ = 'Head Developer & Coder'
__credits_r1__ = 'Killarny'
__credits_l2__ = 'Coder & Skinning'
__credits_r2__ = 'Nuka1195'
__credits_l3__ = 'Graphics & Skinning'
__credits_r3__ = 'Pike'

__acredits_l1__ = 'Xbox Media Center'
__acredits_r1__ = 'Team XBMC'
__acredits_l2__ = 'Usability'
__acredits_r2__ = 'Spiff'
__acredits_l3__ = 'Language Routine'
__acredits_r3__ = 'Rockstar & Donno'

if __name__ == '__main__':
    try:
        ui = gui.GUI()
        if ui.gui_loaded:
            ui.doModal()
            del ui
    except:
        traceback.print_exc()
