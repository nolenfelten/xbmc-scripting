import sys, os, traceback

scriptpath = sys.path[0]
sys.path.append( os.path.join( sys.path[0], 'lib' ) )

import gui

__scriptname__ = 'Apple Movie Trailers'
__author__ = 'Apple Movie Trailers (AMT) Team'
__url__ = 'http://code.google.com/p/xbmc-scripting/'
__credits__ = 'XBMC TEAM, efnet/#xbmc-scripting'
__version__ = '0.91'
__credits_l1__ = 'Head Developer & Coder'
__credits_r1__ = 'Killarny'
__credits_l2__ = 'Coder & Skinning'
__credits_r2__ = 'Nuka1195'
__credits_l3__ = 'Graphics & Skinning'
__credits_r3__ = 'Pike'

def py_cleanup():
    try:
        for root, dirs, files in os.walk( scriptpath, topdown = False ):
            if 'cache' in root:
                continue
            for name in files:
                if os.path.splitext( name )[1] in [ '.pyc', '.pyo' ]:
                    os.remove( os.path.join( root, name ) )
    except:
        pass

if __name__ == '__main__':
    try:
        try:
            ui = gui.GUI()
            if ui.SUCCEEDED:
                ui.doModal()
        except:
            traceback.print_exc()
    finally:
        try:
            ui.close()
            del ui
        except:
            pass
        py_cleanup()

