class _XBMC_Button:
    def __init__( self, action_code ):
        self.action_code = action_code
        self.action_dict = {
            18:'X',
            34:'Y',
            9:'B',
            7:'A',
            10:'Back',
            111:'Left Shoulder',
            112:'Right Shoulder',
            117:'White',
            1:'Left',
            2:'Right',
            3:'Up',
            4:'Down'
        }
    def __str__( self ):
        if self.action_code in self.action_dict:
            return self.action_dict[self.action_code]
        else:
            return 'Unknown (' + str( self.action_code ) + ')'

def XBMC_Button( action_code ): return str( _XBMC_Button( action_code ) )