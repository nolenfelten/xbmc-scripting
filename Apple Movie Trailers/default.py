import sys, os
sys.path.append( os.path.join( sys.path[0], 'lib' ) )

import gui

__scriptname__ = 'Apple Movie Trailers'
__author__ = 'Apple Movie Trailers (AMT) Team'
__url__ = 'http://code.google.com/p/xbmc-scripting/'
__credits__ = 'XBMC TEAM, efnet/#xbmc-scripting'
__version__ = '1.0 pre-release'

if __name__ == '__main__':
    try:
        ui = gui.GUI()
        if ui.SUCCEEDED:
            ui.doModal()
    except:
        import traceback
        traceback.print_exc()
        try:
            ui.close()
        except:
            pass
    try:
        del ui
    except:
        pass
    sys.exit()
