import sys, os
import xbmc, xbmcgui
import guibuilder
import kcputil
import traceback

class GUI( xbmcgui.WindowDialog ):
    def __init__( self, *args, **kwargs ):
        try:
            self._ = kwargs[ "language" ]
            self.__scriptname__ = sys.modules[ '__main__' ].__scriptname__
            self.__version__ = sys.modules[ '__main__' ].__version__
            self.setupGUI()
            if ( not self.SUCCEEDED ): self.close()
            else:
                #self.show()
                self._set_variables()
                self._get_settings()
                self._setup_firmware()
                self._setup_sniff_devices()
                self._set_controls_values()
                self._set_page_visible()
        except:
            traceback.print_exc()
            self.close()

    def setupGUI( self ):
        cwd = os.path.join( os.getcwd().replace( ";", "" ), "resources", "skins" )
        current_skin = xbmc.getSkinDir()
        if ( not os.path.exists( os.path.join( cwd, current_skin ))): current_skin = "default"
        skin_path = os.path.join( cwd, current_skin )
        image_path = os.path.join( skin_path, "gfx" )
        if ( self.getResolution() == 0 or self.getResolution() % 2 ): xml_file = "settings_16x9.xml"
        else: xml_file = "settings.xml"
        if ( not os.path.isfile( os.path.join( skin_path, xml_file ))): xml_file = "settings.xml"
        guibuilder.GUIBuilder( self, os.path.join( skin_path, xml_file ), image_path, useDescAsKey=True, language=self._, fastMethod=True, debug=False )

    def _set_variables( self ):
        self.controller_action = kcputil.setControllerAction()
        self.get_control( "Version Label" ).setLabel( "%s: %s" % ( self._( 1006 ), self.__version__, ) )
        self.get_control( "Update Button" ).setEnabled( xbmc.getCondVisibility( "System.InternetState" ) )
        self.current_page = 1
        self.total_pages = 2
        
    def _get_settings( self ):
        self.settings = kcputil.Settings().get_settings()

    def _save_settings( self ):
        ok = kcputil.Settings().save_settings( self.settings )
        if ( not ok ):
            ok = xbmcgui.Dialog().ok( self.__scriptname__, self._( 230 ) )
        else:
            self._close_dialog()
            
    def _setup_sniff_devices( self ):
        self.sniff_devices = ( "eth0", "en0", "br0", "vlan0", )
        for cnt, sd in enumerate( self.sniff_devices ):
            if ( sd == self.settings[ "sniff_device" ].lower() ):
                self.current_sniff_device = cnt
                break

    def _setup_firmware( self ):
        firmware = []
        self.current_firmware = 0
        os.path.walk( os.path.join( os.getcwd().replace( ";", "" ), "resources", "firmware" ), self._add_firmware, firmware )
        self.firmware = firmware
        for cnt, firmware in enumerate( self.firmware ):
            if ( firmware.lower() == self.settings[ "firmware" ].lower() ):
                self.current_firmware = cnt
                break
        
    def _add_firmware( self, firmware, path, files ):
        folder = os.path.split( path )[ 1 ]
        if ( folder.lower() != "firmware" ):
            firmware += [ folder ]
            
    def _set_controls_values( self ):
        xbmcgui.lock()
        self.get_control( "Setting1 Value" ).setLabel( "%s" % ( self.settings[ "firmware" ], ) )
        self.get_control( "Setting2 Value" ).setLabel( "%s" % ( self.settings[ "router_ip" ], ) )
        self.get_control( "Setting3 Value" ).setLabel( "%s" % ( self.settings[ "router_user" ], ) )
        self.get_control( "Setting4 Value" ).setLabel( "%s" % ( self.settings[ "router_pwd" ], ) )
        self.get_control( "Setting5 Value" ).setLabel( "%s" % ( self.settings[ "path_to_kaid" ], ) )
        self.get_control( "Setting6 Value" ).setLabel( "%s" % ( self.settings[ "path_to_kaid_conf" ], ) )
        self.get_control( "Setting7 Value" ).setLabel( "%s" % ( [ "http://", "ftp://" ][ self.settings[ "upload_method" ] ], ) )
        self.get_control( "Setting8 Value" ).setLabel( "%s" % ( self.settings[ "xbox_user" ], ) )
        self.get_control( "Setting9 Value" ).setLabel( "%s" % ( self.settings[ "xbox_pwd" ], ) )
        self.get_control( "Setting10 Value" ).setLabel( "%s" % ( self.settings[ "sniff_device" ], ) )
        self.get_control( "Setting11 Value" ).setLabel( "%s" % ( str( self.settings[ "exit_to_kai" ] ), ) )
        xbmcgui.unlock()
    
    def _set_page_visible( self ):
        xbmcgui.lock()
        for control in range( 1, 10 ):
            self.get_control( "Setting%s Button" % ( control, ) ).setVisible( self.current_page == 1 )
            self.get_control( "Setting%s Button" % ( control, ) ).setEnabled( self.current_page == 1 )
            self.get_control( "Setting%s Value" % ( control, ) ).setVisible( self.current_page == 1 )
        for control in range( 10, 12 ):
            self.get_control( "Setting%s Button" % ( control, ) ).setVisible( self.current_page == 2 )
            self.get_control( "Setting%s Button" % ( control, ) ).setEnabled( self.current_page == 2 )
            self.get_control( "Setting%s Value" % ( control, ) ).setVisible( self.current_page == 2 )
        self.get_control( "Page Label" ).setLabel( "%d/%d" % ( self.current_page, self.total_pages, ) )
        xbmcgui.unlock()
    
    def _get_keyboard( self, default="", heading="" ):
        keyboard = xbmc.Keyboard( default, heading )
        keyboard.doModal()
        if ( keyboard.isConfirmed() ):
            return keyboard.getText()
        return default

    def _get_numeric( self, default="", heading="", type=3 ):
        '''
          0 : ShowAndGetNumber
          1 : ShowAndGetDate
          2 : ShowAndGetTime
          3 : ShowAndGetIPAddress
        '''
        dialog = xbmcgui.Dialog()
        value = dialog.numeric( type, heading )
        if ( value ): return value
        else: return default

    def _get_browse_dialog( self, default="", heading="", type=1, shares="files" ):
        """
          0 : ShowAndGetDirectory
          1 : ShowAndGetFile
          2 : ShowAndGetImage
          3 : ShowAndGetWriteableDirectory
        """
        dialog = xbmcgui.Dialog()
        value = dialog.browse( type, heading, shares )
        if ( value ): return value
        else: return default

    def _change_setting1( self ):
        self.current_firmware += 1
        if ( self.current_firmware == len( self.firmware ) ): self.current_firmware = 0
        self.settings[ "firmware" ] = self.firmware[ self.current_firmware ]
    
    def _change_setting2( self ):
        self.settings[ "router_ip" ] = self._get_numeric( self.settings[ "router_ip" ], self._( 202 ) )
        
    def _change_setting3( self ):
        self.settings[ "router_user" ] = self._get_keyboard( self.settings[ "router_user" ], self._( 203 ) )

    def _change_setting4( self ):
        self.settings[ "router_pwd" ] = self._get_keyboard( self.settings[ "router_pwd" ], self._( 204 ) )
        
    def _change_setting5( self ):
        self.settings[ "path_to_kaid" ] = self._get_browse_dialog( self.settings[ "path_to_kaid" ], self._( 205 ) )
    
    def _change_setting6( self ):
        self.settings[ "path_to_kaid_conf" ] = self._get_browse_dialog( self.settings[ "path_to_kaid_conf" ], self._( 206 ) )

    def _change_setting7( self ):
        self.settings[ "upload_method" ] = not self.settings[ "upload_method" ]
        
    def _change_setting8( self ):
        self.settings[ "xbox_user" ] = self._get_keyboard( self.settings[ "xbox_user" ], self._( 208 ) )

    def _change_setting9( self ):
        self.settings[ "xbox_pwd" ] = self._get_keyboard( self.settings[ "xbox_pwd" ], self._( 209 ) )

    def _change_setting10( self ):
        self.current_sniff_device += 1
        if ( self.current_sniff_device == len( self.sniff_devices ) ): self.current_sniff_device = 0
        self.settings[ "sniff_device" ] = self.sniff_devices[ self.current_sniff_device ]
            
    def _change_setting11( self ):
        self.settings[ "exit_to_kai" ] = not self.settings[ "exit_to_kai" ]
    
    def _update_script( self ):
        try:
            import update
            updt = update.Update( language=self._ )
            del updt
        except: traceback.print_exc()
            
    #def _show_credits( self ):
    #    import credits
    #    c = credits.GUI( language=self._ )
    #    c.doModal()
    #    del c

    def _change_page( self ):
        self.current_page += 1
        if ( self.current_page > self.total_pages ):
            self.current_page = 1
        self._set_page_visible()
    
    def _close_dialog( self ):
        self.close()
        
    def get_control( self, key ):
        """ Return the control that matches the key """
        try: return self.controls[ key ][ "control" ]
        except: return None

    def onControl( self, control ):
        if ( control is self.get_control( "Ok Button" ) ):
            self._save_settings()
        elif ( control is self.get_control( "Cancel Button" ) ):
            self._close_dialog()
        elif ( control is self.get_control( "Update2 Button" ) ):
            self._update_script()
        #elif ( control is self.get_control( "Credits Button" ) ):
        #    self._show_credits()
        elif ( control is self.get_control( "Page Button" ) ):
            self._change_page()
        else:
            if ( control is self.get_control( "Setting1 Button" ) ):
                self._change_setting1()
            elif ( control is self.get_control( "Setting2 Button" ) ):
                self._change_setting2()
            elif ( control is self.get_control( "Setting3 Button" ) ):
                self._change_setting3()
            elif ( control is self.get_control( "Setting4 Button" ) ):
                self._change_setting4()
            elif ( control is self.get_control( "Setting5 Button" ) ):
                self._change_setting5()
            elif ( control is self.get_control( "Setting6 Button" ) ):
                self._change_setting6()
            elif ( control is self.get_control( "Setting7 Button" ) ):
                self._change_setting7()
            elif ( control is self.get_control( "Setting8 Button" ) ):
                self._change_setting8()
            elif ( control is self.get_control( "Setting9 Button" ) ):
                self._change_setting9()
            elif ( control is self.get_control( "Setting10 Button" ) ):
                self._change_setting10()
            elif ( control is self.get_control( "Setting11 Button" ) ):
                self._change_setting11()
            self._set_controls_values()
            
    def onAction( self, action ):
        control = self.getFocus()
        button_key = self.controller_action.get( action.getButtonCode(), "n/a" )
        if ( button_key == "Keyboard Backspace Button" or button_key == "B Button" or button_key == "Remote Back Button" ):
            self._close_dialog()
        elif ( button_key == "Keyboard ESC Button" or button_key == "Back Button" or button_key == "Remote Menu Button" ):
            self._save_settings()






