import sys, os

def setControllerAction():
    return {
                61478 : "Keyboard Up Arrow",
                61480 : "Keyboard Down Arrow",
                61448 : "Keyboard Backspace Button",
                61533 : "Keyboard Menu Button",
                61467 : "Keyboard ESC Button",
                    216 : "Remote Back Button",
                    247 : "Remote Menu Button",
                    229 : "Remote Title Button",
                    207 : "Remote 0",
                    166 : "Remote Up",
                    167 : "Remote Down",
                    256 : "A Button",
                    257 : "B Button",
                    258 : "X Button",
                    259 : "Y Button",
                    260 : "Black Button",
                    261 : "White Button",
                    274 : "Start Button",
                    275 : "Back Button",
                    270 : "DPad Up",
                    271 : "DPad Down",
                    272 : "DPad Left",
                    273 : "DPad Right"
                }


class Settings:
    def __init__( self, *args, **kwargs ):
        pass

    def get_router_settings( self, firmware ):
        try:
            settings_file = open( os.path.join( os.getcwd().replace( ";", "" ), "resources", "firmware", firmware, "settings.txt" ), "r" )
            router_settings = eval( settings_file.read() )
            settings_file.close()
        except:
            router_settings = self._use_router_defaults()
        return router_settings

    def _use_router_defaults( self, show_dialog=False ):
        router_settings = {
            "url_form": "http://%s/apply.cgi?%s",
            "wget_ftp_kaid": "wget ftp://%s:%s@%s/%s -O %s.gz",
            "wget_ftp_kaid_conf": "wget ftp://%s:%s@%s/%s -O %s",
            "wget_http_kaid": "wget http://%s/%s -O %s.gz",
            "wget_http_kaid_conf": "wget http://%s/%s -O %s",
            "method": "POST",
            "bin_filename": "/tmp/kaid",
            "conf_filename": "/tmp/kaid.conf",
            "command_key": "command_cmd",
            "form_data": { "submit_button": "Command", "submit_type": "start", "change_action": "gozila_cgi", "action": "Apply", "command_cmd": "" },
            "ls_command": "ls %s",
            "ps_command": "ps",
            "kill_command": "killall -9 %s",
            "run_command": "%s -s -c %s -d",
            "finalize_command": "sleep 3;gunzip %s.gz;sleep 2;chmod +x %s",
            "reboot_command": "/sbin/reboot",
            "version_command": "%s -V",
            "version_regex_pat": "var log = .*\\\\x0a\\\\x0a([0-9a-zA-Z]*)",
            "version_command_failed": "not found",
            "ls_command_failed": "No such file or directory"
            }        
        return router_settings
    
    def get_settings( self ):
        try:
            settings_path = os.path.join( "T:\\script_data", sys.modules[ "__main__" ].__scriptname__ )
            settings_file = open( os.path.join( settings_path, "settings.txt" ), "r" )
            settings = eval( settings_file.read() )
            settings_file.close()
        except:
            settings = self._use_defaults()
        return settings

    def _use_defaults( self, show_dialog=False ):
        settings = {  
            "firmware": "Hyper-WRT",
            "router_ip": "192.168.1.1",
            "router_user": "root",
            "router_pwd": "password",
            "path_to_kaid": "q:\\web\\kaid\\kaid.gz", 
            "path_to_kaid_conf": "q:\\web\\kaid\\kaid.conf",
            "upload_method": 1,
            "xbox_user": "xbox",
            "xbox_pwd": "xbox",
            "sniff_device": "vlan0",
            "exit_to_kai": True
            }
        ok = self.save_settings( settings )
        return settings

    def save_settings( self, settings ):
        try:
            settings_path = os.path.join( "T:\\script_data", sys.modules[ "__main__" ].__scriptname__ )
            if ( not os.path.isdir( settings_path ) ):
                os.makedirs( settings_path )
            settings_file = open( os.path.join( settings_path, "settings.txt" ), "w" )
            settings_file.write( repr( settings ) )
            settings_file.close()
            return True
        except:
            return False
            
