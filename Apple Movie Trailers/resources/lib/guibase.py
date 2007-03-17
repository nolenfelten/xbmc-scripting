import xbmc, xbmcgui, language, traceback
_ = language.Language().string

#----------------------------------------------------------------------------#
# main gui
#----------------------------------------------------------------------------#
class GUI( xbmcgui.Window ):

    def __init__( self, custom_imports = [] ):
        try:
            self.setupImports( custom_imports )
            self.cwd = os.getcwd().replace( ";", "" )
            self.debug = os.path.isfile( os.path.join( self.cwd, 'debug.txt' ))
            self.getSettings()
            self.gui_loaded = self.setupGUI()
            if ( not self.gui_loaded ): self.close()
            else:
                self.setupVariables()
        except:
            traceback.print_exc()
            self.gui_loaded = False
            self.exitScript()

    def setupImports( self, custom_imports = [] ):
        try:
            self.progress_pct = 0
            self.progress_dialog = xbmcgui.DialogProgress()
            self.progress_dialog.create( _( 0 ) )
            self.imports = [ 'sys', 'os', 'threading', 'guibuilder', 'shutil', 'datetime', 'default' ]
            self.imports += custom_imports
            self.imported = dict()
            for name in self.imports:
                try:
                    self.custom_import( name )
                except:
                    break
            for name in self.imported.keys():
                globals().update( { name: self.imported[name] } )
        except:
            self.progress_dialog.close()
            raise

    def custom_import( self, name ):
        try:
            self.progress_pct += int( float( 100 ) / len( self.imports ) )
            self.progress_dialog.update( self.progress_pct, _(50), _(51), '%s %s' % ( _( 52 ), name ) )
            self.imported.update( { name: __import__( name ) } )
        except:
            self.progress_dialog.close()
            traceback.print_exc()
            xbmcgui.Dialog().ok( _( 0 ), _( 81 ) )
            self.exitScript()
            raise

    def getSettings( self ):
        self.settings = utilities.Settings().get_settings()

    def setupGUI( self ):
        gb = guibuilder.GUIBuilder()
        dialog = xbmcgui.DialogProgress()
        dialog.create( _( 0 ) )
        ok, self.image_path = gb.create_gui(
            self,
            skin = self.settings[ "skin" ],
            language = _
        )
        dialog.close()
        return ok

    def setupVariables( self ):
        self.skin = self.settings[ "skin" ]
        self.controller_action = utilities.setControllerAction()

    def updateScript( self ):
        import update
        updt = update.Update( language=_ )
        del updt

    def exitScript( self, restart=False ):
        self.close()
        if ( restart ):
            xbmc.executebuiltin( "XBMC.RunScript(%s)" % ( os.path.join( os.getcwd().replace( ";", "" ), "default.py" ), ) )

    def onControl( self, control ):
        pass

    def onAction( self, action ):
        try:
            button_key = self.controller_action.get( action.getButtonCode(), 'n/a' )
            if ( button_key == 'Keyboard ESC Button' or button_key == 'Back Button' or button_key == 'Remote Menu Button' ):
                self.exitScript()
        except:
            traceback.print_exc()

    def debugWrite( self, function, action, lines=[], values=[] ):
        if ( self.debug ):
            Action = ( 'Failed', 'Succeeded', 'Started' )
            Highlight = ( '__', '__', '<<<<< ', '__', '__', ' >>>>>' )
            xbmc.output( '%s%s%s : (%s)\n' % ( Highlight[action], function, Highlight[action + 3], Action[action] ) )
            try:
                for cnt, line in enumerate( lines ):
                    finished_line = '%s\n' % ( line, )
                    xbmc.output( finished_line % values[cnt] )
            except: traceback.print_exc()
