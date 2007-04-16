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

def get_SoccerURL():
    data = urllib.urlopen(Soccer_URL)
    data = data.read()
    temp_s_url = ('content=["].*?[=].*?[=](.*?)["]')
    try:
            s_url = re.findall(temp_s_url, data)
            soccer = s_url[0]
            soccer_url = Main_URL + '/default.dll?page=' + soccer
            #print soccer_url
    except:
            soccer_url = ["unable", "to", "create", "soccer_url"]
    SoccerURL = soccer_url
    return SoccerURL

def get_WorldCupURL():
    data = urllib.urlopen(Worldcup_URL)
    data = data.read()
    temp_wc_url = ('content=["].*?[=].*?[=](.*?)["]')
    try:
            wc_url = re.findall(temp_wc_url, data)
            worldcup = wc_url[0]
            worldcup_url = Main_URL + '/worldcup.dll?page=' + worldcup
            #print worldcup_url
    except:
            worldcup_url = ["unable", "to", "create", "worldcup_url"]
    WorldCupURL = worldcup_url
    return WorldCupURL

def get_HockeyURL():
    data = urllib.urlopen(Hockey_URL)
    data = data.read()
    temp_ho_url = ('content=["].*?[=].*?[=](.*?)["]')
    try:
            ho_url = re.findall(temp_ho_url, data)
            hockey = ho_url[0]
            hockey_url = Main_URL + '/hockey.dll?page=' + hockey
            #print hockey_url
    except:
            hockey_url = ["unable", "to", "create", "hockey_url"]
    HockeyURL = hockey_url
    return HockeyURL

def get_TennisURL():
    data = urllib.urlopen(Tennis_URL)
    data = data.read()
    temp_te_url = ('content=["].*?[=].*?[=](.*?)["]')
    try:
            te_url = re.findall(temp_te_url, data)
            tennis = te_url[0]
            tennis_url = Main_URL + '/tennis.dll?page=' + tennis
            #print tennis_url
    except:
            tennis_url = ["unable", "to", "create", "tennis_url"]
    TennisURL = tennis_url
    return TennisURL

def get_SLatest():
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

def get_Ho_Gr():
    ho_url = get_HockeyURL()
    data = urllib.urlopen(ho_url)
    data = data.read()
    temp_ho_groups = ('<a href=["].*?["] onmouseover=["].*?["] onmouseout=["].*?["]>(.*?)</a></td>')
    try:
        grou = re.findall(temp_ho_groups,data)
        groups = grou[ 2 : ]
    except:
        groups = ["cant", "get", "Hockey", "Groups"]

    Ho_Gr_text = open('Q:\\scripts\\XLiveScore\\txt\\ho_groups.txt', 'w')
    for items in groups:
        Ho_Gr_text.write(items + '|')
    Ho_Gr_text.close()

    Ho_Gr = groups
    return Ho_Gr

def get_Ho_GrLi():
    ho_url = get_HockeyURL()
    data = urllib.urlopen(ho_url)
    data = data.read()
    temp_ho_grouplinks = ('<a href=["]/(.*?)["]')
    try:
        grli = re.findall(temp_ho_grouplinks,data)
        grouplinks = grli[ 8 : ]
    except:
        grouplinks = ["cant", "get", "Hockey", "GroupLinks"]

    Ho_GrLi_text = open('Q:\\scripts\\XLiveScore\\txt\\ho_grli.txt', 'w')
    for items in grouplinks:
        Ho_GrLi_text.write(items + '|')
    Ho_GrLi_text.close()

    Ho_GrLi = grouplinks
    return Ho_GrLi

def get_Te_Gr():
    te_url = get_TennisURL()
    data = urllib.urlopen(te_url)
    data = data.read()
    temp_te_groups = ('<a href=["].*?["] onmouseover=["].*?["] onmouseout=["].*?["]>(.*?)</a></td>')
    try:
        grou = re.findall(temp_te_groups,data)
        groups = grou[ 2 : ]
    except:
        groups = ["cant", "get", "Tennis", "Groups"]

    Te_Gr_text = open('Q:\\scripts\\XLiveScore\\txt\\te_groups.txt', 'w')
    for items in groups:
        Te_Gr_text.write(items + '|')
    Te_Gr_text.close()

    Te_Gr = groups
    return Te_Gr

def get_Te_GrLi():
    te_url = get_TennisURL()
    data = urllib.urlopen(te_url)
    data = data.read()
    temp_te_grouplinks = ('<a href=["]/(.*?)["]')
    try:
        grli = re.findall(temp_te_grouplinks,data)
        grouplinks = grli[ 8 : ]
    except:
        grouplinks = ["cant", "get", "Tennis", "GroupLinks"]

    Te_GrLi_text = open('Q:\\scripts\\XLiveScore\\txt\\te_grli.txt', 'w')
    for items in grouplinks:
        Te_GrLi_text.write(items + '|')
    Te_GrLi_text.close()

    Te_GrLi = grouplinks
    return Te_GrLi

def get_WC_Gr():
    wc_url = get_WorldCupURL()
    data = urllib.urlopen(wc_url)
    data = data.read()
    temp_wc_groups = ('<a href=["].*?["] onmouseover=["].*?["] onmouseout=["].*?["]>(.*?)</a></td>')
    try:
        grou = re.findall(temp_wc_groups,data)
        groups = grou[ 2 : ]
    except:
        groups = ["cant", "get", "WorldCup", "Groups"]

    WC_Gr_text = open('Q:\\scripts\\XLiveScore\\txt\\wc_groups.txt', 'w')
    for items in groups:
        WC_Gr_text.write(items + '|')
    WC_Gr_text.close()

    WC_Gr = groups
    return WC_Gr

def get_WC_GrLi():
    wc_url = get_WorldCupURL()
    data = urllib.urlopen(wc_url)
    data = data.read()
    temp_wc_grouplinks = ('<a href=["]/(.*?)["]')
    try:
        grli = re.findall(temp_wc_grouplinks,data)
        grouplinks = grli[ 8 : ]
    except:
        grouplinks = ["cant", "get", "WorldCup", "GroupLinks"]

    WC_GrLi_text = open('Q:\\scripts\\XLiveScore\\txt\\wc_grli.txt', 'w')
    for items in grouplinks:
        WC_GrLi_text.write(items + '|')
    WC_GrLi_text.close()

    WC_GrLi = grouplinks
    return WC_GrLi

def get_SocCou():
    s_url = get_SoccerURL()
    data = urllib.urlopen(s_url)
    data = data.read()
    temp_countries = ('<a href=["].*?["] onmouseover=["].*?["] onmouseout=["].*?["]>(.*?)</a></td>')
    try:
        cou = re.findall(temp_countries,data)
        #countries = "\n".join( cou[ 0 : -2 ] )
        countries = cou[ 0 : -2 ]
    except:
        countries = ["cant", "get", "SocCou()"]

    SocCou_text = open('Q:\\scripts\\XLiveScore\\txt\\s_cou.txt', 'w')
    for items in countries:
        SocCou_text.write(items + '|')
    SocCou_text.close()

    SocCou = countries
    return SocCou

def get_SocCouLi():
    s_url = get_SoccerURL()
    data = urllib.urlopen(s_url)
    data = data.read()
    temp_countrylinks = ('<a href=["]/(.*?)["]')
    try:
        coli = re.findall(temp_countrylinks,data)
        #ountrylinks = "\n".join( coli[ 6 : -5 ] )
        countrylinks = coli[ 6 : -5 ]
    except:
        countrylinks = ["cant", "get", "SocCouLi()"]

    SocCouLi_text = open('Q:\\scripts\\XLiveScore\\txt\\s_couli.txt', 'w')
    for items in countrylinks:
        SocCouLi_text.write(items + '|')
    SocCouLi_text.close()

    SocCouLi = countrylinks
    return SocCouLi

def get_HomeTeams():
    s_url = get_SoccerURL()
    data = urllib.urlopen(s_url)
    data = data.read()
    temp_home_teams = ('<td align=["]right["] width=["]118["]>(.*?)</td>')
    try:
        htea = re.findall(temp_home_teams,data)
        #h_teams = "\n".join( htea[ 0 : ] )
        #h_teams = str( htea[ 0 : ] )
        h_teams = htea[ 0 : ]
    except:
        h_teams = ["cant", "get", "HomeTeams"]
    HT_text = open('Q:\\scripts\\XLiveScore\\txt\\s_ht.txt', 'w')
    for items in h_teams:
        HT_text.write(items + '|')
    HT_text.close()

    HomeTeams = h_teams
    return HomeTeams

def get_AwayTeams():
    s_url = get_SoccerURL()
    data = urllib.urlopen(s_url)
    data = data.read()
    temp_away_teams = ('>.*?</td><td width=["]118["]>(.*?)</td></tr><tr><td')
    try:
        atea = re.findall(temp_away_teams,data)
        #a_teams = "\n".join( atea[ 0 : ] )
        #a_teams = str( atea[ 0 : ] )
        a_teams = atea[ 0 : ]
    except:
        a_teams = ["cant", "get", "AwayTeams()"]

    AT_text = open('Q:\\scripts\\XLiveScore\\txt\\s_at.txt', 'w')
    for items in a_teams:
        AT_text.write(items + '|')
    AT_text.close()

    AwayTeams = a_teams
    return AwayTeams

def get_Scores():
    s_url = get_SoccerURL()
    data = urllib.urlopen(s_url)
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

    Scores_text = open('Q:\\scripts\\XLiveScore\\txt\\s_scores.txt', 'w')
    for items in score_a:
        Scores_text.write(items + '|')
    Scores_text.close()

    Scores = score_a
    return Scores

def get_Ho_GrLi_text():
    GrLi_text = open('Q:\\scripts\\XLiveScore\\txt\\ho_grli.txt', 'r')
    grlinksarray = GrLi_text.read().split("|")
    grlinksarray.pop()
    GrLi_text.close()
    GrLi_array = grlinksarray
    return GrLi_array

def get_Ho_Gr_text():
    Gr_text = open('Q:\\scripts\\XLiveScore\\txt\\ho_groups.txt', 'r')
    groupsarray = Gr_text.read().split("|")
    groupsarray.pop()
    Gr_text.close()
    Gr_array = groupsarray
    return Gr_array

def get_Te_GrLi_text():
    GrLi_text = open('Q:\\scripts\\XLiveScore\\txt\\te_grli.txt', 'r')
    grlinksarray = GrLi_text.read().split("|")
    grlinksarray.pop()
    GrLi_text.close()
    GrLi_array = grlinksarray
    return GrLi_array

def get_Te_Gr_text():
    Gr_text = open('Q:\\scripts\\XLiveScore\\txt\\te_groups.txt', 'r')
    groupsarray = Gr_text.read().split("|")
    groupsarray.pop()
    Gr_text.close()
    Gr_array = groupsarray
    return Gr_array

def get_WC_GrLi_text():
    GrLi_text = open('Q:\\scripts\\XLiveScore\\txt\\wc_grli.txt', 'r')
    grlinksarray = GrLi_text.read().split("|")
    grlinksarray.pop()
    GrLi_text.close()
    GrLi_array = grlinksarray
    return GrLi_array

def get_WC_Gr_text():
    Gr_text = open('Q:\\scripts\\XLiveScore\\txt\\wc_groups.txt', 'r')
    groupsarray = Gr_text.read().split("|")
    groupsarray.pop()
    Gr_text.close()
    Gr_array = groupsarray
    return Gr_array

def get_CouLi_text():
    CouLi_text = open('Q:\\scripts\\XLiveScore\\txt\\s_couli.txt', 'r')
    coulinksarray = CouLi_text.read().split("|")
    coulinksarray.pop()
    CouLi_text.close()
    CouLi_array = coulinksarray
    return CouLi_array

def get_Cou_text():
    Cou_text = open('Q:\\scripts\\XLiveScore\\txt\\s_cou.txt', 'r')
    countriesarray = Cou_text.read().split("|")
    countriesarray.pop()
    Cou_text.close()
    Cou_array = countriesarray
    return Cou_array

def get_Scores_text():
    Scores_text = open('Q:\\scripts\\XLiveScore\\txt\\s_scores.txt', 'r')
    scoresarray = Scores_text.read().split("|")
    scoresarray.pop()
    Scores_text.close()
    Scores_array = scoresarray
    return Scores_array

def get_AT_text():
    AT_text = open('Q:\\scripts\\XLiveScore\\txt\\s_at.txt', 'r')
    awayteamsarray = AT_text.read().split("|")
    awayteamsarray.pop()
    AT_text.close()
    AT_array = awayteamsarray
    return AT_array

def get_HT_text():
    HT_text = open('Q:\\scripts\\XLiveScore\\txt\\s_ht.txt', 'r')
    hometeamsarray = HT_text.read().split("|")
    hometeamsarray.pop()
    HT_text.close()
    HT_array = hometeamsarray
    return HT_array

class LiveScoreGUI( xbmcgui.WindowXML ):
    STATE_MAIN = 1
    STATE_SOCCER = 2
    STATE_WORLDCUP = 3
    STATE_HOCKEY = 4
    STATE_TENNIS = 5

    def onInit(self):
        self.getmycontrols()
        self.resetlists()
        dialog.update(30, 'Fetching Soccer Teams & Scores')
        try:
            hometeamsarray = get_HomeTeams()
        except:
            hometeamsarray = ["cant", "get", "hometeams"]
        dialog.update(50)
        try:
            awayteamsarray = get_AwayTeams()
        except:
            awayteamsarray = ["cant", "get", "awayteams"]
        dialog.update(75)
        try:
            #scoresarray = ["0-5", "9-6", "10-5","10-5","9-6", "0-5", "9-6","0-5", "9-6", "0-5", "9-6", "10-5","10-5","9-6", "0-5", "9-6","0-5", "9-6", "0-5"]
            scoresarray = get_Scores()
        except:
            scoresarray = ["cant", "get", "scores"]
        dialog.update(100)
        dialog.close()
        self.buildlists(hometeamsarray,awayteamsarray,scoresarray)
        self.setFocus(self.Latest_Soccer)
        #self.state = LiveScoreGUI.STATE_MAIN

    def removetxt(self):
        if os.path.isfile('Q:\\scripts\\XLiveScore\\txt\\ho_groups.txt') == True:
            os.remove('Q:\\scripts\\XLiveScore\\txt\\ho_groups.txt')
        if os.path.isfile('Q:\\scripts\\XLiveScore\\txt\\ho_grli.txt') == True:
            os.remove('Q:\\scripts\\XLiveScore\\txt\\ho_grli.txt')
        if os.path.isfile('Q:\\scripts\\XLiveScore\\txt\\te_groups.txt') == True:
            os.remove('Q:\\scripts\\XLiveScore\\txt\\te_groups.txt')
        if os.path.isfile('Q:\\scripts\\XLiveScore\\txt\\te_grli.txt') == True:
            os.remove('Q:\\scripts\\XLiveScore\\txt\\te_grli.txt')
        if os.path.isfile('Q:\\scripts\\XLiveScore\\txt\\wc_groups.txt') == True:
            os.remove('Q:\\scripts\\XLiveScore\\txt\\wc_groups.txt')
        if os.path.isfile('Q:\\scripts\\XLiveScore\\txt\\wc_grli.txt') == True:
            os.remove('Q:\\scripts\\XLiveScore\\txt\\wc_grli.txt')
        if os.path.isfile('Q:\\scripts\\XLiveScore\\txt\\s_scores.txt') == True:
            os.remove('Q:\\scripts\\XLiveScore\\txt\\s_scores.txt')
        if os.path.isfile('Q:\\scripts\\XLiveScore\\txt\\s_couli.txt') == True:
            os.remove('Q:\\scripts\\XLiveScore\\txt\\s_couli.txt')
        if os.path.isfile('Q:\\scripts\\XLiveScore\\txt\\s_cou.txt') == True:
            os.remove('Q:\\scripts\\XLiveScore\\txt\\s_cou.txt')
        if os.path.isfile('Q:\\scripts\\XLiveScore\\txt\\s_at.txt') == True:
            os.remove('Q:\\scripts\\XLiveScore\\txt\\s_at.txt')
        if os.path.isfile('Q:\\scripts\\XLiveScore\\txt\\s_ht.txt') == True:
            os.remove('Q:\\scripts\\XLiveScore\\txt\\s_ht.txt')

    def buildscorelists(self, array1):
        for i in range (0, len(array1)):
            self.teamslist.addItem(xbmcgui.ListItem(array1[i]))
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

    def getmycontrols(self):
        self.teamslist = self.getControl(80)
        self.scorelist = self.getControl(81)
        self.invisilist = self.getControl(82)
        self.Soccer_Button = self.getControl(71)
        self.Worldcup_Button = self.getControl(72)
        self.Hockey_Button = self.getControl(73)
        self.Tennis_Button = self.getControl(74)
        self.Latest_Soccer = self.getControl(76)
        self.Latest_Worldcup = self.getControl(77)
        self.Latest_Hockey = self.getControl(78)
        self.Latest_Tennis = self.getControl(79)

    def onAction(self, action):
        #line below makes it so the lists scroll together :-D
        xbmcgui.lock()
        self.scorelist.selectItem(self.invisilist.getSelectedPosition())
        self.teamslist.selectItem(self.invisilist.getSelectedPosition())
        xbmcgui.unlock()
        if action == ACTION_PREVIOUS_MENU:
            self.removetxt()
            self.close()

    def onClick(self, controlID):
# Groups Buttons
        if ( controlID == 71):
            # Soccer Button
            self.resetlists()
            dialog.create(__scriptname__)
            dialog.update(5, 'Fetching Soccer Countries & Countrylinks')
            try:
                mycouarray = get_SocCou()
            except:
                mycouarray = ["cant", "get", "countries"]
            dialog.update(50)
            try:
                mycouliarray = get_SocCouLi()
            except:
                mycouliarray = ["cant", "get", "countrylinks"]
            dialog.update(100)
            dialog.close()
            self.buildcoulists(mycouarray,mycouliarray)
            self.setFocus(self.invisilist)

        elif ( controlID == 72):
            # WorldCup Button
            self.resetlists()
            dialog.create(__scriptname__)
            dialog.update(5, 'Fetching WorldCup Groups & Grouplinks')
            try:
                groupsarray = get_WC_Gr()
            except:
                groupsarray = ["cant", "get", "groups"]
            dialog.update(50)
            try:
                grlinksarray = get_WC_GrLi()
            except:
                grlinksarray = ["cant", "get", "grouplinks"]
            dialog.update(100)
            dialog.close()
            self.buildcoulists(groupsarray,grlinksarray)
            self.setFocus(self.invisilist)

        elif ( controlID == 73):
            # Hockey Button
            self.resetlists()
            dialog.create(__scriptname__)
            dialog.update(5, 'Fetching Hockey Groups & Grouplinks')
            try:
                groupsarray = get_Ho_Gr()
            except:
                groupsarray = ["cant", "get", "groups"]
            dialog.update(50)
            try:
                grlinksarray = get_Ho_GrLi()
            except:
                grlinksarray = ["cant", "get", "grouplinks"]
            dialog.update(100)
            dialog.close()
            self.buildcoulists(groupsarray,grlinksarray)
            self.setFocus(self.invisilist)

        elif ( controlID == 74):
            # Tennis Button
            self.resetlists()
            dialog.create(__scriptname__)
            dialog.update(5, 'Fetching Tennis Groups & Grouplinks')
            try:
                groupsarray = get_Te_Gr()
            except:
                groupsarray = ["cant", "get", "groups"]
            dialog.update(50)
            try:
                grlinksarray = get_Te_GrLi()
            except:
                grlinksarray = ["cant", "get", "grouplinks"]
            dialog.update(100)
            dialog.close()
            self.buildcoulists(groupsarray,grlinksarray)
            self.setFocus(self.invisilist)
# Groups Buttons
# Latest Buttons
        elif ( controlID == 76):
            #Latest Soccer Button
            self.resetlists()
            dialog.create(__scriptname__)
            dialog.update(5, 'Fetching Soccer Teams & Scores')
            try:
                myteamarray1 = get_HomeTeams()
            except:
                myteamarray1 = ["cant", "get", "hometeams"]
            dialog.update(35)
            try:
                myteamarray2 = get_AwayTeams()
            except:
                myteamarray2 = ["cant", "get", "awayteams"]
            dialog.update(68)
            try:
                #myteamscores = ["0-5", "9-6", "10-5","10-5","9-6", "0-5", "9-6","0-5", "9-6", "0-5", "9-6", "10-5","10-5","9-6", "0-5", "9-6","0-5", "9-6", "0-5"]
                myteamscores = get_Scores()
            except:
                myteamscores = ["cant", "get", "scores"]
            dialog.update(100)
            dialog.close()
            self.buildlists(myteamarray1,myteamarray2,myteamscores)
            self.setFocus(self.invisilist)

        #elif ( controlID == 77):
            # Latest WorldCup Button
        #elif ( controlID == 78):
            # Latest Hockey Button
        #elif ( controlID == 79):
            # Latest Tennis Button
# Latest Buttons

    def onFocus(self, controlID):
# Groups Buttons
        if ( controlID == 71):
            # Soccer Button
            if os.path.isfile('Q:\\scripts\\XLiveScore\\txt\\s_cou.txt') == True:
                if os.path.isfile('Q:\\scripts\\XLiveScore\\txt\\s_couli.txt') == True:
                    self.resetlists()
                    countriesarray = get_Cou_text()
                    coulinksarray = get_CouLi_text()
                    self.buildcoulists(countriesarray,coulinksarray)

        elif ( controlID == 72):
            # WorldCup Button
            if os.path.isfile('Q:\\scripts\\XLiveScore\\txt\\wc_groups.txt') == True:
                if os.path.isfile('Q:\\scripts\\XLiveScore\\txt\\wc_grli.txt') == True:
                    self.resetlists()
                    groupsarray = get_WC_Gr_text()
                    grlinksarray = get_WC_GrLi_text()
                    self.buildcoulists(groupsarray,grlinksarray)

        elif ( controlID == 73):
            # Hockey Button
            if os.path.isfile('Q:\\scripts\\XLiveScore\\txt\\ho_groups.txt') == True:
                if os.path.isfile('Q:\\scripts\\XLiveScore\\txt\\ho_grli.txt') == True:
                    self.resetlists()
                    groupsarray = get_Ho_Gr_text()
                    grlinksarray = get_Ho_GrLi_text()
                    self.buildcoulists(groupsarray,grlinksarray)

        elif ( controlID == 74):
            # Tennis Button
            if os.path.isfile('Q:\\scripts\\XLiveScore\\txt\\te_groups.txt') == True:
                if os.path.isfile('Q:\\scripts\\XLiveScore\\txt\\te_grli.txt') == True:
                    self.resetlists()
                    groupsarray = get_Te_Gr_text()
                    grlinksarray = get_Te_GrLi_text()
                    self.buildcoulists(groupsarray,grlinksarray)
# Groups Buttons
# Latest Buttons
        elif ( controlID == 76):
            # Latest Soccer Button
            if os.path.isfile('Q:\\scripts\\XLiveScore\\txt\\s_ht.txt') == True:
                if os.path.isfile('Q:\\scripts\\XLiveScore\\txt\\s_at.txt') == True:
                    if os.path.isfile('Q:\\scripts\\XLiveScore\\txt\\s_scores.txt') == True:
                        self.resetlists()
                        hometeamsarray = get_HT_text()
                        awayteamsarray = get_AT_text()
                        scoresarray = get_Scores_text()
                        self.buildlists(hometeamsarray,awayteamsarray,scoresarray)

        #elif ( controlID == 77):
            # Latest WorldCup Button
        #elif ( controlID == 78):
            # Latest Hockey Button
        #elif ( controlID == 79):
            # Latest Tennis Button
# Latest Buttons

    def set_button_state(self, state):
        xbmcgui.lock()
        visible = bool(state & XLiveScoreGUI.STATE_MAIN)
        self.Soccer_Button.setVisible(visible)
        #if visible:
              #dominant = self.Soccer_Button
        self.Worldcup_Button.setVisible(visible)
        self.Hockey_Button.setVisible(visible)
        self.Tennis_Button.setVisible(visible)
        #if visible:
            #dominant = self.Tennis_Button
        self.Latest_Soccer.setVisible(visible)
        #if visible:
            #dominant = self.Latest_Soccer
        self.Latest_Worldcup.setVisible(visible)
        self.Latest_Hockey.setVisible(visible)
        self.Latest_Tennis.setVisible(visible)
        if visible:
            dominant = self.Latest_Tennis
        self.setFocus(dominant)
        self.state = state
        xbmcgui.unlock()
    
ls = LiveScoreGUI("XLiveScore_Main.xml",SCRIPTDIR,"DefaultSkin")
ls.doModal()
del ls
