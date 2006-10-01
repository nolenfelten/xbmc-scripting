import sys, traceback
import os.path
import ConfigParser

ScriptPath              = os.getcwd()
if ScriptPath[-1]==';': ScriptPath=ScriptPath[0:-1]
if ScriptPath[-1]!='\\': ScriptPath=ScriptPath+'\\'

SETTINGS_FILE = os.path.join( os.path.join( ScriptPath, 'config'), 'settings.ini' )
config = ConfigParser.ConfigParser()

def printLastError():
    e = sys.exc_info()
    traceback.print_exception( e[0], e[1], e[2] )

def lastErrorString():
    return sys.exc_info()[1]

def Read():
    config.read( SETTINGS_FILE )
    try: keys = config.options( 'settings' )
    except: keys = []
    if not len( keys ):
        keys = [ 'site', 'skinpath' ]
    settings = {}
    for key in keys:
        try: value = config.get( 'settings', key )
        except: value = None
        if key == 'site':
            if not value:
                value = '0'
            value = int( value )
        if key == 'skinpath' and not value:
            value = 'q:\skintemp'
        settings.update( { key : value } )
    Save( settings )
    return settings

def Save( settings ):
    try: config.add_section( 'settings' )
    except: pass
    for setting in settings:
        key = setting
        value = settings[setting]
        config.set( 'settings', key, value )
    config.write( open( SETTINGS_FILE, 'wb' ) )
    return
