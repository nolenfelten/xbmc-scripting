import urllib2, urlparse, xml.dom.minidom, os
import cachedhttp_mod as cachedhttp
from debug import *
from installer import *

from config import *

sites = {
    0 : ( 'xbmcskins_net', 'http://xbmcskins.net/rss' ),
    1 : ( 'allxboxskins', 'http://www.allxboxskins.com/rssxbmc.xml' ),
    # 2 : ( 'xbox_skins_net', 'http://www.xbox-skins.net/rss/XBMC/dash/XBMC.php' ), # disabled until they fix their rss feed - i'm not about to parse that nasty html they have
}

fetcher = cachedhttp.CachedHTTPWithProgress()

class Skin:
    def __init__( self, itemTag ):
        self.title = str( itemTag.getElementsByTagName('title').item(0).childNodes[0].data ).strip()
        self.link = self.formatURL( str( itemTag.getElementsByTagName('link').item(0).childNodes[0].data ).strip() )
        self.thumb_url = self.formatURL( str( itemTag.getElementsByTagName('thumb').item(0).childNodes[0].data ).strip() )
    def formatURL( self, url ):
        formatted = url
        formatted = formatted.replace( ' ', '%20' )
        return formatted
    def getThumb( self, default ):
        thumbnail = default
        newthumbnail = fetcher.cacheFilename( self.thumb_url )
        if len( newthumbnail ): thumbnail = newthumbnail
        else:
            try:
                newthumbnail = fetcher.urlretrieve( self.thumb_url )
                if len( newthumbnail ): thumbnail = newthumbnail
            except:
                debugPrint( error, self.thumb_url )
        return thumbnail
    def __str__( self ):
        return str( self.data )

class allxboxskins_Skin(Skin):
    def __init__( self, itemTag ):
        Skin.__init__( self, itemTag )
        self.link = self.link.replace( '?app=xbmc&pv=', '?app=XBMC&cat=0&ps=&pageno=&id=' )
        self.thumb_url = self.thumb_url.replace( '_thumb', '_preview' )

class Skins:
    def __init__( self ):
        global settings
        settings = Read()
        self.raw_data = None
        self.doc = None
        self.items = []
        self.url = ''
        self.url = sites[settings['site']][1]
        self.getList()
        self.parseList()
    def getList( self ):
        try:
            if self.url != None:
                fetcher.flushCache( self.url )
                self.raw_data = fetcher.urlopen( self.url )
            else: self.raw_data = None
            if self.raw_data == None:
                debugPrint( popup, 'Couldn\'t fetch skinlist, returned empty object' )
        except:
            debugPrint( error, 'Error while fetching skinlist:' )
            pass
    def parseList( self ):
        try:
            if self.raw_data == None: return
            self.doc = xml.dom.minidom.parseString( self.raw_data )
            channel = self.doc.documentElement.getElementsByTagName('channel')
            itemlist = channel.item( channel.length-1 ).getElementsByTagName('item')
            for item in itemlist:
                global settings
                if sites[settings['site']][0] == 'allxboxskins':
                    # allxboxskins needs special handling
                    skin = allxboxskins_Skin( item )
                else: skin = Skin( item )
                self.items += [ skin ]
        except:
            debugPrint( error, 'Parsing failed:' )
            pass
