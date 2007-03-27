'''
    Thanks to Grischa Brockhaus creator of WrtKaidCommander
    
    by: Nuka1195
'''
import os
import xbmc
import urllib, socket
import utilities
import re

socket.setdefaulttimeout( 5.0 ) #seconds

class Commands( urllib.FancyURLopener ):
    """ Main class for controlling a linksys WRT54G router """
    def __init__( self ):
        """ initialize FancyURLopener with self """
        urllib.FancyURLopener.__init__( self )
        self._set_variables()
        self._get_settings()
    
    def _set_variables( self ):
        """ initially sets variables to -1 so status labels will be blank """
        self.STATUS_KAID_RUNNING = -1
        self.STATUS_ROUTER = -1
        self.STATUS_XBOX = -1
    
    def _get_settings( self ):
        """ get user and router settings """
        self.settings = utilities.Settings().get_settings()
        self.router_settings = utilities.Settings().get_router_settings( self.settings[ "firmware" ] )

    def _parse_data( self, data, failed, pattern=None ):
        """ searches router source for successful command completion """
        try:
            command_failed = data.find( failed )
            if ( command_failed != -1 ): return False
            if ( pattern is not None ):
                result = re.findall( pattern, data )
                return result
            else: return True
        except:
            return None
        
    def _status_xbox( self ):
        """ checks the status of the kai daemon and configuration files on the xbox """
        try:
            if ( os.path.exists( self.settings[ "path_to_kaid" ] ) and os.path.exists( self.settings[ "path_to_kaid_conf" ] ) ):
                self.STATUS_XBOX = 1
            else:
                self.STATUS_XBOX = 0
        except:
            self.STATUS_XBOX = 2
        return self.STATUS_XBOX
        
    def _status_router_kaid( self ):
        """ check the status of the kai daemon on the router and returns the version """
        version = ""
        self.STATUS_ROUTER = 0
        command = self.router_settings[ "version_command" ] % ( self.router_settings[ "bin_filename" ], )
        ok, result = self._do_command( command )
        if ( ok ):
            data = str(result.read())
            version = self._parse_data( data, self.router_settings[ "version_command_failed" ], self.router_settings[ "version_regex_pat" ] )
            if ( version ): self.STATUS_ROUTER = 1
        else: 
            self.STATUS_ROUTER = 2
            self.STATUS_KAID_RUNNING = 2
        return self.STATUS_ROUTER, version
        
    def _status_router_kaid_conf( self ):
        """ checks the status of the kai configuration file on the router """
        command = self.router_settings[ "ls_command" ] % ( self.router_settings[ "conf_filename" ], )
        ok, result = self._do_command( command )
        if ( ok ):
            data = result.read()
            self.STATUS_ROUTER = self._parse_data( data, self.router_settings[ "ls_command_failed" ] )
        return self.STATUS_ROUTER

    def _status_kaid_running( self ):
        """ checks the running status of the kai daemon on the router """
        self.STATUS_KAID_RUNNING = 0
        if ( self.STATUS_ROUTER != 2 ):
            command = "%s" % ( self.router_settings[ "ps_command" ], )
            ok, result = self._do_command( command )
            if ( ok ):
                data = result.read()
                self.STATUS_KAID_RUNNING = ( not self._parse_data( data, self.router_settings[ "bin_filename" ] ) )
        return self.STATUS_KAID_RUNNING

    def _kaid_restart( self ):
        """ restarts the kai daemon """
        # kill the daemon first if it's running
        ok = self._kaid_kill()
        command = self.router_settings[ "run_command" ] % (self.router_settings[ "bin_filename" ], self.router_settings[ "conf_filename" ], )
        ok, result = self._do_command( command )
        return ok

    def _kaid_kill( self ):
        """ kills the kai daemon process """
        command = self.router_settings[ "kill_command" ] % ( os.path.split( self.router_settings[ "bin_filename" ] )[ 1 ], )
        ok, result = self._do_command( command )
        return ok

    def _kaid_upload( self ):
        """ uploads the kai daemon to the router """
        ok = self._kaid_kill()
        if ( self.settings[ "upload_method" ] == 1 ):
            command = self.router_settings[ "wget_ftp_kaid" ] % ( self.settings[ "xbox_user" ],
                self.settings[ "xbox_pwd" ], xbmc.getIPAddress(), self.settings[ "path_to_kaid" ].replace( ":" , "" ).replace( "\\", "/" ),
                self.router_settings[ "bin_filename" ], )
        else:
            command = self.router_settings[ "wget_http_kaid" ] % ( xbmc.getIPAddress(), self.settings[ "path_to_kaid" ].replace( ":" , "" ).replace( "\\", "/" ),
                self.router_settings[ "bin_filename" ], )
        ok, result = self._do_command( command )
        if ( ok ):
            ok = self._kaid_conf_upload()
        return ok
            
    def _kaid_conf_upload( self ):
        """ uploads the kai configuration file to the router """
        if ( self.settings[ "upload_method" ] == 1 ):
            command = self.router_settings[ "wget_ftp_kaid_conf" ] % ( self.settings[ "xbox_user" ],
                self.settings[ "xbox_pwd" ], xbmc.getIPAddress(), self.settings[ "path_to_kaid_conf" ].replace( ":" , "" ).replace( "\\", "/" ),
                self.router_settings[ "conf_filename" ], )
        else:
            command = self.router_settings[ "wget_http_kaid_conf" ] % ( xbmc.getIPAddress(), self.settings[ "path_to_kaid_conf" ].replace( ":" , "" ).replace( "\\", "/" ),
                self.router_settings[ "conf_filename" ], )
        ok, result = self._do_command( command )
        return ok
    
    def _finalize_upload( self ):
        """ unzips and chmods the kai daemon """
        command = self.router_settings[ "finalize_command" ] % ( self.router_settings[ "bin_filename" ], self.router_settings[ "bin_filename" ], )
        ok, result = self._do_command( command )
        return ok
            
    def _router_reboot( self ):
        """ reboots the router """
        ok, result = self._do_command( self.router_settings[ "reboot_command" ] )
        if ( ok ):
            self.STATUS_KAID_RUNNING = 0
            self.STATUS_ROUTER = 0
            return True
        return False
        
    def _config_file_patch( self ):
        """ patches the kai configuration file with the users SniffDevice setting """
        try:
            conf_file = open( self.settings[ "path_to_kaid_conf" ], 'rb' )
            data = conf_file.read()
            conf_file.close()
            data = data.replace( "SniffDevice = ", "SniffDevice = %s\n#" % ( self.settings[ "sniff_device" ], ) )
            conf_file = open( self.settings[ "path_to_kaid_conf" ], 'wb' )
            conf_file.write( data )
            conf_file.close()
            return True
        except:
            return False

    def _do_command( self, command ):
        """ main command gets run here """
        try:
            self.router_settings[ "form_data" ][ self.router_settings[ "command_key" ] ] = command
            form_data = urllib.urlencode( self.router_settings[ "form_data" ] )
            # two methods POST or GET
            if ( self.router_settings[ "method" ] == "POST" ):
                result = self.open( self.router_settings[ "url_form" ] % ( self.settings[ "router_ip" ], form_data, ) )
            else: # get method
                result = ( self.open( self.router_settings[ "url_form" ] % ( self.settings[ "router_ip" ], ), form_data ) )
            self.close()
            command_success = True
        except:
            result = None
            command_success = False
        return command_success, result

    def get_user_passwd( self, host, realm, clear_cache=0 ):
        """ subclassed method to override the need for user to input user/password """
        if ( host == self.settings[ "router_ip" ] ):
            return ( self.settings[ "router_user" ], self.settings[ "router_pwd" ], )
        else:
            return ( None, None, )

    def prompt_user_passwd( self, host, realm ):
        """ dummy method """
        return self.get_user_passwd( host, realm )
