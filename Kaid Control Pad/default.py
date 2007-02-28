"""
    This script allows you to control kai daemon on your linksys wrt54g router.
    
    Nuka1195
"""

__scriptname__ = "Kaid Control Pad"
__author__ = "Nuka1195"
__url__ = "http://code.google.com/p/xbmc-scripting/"
__credits__ = "XBMC TEAM, freenode/#xbmc-scripting"
__version__ = "pre-2.0"

def _dialog_progress_create():
    global dialog
    dialog = xbmcgui.DialogProgress()
    dialog.create( __scriptname__, "Setting up script, please wait..." )

def _dialog_progress_close():
    global dialog
    dialog.close()

import sys, os
import xbmc, xbmcgui
#_dialog_progress_create()
import threading
import traceback

RESOURCE_PATH = os.path.join( os.getcwd().replace( ";", "" ), "resources" )

sys.path.append( os.path.join( RESOURCE_PATH, "lib" ) )

import wrt54g
import kcputil
import guibuilder
import language
_ = language.Language().string

##xLinkKai_UserName = xbmc.getInfoLabel( "xLinkKai.UserName" )

class GUI( xbmcgui.WindowDialog ):

    def __init__(self):
        try:
            self.timer_msg = None
            self.setupGUI()
            if ( not self.SUCCEEDED ): self.exitScript()
            else:
                self.show()
                self.setup_variables()
                self.wrt54g = wrt54g.Commands()
                self.check_status()
                #_dialog_progress_close()
        except: 
            #_dialog_progress_close()
            traceback.print_exc()
            self.close()

    def setupGUI( self ):
        current_skin = xbmc.getSkinDir()
        if ( not os.path.exists( os.path.join( RESOURCE_PATH, "skins", current_skin ))): current_skin = "default"
        skin_path = os.path.join( RESOURCE_PATH, "skins", current_skin )
        image_path = os.path.join( skin_path, "gfx" )
        if ( self.getResolution() == 0 or self.getResolution() % 2 ): xml_file = "skin_16x9.xml"
        else: xml_file = "skin.xml"
        if ( not os.path.isfile( os.path.join( skin_path, xml_file ))): xml_file = "skin.xml"
        guibuilder.GUIBuilder( self, os.path.join( skin_path, xml_file ), image_path, fastMethod=True, 
            title=__scriptname__, useDescAsKey=True, debug=False, language=_ )

    def setup_variables( self ):
        self.controller_action = kcputil.setControllerAction()
        self.set_message( 700 )
        self.KAID_VERSION = ""
        
    def get_control( self, key ):
        """ Return the control that matches the key """
        return self.controls[ key ][ 'control' ]

    def set_status_labels( self ):
        self.get_control( "Kaid Status Label" ).setLabel( [ "", _( 300 + self.wrt54g.STATUS_KAID_RUNNING ) ][ self.wrt54g.STATUS_KAID_RUNNING != -1 ] )
        self.get_control( "Kaid Status Label" ).setEnabled( self.wrt54g.STATUS_KAID_RUNNING == 1 )
        self.get_control( "Router Status Label" ).setLabel( self.KAID_VERSION )
        self.get_control( "Router Status Label" ).setEnabled( self.wrt54g.STATUS_ROUTER == 1 )
        self.get_control( "Xbox Status Label" ).setLabel( [ "", _( 320 + self.wrt54g.STATUS_XBOX ) ][ self.wrt54g.STATUS_XBOX != -1 ] )
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

    def set_message( self, msg_id=700, status=2 ):
        xbmcgui.lock()
        self.clear_message_timer()
        self.hide_status_bar()
        key = [ "Error Message Label", "Success Message Label",  "Info Message Label" ][ status ]
        self.get_control( key ).reset()
        self.get_control( key ).addLabel( _( msg_id ) )
        self.get_control( key ).setVisible( True )
        if ( status == 0 ):
            self.timer_msg = threading.Timer( 10, self.set_message, ( 700, ) )
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
            settings = settings.GUI( language=_, scriptname=__scriptname__, version=__version__ )
            settings.doModal()
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
        self.set_message( 600, 1 )
        ok = self.wrt54g._status_xbox()
        if ( ok == 2 ): self.set_message( 801, 0)
        else: self.set_message()
        if ( update ): self._set_status()
            
    def _status_router( self, update=True ):
        self.set_message( 601, 1 )
        ok, version = self.wrt54g._status_router_kaid()
        if ( version ): tmp_version = "Kaid (v.%s)" % ( version[ 0 ], )
        else: tmp_version = _( 311 )
        self.KAID_VERSION = [ _( 310 ), tmp_version, _( 312 ) ][ self.wrt54g.STATUS_ROUTER ]
        if ( self.wrt54g.STATUS_ROUTER == 2 ):
            self.set_message( 801, 0)
        elif ( self.wrt54g.STATUS_ROUTER ):
            self.set_message( 602, 1 )
            ok = self.wrt54g._status_router_kaid_conf()
            if ( ok ): self.set_message( 801, 0)
            else: self.set_message()
        if ( update ): self._set_status()

    def _status_kaid_running( self, update=True ):
        if ( self.wrt54g.STATUS_ROUTER != 2 ):
            self.set_message( 603, 1 )
            ok = self.wrt54g._status_kaid_running()
            if ( ok == 2 ): self.set_message( 801, 0)
            else: self.set_message()
        if ( update ): self._set_status()
        
    def _kaid_restart( self ):
        self.set_message( 610 + ( not self.wrt54g.STATUS_KAID_RUNNING ), 1 )
        ok = self.wrt54g._kaid_restart()
        if ( not ok ): self.set_message( 813, 0 )
        else: 
            self.show_progressbar( 5 )
            self._status_kaid_running()
            
    def _kaid_kill( self ):
        self.set_message( 612, 1 )
        ok = self.wrt54g._kaid_kill()
        if ( not ok ): self.set_message( 800, 0)
        else: 
            self.set_message()
        self._status_kaid_running()
        
    def _kaid_upload( self ):
        self.set_message( 613, 1 )
        ok = self.wrt54g._kaid_upload()
        if ( not ok ): self.set_message( 813, 0 )
        else: 
            self.set_message( 620, 1 )
            ok = self.wrt54g._finalize_upload()
            if ( not ok ): self.set_message( 820, 0 )
            else: 
                self.check_status()
                #self.set_message( 621, 1 )
                #ok = self.wrt54g._config_file_patch()
                #if ( not ok ): self.set_message( 821, 0 )
                #else:
                self._kaid_restart()

    def _router_reboot( self ):
        self.set_message( 614, 1 )
        ok = self.wrt54g._router_reboot()
        if ( not ok ): self.set_message( 800, 0)
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
    
    def exitScript(self):
        self.clear_message_timer()
        self.close()

    def onAction(self, action):
        button_key = self.controller_action.get( action.getButtonCode(), "n/a" )
        if ( button_key == "Keyboard ESC Button" or button_key == "Back Button" or button_key == "Remote Menu Button" ):
            self.exitScript()
        elif ( button_key == "Keyboard Menu Button" or button_key == "Y Button" or button_key == "Remote Title Button" or button_key == "White Button" ):
            self.change_settings()
    
    def onControl(self, control):
        if ( control == self.get_control( "Restart Button" ) ):
            self._kaid_restart()
        elif ( control == self.get_control( "Stop Button" ) ):
            self._kaid_kill()
        elif ( control == self.get_control( "Upload Button" ) ):
            self._kaid_upload()
        elif ( control == self.get_control( "Reboot Button" ) ):
            self._router_reboot()


if ( __name__ == "__main__" ):
    ui = GUI()
    ui.doModal()
    del ui
