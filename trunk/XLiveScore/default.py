__scriptname__ = 'XLiveScore'
__author__ = 'bootsy'
__version__ = '0.0'
import xbmc, xbmcgui

dialog = xbmcgui.DialogProgress()
dialog.create(__scriptname__)
dialog.update(5, 'Importing modules & initializing...')

import sys, os
dialog.update(10)
import urllib, re
dialog.update(25)

Main_URL = 'http://www.livescore.com'
Soccer_URL = 'http://www.livescore.com/default.dll'
Worldcup_URL = 'http://www.livescore.com/worldcup.dll'
Hockey_URL = 'http://www.livescore.com/hockey.dll'
Tennis_URL = 'http://www.livescore.com/tennis.dll'

SCRIPTDIR = os.getcwd().replace(";","")+"\\"

# Gamepad constans
ACTION_MOVE_LEFT      = 1  
ACTION_MOVE_RIGHT     = 2
ACTION_MOVE_UP        = 3
ACTION_MOVE_DOWN      = 4
ACTION_PAGE_UP        = 5 
ACTION_PAGE_DOWN      = 6
ACTION_SELECT_ITEM    = 7
ACTION_HIGHLIGHT_ITEM = 8
ACTION_PARENT_DIR     = 9
ACTION_PREVIOUS_MENU  = 10
ACTION_SHOW_INFO      = 11
ACTION_PAUSE          = 12
ACTION_STOP           = 13
ACTION_NEXT_ITEM      = 14
ACTION_PREV_ITEM      = 15

KEY_BUTTON_BACK = 275
KEY_KEYBOARD_ESC = 61467

def get_SourceURL():
    data = urllib.urlopen(Soccer_URL)
    data = data.read()
    temp = ('content=["].*?[=].*?[=](.*?)["]')
    try:
            s_url = re.findall(temp, data)
            source = s_url[0]
            source_url = Main_URL + '/default.dll?page=' + source
            #print source_url
    except:
            source_url = ["unable", "to", "create", "source_url"]
    SourceURL = source_url
    return SourceURL

def get_SLatest():                                              #dont watch it, it´s just for temp stuff, isnt used in code
    source_url = get_SourceURL()
    data = urllib.urlopen(source_url)
    data = data.read()
    temp_country_a = ('class=["]title["].*?>.*?<b>(.*?)</b>.*?</td>')
    temp_league_a = ('class=["]title["].*?>.*?<b>.*?</b>(.*?)</td>')
    temp_teamL = ('<td align=["]right["] width=["]118["]>(.*?)</td>')
    temp_teamR = ('>.*?</td><td width=["]118["]>(.*?)</td></tr><tr><td')
    temp_score_a = ('["] href=["]/.*?["]>(.*?)</a></td>')                                   #just the ones with a link
    #temp_score_a = ('["]>(.*?)<')
    temp_gamelink = ('["] href=["](.*?)["]>.*?</a></td>')
    temp_countries = ('<a href=["].*?["] onmouseover=["].*?["] onmouseout=["].*?["]>(.*?)</a></td>')
    temp_countrylinks = ('<a href=["]/(.*?)["]')

    try:
            coun = re.findall(temp_country_a,data)
            country_a = "\n".join( coun[ 0 : ] )

            lea = re.findall(temp_league_a,data)
            league_a = "\n".join( lea[ 0 : ] )

            teaL = re.findall(temp_teamL,data)
            teamL = "\n".join( teaL[ 0 : ] )

            teaR = re.findall(temp_teamR,data)
            teamR = "\n".join( teaR[ 0 : ] )

            sco = re.findall(temp_score_a,data)
            score_a = "\n".join( sco[ 0 : ] )

            gal = re.findall(temp_gamelink,data)
            gamelink = "\n".join( gal[ 0 : ] )

            cou = re.findall(temp_countries,data)
            countries = "\n".join( cou[ 0 : -2 ] )

            coli = re.findall(temp_countrylinks,data)
            countrylinks = "\n".join( coli[ 6 : -5 ] )

            header = country_a + '\n' + league_a
            #header = countries + '\n' + '\n' + countrylinks
            #header = score_a
    except:
            header = 'nothing found'

    SLatest = header
    return SLatest

def get_SocCou():
    source_url = get_SourceURL()
    data = urllib.urlopen(source_url)
    data = data.read()
    temp_countries = ('<a href=["].*?["] onmouseover=["].*?["] onmouseout=["].*?["]>(.*?)</a></td>')
    try:
            cou = re.findall(temp_countries,data)
            #ountries = "\n".join( cou[ 0 : -2 ] )
            countries = cou[ 0 : -2 ]
    except:
           countries = cou["cant", "get", "SocCou()" ]
    SocCou = countries
    return SocCou

def get_SocCouLi():
    source_url = get_SourceURL()
    data = urllib.urlopen(source_url)
    data = data.read()
    temp_countrylinks = ('<a href=["]/(.*?)["]')
    try:
            coli = re.findall(temp_countrylinks,data)
            #ountrylinks = "\n".join( coli[ 6 : -5 ] )
            countrylinks = coli[ 6 : -5 ]
    except:
            countrylinks = ["cant", "get", "SocCouLi()"]
    SocCouLi = countrylinks
    return SocCouLi

def get_HomeTeams():
    source_url = get_SourceURL()
    data = urllib.urlopen(source_url)
    data = data.read()
    temp_home_teams = ('<td align=["]right["] width=["]118["]>(.*?)</td>')
    try:
            htea = re.findall(temp_home_teams,data)
            #h_teams = "\n".join( htea[ 0 : ] )
            #h_teams = str( htea[ 0 : ] )
            h_teams = htea[ 0 : ]
    except:
           h_teams = ["cant", "get", "HomeTeams"]
    HomeTeams = h_teams
    return HomeTeams

def get_AwayTeams():
    source_url = get_SourceURL()
    data = urllib.urlopen(source_url)
    data = data.read()
    temp_away_teams = ('>.*?</td><td width=["]118["]>(.*?)</td></tr><tr><td')
    try:
            atea = re.findall(temp_away_teams,data)
            #a_teams = "\n".join( atea[ 0 : ] )
            #a_teams = str( atea[ 0 : ] )
            a_teams = atea[ 0 : ]
    except:
           a_teams = ["cant", "get", "AwayTeams()"]
    AwayTeams = a_teams
    return AwayTeams

def get_Scores():
    source_url = get_SourceURL()
    data = urllib.urlopen(source_url)
    data = data.read()
    #temp_score_a = ('["] href=["]/.*?["]>(.*?)</a></td>')            #just the ones with a link
    #temp_score_a = ('["]>(.*?) - .*?</.*?')
    temp_score_a = ('["]>.*? - (.*?)</.*?')
    try:
            sco = re.findall(temp_score_a,data)
            #sco = re.match([0-40],scor)
            #score_a = "\n".join( sco[ 0 : ] )
            score_a = sco[ 0 : ]
    except:
            score_a = ["cant", "get", "Scores()"]
    Scores = score_a
    return Scores

class LiveScoreGUI( xbmcgui.WindowXML ):
    STATE_MAIN = 1
    STATE_SOCCER = 2
    STATE_WORLDCUP = 3
    STATE_HOCKEY = 4
    STATE_TENNIS = 5

    def onInit(self):
        self.getmycontrols()
        self.clearList()
        self.resetlists()
        dialog.update(30, 'Fetching teams & scores')
        myteamarray1 = get_HomeTeams()
        dialog.update(50)
        myteamarray2 = get_AwayTeams()
        dialog.update(75)
        myteamscores = ["0-5", "9-6", "10-5","10-5","9-6", "0-5", "9-6","0-5", "9-6", "0-5", "9-6", "10-5","10-5","9-6", "0-5", "9-6","0-5", "9-6", "0-5"]
        #myteamscores = get_Scores()
        dialog.update(100)
        dialog.close()
        self.buildlists(myteamarray1,myteamarray2,myteamscores)
        self.state = LiveScoreGUI.STATE_MAIN
        self.setFocus(self.A_Soccer_Button)

    def buildscorelists(self, array1):
        for i in range (0, len(array1)):
            x = array1
            #quest = ["?"]
            if x >= 0:
            #if x == quest:
                self.teamslist.addItem(xbmcgui.ListItem(array1[i]))
                #self.scorelist.addItem(array3[i])
                self.invisilist.addItem("")

    def buildcoulists(self, array1, array2):
        for i in range (0, len(array1)):
            self.teamslist.addItem(xbmcgui.ListItem(array1[i], array2[i]))
            self.invisilist.addItem("")

    def buildlists(self, array1, array2, array3):
        for i in range (0, len(array1)):
            self.teamslist.addItem(xbmcgui.ListItem(array1[i], array2[i]))
            self.scorelist.addItem(array3[i])
            self.invisilist.addItem("")
            
    def resetlists(self):
        self.teamslist.reset()
        self.scorelist.reset()
        self.invisilist.reset()

    def setvisibility(self):
        self.textarea.setVisible(False)
        self.Germany_Button.setVisible(False)

    def getmycontrols(self):
        self.List = self.getControl(50)
        self.teamslist = self.getControl(80)
        self.scorelist = self.getControl(81)
        self.invisilist = self.getControl(82)
        self.Soccer_Button = self.getControl(71)
        self.Worldcup_Button = self.getControl(72)
        self.Hockey_Button = self.getControl(73)
        self.Tennis_Button = self.getControl(74)
        self.A_Soccer_Button = self.getControl(76)
        self.A_Worldcup_Button = self.getControl(77)
        self.A_Hockey_Button = self.getControl(78)
        self.A_Tennis_Button = self.getControl(79)

    def onAction(self, action):
        #line below makes it so the lists scroll together :-D
        #xbmcgui.lock()
        self.scorelist.selectItem(self.invisilist.getSelectedPosition())
        self.teamslist.selectItem(self.invisilist.getSelectedPosition())
        #xbmcgui.unlock()
        if action == ACTION_PREVIOUS_MENU:
          #if self.state is LiveScoreGUI.STATE_MAIN:
          self.close()
          #else:
                #self.set_button_state(LiveScoreGUI.STATE_MAIN)

    def onClick(self, controlID):
        if ( controlID == 71):
            # Soccer Button
            self.clearList()
            self.resetlists()
            dialog.create(__scriptname__)
            dialog.update(5, 'Fetching countries & countrylinks')
            mycouarray1 = get_SocCou()
            dialog.update(50)
            mycouliarray2 = get_SocCouLi()
            dialog.update(100)
            dialog.close()
            self.buildcoulists(mycouarray1,mycouliarray2)

        elif ( controlID == 72):
            #self.set_button_state(LiveScoreGUI.STATE_WORLDCUP)
            self.clearList()
            self.resetlists()
            dialog.create(__scriptname__)
            dialog.update(5, 'Fetching scores')
            scoresarray = get_Scores()
            dialog.update(100)
            dialog.close()
            self.buildscorelists(scoresarray)
            
        #elif ( controlID == 73):
            #self.set_button_state(LiveScoreGUI.STATE_HOCKEY)
        #elif ( controlID == 74):
            #self.set_button_state(LiveScoreGUI.STATE_TENNIS)
        elif ( controlID == 76):
            #Latest Soccer Button
            self.clearList()
            self.resetlists()
            dialog.create(__scriptname__)
            dialog.update(5, 'Fetching teams & scores')
            myteamarray1 = get_HomeTeams()
            dialog.update(35)
            myteamarray2 = get_AwayTeams()
            dialog.update(68)
            #myteamscores = ["0-5", "9-6", "10-5","10-5","9-6", "0-5", "9-6","0-5", "9-6", "0-5", "9-6", "10-5","10-5","9-6", "0-5", "9-6","0-5", "9-6", "0-5"]
            myteamscores = get_Scores()
            dialog.update(100)
            dialog.close()
            self.buildlists(myteamarray1,myteamarray2,myteamscores)

        #elif ( controlID == 77):
            #self.set_button_state(LiveScoreGUI.STATE_HOCKEY)
        #elif ( controlID == 78):
            #self.set_button_state(LiveScoreGUI.STATE_TENNIS)
        #elif ( controlID == 79):
            #self.set_button_state(LiveScoreGUI.STATE_WORLDCUP)
        #pass

    def onFocus(self, controlID):
        #This has to be here even if empty!
        pass

    def set_button_state(self, state):
        xbmcgui.lock()
        visible = bool(state & XLiveScoreGUI.STATE_MAIN)
        self.Soccer_Button.setVisible(visible)
        self.Worldcup_Button.setVisible(visible)
        self.Hockey_Button.setVisible(visible)
        self.Tennis_Button.setVisible(visible)
        if visible:
              dominant = self.Tennis_Button
        self.setFocus(dominant)
        self.state = state
        xbmcgui.unlock()
    
ls = LiveScoreGUI("XLiveScore_Main.xml",SCRIPTDIR,"DefaultSkin")
ls.doModal()
del ls
