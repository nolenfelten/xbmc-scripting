"""
Update module

Nuka1195
"""

import sys, os, xbmcgui, urllib, traceback
from sgmllib import SGMLParser
import XinBox_Util
import XinBox_InfoDialog

__scriptname__ = XinBox_Util.__scriptname__
__version__ = XinBox_Util.__version__
__udata__ = XinBox_Util.__settingdir__


class Parser( SGMLParser ):
    """ Parser Class: grabs all tag versions and urls """
    def reset( self ):
        self.tags = []
        self.url = None
        self.tag_found = None
        self.url_found = True
        SGMLParser.reset( self )

    def start_a( self, attrs ):
        for key, value in attrs:
            if ( key == "href" ): self.tag_found = value
    
    def handle_data( self, text ):
        if ( self.tag_found == text.replace( " ", "%20" ) ):
            self.tags.append( self.tag_found )
            self.tag_found = False
        if ( self.url_found ):
            self.url = text.replace( " ", "%20" )
            self.url_found = False
            
    def unknown_starttag( self, tag, attrs ):
        if ( tag == "h2" ):
            self.url_found = True 

class Update( xbmcgui.WindowXML):
    """ Update Class: used to update scripts from http://code.google.com/p/xbmc-scripting/ """
    def __init__(self,strXMLname, strFallbackPath,strDefaultName,bforeFallback=0,lang=False):
        self.srcpath = strFallbackPath
        self.language = lang
        self.control_action = XinBox_Util.setControllerAction()

    def onInit(self):
        self.getControl(72).setVisible(False)
        self.showing = False
        self.nonlist = []
        self.returnval = 0
        self.getControl(80).setLabel(self.language(410))
        self.getControl(81).setLabel("V." + __version__)
        self.getControl(61).setLabel(self.language(393))
        self.getControl(62).setLabel(self.language(13))
        self.base_url = XinBox_Util.__BaseURL__
        self.dialog = xbmcgui.DialogProgress()
        self._check_for_new_version()


    def onAction( self, action ):
        button_key = self.control_action.get( action.getButtonCode(), 'n/a' )
        actionID   =  action.getId()
        try:focusid = self.getFocusId()
        except:focusid = 0
        try:control = self.getFocus()
        except: control = 0
        if ( button_key == 'Keyboard ESC Button' or button_key == 'Back Button' or button_key == 'Remote Menu'):
            self.close()
        elif ( button_key == 'Keyboard Menu Button' or button_key == 'Y Button' or button_key == 'Remote Info' ):
            if focusid == 50:
                self.launchinfo(164,"")
            elif focusid == 61:
                self.launchinfo(165,"")
            elif focusid == 62:
                self.launchinfo(166,"")

    def launchinfo(self, focusid, label,heading=False):
        dialog = XinBox_InfoDialog.GUI("XinBox_InfoDialog.xml",self.srcpath,"DefaultSkin",thefocid=focusid,thelabel=label,language=self.language,theheading=heading)
        dialog.doModal()
        value = dialog.value
        del dialog
        return value
    
    def onClick(self, controlID):
        if controlID == 50:
            if self.getCurrentListPosition() in self.nonlist:
                self.getControl(62).setEnabled(False)
            else:self.getControl(62).setEnabled(True)
            self.getControl(82).setLabel("%s %s" % (self.language(396), self.versions[self.getCurrentListPosition()][ : -1 ]))
            self.setFocusId(9000)
        elif controlID == 61:
            if self.showing:
                self.getControl(72).setVisible(False)
                self.showing = False
                self.getControl(50).setVisible(True)
            else:self.showlog(self.getCurrentListPosition())
        elif controlID == 62:
            self._update_script(self.getCurrentListPosition())

    def onFocus(self, controlID):
        pass       
            
    def _check_for_new_version( self ):
        self.dialog.create( __scriptname__ + " V." + __version__, self.language(391) )
        # get version tags
        new = None
        Newer = False
        htmlsource = self._get_html_source( "%s/tags/%s" % ( self.base_url, __scriptname__.replace( " ", "%20" ), ) )
        if ( htmlsource ):
            self.versions, url = self._parse_html_source( htmlsource )
            self.url = url[ url.find( ":%20" ) + 4 : ]
            if ( self.versions ):
                new = True
                self.versions.reverse()
                for i,version in enumerate(self.versions):
                    if ( __version__ < version[ : -1 ] ):
                        Newer = True
                        if i == 0:self.addItem(xbmcgui.ListItem("%s %s %s" %(__scriptname__ ,self.language(396), version[ : -1 ]), self.language(405),"XBNewest.png","XBNewest.png"))
                        else:self.addItem(xbmcgui.ListItem("%s %s %s" %(__scriptname__ ,self.language(396), version[ : -1 ]), self.language(406),"XBnewer.png","XBnewer.png"))
                    elif ( __version__ == version[ : -1 ] ):
                        self.nonlist.append(self.getListSize())
                        self.addItem(xbmcgui.ListItem("%s %s %s" %(__scriptname__ ,self.language(396), version[ : -1 ]), self.language(407),"XBCurrent.png","XBCurrent.png"))
                    elif ( "0.3" >= version[ : -1 ] ):
                        self.nonlist.append(self.getListSize())
                        self.addItem(xbmcgui.ListItem("%s %s %s" %(__scriptname__ ,self.language(396), version[ : -1 ]), self.language(409),"XBIncompatible.png","XBIncompatible.png"))
                    else:self.addItem(xbmcgui.ListItem("%s %s %s" %(__scriptname__ ,self.language(396), version[ : -1 ]), self.language(408),"XBolder.png","XBolder.png"))           
            if Newer:
                self.getControl(83).setLabel(self.language(404))
            else:self.getControl(83).setLabel(self.language(390))
        self.dialog.close()
        if new == None or self.getListSize() == 0:
            xbmcgui.Dialog().ok( __scriptname__ + " V." + __version__, self.language(401))
            self.close()
        
                
    def _update_script( self , pos):
        """ main update function """
        try:
            if ( xbmcgui.Dialog().yesno( __scriptname__ + " V." + __version__, self.language(392) % (self.versions[pos][ : -1]))):
                self.dialog.create( __scriptname__ + " V." + __version__ + " -> V." + self.versions[pos][ : -1], self.language(394), self.language(395))
                script_files = []
                folders = ["%s/%s" % ( self.url, self.versions[pos], )]
                while folders:
                    try:
                        htmlsource = self._get_html_source( "%s%s" % ( self.base_url, folders[0] ) )
                        if ( htmlsource ):
                            items, url = self._parse_html_source( htmlsource )
                            files, dirs = self._parse_items( items )
                            url = url[ url.find( ":%20" ) + 4 : ]
                            for file in files:
                                script_files.append( "%s/%s" % ( url, file, ) )
                            for folder in dirs:
                                folders.append( "%s/%s" % ( folders[ 0 ], folder, ) )
                        else: 
                            raise
                        folders = folders[ 1 : ]
                    except:
                        folders = None
                self._get_files( script_files, self.versions[pos][ : -1 ] )
        except:
            self.dialog.close()
            xbmcgui.Dialog().ok( __scriptname__ + " V." + __version__ + " -> V." + self.versions[pos][ : -1], self.language(402))

    def showlog(self, pos):
        try:
            self.showing = True
            self.dialog.create( __scriptname__ + " V." + __version__, self.language(400))
            urllib.urlretrieve( "%s%s/%s%s" % ( self.base_url, self.url , self.versions[pos], "/Changelog.txt", ), "%s%s" % ( "X:\\", "XinBoxlog.txt", ) )
            f = open("X:\\XinBoxlog.txt")
            log = f.read()
            f.close()
            if "<!DOCTYPE HTML" in log:log = self.language(411)
            self.getControl(50).setVisible(False)
            self.getControl(72).setVisible(True)
            self.getControl(72).setText(log)
            self.dialog.close()
        except:
            self.dialog.close()
            self.getControl(72).setVisible(False)
            self.getControl(50).setVisible(True)
            self.showing = False

    def removedir(self,mydir):
        try:
            for root, dirs, files in os.walk(mydir, topdown=False):
                for name in files:
                    os.remove(os.path.join(root, name))
                for name in dirs:
                    os.rmdir(os.path.join(root, name))
            os.rmdir(mydir)
        except:pass
        
    def _get_files( self, script_files, version ):
        """ fetch the files """
        try:
            for cnt, url in enumerate( script_files ):
                items = os.path.split( url )
                path = items[ 0 ].replace( "/tags/%s/" % ( __scriptname__.replace( " ", "%20" ), ), "Q:\\scripts\\%s_v" % ( __scriptname__, ) ).replace( "/", "\\" ).replace( "%20", " " )
                file = items[ 1 ].replace( "%20", " " )
                pct = int( ( float( cnt ) / len( script_files ) ) * 100 )
                self.dialog.update( pct, "%s %s" % ( self.language(397), url, ), "%s %s" % ( self.language(398), path, ), "%s %s" % ( self.language(399), file, ) )
                if ( self.dialog.iscanceled() ): raise
                if ( not os.path.isdir( path ) ): os.makedirs( path )
                urllib.urlretrieve( "%s%s" % ( self.base_url, url, ), "%s\\%s" % ( path, file, ) )
        except:
            self.removedir("Q:\\\\scripts\\\\%s_v%s" % ( __scriptname__, version, ))
            raise
        else:
            self.dialog.close()
            if xbmcgui.Dialog().yesno( __scriptname__ + " V." + __version__ + " -> V." + version, self.language(49), self.language(403) % __version__):
                self.createpy2(version)
            else:self.createpy(version)
            self.returnval = 1
            self.close()

    def createpy(self, version):
        mylines = []
        f = open(sys.path[0] + "\\src\\lib\\XinBox_UpdateTemplate.py", "r")
        for line in f.readlines():
            if "origpath =" in line:mylines.append("origpath = " + '"' + sys.path[0].replace("\\","\\\\") + '"' + "\n")
            elif "newpath =" in line:mylines.append("newpath = " + '"' + "Q:\\\\scripts\\\\%s_v%s" % ( __scriptname__, version, ) + '"' + "\n")
            else:mylines.append(line)
        f.close
        f = open("X:\\XinBox_Update.py", "w")
        f.writelines(mylines)
        f.close()

    def createpy2(self, version):
        mylines = []
        f = open(sys.path[0] + "\\src\\lib\\XinBox_UpdateTemplate2.py", "r")
        for line in f.readlines():
            if "origver =" in line:mylines.append("origver = " + '"' + __version__ + '"' + "\n")
            elif "origpath =" in line:mylines.append("origpath = " + '"' + sys.path[0].replace("\\","\\\\") + '"' + "\n")
            elif "newpath =" in line:mylines.append("newpath = " + '"' + "Q:\\\\scripts\\\\%s_v%s" % ( __scriptname__, version, ) + '"' + "\n")
            else:mylines.append(line)
        f.close()
        f = open("X:\\XinBox_Update.py", "w")
        f.writelines(mylines)
        f.close()
               
    def _get_html_source( self, url ):
        """ fetch the SVN html source """
        try:
            sock = urllib.urlopen( url )
            htmlsource = sock.read()
            sock.close()
            return htmlsource
        except: return None

    def _parse_html_source( self, htmlsource ):
        """ parse html source for tagged version and url """
        try:
            parser = Parser()
            parser.feed( htmlsource )
            parser.close()
            return parser.tags, parser.url
        except: return None, None
            
    def _parse_items( self, items ):
        """ separates files and folders """
        folders = []
        files = []
        for item in items:
            if ( item.endswith( "/" ) ):
                folders.append( item )
            else:
                files.append( item )
        return files, folders
