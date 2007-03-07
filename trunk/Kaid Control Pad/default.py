"""
    This script allows you to control kai daemon on your linksys wrt54g router.
    
    Nuka1195
"""

__scriptname__ = "Kaid Control Pad"
__author__ = "Nuka1195"
__url__ = "http://code.google.com/p/xbmc-scripting/"
__credits__ = "XBMC TEAM, freenode/#xbmc-scripting"
__version__ = "pre-2.0"

import sys, os
import xbmc, xbmcgui
import threading, thread
import traceback

RESOURCE_PATH = os.path.join( os.getcwd().replace( ";", "" ), "resources" )

sys.path.append( os.path.join( RESOURCE_PATH, "lib" ) )

import wrt54g
import utilities
import guibuilder
import language
_ = language.Language().string

##xLinkKai_UserName = xbmc.getInfoLabel( "xLinkKai.UserName" )

class GUI( xbmcgui.WindowDialog ):

    def __init__( self ):
        try:
            self.timer_msg = None
            self.gui_loaded = self.setupGUI()
            if ( not self.gui_loaded ): self.exit_script()
            else:
                thread.start_new_thread(self.setup_all, ())
        except: 
            traceback.print_exc()
            self.close()

    def setupGUI( self ):
        gb = guibuilder.GUIBuilder()
        ok = gb.create_gui( self, fastMethod=True, title=__scriptname__, useDescAsKey=True, language=_ )
        return ok
        
    def setup_all( self ):
        #self.show()
        dummy = xbmc.getCondVisibility( "System.InternetState" ) # per GeminiServers instructions
        self.setup_variables()
        self.wrt54g = wrt54g.Commands()
        self.check_status()
        
    def setup_variables( self ):
        self.controller_action = utilities.setControllerAction()
        self.KAID_VERSION = ""
        
    def set_status_labels( self ):
        self.get_control( "Kaid Status Label" ).setLabel( [ "", _( 101 + self.wrt54g.STATUS_KAID_RUNNING ) ][ self.wrt54g.STATUS_KAID_RUNNING != -1 ] )
        self.get_control( "Kaid Status Label" ).setEnabled( self.wrt54g.STATUS_KAID_RUNNING == 1 )
        self.get_control( "Router Status Label" ).setLabel( self.KAID_VERSION )
        self.get_control( "Router Status Label" ).setEnabled( self.wrt54g.STATUS_ROUTER == 1 )
        self.get_control( "Xbox Status Label" ).setLabel( [ "", _( 121 + self.wrt54g.STATUS_XBOX ) ][ self.wrt54g.STATUS_XBOX != -1 ] )
        self.get_control( "Xbox Status Label" ).setEnabled( self.wrt54g.STATUS_XBOX == 1 )
        
    def set_status_buttons( self ):
        self.get_control( "Restart Button" ).setLabel( _( 10 + ( self.wrt54g.STATUS_KAID_RUNNING != 1 ) ) )
        self.get_control( "Restart Button" ).setEnabled( self.wrt54g.STATUS_ROUTER == True )
        self.get_control( "Stop Button" ).setEnabled( self.wrt54g.STATUS_KAID_RUNNING == True )
        self.get_control( "Upload Button" ).setEnabled( self.wrt54g.STATUS_XBOX == True and self.wrt54g.STATUS_ROUTER != 2 )
        self.get_control( "Reboot Button" ).setEnabled( self.wrt54g.STATUS_ROUTER != 2 )
        if ( self.wrt54g.STATUS_ROUTER == True ):
            self.setFocus( self.get_control( "Restart Button" ) )
        elif ( self.wrt54g.STATUS_XBOX == True and self.wrt54g.STATUS_ROUTER != 2 ):
            self.setFocus( self.get_control( "Upload Button" ) )
        else:
            self.setFocus( self.get_control( "Settings Button" ) )

    def set_message( self, msg_id=750, status=2 ):
        xbmcgui.lock()
        self.clear_message_timer()
        self.hide_status_bar()
        key = [ "Error Message Label", "Success Message Label",  "Info Message Label" ][ status ]
        self.get_control( key ).reset()
        self.get_control( key ).addLabel( _( msg_id ) )
        self.get_control( key ).setVisible( True )
        if ( status == 0 ):
            self.timer_msg = threading.Timer( 10, self.set_message, ( 750, ) )
            self.timer_msg.start()
        xbmcgui.unlock()

    def hide_status_bar( self ):
        self.get_control( "Info Message Label" ).setVisible( False )
        self.get_control( "Success Message Label" ).setVisible( False )
        self.get_control( "Error Message Label" ).setVisible( False )
        self.get_control( "Progressbar" ).setVisible( False )

    def clear_message_timer( self ):
        if ( self.timer_msg ): self.timer_msg.cancel()

    def change_settings( self ):
        try:
            import settings
            settings = settings.GUI( language=_ )
            if ( settings.gui_loaded ):
                settings.doModal()
                if ( settings.changed ):
                    self.wrt54g._get_settings()
                    if ( settings.restart ):
                        self.check_status()
            del settings
        except: traceback.print_exc()
            
    def check_status( self ):
        self._status_xbox( False )
        self._status_router( False )
        self._status_kaid_running( False )
        self._set_status()
        
    def _set_status( self ):
        self.set_status_labels()
        self.set_status_buttons()

    def _status_xbox( self, update=True ):
        self.set_message( 500, 1 )
        ok = self.wrt54g._status_xbox()
        if ( ok == 2 ): self.set_message( 530, 0)
        else: self.set_message()
        if ( update ): self._set_status()
            
    def _status_router( self, update=True ):
        self.set_message( 501, 1 )
        ok, version = self.wrt54g._status_router_kaid()
        if ( ok and version ): tmp_version = "Kaid (v.%s)" % ( version[ 0 ], )
        else: tmp_version = _( 112 )
        self.KAID_VERSION = [ _( 111 ), tmp_version, _( 113 ) ][ self.wrt54g.STATUS_ROUTER ]
        if ( ok == 2 ): self.set_message( 531, 0)
        elif ( self.wrt54g.STATUS_ROUTER ):
            self.set_message( 502, 1 )
            ok = self.wrt54g._status_router_kaid_conf()
            if ( ok == 2 ): self.set_message( 531, 0)
            else: self.set_message()
        if ( update ): self._set_status()

    def _status_kaid_running( self, update=True ):
        if ( self.wrt54g.STATUS_ROUTER != 2 ):
            self.set_message( 503, 1 )
            ok = self.wrt54g._status_kaid_running()
            if ( ok == 2 ): self.set_message( 531, 0)
            else: self.set_message()
        if ( update ): self._set_status()
        
    def _kaid_restart( self ):
        self.set_message( 600 + ( not self.wrt54g.STATUS_KAID_RUNNING ), 1 )
        ok = self.wrt54g._kaid_restart()
        if ( not ok ): self.set_message( 630, 0 )
        else: 
            self.show_progressbar( 5 )
            self._status_kaid_running()
            
    def _kaid_kill( self ):
        self.set_message( 602, 1 )
        ok = self.wrt54g._kaid_kill()
        if ( not ok ): self.set_message( 630, 0)
        else: 
            self.set_message()
        self._status_kaid_running()
        
    def _kaid_upload( self ):
        self.set_message( 603, 1 )
        ok = self.wrt54g._kaid_upload()
        if ( not ok ): self.set_message( 633, 0 )
        else: 
            self.set_message( 606, 1 )
            ok = self.wrt54g._finalize_upload()
            if ( not ok ): self.set_message( 636, 0 )
            else: 
                self.check_status()
                #self.set_message( 607, 1 )
                #ok = self.wrt54g._config_file_patch()
                #if ( not ok ): self.set_message( 637, 0 )
                #else:
                self._kaid_restart()

    def _router_reboot( self ):
        self.set_message( 604, 1 )
        ok = self.wrt54g._router_reboot()
        if ( not ok ): self.set_message( 630, 0)
        else: 
            self.show_progressbar( 20 )
            self.set_message()
        self._set_status()

    def show_progressbar( self, seconds ):
        sleep_time = int( float( seconds * 1000 ) / 100 )
        self.hide_status_bar()
        self.get_control( "Progressbar" ).setPercent( 0 )
        self.get_control( "Progressbar" ).setVisible( True )
        for percent in range( 101 ):
            self.get_control( "Progressbar" ).setPercent( percent )
            xbmc.sleep( sleep_time )
        self.get_control( "Progressbar" ).setVisible( False )
    
    def exit_script( self, restart=False ):
        self.clear_message_timer()
        self.close()
        if ( restart ): xbmc.executebuiltin( "XBMC.RunScript(%s)" % ( os.path.join( os.getcwd().replace( ";", "" ), "default.py" ), ) )

    def get_control( self, key ):
        """ Return the control that matches the key """
        try: return self.controls[ key ][ "control" ]
        except: return None

    def onControl( self, control ):
        if ( control == self.get_control( "Restart Button" ) ):
            self._kaid_restart()
        elif ( control == self.get_control( "Stop Button" ) ):
            self._kaid_kill()
        elif ( control == self.get_control( "Upload Button" ) ):
            self._kaid_upload()
        elif ( control == self.get_control( "Reboot Button" ) ):
            self._router_reboot()
        elif ( control == self.get_control( "Settings Button" ) ):
            self.change_settings()

    def onAction(self, action):
        button_key = self.controller_action.get( action.getButtonCode(), "n/a" )
        if ( button_key == "Keyboard ESC Button" or button_key == "Back Button" or button_key == "Remote Menu Button" ):
            self.exit_script()
        elif ( button_key == "Keyboard Menu Button" or button_key == "Y Button" or button_key == "Remote Title Button" or button_key == "White Button" ):
            self.change_settings()
    

if ( __name__ == "__main__" ):
    ui = GUI()
    if ( ui.gui_loaded ): ui.doModal()
    del ui
