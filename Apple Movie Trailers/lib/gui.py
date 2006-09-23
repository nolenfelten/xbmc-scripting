import sys, os
import xbmc, xbmcgui
import cachedhttp_mod as cachedhttp
import trailers

fetcher = cachedhttp.CachedHTTP()
fetcher_with_dialog = cachedhttp.CachedHTTPWithProgress()

class GUI( xbmcgui.Window ):
    def __init__( self ):
        self.setupGUI()
        if ( not self.SUCCEEDED ): self.close()
        else:
            self.initVariables()
            self.setupConstants()
            self.trailers = trailers.Trailers()
            self.showCategories()

    def setupGUI(self):
        import guibuilder
        skinPath = os.path.join( os.getcwd(), 'skins' ).replace( ';', '' ) # workaround apparent xbmc bug - os.getcwd() returns an extraneous semicolon (;) at the end of the path
        self.skinPath = os.path.join( skinPath, self.getSkin( skinPath ) )
        self.imagePath = os.path.join( self.skinPath, 'gfx' )
        guibuilder.GUIBuilder( self, os.path.join( self.skinPath, 'skin.xml' ), self.imagePath, useDescAsKey=True, debug=False )

    def getSkin( self, skinPath ):
        try:
            f = open( os.path.join( skinPath, 'currentskin.txt' ) )
            skin = f.read()
            f.close()
        except:
            skin = 'Default'
        return skin

    def initVariables( self ):
        self.currentList = 0
        self.previousList = self.currentList

    def setupConstants( self ):
        self.controllerAction = {
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

    def createConf( self, filename ):
        try:
            if ( not os.path.isfile( filename + '.conf' ) ):
                f = open( filename + '.conf' , 'w' )
                f.write( 'nocache=1' )
                f.close
        except: pass

    def showVideo( self, title ):
        thumbnail, description, url = self.trailer_list[title]
        if url:
            selected_video = self.trailers.get_video( url )
            filename = fetcher_with_dialog.urlretrieve( selected_video )
            self.createConf( filename )
            if filename:
                xbmc.Player().play( filename )

    def showTrailerInfo( self, title ):
        thumbnail, description, url = self.trailer_list[title]
        if url:
            # Trailer Thumbnail
            self.controls['Trailer Thumbnail']['control'].setImage( thumbnail )
            # Trailer Description
            self.controls['Trailer Title']['control'].setLabel( title )
            self.controls['Trailer Info']['control'].reset()
            if description:
                self.controls['Trailer Info']['control'].setText( description )

    def showTrailers ( self, genre, url ):
        self.controls['Trailer List']['control'].reset()
        self.trailer_list = self.trailers.get_trailer_dict( genre, url )
        if type( self.trailer_list.values()[0] ) == str:
            dialog = xbmcgui.DialogProgress()
            header = 'Fetching movie information..'
            line1 = 'Please wait a moment.'
            errorline = ''
            dialog.create( header, line1 )
            dialog.update( 0 ) # hide the progress bar until it's needed
            position = 0 # to keep track of the position we are at in the trailer_list, for percentage computation
            percentage = 0
            for title in self.trailer_list: # fill the information first
                dialog.update( percentage, line1, 'Fetching: ' + title, errorline )
                try:
                    # get the info url (this url will not be saved after we are done here)
                    movie_info_url = self.trailer_list[title]
                    # retrieve trailer information (don't overwrite the original title value, we don't want to cause problems with indexing)
                    title2, thumbnail, description, urls = self.trailers.get_trailer_info( movie_info_url )
                    # download the actual thumbnail to the local filesystem (or get the cached filename)
                    thumbnail = fetcher.urlretrieve( thumbnail )
                    if not thumbnail:
                        # default if the actual thumbnail couldn't be found for some reason
                        thumbnail = os.path.join( self.imagePath, 'blank_thumbnail.png' )
                    # save all this info to the trailer list under this title
                    # { title: [ thumbnail, description, url ] }
                    self.trailer_list[title] = [ thumbnail, description, urls[0] ]
                except:
                    errorline = 'Error retrieving one or more titles.'
                # if the user pushed cancel, we end retrieval here
                if dialog.iscanceled():
                    break
                # update the progress dialog
                position += 1
                percentage = int( float( position ) / len( self.trailer_list ) * 100 )
                dialog.update( percentage )
        titles = self.trailer_list.keys()
        titles.sort()
        for title in titles: # now fill the list control
            l = xbmcgui.ListItem( title , '', self.trailer_list[title][0] )
            self.controls['Trailer List']['control'].addItem( l )
        dialog.close()
    
    def showCategories( self ):
        self.genre_list = {}
        self.controls['Genre List']['control'].reset()
        self.trailers.update_genre_list()
        self.genres = self.trailers.get_genre_list()
        count = 0
        for genre, url in self.genres:
            l = xbmcgui.ListItem( genre )
            self.controls['Genre List']['control'].addItem( l )
            self.genre_list[genre] = url
    
    def exitScript(self):
        self.close()
    
    def showList( self, clist ):
        self.previousList = self.currentList
        self.currentList = clist
        self.controls['Exclusives List']['control'].setVisible( clist == 0 )
        self.controls['Newest List']['control'].setVisible( clist == 1)
        # self.controls['Featured HD List']['control'].setVisible( clist == 2)
        self.controls['Genre List']['control'].setVisible( clist == 3)
        self.controls['Trailer List']['control'].setVisible( clist == 4)
        self.controls['Trailer Thumbnail']['control'].setVisible(xbmc.getCondVisibility( self.controls['Trailer Thumbnail']['visible'] ) )
        self.controls['Trailer Title']['control'].setVisible(xbmc.getCondVisibility( self.controls['Trailer Title']['visible'] ) )
        self.controls['Trailer Info']['control'].setVisible(xbmc.getCondVisibility( self.controls['Trailer Info']['visible'] ) )
    
    def onControl( self, control ):
        try:
            if ( control == self.controls['Exclusives Button']['control'] ):
                self.showList( 0 )
            elif ( control == self.controls['Newest Button']['control'] ):
                self.showList( 1 )
            # elif ( control == self.controls['Featured HD Button']['control'] ):
                # self.showList( 2 )
            elif ( control == self.controls['Genre Button']['control'] ):
                self.showList( 3 )
            elif ( control == self.controls['Genre List']['control'] ):
                selection = control.getSelectedItem()
                if selection:
                    genre = selection.getLabel()
                    url = self.genre_list[genre]
                    self.showTrailers( genre, url )
                    self.showList( 4 )
                    self.setFocus(self.controls['Trailer List']['control'])
            elif ( control == self.controls['Trailer List']['control'] ):
                selection = control.getSelectedItem()
                title = selection.getLabel()
                self.showVideo( title )
        except:
            print 'ERROR: onControl'

    def onAction( self, action ):
        buttonDesc = self.controllerAction.get(action.getButtonCode(), 'n/a')
        if ( buttonDesc == 'Back Button' ): self.exitScript()
        elif ( buttonDesc == 'B Button' ): self.showList( self.previousList )
        else:
            control = self.getFocus()
            if ( control == self.controls['Trailer List']['control'] ):
                try:
                    selection = control.getSelectedItem()
                    if selection != None:
                        title = selection.getLabel()
                        self.showTrailerInfo( title )
                except:
                    print 'ERROR: onAction'
