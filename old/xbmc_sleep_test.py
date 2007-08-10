import xbmcgui, xbmc
import threading

ACTION_MOVE_LEFT     = 1
ACTION_MOVE_RIGHT    = 2
ACTION_MOVE_UP       = 3
ACTION_MOVE_DOWN     = 4
ACTION_SELECT_ITEM   = 7
ACTION_PARENT_DIR    = 9
ACTION_PREVIOUS_MENU = 10

class GUI(xbmcgui.Window):
    def __init__(self):
        self.pad = xbmcgui.ControlImage( 50,50,200,200,"panel2.png")
        self.addControl( self.pad )
        StartSlide( self ).start()

    def slidepad_right( self ):
        #for i in range( 50, 500):
        xbmcgui.lock()
        #self.pad.setPosition( i, 50 )
        xbmc.sleep(10)
        xbmcgui.unlock()

    def slidepad_left( self ):
        for i in range( 500, 50, -1):
            xbmcgui.lock()
            self.pad.setPosition( i, 50 )
            xbmc.sleep(10)
            xbmcgui.unlock()
            
    def onAction( self, action ):
        if action == 9 or action==10:
            self.close()
        #elif action == 2:
        #    StartSlide( self ).start()

        #    thread.start_new_thread(self.slidepad_right, ())
        #elif action == 1:
        #    thread.start_new_thread(self.slidepad_left, ())

class StartSlide(threading.Thread):

    def __init__(self, windowOverlay):
        self.windowOverlay = windowOverlay
        threading.Thread.__init__(self)

    def run(self):
        self.windowOverlay.slidepad_right()
            
if ( __name__ == "__main__" ):
    ui = GUI()
    ui.doModal()
    del ui
