import xbmc, xbmcgui
import sys, os
import trailers, threading
import guibuilder

class GUI( xbmcgui.Window ):
    def __init__( self ):
        self.getSettings()
        self.setupGUI()
        if ( not self.SUCCEEDED ): self.close()
        else:
            self.setupConstants()
            self.trailers = trailers.Trailers()
            self.showCategories()
            self.setGenre( 'Newest' )
            self.getTrailerInfo(  self.controls['Newest List']['control'].getSelectedItem() )

    def setupGUI(self):
        skinPath = os.path.join( os.getcwd(), 'skins' ).replace( ';', '' ) # workaround apparent xbmc bug - os.getcwd() returns an extraneous semicolon (;) at the end of the path
        self.skinPath = os.path.join( skinPath, self.settings['skin'] )
        self.imagePath = os.path.join( self.skinPath, 'gfx' )
        guibuilder.GUIBuilder( self, os.path.join( self.skinPath, 'skin.xml' ), self.imagePath, title='Apple Movie Trailers', useDescAsKey=True, debug=False )

    def getSettings( self ):
        try:
            self.settings = {}
            f = open( os.path.join( os.getcwd(), 'data', 'settings.txt' ).replace( ';', '' ), 'r' )
            settings = f.read().split('|')
            f.close()
            self.settings['trailer size'] = int( settings[0] )
            self.settings['download trailer'] = int( settings[1] )
            self.settings['skin'] = settings[2]
        except:
            self.settings = {'trailer size' : 2, 'download trailer' : False, 'skin' : 'default'}
                
    def saveSettings( self ):
        try:
            f = open( os.path.join( os.getcwd(), 'data', 'settings.txt' ).replace( ';', '' ), 'w' )
            settings = '%d|%d|%s' % ( self.settings['trailer size'], self.settings['download trailer'], self.settings['skin'], )
            f.write(settings)
            f.close()
        except:
            dialog = xbmcgui.Dialog()
            ok = dialog.ok('Apple Movie Trailers', 'There was an error saving your settings.')

    def setupConstants( self ):
        # self.Timer is currently used for the Player() subclass to update screen on a onPlayback* event
        self.Timer = threading.Timer(60*60, self.exitScript,() )
        self.Timer.start()
        self.MyPlayer = MyPlayer(xbmc.PLAYER_CORE_MPLAYER, function=self.myPlayerChanged)
        self.controllerAction = {
            216 : 'Remote Back Button',
            247 : 'Remote Menu Button',
            256 : 'A Button',
            257 : 'B Button',
            258 : 'X Button',
            259 : 'Y Button',
            260 : 'Black Button',
            261 : 'White Button',
            274 : 'Start Button',
            275 : 'Back Button',
            270 : 'DPad Up',
            271 : 'DPad Down',
            272 : 'DPad Left',
            273 : 'DPad Right'
        }
    
    # this function is used for skins like XBMC360 that have player information on screen
    def myPlayerChanged(self):
        self.controls['X Button On']['control'].setVisible( xbmc.getCondVisibility( self.controls['X Button On']['visible'] ) )
        self.controls['X Button Off']['control'].setVisible( xbmc.getCondVisibility( self.controls['X Button Off']['visible'] ) )
        self.controls['Full-Screen Visualisation Label']['control'].setVisible( xbmc.getCondVisibility( self.controls['Full-Screen Visualisation Label']['visible'] ) )
        self.controls['Full-Screen Video Label']['control'].setVisible( xbmc.getCondVisibility( self.controls['Full-Screen Video Label']['visible'] ) )
        
    def createConf( self, filename ):
        try:
            if ( not os.path.isfile( filename + '.conf' ) ):
                f = open( filename + '.conf' , 'w' )
                f.write( 'nocache=1' )
                f.close()
        except: pass

    def showVideo( self, title ):
        trailer_urls = self.trailers.get_video( self.genre, title )
        if ( self.settings['trailer size'] > len( trailer_urls ) ):
            choice = len( trailer_urls ) - 1
        else:
            choice = self.settings['trailer size']
        try:
            if ( not self.settings['download trailer'] ):
                filename = trailer_urls[choice].replace( '//', '/' ).replace( '/', '//', 1 )
                self.MyPlayer.play( filename )
            #else:
                ## don't create conf file for streaming
                #    self.createConf( filename )
        except:
            xbmc.output('ERROR: playing %s at %s' % ( title, filename, ) )

    def showTrailerInfo( self, title ):
        thumbnail, description = self.trailers.get_trailer_info( self.genre, title )
        # Trailer Thumbnail
        self.controls['Trailer Thumbnail']['control'].setImage( thumbnail )
        # Trailer Description
        self.controls['Trailer Title']['control'].setLabel( title )
        self.controls['Trailer Info']['control'].reset()
        if description:
            self.controls['Trailer Info']['control'].setText( description )

    def showTrailers( self, genre ):
        self.controls['Trailer List']['control'].reset()
        self.controls['Exclusives List']['control'].reset()
        self.controls['Newest List']['control'].reset()
        if ( genre == 'Newest' ):
            titles = self.trailers.get_newest_list()
            for title in titles: # now fill the list control
                thumbnail, description = self.trailers.get_trailer_info( genre, title )
                l = xbmcgui.ListItem( title, '', thumbnail )
                self.controls['Newest List']['control'].addItem( l )
        
        elif ( genre == 'Exclusives' ):
            titles = self.trailers.get_exclusives_list()
            for title in titles: # now fill the list control
                thumbnail, description = self.trailers.get_trailer_info( genre, title )
                l = xbmcgui.ListItem( title, '', thumbnail )
                self.controls['Exclusives List']['control'].addItem( l )
        
        elif ( genre != 'Genre' ):
            titles = self.trailers.get_trailer_list( genre )
            for title in titles: # now fill the list control
                thumbnail, description = self.trailers.get_trailer_info( genre, title )
                ## remove thumbnail from list to save memory
                l = xbmcgui.ListItem( title, '', thumbnail )
                self.controls['Trailer List']['control'].addItem( l )
    
    def showCategories( self ):
        self.controls['Genre List']['control'].reset()
        for genre in self.trailers.get_genre_list():
            l = xbmcgui.ListItem( genre )
            self.controls['Genre List']['control'].addItem( l )

    def exitScript(self):
        if ( self.Timer ): self.Timer.cancel()
        self.close()
    
    def showList( self, key ):
        self.controls['Exclusives List']['control'].setVisible( key == 'Exclusives List' )
        self.controls['Exclusives List']['control'].setEnabled( key == 'Exclusives List' )
        self.controls['Newest List']['control'].setVisible( key == 'Newest List' )
        self.controls['Newest List']['control'].setEnabled( key == 'Newest List' )
        self.controls['Genre List']['control'].setVisible( key == 'Genre List' )
        self.controls['Genre List']['control'].setEnabled( key == 'Genre List' )
        self.controls['Trailer List']['control'].setVisible( key == 'Trailer List' )
        self.controls['Trailer List']['control'].setEnabled( key == 'Trailer List' )
        ## until initial visibilty is solved just hardcode them
        #self.controls['Trailer Thumbnail']['control'].setVisible(xbmc.getCondVisibility( self.controls['Trailer Thumbnail']['visible'] ) )
        #self.controls['Trailer Title']['control'].setVisible(xbmc.getCondVisibility( self.controls['Trailer Title']['visible'] ) )
        #self.controls['Trailer Info']['control'].setVisible(xbmc.getCondVisibility( self.controls['Trailer Info']['visible'] ) )
        self.controls['Trailer Backdrop']['control'].setVisible( key != 'Genre List' )
        self.controls['Trailer Thumbnail']['control'].setVisible( key != 'Genre List' )
        self.controls['Trailer Title']['control'].setVisible( key != 'Genre List' )
        self.controls['Trailer Info']['control'].setVisible( key != 'Genre List' )
        self.controls['Trailer Info']['control'].setEnabled( key != 'Genre List' )
        self.setCategoryLabel( self.genre )    
        self.setFocus(self.controls[key]['control'])
        
    def setGenre( self, genre ):
        self.genre = genre
        self.showTrailers( genre )
        self.showList( '%s List' % (genre,) )
        
    def setGenreLabel( self, genre ):
        self.controls['Genre Label']['control'].setLabel( '<%s>' % (genre,) )
        
    def setCategoryLabel( self, category ):
        self.controls['Category Label']['control'].setLabel( category )
            
    def setListNavigation( self, button ):
        self.controls['Exclusives List']['control'].controlLeft( self.controls[button]['control'] )
        self.controls['Trailer Info']['control'].controlRight( self.controls[button]['control'] )
        
    def getTrailerInfo( self, choice ):
        title = choice.getLabel()
        self.showTrailerInfo( title )
    
    def getTrailer( self, choice ):
        title = choice.getLabel()
        self.showVideo( title )
        
    def getTrailerGenre( self, choice ):
        self.genre = choice.getLabel()
        self.showTrailers( self.genre )
        self.setGenreLabel( self.genre )
        self.setCategoryLabel( self.genre )
        self.showList( 'Trailer List' )
    
    def onControl( self, control ):
        try:
            if ( control is self.controls['Newest Button']['control'] ):
                self.setGenre( 'Newest' )
            elif ( control is self.controls['Exclusives Button']['control'] ):
                self.setGenre( 'Exclusives' )
            elif ( control is self.controls['Genre Button']['control'] ):
                self.setGenre( 'Genre' )
            elif ( control is self.controls['Genre List']['control'] ):
                self.getTrailerGenre( control.getSelectedItem() )
            elif ( control is self.controls['Exclusives List']['control'] or\
                control is self.controls['Newest List']['control'] or\
                control is self.controls['Trailer List']['control'] ):
                self.getTrailer( control.getSelectedItem() )
        except: print 'ERROR: in onControl'
            
    def onAction( self, action ):
        try:
            buttonDesc = self.controllerAction.get(action.getButtonCode(), 'n/a')
            if ( buttonDesc == 'Back Button' or buttonDesc == 'Remote Menu Button' ): self.exitScript()
            elif (buttonDesc == 'B Button' or buttonDesc == 'Remote Back Button' ):
                if ( self.genre != 'Newest' and self.genre != 'Exclusives' and self.genre != 'Genre'):
                    self.setGenre( 'Genre' )
            else:
                control = self.getFocus()
                if ( 
                        control is self.controls['Exclusives List']['control'] or
                        control is self.controls['Newest List']['control'] or
                        control is self.controls['Trailer List']['control']
                    ):
                    self.getTrailerInfo( control.getSelectedItem() )
                elif ( control is self.controls['Exclusives Button']['control'] ):
                    self.setListNavigation('Exclusives Button')
                elif ( control is self.controls['Newest Button']['control'] ):
                    self.setListNavigation('Newest Button')
                elif ( control is self.controls['Genre Button']['control'] ):
                    self.setListNavigation('Genre Button')
                elif ( control is self.controls['Settings Button']['control'] ):
                    self.setListNavigation('Settings Button')
        except: print 'ERROR: in onAction'



## Thanks Thor918 for this class ##
class MyPlayer(xbmc.Player):
    def  __init__(self, *args, **kwargs):
        if (kwargs.has_key('function')): 
            self.function = kwargs['function']
            xbmc.Player.__init__(self)
    
    def onPlayBackStopped(self):
        self.function()
    
    def onPlayBackEnded(self):
        self.function()
    
    def onPlayBackStarted(self):
        self.function()
    
