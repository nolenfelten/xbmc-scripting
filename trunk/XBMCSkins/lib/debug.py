import traceback, sys
import xbmcgui

DEBUGMODE = 1

error = 'Error'
msg = 'Message'
popup = 'Popup'

#Debug data print function. Self explanatory...
def debugPrint( type, text, verbose=1 ):
    if DEBUGMODE == 1:
        if type == msg:
            print text
        elif type == error:
            print "\n" + "-"*5 + text + "-"*5
            if verbose:
                traceback.print_exc(file=sys.stdout)
            else:
                print traceback.format_exception_only( sys.exc_type, sys.exc_value )[0]
            print "-"*65 + "\n"
    if type == popup:
        xbmcgui.Dialog().ok('Error', text)
    else:
        return
