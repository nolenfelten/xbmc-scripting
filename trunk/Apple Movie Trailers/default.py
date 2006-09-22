import sys, os
sys.path.append( os.path.join( sys.path[0], 'lib' ) )

import gui

if __name__ == '__main__':
    ui = gui.GUI()
    if ui.SUCCEEDED:
        ui.doModal()
    del ui
