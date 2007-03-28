"""
Settings module

Nuka1195
"""

import sys
import os
import xbmc
import xbmcgui
import utilities


class GUI( xbmcgui.WindowXMLDialog ):
    """ Settings module: used for changing settings """
    def __init__( self, *args, **kwargs ):
        self._ = kwargs[ "language" ]
    
    def onInit( self ):
        self._set_labels()
        self._set_variables()
        self._get_settings()
        self._setup_special()
        self._set_controls_values()
        self._set_restart_required()

    def _set_labels( self ):
        xbmcgui.lock()
        try:
            self.getControl( 2 ).setLabel( sys.modules[ "__main__" ].__scriptname__ )
            self.getControl( 3 ).setLabel( "%s: %s" % ( self._( 1006 ), sys.modules[ "__main__" ].__version__, ) )
            self.getControl( 10 ).setLabel( self._( 201 ) )
            self.getControl( 20 ).setLabel( self._( 202 ) )
            self.getControl( 30 ).setLabel( self._( 203 ) )
            self.getControl( 40 ).setLabel( self._( 204 ) )
            self.getControl( 50 ).setLabel( self._( 205 ) )
            self.getControl( 60 ).setLabel( self._( 206 ) )
            self.getControl( 70 ).setLabel( self._( 207 ) )
            self.getControl( 80 ).setLabel( self._( 208 ) )
            self.getControl( 90 ).setLabel( self._( 209 ) )
            self.getControl( 100 ).setLabel( self._( 210 ) )
            self.getControl( 110 ).setLabel( self._( 211 ) )
            self.getControl( 200 ).setLabel( self._( 250 ) )
            self.getControl( 210 ).setLabel( self._( 251 ) )
            self.getControl( 220 ).setLabel( self._( 252 ) )
            self.getControl( 230 ).setLabel( self._( 253 ) )
        except: pass
        xbmcgui.unlock()
            
    def _set_variables( self ):
        """ initializes variables """
        self.controller_action = utilities.setControllerAction()
        # setEnabled( False ) if not used
        self.getControl( 230 ).setVisible( False )
        self.getControl( 230 ).setEnabled( False )

    def _get_settings( self ):
        """ reads settings """
        self.settings = utilities.Settings().get_settings()

    def _save_settings( self ):
        """ saves settings """
        ok = utilities.Settings().save_settings( self.settings )
        if ( not ok ):
            ok = xbmcgui.Dialog().ok( sys.modules[ "__main__" ].__scriptname__, self._( 230 ) )
        else:
            self._check_for_restart()

    def _get_keyboard( self, default="", heading="", hidden=False ):
        """ shows a keyboard and returns a value """
        keyboard = xbmc.Keyboard( default, heading, hidden )
        keyboard.doModal()
        if ( keyboard.isConfirmed() ):
            return keyboard.getText()
        return default

    def _get_numeric( self, default="", heading="", type=3 ):
        """ shows a numeric dialog and returns a value
            - 0 : ShowAndGetNumber		(default format: #)
            - 1 : ShowAndGetDate			(default format: DD/MM/YYYY)
            - 2 : ShowAndGetTime			(default format: HH:MM)
            - 3 : ShowAndGetIPAddress	(default format: #.#.#.#)
        """
        dialog = xbmcgui.Dialog()
        value = dialog.numeric( type, heading, default )
        return value

    def _get_browse_dialog( self, default="", heading="", type=1, shares="files", mask="", use_thumbs=False, treat_as_folder=False ):
        """ shows a browse dialog and returns a value
            - 0 : ShowAndGetDirectory
            - 1 : ShowAndGetFile
            - 2 : ShowAndGetImage
            - 3 : ShowAndGetWriteableDirectory
        """
        dialog = xbmcgui.Dialog()
        value = dialog.browse( type, heading, shares, mask, use_thumbs, treat_as_folder, default )
        return value

##### Start of unique defs #####################################################

##### Special defs, script dependent, remember to call them from _setup_special #################
    
    def _set_restart_required( self ):
        """ copies self.settings and adds any settings that require a restart on change """
        self.settings_original = self.settings.copy()
        self.settings_restart = ( "firmware", "router_ip", "router_user", "router_pwd", )

    def _setup_special( self ):
        """ calls any special defs """
        self._setup_sniff_devices()
        self._setup_firmware()

    def _setup_sniff_devices( self ):
        """ special def for setting up sniff device choices """
        self.sniff_devices = [ "eth0", "en0", "br0", "vlan0" ]
        try: self.current_sniff_device = self.sniff_devices.index( self.settings[ "sniff_device" ] )
        except: self.current_sniff_device = 0
            
    def _setup_firmware( self ):
        """ special def for setting up firmware choices """
        self.firmware = os.listdir( os.path.join( os.getcwd().replace( ";", "" ), "resources", "firmware" ) )
        try: self.current_firmware = self.firmware.index( self.settings[ "firmware" ] )
        except: self.current_firmware = 0
        
###### End of Special defs #####################################################

    def _set_controls_values( self ):
        """ sets the value labels """
        xbmcgui.lock()
        try:
            self.getControl( 11 ).setLabel( self.settings[ "firmware" ] )
            self.getControl( 21 ).setLabel( self.settings[ "router_ip" ] )
            self.getControl( 31 ).setLabel( self.settings[ "router_user" ] )
            self.getControl( 41 ).setLabel( self.settings[ "router_pwd" ] )
            self.getControl( 51 ).setLabel( self.settings[ "path_to_kaid" ] )
            self.getControl( 61 ).setLabel( self.settings[ "path_to_kaid_conf" ] )
            self.getControl( 71 ).setLabel( ( "http://", "ftp://", )[ self.settings[ "upload_method" ] ] )
            self.getControl( 81 ).setLabel( self.settings[ "xbox_user" ] )
            self.getControl( 91 ).setLabel( self.settings[ "xbox_pwd" ] )
            self.getControl( 101 ).setLabel( self.settings[ "sniff_device" ] )
            self.getControl( 111 ).setSelected( self.settings[ "exit_to_kai" ] )
        except: pass
        xbmcgui.unlock()
    
    def _change_setting1( self ):
        """ changes settings #1 """
        self.current_firmware += 1
        if ( self.current_firmware == len( self.firmware ) ): self.current_firmware = 0
        self.settings[ "firmware" ] = self.firmware[ self.current_firmware ]
    
    def _change_setting2( self ):
        """ changes settings #2 """
        self.settings[ "router_ip" ] = self._get_numeric( self.settings[ "router_ip" ], self._( 202 ) )
        
    def _change_setting3( self ):
        """ changes settings #3 """
        self.settings[ "router_user" ] = self._get_keyboard( self.settings[ "router_user" ], self._( 203 ) )

    def _change_setting4( self ):
        """ changes settings #4 """
        self.settings[ "router_pwd" ] = self._get_keyboard( self.settings[ "router_pwd" ], self._( 204 ) )
        
    def _change_setting5( self ):
        """ changes settings #5 """
        self.settings[ "path_to_kaid" ] = self._get_browse_dialog( self.settings[ "path_to_kaid" ], self._( 205 ) )
    
    def _change_setting6( self ):
        """ changes settings #6 """
        self.settings[ "path_to_kaid_conf" ] = self._get_browse_dialog( self.settings[ "path_to_kaid_conf" ], self._( 206 ) )

    def _change_setting7( self ):
        """ changes settings #7 """
        self.settings[ "upload_method" ] = not self.settings[ "upload_method" ]
        
    def _change_setting8( self ):
        """ changes settings #8 """
        self.settings[ "xbox_user" ] = self._get_keyboard( self.settings[ "xbox_user" ], self._( 208 ) )

    def _change_setting9( self ):
        """ changes settings #9 """
        self.settings[ "xbox_pwd" ] = self._get_keyboard( self.settings[ "xbox_pwd" ], self._( 209 ) )

    def _change_setting10( self ):
        """ changes settings #10 """
        self.current_sniff_device += 1
        if ( self.current_sniff_device == len( self.sniff_devices ) ): self.current_sniff_device = 0
        self.settings[ "sniff_device" ] = self.sniff_devices[ self.current_sniff_device ]
            
    def _change_setting11( self ):
        """ changes settings #11 """
        self.settings[ "exit_to_kai" ] = not self.settings[ "exit_to_kai" ]
        
##### End of unique defs ######################################################
    
    def _update_script( self ):
        """ checks for updates to the script """
        import update
        updt = update.Update( language=self._ )
        del updt
            
    def _show_credits( self ):
        """ shows a credit window """
        import credits
        c = credits.GUI( language=self._ )
        c.doModal()
        del c

    def _check_for_restart( self ):
        """ checks for any changes that require a restart to take effect """
        restart = False
        for setting in self.settings_restart:
            if ( self.settings_original[ setting ] != self.settings[ setting ] ):
                restart = True
                break
        self._close_dialog( True, restart )

    def _close_dialog( self, changed=False, restart=False ):
        """ closes this dialog window """
        self.changed = changed
        self.restart = restart
        self.close()
        
    def get_control( self, key ):
        """ returns the control that matches the key """
        try: return self.controls[ key ][ "control" ]
        except: return None

    def onClick( self, controlId ):
        if ( controlId == 200 ):
            self._save_settings()
        elif ( controlId == 210 ):
            self._close_dialog()
        elif ( controlId == 220 ):
            self._update_script()
        elif ( controlId == 230 ):
            self._show_credits()
        else:
            if ( controlId == 10 ):
                self._change_setting1()
            elif ( controlId == 20 ):
                self._change_setting2()
            elif ( controlId == 30 ):
                self._change_setting3()
            elif ( controlId == 40 ):
                self._change_setting4()
            elif ( controlId == 50 ):
                self._change_setting5()
            elif ( controlId == 60 ):
                self._change_setting6()
            elif ( controlId == 70 ):
                self._change_setting7()
            elif ( controlId == 80 ):
                self._change_setting8()
            elif ( controlId == 90 ):
                self._change_setting9()
            elif ( controlId == 100 ):
                self._change_setting10()
            elif ( controlId == 110 ):
                self._change_setting11()
            self._set_controls_values()

    def onFocus( self, controlId ):
        pass

    def onAction( self, action ):
        button_key = self.controller_action.get( action.getButtonCode(), "n/a" )
        if ( button_key == "Keyboard Backspace Button" or button_key == "B Button" or button_key == "Remote Back Button" ):
            self._close_dialog()
        elif ( button_key == "Keyboard ESC Button" or button_key == "Back Button" or button_key == "Remote Menu Button" ):
            self._save_settings()
