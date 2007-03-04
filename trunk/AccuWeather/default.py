'''
for support: http://www.xbmc.xbox-scene.com/forum/forumdisplay.php?f=27

This script retrieves maps & radars from AccuWeather.com.

Thanks to thor918 for the MyPlayer() class.
Thanks to Phunck for the settings import functions.
Thanks to Affini for his suggestions.

Nuka1195
'''
debug = False
debugWrite = False
__line1__  = 'Setting up script:'

__scriptname__ = 'AccuWeather'
__author__ = 'Nuka1195'
__url__ = 'http://code.google.com/p/xbmc-scripting/'
__credits__ = 'XBMC TEAM, freenode/#xbmc-scripting'
__version__ = '0.9.1'

def createProgressDialog():
    global dialog, pct
    pct = 0
    dialog = xbmcgui.DialogProgress()
    dialog.create(__scriptname__)
    updateProgressDialog(__line1__, 'Importing modules & initializing...')

def updateProgressDialog(line1 = '', line2 = '', line3 = ''):
    global dialog, pct
    pct += 5
    if (line3): dialog.update(pct, line1, line2, line3)
    elif (line2): dialog.update(pct, line1, line2)
    elif (line1): dialog.update(pct, line1)
    else: dialog.update(pct)

def closeProgessDialog():
    global dialog
    dialog.close()
    
import xbmcgui, xbmc
createProgressDialog()

import threading, sys
updateProgressDialog()

import urllib, urllib2
updateProgressDialog()

import time, socket
updateProgressDialog()

import re, os
updateProgressDialog()

socket.setdefaulttimeout(15.0) #seconds

resourcesPath = os.path.join( os.getcwd().replace( ";", "" ), 'resources\\' )
sys.path.append( os.path.join( resourcesPath, 'lib' ) )
sys.path.append( os.path.join( resourcesPath, 'lib', '_xmlplus.zip' ) )
sys.path.append( os.path.join( resourcesPath, 'lib', '_PIL.zip' ) )
    
from PIL import Image
updateProgressDialog()

import configmgr, weatherparser, guibuilder
updateProgressDialog()

MapPath = os.path.join( resourcesPath, 'maps\\' )
ImagePath = os.path.join( resourcesPath, 'images' )
DefaultPath = os.path.join( resourcesPath, 'defaults\\' )

ACTION_MOVE_LEFT                             = 1
ACTION_MOVE_RIGHT                        = 2
ACTION_MOVE_UP       = 3
ACTION_MOVE_DOWN     = 4
ACTION_PARENT_DIR                        = 9
ACTION_PREVIOUS_MENU                     = 10
ACTION_WHITE_BUTTON                    = 117
ACTION_Y_BUTTON                            = 34

class GUI(xbmcgui.Window):
    def __init__(self):
        self.INITIALIZING = True
        self.initValues()
        self.gui_loaded = self.getConfigValues()
        if ( not self.gui_loaded ): self.exitScript()
        else:
            self.setDefaultMap()
            self.gui_loaded = self.setupGUI()
            closeProgessDialog()
            if (not self.gui_loaded):
                xbmcgui.Dialog().ok( __scriptname__, 'There was an error setting up your GUI.', 'Check your skin file:', os.path.join( skin_path, xml_file ))
                self.exitScript()
            else:
                if (self.LOCATION): self.getCodes()
                self.getRSSFeed()
                self.addMaps()
                self.INITIALIZING = False


    def initValues(self):
        updateProgressDialog(__line1__, 'Initializing variables...')
        self.SUCCEEDED             = False
        self.ANIMATE                 = False
        self.FORCE_REFRESH     = False
        self.TYPE                     = 0
        self.CATEGORY             = 0
        self.LEVEL                     = 0
        self.SITE                     = 0
        self.MAPFILES             = 0
        self.FRAME                 = 0
        self.MyPlayer                 = MyPlayer(function=self.playerChk)


    def setupGUI( self ):
        gb = guibuilder.GUIBuilder()
        ok = gb.create_gui( self, title=__scriptname__, line1=__line1__, dlg=dialog, pct=pct )
        return ok

    
    def getConfigValues(self):
        try:
            ############ Import settings ###########
            updateProgressDialog(__line1__, 'Importing main script settings...')
            curLocation, curURL_Location = self.getLocation()
            if ( curURL_Location != 'US' ): raise
            settings                                = configmgr.ReadSettings(resourcesPath + curURL_Location + '_CfgFile.xml')
            self.codeURL                        = settings['codeURL']
            self.worldCodeURL                = settings['worldCodeURL']
            self.metroCodeURL                = settings['metroCodeURL']
            self.localCodeURL                = settings['localCodeURL']
            self.rssCodeURL                    = settings['rssCodeURL']
            self.map_URL                        = settings['map_URL']
            self.urlCategories                    = settings['urlCategories']
            self.imageName                    = settings['imageName']
            self.category                        = settings['category']
            self.category_level                = settings['category_level']
            self.level                            = settings['level']
            self.category_type                = settings['category_type']
            self.level_type                    = settings['level_type']
            self.type_title                        = settings['type_title']
            self.type                            = settings['type']
            self.type_url                        = settings['type_url']
            self.type_options                    = settings['type_options']
            self.imageMask                    = settings['imageMask']
            self.animate                        = settings['animate']
            self.anim                            = settings['anim']
            self.large                            = settings['large']

            ############ Import default codes ###########
            updateProgressDialog(__line1__, 'Importing user default settings...')
            location = ('%s%s.xml' % (DefaultPath, curLocation.replace(' ','_').replace(',', ''),))
            if (not os.path.exists(location)): location = DefaultPath + 'default_' + curURL_Location +'.xml'
            defaults                                = configmgr.ReadSettings(location)
            self.URL_Location                 = defaults['URL_Location']
            self.defaultMap_Category        = defaults['defaultMap_Category']
            self.defaultMap_Level            = defaults['defaultMap_Level']
            self.defaultMap_Type            = defaults['defaultMap_Type']
            self.location                        = defaults['location']
            self.site                            = defaults['defaults']
            if (self.location != curLocation): self.LOCATION = curLocation
            else: self.LOCATION = None
        except:
            closeProgessDialog()
            dlg = xbmcgui.Dialog()
            if ( curURL_Location != 'US' ):
                dlg.ok(__scriptname__, "You can't use this script, it currently is only for residents in USA", "World and Canada support coming.")
            else:
                dlg.ok(__scriptname__, 'There was an error importing your settings.', 'Check your configuration files.')
            return False
        return True


    def saveDefaults(self):
        try:
            dlg = xbmcgui.DialogProgress()
            dlg.create(__scriptname__, 'Saving your cities codes...')
            dlg.update(10)
            fname = ('%s%s.xml' % (DefaultPath, self.location.replace(' ','_').replace(',', ''),))
            ##print "SAVE DEFAULTS", fname
            defaults = {}
            defaults['URL_Location']                = self.URL_Location
            defaults['defaultMap_Category']        = self.defaultMap_Category
            defaults['defaultMap_Level']            = self.defaultMap_Level
            defaults['defaultMap_Type']            = self.defaultMap_Type
            defaults['location']                        = self.location
            defaults['defaults']                        = self.site
            dlg.update(50)
            ##print defaults
            configmgr.saveDefaults(defaults, fname, 'AccuWeather.com default settings')
            dlg.update(100)
        except:
            dlg.close()
            dlg = xbmcgui.Dialog()
            dlg.ok(__scriptname__, 'There was an error saving your settings.')
        else:
            dlg.close()


    def setAsDefault(self):
        self.defaultMap_Category     = self.CATEGORY
        self.defaultMap_Level         = self.LEVEL
        self.defaultMap_Type         = self.TYPE
        self.saveDefaults()


    def getLocation(self):
        t = 0
        while t < 5:
            location = xbmc.getInfoLabel('Weather.Location').split( '(' )[ 0 ].strip()
            if location.lower() != 'busy': break
            t += 1
            xbmc.sleep(500)
        tmp = location.replace(', ', '%2C').replace(' ', '%20')
        if (tmp.split('%2C')[1].lower() == 'canada'): URL_Location = 'Canada'
        #elif (location.split('%2C')[1].lower() == 'united%20kingdom'): URL_Location = 'UK'
        elif (len(tmp.split('%2C')[1]) == 2): URL_Location = 'US'
        else: URL_Location = 'World'
        return location, URL_Location


    def searchCodes(self, location):
        if (not debug):
            request = urllib2.Request(self.codeURL + location)
            opener = urllib2.build_opener()
            usock = opener.open(request)
        else: usock = open(os.getcwd().replace( ";", "" ) + '\\codes.txt','r')
        htmlSource = usock.read()
        usock.close()
        ####################### write source for testing #######################
        if (debugWrite):
            usock = open(os.getcwd().replace( ";", "" ) + '\\codes.txt','w')
            usock.write(htmlSource)
            usock.close
        ##############################################################
        parser = weatherparser.CityParser()
        parser.feed(htmlSource)
        parser.close()
        return parser, htmlSource


    def getCodes(self):
        try:
            dlg = xbmcgui.DialogProgress()
            dlg.create(__scriptname__, 'Retrieving your cities codes...')
            dlg.update(10)
            self.location = self.LOCATION
            if (self.URL_Location == 'Canada'): location = self.LOCATION.split(', ')[0].replace(' ', '%20')
            else: location = self.LOCATION.replace(', ', '%2C').replace(' ', '%20')
            parser, htmlSource = self.searchCodes(location)
            dlg.update(50)
            #'<meta http-equiv="Set-Cookie" content="canada=1|M3H 6A7|ON|TORONTO|-5|1|YYZ|YYZ|ON|CWKR|43.75|-79.44|YYZ|;path=/;domain=.accuweather.com;expires=Tuesday, 29-Aug-06 00:00:00 GMT;"/>'
            #>WINDSOR, NS (B0N 2T0)</a>
            if (len(parser.city) == 0):
                if (self.URL_Location == 'Canada'): # let the user select
                    pattern = 'class"textmed">(.*?\([A-Z][0-9][A-Z] [0-9][A-Z][0-9]\))'
                    pattern2 = '\(([A-Z][0-9][A-Z] [0-9][A-Z][0-9])\)'
                #zipcode=EUR|DE|GM007|FRANKFURT|">Frankfurt
                if (self.URL_Location == 'World'): # let the user select
                    pattern = 'zipcode=(.*?)">.*?</a></td>'
                    pattern2 = '.*'
                #EUR|DE|GM007|FRANKFURT|">Frankfurt
#<a href="http://wwwa.accuweather.com/index-world-forecast.asp?partner=accuweather&myadc=0&amp;traveler=0&amp;zipcode=EUR|DE|GM007|FRANKFURT|">Frankfurt</a></td>
#locz=1|48161|MIMO|083|@MI|ARB|TTF|MIZ083|MIC115|5|1|41.91|-83.47|MONROE|MI|KPTK|NE|MI_||;path=/;domain=.accuweather.com;expires=Saturday, 02-Sep-06 00:00:00 GMT;">#0            1            2        3        4        5        6        7            8        910    11        12        13     14  15   16  17 18
                
                
                choices = re.findall(pattern, htmlSource)
                if (len(choices)):
                    #dlg.close()
                    dlgs = xbmcgui.Dialog()
                    choice = dlgs.select('Select your city.', choices)
                    location = re.findall(pattern2, choices[choice])[0].replace(' ','%20')
                    if (location): parser, htmlSource = self.searchCodes(location)
                    else: raise
            dlg.update(75)

            if (self.URL_Location == 'US'): # United States
                l = parser.city[0].split('|')
                # this is for us cities
                self.site[0] = 'US_'
                self.site[1] = l[16]
                self.site[2] = l[17]
                self.site[3] = l[15]
                self.site[4] = l[18]
                self.site[5] = 'NAMER'#l[4]
                self.site[6] = l[1]
                self.site[7] = l[7]
            elif (self.URL_Location == 'Canada'): # Canada
                print 'Canada'
                l = parser.city[0].split('|')
                self.site[0] = 'CNC'
                self.site[1] = l[8]
                self.site[2] = ''
                self.site[3] = l[9]
                self.site[4] = l[12]
                self.site[5] = 'NAMER'#l[4]
                self.site[6] = l[1].replace(' ','%20')
                self.site[7] = l[7]
            else: # World/ United Kingdom
                l = parser.city[0].split('|')
                self.site[0] = l[11]
                self.site[1] = l[3]
                self.site[2] = l[12]
                self.site[3] = l[13]
                self.site[4] = l[14]
                self.site[5] = l[13]
                self.site[6] = l[1]
                self.site[7] = l[7]
                print 'World'
#<meta http-equiv="Set-Cookie" content="world=3|EUROPE|GERMANY|EUR|DE|GM002|FRANKFURT|ETIN|1.00|1||EDDN|DL|EURM|DL|49.68|10.53|;path=/;domain=.accuweather.com;expires=Tuesday, 29-Aug-06 00:00:00 GMT;">
#                                                    0            1                        2                3            4        5            6                    7                                11        12        13         14        15        16                    
#<meta http-equiv="Set-Cookie" content="world=3|AFRICA            |Botswana            |AFR        |BW    |BC000|FRANCISTOWN|FBFT        |2.00         |0|    |              |BC          |AFRS        |BC      |-21.16    |27.51         |;path=/;domain=.accuweather.com;expires=Monday, 21-Aug-06 00:00:00 GMT;">
#<meta http-equiv="Set-Cookie" content="world=3|NORTH AMERICA|UNITED STATES    |NAM        |US    |MI     |DETROIT        |YQG         |-5.00    |1|    |YQG        |US_        |UN           |US_    |42.33      |-83.04        |;path=/;domain=.accuweather.com;expires=Monday, 21-Aug-06 00:00:00 GMT;">
#<meta http-equiv="Set-Cookie" content="world=3|NORTH AMERICA|Canada                |NAM        |CA    |ON      |TORONTO       |YYZ         |-5        |1|    |            |CN_        |CANM        |        |43.66    |-79.41        |;path=/;domain=.accuweather.com;expires=Monday, 21-Aug-06 00:00:00 GMT;">
#<meta http-equiv="Set-Cookie" content="world=3|NORTH AMERICA|UNITED STATES    |NAM        |US    |MI      |MONROE           |MIMO    |-5.00    |1|    |            |US_        |UN            |US_    |41.91    |-83.39        |;path=/;domain=.accuweather.com;expires=Monday, 21-Aug-06 00:00:00 GMT;">
#<meta http-equiv="Set-Cookie" content="locz=1          |48161                  |MIMO                    |083            |@MI    |ARB          |TTF                   |MIZ083    |MIC115    |5            |1            |41.91        |-83.47    |MONROE    |MI    |KPTK    |NE            |MI_|DTW|;path=/;domain=.accuweather.com;expires=Monday, 21-Aug-06 00:00:00 GMT;">
#<meta http-equiv="Set-Cookie" content="canada=1    |M3H 6A7                |ON                    |TORONTO    |-5        |1            |YYZ                |YYZ        |ON        |CWKR    |43.75        |-79.44    |YYZ        |;path=/;domain=.accuweather.com;expires=Tuesday, 22-Aug-06 00:00:00 GMT;"/>

            dlg.update(100)
        except:
            try: dlg.close()
            except: pass
            dlg = xbmcgui.Dialog()
            dlg.ok(__scriptname__, 'There was an error retrieving the codes for your city.', 'Try another city.')
        else:
            try: dlg.close()
            except: pass
            if (self.site[3] == ''): self.getOtherCodes(self.localCodeURL, 'local', 3)
            if (self.site[4] == ''): self.getOtherCodes(self.metroCodeURL, 'metro', 4)
            #self.getRSSCodes()
            self.saveDefaults()


    def getOtherCodes(self, url, msg, opt):
            try:
                dlg = xbmcgui.DialogProgress()
                dlg.create(__scriptname__, 'No %s code was found for your city.' % (msg,), 'Retrieving %s code list...' % (msg,))
                dlg.update(10)
                #source = ('%slevel=%s&type=%s&site=%s' % (self.metroCodeURL, 'metro', 're2', 'MLB',))
                # retrieve web page
                if (not debug): usock = urllib.urlopen(url)
                else: usock = open(os.getcwd().replace( ";", "" ) + '\\othercodes.txt','r')
                htmlSource = usock.read()
                usock.close()
                dlg.update(60)
                ####################### write source for testing #######################
                if (debugWrite):
                    usock = open(os.getcwd().replace( ";", "" ) + '\\othercodes.txt','w')
                    usock.write(htmlSource)
                    usock.close
                ##############################################################
                # Parse source for metro codes
                parser = weatherparser.OtherParser()
                parser.feed(htmlSource)
                parser.close()
                dlg.update(100)
            except:
                dlg.close()
                dlg = xbmcgui.Dialog()
                dlg.ok(__scriptname__, 'There was an error retrieving the %s codes.' % (msg,),\
                    'Try manually editing your defaults\\cityname.xml file.')
            else:
                dlg.close()
                dlg = xbmcgui.Dialog()
                choice = dlg.select('AccuWeather.com %s codes' % (msg,), parser.metro)
                self.site[opt] = re.findall('\(([A-Z]*)\)', parser.metro[choice])[0]


####################### Don't need for US, edit for world maybe #####################
#    def getRSSCodes(self):
#        try:
#            dlg = xbmcgui.DialogProgress()
#            dlg.create(__scriptname__, 'Retrieving county list for your state...')
#            dlg.update(10)
#            source = (self.rssCodeURL[0].replace('*STATE*', self.location[-2:]))
#            # retrieve web page
#            if (not debug):
#                request = urllib2.Request(source)
#                opener = urllib2.build_opener()
#                usock = opener.open(request)
#            else: usock = open(os.getcwd().replace( ";", "" ) +'\\alertcodes.txt','r')
#            htmlSource = usock.read()
#            usock.close()
#            dlg.update(60)
            ####################### write source for testing #######################
#            if (debugWrite):
#                usock = open(os.getcwd().replace( ";", "" ) + '\\alertcodes.txt','w')
#                usock.write(htmlSource)
#                usock.close
            ##############################################################
#            # Parse source for metro codes
#            parser = weatherparser.AlertParser()
#            parser.feed(htmlSource)
#            parser.close()

#            parser.rssFeeds.sort()
#            rssCity = []
#            rssCode = []
#            for city in parser.rssFeeds:
#                rssCity.append(city.split('/')[0])
#                rssCode.append(city.split('/')[1])
#            dlg.update(100)
    
#        except:
#            dlg.close()
#            dlg = xbmcgui.Dialog()
#            dlg.ok(__scriptname__, 'There was an error retrieving the list.',\
#                'Try manually editing your defaults\\cityname.xml file.')
#        else:
#            dlg.close()
#            dlg = xbmcgui.Dialog()
#            choice = dlg.select('AccuWeather.com - NOAA, %s county list' % (self.location[-2:],), rssCity)
#            self.site[7] = rssCode[choice]
#        self.saveDefaults()


    ####################### Maybe use for 16:9 display #####################
    def setImageWidth(self, width, designResolution, resolution):
        pixelWidthMultiplier = [1.0,1.0,0.91158472251529858619962017303229,1.215446296687064781599493564043,\
        0.91158472251529858619962017303229,1.215446296687064781599493564043,1.0940170940170940170940170940171,\
        1.4586894586894586894586894586895,0.91158472251529858619962017303229,1.215446296687064781599493564043]
        if not (resolution == designResolution):
            width = int((width * pixelWidthMultiplier[designResolution]) / pixelWidthMultiplier[resolution])
        return width


    def addMaps(self, silent = False):
        try: self.mapTimer.cancel()
        except: pass
        self.ANIMATE = False
        fpath = MapPath + self.level[self.LEVEL] + '_' + self.type[self.TYPE] + '\\'
        # Check if map already exists and is new enough
        result, mapFiles, ext, ck, refreshTime = self.checkFile(fpath)
        # If old or non-existent download new
        if (mapFiles == -1 or self.FORCE_REFRESH): 
            self.FORCE_REFRESH = False
            result, mapFiles, ext, ck = self.getMaps(result, ext, ck, silent)
        else: xbmc.sleep(600)
        try:
            xbmcgui.lock()
            for frame in range(10): self.controls[50 + frame]['control'].setVisible(False)
            
            if (result):
                for frame in range(mapFiles):
                    self.controls[50 + frame]['control'].setImage('%s%s%d%s' % (fpath, self.imageName[5], frame, ext[5],))
            else:
                self.mapFiles = 0
                self.controls[50 + self.mapFiles]['control'].setImage(ImagePath + '\\na.gif')
            self.controls[50]['control'].setVisible(True)
            
            if (ext[0] != 'n/a' and result): self.controls[200]['control'].setImage('%s%s%s' % (fpath, self.imageName[0], ext[0],))
            else: self.controls[200]['control'].setImage('')
            
            if (ext[1] != 'n/a' and result): self.controls[201]['control'].setImage('%s%s%s' % (fpath, self.imageName[1], ext[1],), ck[1])
            else: self.controls[201]['control'].setImage('')
            
            if (ext[2] != 'n/a' and result): self.controls[202]['control'].setImage('%s%s%s' % (fpath, self.imageName[2], ext[2],), ck[2])
            else: self.controls[202]['control'].setImage('')
            
            if (ext[3] != 'n/a' and result): self.controls[203]['control'].setImage('%s%s%s' % (fpath, self.imageName[3], ext[3],), ck[3])
            else: self.controls[203]['control'].setImage('')

            #Grid maybe re-enable it (only used for doppler)
            #if (ext[4] != 'n/a' and result): self.controls[204]['control'].setImage('%s%s%s' % (fpath, self.imageName[4], ext[4],), ck[4])
            #else: self.controls[204]['control'].setImage('')
            
            self.MAPFILES = mapFiles
            self.FRAME = 0
            if (mapFiles > 1 and 1&self.type_options[self.TYPE]):
                self.ANIMATE = True
                self.animateMap = animateMap(self)
            self.setButtonsStatus()
            self.CHANGING_MAP = False
            self.mapTimer = threading.Timer(refreshTime, self.addMaps,(False))
            self.mapTimer.start()

        except: print 'ERROR: Adding maps'
        xbmcgui.unlock()


    def getRSSFeed(self, silent = False):
        try: self.rssTimer.cancel()
        except: pass
        try:
            if (not silent):
                dlg = xbmcgui.DialogProgress()
                dlg.create(__scriptname__, 'Retrieving NOAA RSS feed for your county...')
                dlg.update(10)
            source = (self.rssCodeURL + self.site[7])
            # retrieve web page
            if (not debug): usock = urllib.urlopen(source)
            else: usock = open(os.getcwd().replace( ";", "" ) +'\\alertrss.txt','r')
            xmlSource = usock.read()
            usock.close()
            if (not silent): dlg.update(60)
            ####################### write source for testing #######################
            if (debugWrite):
                usock = open(os.getcwd().replace( ";", "" ) + '\\alertrss.txt','w')
                usock.write(xmlSource)
                usock.close
            ##############################################################
            
            # Parse source for descriptions
            pattern = '<description>\r?\n?[ \t]*(.*?)\r?\n?[ \t]*</description>'
            feed = re.findall(pattern, xmlSource)
    
            self.controls[20]['control'].reset()

            if (feed):
                feed[0] = feed[0] + '...'
                pattern = '&lt;br&gt;'
                pattern2 = '\$\$(.*)$'
                for description in feed:
                    description = description.replace(pattern, ' ')
                    description = re.sub(pattern2, '***', description)
                    while (len(description) > 255):
                        for i in range(247, 0, -1):
                            if (description[i]) == ' ': break
                        self.controls[20]['control'].addLabel(description[:i] + ' (cont)')
                        description = description[i + 1:]
                    self.controls[20]['control'].addLabel(description)
            if (not silent):
                dlg.update(100)
                dlg.close()
            self.rssTimer = threading.Timer((30 * 60), self.getRSSFeed,(True))
            self.rssTimer.start()
        
        except:
            if (not silent):
                dlg.close()
                dlg = xbmcgui.Dialog()
                dlg.ok(__scriptname__, 'There was an error retrieving the Alert RSS feed.')


    def getMaps(self, result, ext, ck, silent):
        if (not silent):
            dlg = xbmcgui.DialogProgress()
            dlg.create(__scriptname__, 'Downloading maps...')
            dlg.update(10)
        fpath = MapPath + self.level[self.LEVEL] + '_' + self.type[self.TYPE] + '\\'
        IMAGES = [''] * 8
        mapFiles = 0
        # Check for multiple frames
        if 1&self.type_options[self.TYPE] or 16&self.type_options[self.TYPE]: anim = 1
        else: anim = 0
        # Check for size
        if 4&self.type_options[self.TYPE]: large = 1
        else: large = 0
        # Check for multiple days.
        if (512&self.type_options[self.TYPE]): days = 3
        elif (1024&self.type_options[self.TYPE]): days = 2
        else: days = 1
        try:
            # routine to download main web page and parse for image file links
            fday = 1
            while (fday <= days):
                ##print 'ANIM',self.anim[anim]
                ##print 'large', self.large
                source = ('%s%s%s%s%s%s%s%s%s%s%d%s%d%s%d' % (self.map_URL[self.type_url[self.TYPE]],\
                self.urlCategories[0], self.site[6], self.urlCategories[1], self.level[self.LEVEL].lower(), self.urlCategories[2],\
                self.site[self.LEVEL], self.urlCategories[3], self.type[self.TYPE], self.urlCategories[4], self.large[large],\
                self.urlCategories[5], self.anim[anim], self.urlCategories[6], fday,))
                ##print source
                #print "GOT SOURCE"
                # retrieve web page
                if (not debug): usock = urllib.urlopen(source)
                else: usock = open(os.getcwd().replace( ";", "" ) + '\\url.txt','r')
                htmlSource = usock.read()
                usock.close()
                if (not silent):
                    if (dlg.iscanceled()): raise
                ####################### write source for testing #######################
                if (debugWrite):
                    usock = open(os.getcwd().replace( ";", "" ) + '\\url.txt','w')
                    usock.write(htmlSource)
                    usock.close
                ##############################################################
                # parse source for image file links
                parser = weatherparser.ImageParser()
                parser.feed(htmlSource)
                parser.close()
                if (not silent):
                    if (dlg.iscanceled()): raise
                # select only maps, legends and overlays links
                for image in parser.images:
                    # if it's the first day go ahead and find legend and overlays links
                    if (fday == 1):
                        for c in range(5):
                            if (image.lower().find(self.imageMask[c].lower()) != -1):
                                IMAGES[c] = image
                                break
                    # find map link
                    if (IMAGES[4 + fday] == ''):
                        for c in range(5, len(self.imageMask)):
                            if (image.lower().find(self.imageMask[c].lower()) != -1):
                                IMAGES[4 + fday] = image
                                break
                if (not silent):
                    if (dlg.iscanceled()): raise
                    dlg.update(int(30 / (days - (fday - 1))))
                fday += 1    
            ############################# end of while loop ###########################
            # download images if valid link found
            if (IMAGES[5] != ''):
                # if path does not exist create it
                if (not os.path.exists(fpath)):
                    os.makedirs(fpath)
                # download legend and overlays if they exist
                for url in range(5):
                    if (not silent):
                        if (dlg.iscanceled()): raise
                    if (IMAGES[url] != ''):
                        ext[url] = IMAGES[url][-4:]
                        if ((not os.path.exists(fpath + self.imageName[url] + ext[url])) or url == 0 or not result):
                            # download image
                            if (not debug):
                                loc = urllib.URLopener()
                                loc.retrieve(IMAGES[url], fpath + self.imageName[url] + ext[url])
                # download maps                
                for url in range(5,8):
                    if (not silent):
                        if (dlg.iscanceled()): raise
                    if (IMAGES[url] != ''):
                        ext[url] = IMAGES[url][-4:]
                        # if it's a jpg no conversion necessary so set the name final
                        if (ext[url] == '.gif'): x = '_'
                        else: x =''
                        # download image
                        if (not debug):
                            loc = urllib.URLopener()
                            loc.retrieve(IMAGES[url], fpath + self.imageName[5] + x + str(url - 5) + ext[url])
                    if (not silent): dlg.update(int(30 + (30 / (8 - url))))
                if (not silent):
                    if (dlg.iscanceled()): raise
                if (ext[5] == '.gif'): mapFiles = self.parseWeatherGIF(fpath, ext)
                else: mapFiles = fday - 1
                if (not silent): dlg.update(80)
                ext, ck = self.convertOverlays(result, fpath, ext, ck)
                self.writeCheckFile(fpath, ext, mapFiles, ck)
            if (not silent): dlg.update(100)
        except:
            if (not silent):
                dlg.close()
                if (not dlg.iscanceled()):
                    dlg = xbmcgui.Dialog()
                    dlg.ok(__scriptname__, 'There was an error downloading the map.', source[0:60], source[60:120])
            return False, 0, ext, ck
        else:
            if (not silent): dlg.close()
            return True, mapFiles, ext, ck


    # needed for colorkey to work
    def convertOverlays(self, result, fpath, ext, ck):
        try:
            for i in range(1, 5):
                if (ext[i] != 'n/a'):
                    if ((not os.path.exists(fpath + self.imageName[i] + '.png')) or (not result)):
                        tmp = Image.open(fpath + self.imageName[i] + ext[i]).convert('RGB')
                        ck[i] = ('0xFF%02x%02x%02x' % max(tmp.getcolors())[1])
                        tmp.save(fpath + self.imageName[i] + '.png')
                    ext[i] = '.png'
        except: pass
        return ext, ck


    def parseWeatherGIF(self, fpath, ext):
        mapFiles = 1
        for c in range(5,8):
            try:
                image = Image.open(fpath + self.imageName[5] + '_' + str(c - 5) + ext[c])
                # if the image needs cropping
                if (32&self.type_options[self.TYPE]):
                    # get overlay size to crop weather.gif
                    im = Image.open(fpath + self.imageName[1] + ext[1])
                    oSize = im.size
                    mSize = image.size
                    ext[0] = ext[5]
                    # crop legend
                    im = image.crop((0,oSize[1],mSize[0],mSize[1],)).save(fpath + self.imageName[0] + ext[0])
                # parse and save individual frames of gif
                while 1:
                    if (32&self.type_options[self.TYPE]): im = image.crop((0,0,mSize[0],oSize[1],))\
                        .save('%s%s%d%s' % (fpath, self.imageName[5], image.tell() + (c - 5), ext[5],))
                    else: image.save('%s%s%d%s' % (fpath, self.imageName[5], image.tell() + (c - 5), ext[5],))
                    mapFiles = image.tell() + (c - 4)
                    image.seek(image.tell() + 1)
            except: pass
        return mapFiles


    def writeCheckFile(self, fpath, ext, mapFiles, ck):
        try:
            f = open(fpath + 'chkfile.txt', 'w')
            s = ('%s|%d|%s|%s|%s|%s|%s|%s|%s|%s|%s|%f|%s|%s|%s|%s|%s' % (self.site[self.LEVEL], mapFiles, ext[0],\
            ext[1], ext[2], ext[3], ext[4], ext[5], ext[6],ext[7], 'not used',time.time(),ck[0], ck[1], ck[2], ck[3], ck[4],))
            f.write(s)
        except: print "ERROR SAVING CHK FILE"
        f.close()


    def checkFile(self, fpath):
        if 64&self.type_options[self.TYPE]: refreshTime = 15
        elif 128&self.type_options[self.TYPE]: refreshTime = 30
        elif 256&self.type_options[self.TYPE]: refreshTime = 60
        else: refreshTime = 120            
        c = ''
        status = False
        mf = -1
        ext = ['n/a'] * 8
        ck = [0] * 5
        REFRESH_TIME = refreshTime * 60
        try:
            f = open(fpath + 'chkfile.txt', 'r')
            l = f.read().split('|')
            f.close()
            ext = [l[2], l[3], l[4], l[5], l[6], l[7], l[8], l[9]]
            ck = [l[12], l[13], l[14], l[15], l[16]]
            if (l[0] == self.site[self.LEVEL]):
                status = True
                now = time.time()
                fTime = float(l[11])
                tDiff = now - fTime
                if (tDiff < (refreshTime * 60)): 
                    mf = int(l[1])
                    REFRESH_TIME = int((refreshTime * 60) - tDiff)
        except: pass
        return status, mf, ext, ck, REFRESH_TIME


    def setDefaultMap(self):
        self.CATEGORY    = self.defaultMap_Category
        self.LEVEL            = self.defaultMap_Level
        self.TYPE            = self.defaultMap_Type


    def switchCategory(self, x):
        self.CATEGORY += x
        if (self.CATEGORY < 0): self.CATEGORY = len(self.category) - 1
        elif (self.CATEGORY == len(self.category)): self.CATEGORY = 0
        self.setLevelStatus()
        self.setTypeStatus()
        self.setButtonsStatus()


    def setLevelStatus(self):
        # change level if it is not in category
        if ((2**self.LEVEL)&self.category_level[self.CATEGORY] == 0):
            for self.LEVEL in range(len(self.level)):
                if ((2**self.LEVEL)&self.category_level[self.CATEGORY]): break


    def switchLevel(self, x):
        while 1:
            self.LEVEL += x
            if (self.LEVEL < 0): self.LEVEL = len(self.level) - 1
            elif (self.LEVEL == len(self.level)): self.LEVEL = 0
            if ((2**self.LEVEL)&self.category_level[self.CATEGORY]): break
        self.setTypeStatus()
        self.setButtonsStatus()


    def setTypeStatus(self):
        # change type if it is not in category and level
        if ((2**self.TYPE)&self.category_type[self.CATEGORY] == 0 or (2**self.TYPE)&self.level_type[self.LEVEL] == 0):
            for self.TYPE in range(len(self.type)):
                if ((2**self.TYPE)&self.category_type[self.CATEGORY] and (2**self.TYPE)&self.level_type[self.LEVEL]): break


    def switchType(self, x):
        while 1:
            self.TYPE += x
            if (self.TYPE < 0): self.TYPE = len(self.type_title) - 1
            elif (self.TYPE == len(self.type_title)): self.TYPE = 0
            if ((2**self.TYPE)&self.category_type[self.CATEGORY] and (2**self.TYPE)&self.level_type[self.LEVEL]): break
        self.setButtonsStatus()


    def switchAnimate(self):
        self.ANIMATE = not self.ANIMATE
        self.setButtonsStatus()
        if (self.ANIMATE): self.animateMap = animateMap(self)


    def switchFrame(self, x):
        tmpFrame = self.FRAME
        self.FRAME += x
        if (self.FRAME < 0): self.FRAME = self.MAPFILES - 1
        elif (self.FRAME == self.MAPFILES): self.FRAME = 0
        self.controls[50 + self.FRAME]['control'].setVisible(True)
        self.controls[50 + tmpFrame]['control'].setVisible(False)
        self.setButton4()


    def setButtonsStatus(self):
        self.controls[10]['control'].setLabel(self.category[self.CATEGORY])
        self.controls[11]['control'].setLabel(self.level[self.LEVEL])
        self.controls[12]['control'].setLabel(self.type_title[self.TYPE])
        self.controls[13]['control'].setLabel(self.animate[self.ANIMATE])
        self.controls[13]['control'].setEnabled(self.MAPFILES > 1)
        self.setButton4()


    def setButton4(self):
        self.controls[14]['control'].setLabel('Frame:  (%d/%d)' % (self.FRAME + (1 * (self.MAPFILES > 0)),self.MAPFILES,))
        self.controls[14]['control'].setEnabled(self.MAPFILES > 1 and not self.ANIMATE)


    def refreshMap(self):
        self.FORCE_REFRESH = True
        self.addMaps()


    def playerChk(self):
        try:
            self.controls[300]['control'].setVisible(xbmc.getCondVisibility(self.controls[300]['visible']))
            self.controls[301]['control'].setVisible(xbmc.getCondVisibility(self.controls[301]['visible']))
            self.controls[302]['control'].setVisible(xbmc.getCondVisibility(self.controls[302]['visible']))
            self.controls[303]['control'].setVisible(xbmc.getCondVisibility(self.controls[303]['visible']))
        except: pass

    def exitScript(self):
        self.ANIMATE = False
        try: self.mapTimer.cancel()
        except: pass
        try: self.rssTimer.cancel()
        except: pass
        for thread in threading.enumerate():
            if (thread.isAlive() and thread != threading.currentThread()):
                thread.join(1)
        self.close()


    def displayArrows( self, button ):
        xbmcgui.lock()
        try:
            if ( button ):
                left_x = self.controls[100]['control'].getPosition()[ 0 ]
                right_x = self.controls[101]['control'].getPosition()[ 0 ]
                y = self.controls[ button ][ 'control' ].getPosition()[1]
                y += int( ( self.controls[ button ][ 'control' ].getHeight() - self.controls[ 100 ][ 'control' ].getHeight() ) / 2)
                self.controls[100]['control'].setPosition( left_x, y )
                self.controls[101]['control'].setPosition( right_x, y )
            self.controls[100]['control'].setVisible( button )
            self.controls[101]['control'].setVisible( button )
        except: pass
        xbmcgui.unlock()
        
        
    def onAction(self, action):
        if (action == ACTION_PARENT_DIR or action == ACTION_PREVIOUS_MENU): self.exitScript()
        elif (action == ACTION_WHITE_BUTTON or action == ACTION_Y_BUTTON): self.refreshMap()
        elif (action == ACTION_MOVE_LEFT or action == ACTION_MOVE_RIGHT):
            c = self.getFocus()
            x = (-(ACTION_MOVE_LEFT) + ((action == ACTION_MOVE_RIGHT) * 2))
            if (c == self.controls[10]['control']): self.switchCategory(x)
            elif (c == self.controls[11]['control']): self.switchLevel(x)
            elif (c == self.controls[12]['control']): self.switchType(x)
            elif (c == self.controls[13]['control']): self.switchAnimate()
            elif (c == self.controls[14]['control']): self.switchFrame(x)
        elif (action == ACTION_MOVE_UP or action == ACTION_MOVE_DOWN):
            c = self.getFocus()
            if (c == self.controls[10]['control']): self.displayArrows( 10 )#exec self.controls[10]['onfocus']
            elif (c == self.controls[11]['control']): self.displayArrows( 11 )#exec self.controls[11]['onfocus']
            elif (c == self.controls[12]['control']): self.displayArrows( 12 )#exec self.controls[12]['onfocus']
            elif (c == self.controls[13]['control']): self.displayArrows( 13 )#exec self.controls[13]['onfocus']
            elif (c == self.controls[14]['control']): self.displayArrows( 14 )#exec self.controls[14]['onfocus']
            elif (c == self.controls[15]['control']): self.displayArrows( False )#exec self.controls[15]['onfocus']


    def onControl(self, control):
        if (not self.INITIALIZING):
            if (control == self.controls[10]['control'] or control == self.controls[11]['control'] or control == self.controls[12]['control']): self.addMaps()
            elif (control == self.controls[13]['control']): self.switchAnimate()
            elif (control == self.controls[14]['control']): self.switchFrame(1)
            elif (control == self.controls[15]['control']): self.setAsDefault()



class animateMap(threading.Thread):
    def __init__(self, win):
        threading.Thread.__init__(self)
        self.win = win
        self.start()
    
    def run(self):
        while (self.win.ANIMATE):
            self.win.switchFrame(1)
            if (not self.win.ANIMATE): break
            xbmc.sleep(300 + (1200 * (self.win.FRAME == (self.win.MAPFILES - 1))))



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
    

if ( __name__ == "__main__" ):
    ui = GUI()
    if ( ui.gui_loaded ): ui.doModal()
    del ui
