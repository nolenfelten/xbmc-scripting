import sys
sys.path.append(sys.path[0] + '\\lib')
import gui

if __name__ == '__main__':
    ui = gui.GUI()
    ui.doModal()
    del ui
