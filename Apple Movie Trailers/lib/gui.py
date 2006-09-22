import threading, time, sys, os
import xbmc, xbmcgui
import debug
import cachedhttp_mod as cachedhttp
import elementtree.ElementTree as ET

def append_ns( text ):
    BASENS = '{http://www.apple.com/itms/}'
    result = list()
    for each in text.split( '/' ):
        result += [ BASENS + each ]
    return '/'.join( result )
ns = append_ns

fetcher = cachedhttp.CachedHTTP()
fetcher_with_dialog = cachedhttp.CachedHTTPWithProgress()

class Trailers:
    def __init__( self ):
        self.BASEURL = 'http://www.apple.com'
        self.BASEXML = self.BASEURL + '/moviesxml/h/index.xml'
        self.genres = dict()

    def update_genre_list( self ):
        base_xml = fetcher.urlopen( self.BASEXML )
        base_xml = ET.fromstring( base_xml )

        self.genres = {
            'special': dict(),
            'standard': dict(),
        }
        elements = base_xml.getiterator( ns('GotoURL') )
        for each in elements:
            url = each.get( 'url' )
            name = ' '.join( url.split( '/' )[-1].split( '_' )[:-1] )
            if '/moviesxml/g' in url:
                self.genres['standard'].update( { name: url } )

        view_matrix = {
            'view1': 'Exclusives',
            'view2': 'Newest',
            'view3': 'Featured HD',
        }
        elements = base_xml.getiterator( ns('Include') )
        for each in elements:
            url = each.get( 'url' )
            for view in view_matrix:
                if view in url:
                    url = '/moviesxml/h/' + url
                    self.genres['special'].update( { view_matrix[view]: url } )    

    def get_trailer_dict( self, genre, url ):
        url = self.BASEURL + url
        #print url
        element = fetcher.urlopen( url )
        if '<Document' not in element:
            element = '<Document>' + element + '</Document>'
        element = ET.fromstring( element )
        elements = element.getiterator( ns('GotoURL') )
        trailer_dict = dict()
        for element in elements:
            url2 = element.get( 'url' )
            title = None
            if 'index_1' in url2:
                continue
            if '/moviesxml/g' in url2:
                continue
            if url2[0] != '/':
                continue
            if url2 in trailer_dict.keys():
                title = element.getiterator( ns('B') )[0].text
                trailer_dict[url2] = title
                continue
            trailer_dict.update( { url2: title } )
        #return trailer_dict
        reordered_dict = dict()
        for key in trailer_dict:
            reordered_dict.update( { trailer_dict[key]: key } )
        return reordered_dict

    def get_trailer_info( self, url ):
        url = self.BASEURL + url
        element = fetcher.urlopen( url )
        element = ET.fromstring( element )
        title = element.getiterator( ns('b') )[0].text
        thumbnail = element.getiterator( ns('PictureView') )[1].get( 'url' )
        description = element.getiterator( ns('SetFontStyle') )[2].text.strip()
        urls = list()
        for each in element.getiterator( ns('GotoURL') ):
            url = each.get( 'url' )
            if 'index_1' in url:
                continue
            if '/moviesxml/g' in url:
                continue
            if url[0] != '/':
                continue
            if url in urls:
                continue
            urls += [ url ]
        return [ title, thumbnail, description, urls ]

    def get_video( self, url ):
        url = self.BASEURL + url
        element = fetcher.urlopen( url )
        element = ET.fromstring( element )
        trailer_urls = list()
        for each in element.getiterator( ns('string') ):
            text = each.text
            if text == None:
                continue
            if 'http' not in text:
                continue
            if 'movies.apple.com' not in text:
                continue
            if text[-3:] == 'm4v':
                continue
            if text in trailer_urls:
                continue
            trailer_urls += [ text ]
        try:
            dialog = xbmcgui.Dialog()
            selection = dialog.select( 'Choose a trailer to view:', trailer_urls )
            selection = trailer_urls[selection].replace( '//', '/' ).replace( '/', '//', 1 )
            return selection
        except:
            return None

    def get_genre_list( self ):
        genre_list = dict()
        for each in self.genres:
            genre_list.update( self.genres[each] )
        genre_list = genre_list.items()
        genre_list.sort()
        return genre_list

class GUI( xbmcgui.Window ):
    def __init__( self ):
        self.setupGUI()
        if ( not self.SUCCEEDED ): self.close()
        else:
            self.setupConstants()
            self.trailers = Trailers()
            self.showCategories()

    def setupGUI(self):
        import guibuilder
        skinPath = os.path.join( os.getcwd(), 'skins' ).replace( ';', '' )
        self.skinPath = os.path.join( skinPath, self.getSkin( skinPath ) )
        self.imagePath = os.path.join( self.skinPath, 'gfx' )
        guibuilder.GUIBuilder( self, os.path.join( self.skinPath, 'skin.xml' ), self.imagePath, useDescAsKey=True, debug=False )

    def getSkin( self, skinPath ):
        try:
            f = open(os.path.join( skinPath, 'currentskin.txt' ))
            skin = f.read()
            f.close()
        except:
            skin = 'Default'
        return skin
    
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
            self.controls['Trailer Info']['control'].reset()
            if description:
                text = '\n'.join( ( title, description ) )
                self.controls['Trailer Info']['control'].setText( text )

    def showTrailers ( self, genre, url ):
        self.controls['Trailer List']['control'].reset()
        self.trailer_list = self.trailers.get_trailer_dict( genre, url )
        dialog = xbmcgui.DialogProgress()
        header = 'Fetching movie information..'
        line1 = 'Please wait a moment.'
        dialog.create( header, line1 )
        dialog.update( 0 ) # hide the progress bar until it's needed
        position = 0 # to keep track of the position we are at in the trailer_list, for percentage computation
        percentage = 0
        for title in self.trailer_list: # fill the information first
            dialog.update( percentage, header, line1, 'Fetching: ' + title )
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
            # if the user pushed cancel, we end retrieval here
            if dialog.iscanceled():
                break
            # update the progress dialog
            position += 1
            percentage = 100 / ( len( self.trailer_list ) / position )
            dialog.update( percentage )
        for title in self.trailer_list: # now fill the list control
            l = xbmcgui.ListItem( title )
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
    
    def showList( self, glist ):
        print 'showGenreList', glist
        self.controls['Exclusives List']['control'].setVisible( glist == 0 )
        self.controls['Newest List']['control'].setVisible( glist == 1)
        self.controls['Featured HD List']['control'].setVisible( glist == 2)
        self.controls['Genre List']['control'].setVisible( glist == 3)
        self.controls['Trailer List']['control'].setVisible( glist == 4)
    
    def onControl( self, control ):
        try:
            if ( control == self.controls['Exclusives Button']['control'] ):
                self.showList( 0 )
            elif ( control == self.controls['Newest Button']['control'] ):
                self.showList( 1 )
            elif ( control == self.controls['Featured HD Button']['control'] ):
                self.showList( 2 )
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
        except: print 'ERROR: onControl'
            #debug.printDebug( debug.error, 'onControl' )

    def onAction( self, action ):
        buttonDesc = self.controllerAction.get(action.getButtonCode(), 'n/a')
        if ( buttonDesc == 'Back Button' ): self.exitScript()
        else:
            control = self.getFocus()
            if ( control == self.controls['Trailer List']['control'] ):
                try:
                    selection = control.getSelectedItem()
                    #print 'Selected:', selection
                    if selection != None:
                        title = selection.getLabel()
                    #    print 'Title:', title
                        self.showTrailerInfo( title )
                    else:
                        print 'no goddamn selection?'
                except: print 'ERROR: onAction'
                    #debug.printDebug( debug.error, 'onAction' )
