"""
    YouTube.Com Script for XBMC
    Using RSS Feed for the Data
    Coding By Donno [darkdonno@gmail.com]
    BackButton by BlackBolt
    Version: 1.8

    THIS IS THE MC360 PORT

"""
saves_folder = "e:\\youtube_downloads\\"
DEBUG = 0

import urllib,urllib2 , re, os
import xbmc, xbmcgui

try: Emulating = xbmcgui.Emulating
except: Emulating = False

download_first = 1

__title__ = "YouTube.com"
__version__ = '1.6'
__coder__ = 'Donno'
__author__ = 'Donno [darkdonno@gmail.com]'
__date__ = '2006'
__maintaner__ = 'Donno'

ACTION_PREVIOUS_MENU = 10
ACTION_Y = 34
ACTION_WHITE = 117

global yPath
yPath = ""
yPathMain = os.getcwd().replace(";","")+"\\"

SD = xbmc.getSkinDir().lower()
txtboxColor = "0xFF000000"
fc = "0xFF000000"

button_normal=yPath+"button-nofocus.png"
button_hl=yPath+"button-focus.png"

thefont10 = "font10"
thefont14 = "font14"
thefont13 = "font13"

# Incase some of the url change look at these varibles first
base_url = "http://youtube.com/rss/global/"
base_search = "http://youtube.com/rss/search/"
base_tag = "http://youtube.com/rss/tag/"
base_v_url = "http://youtube.com/get_video?video_id="
base_t_url =    "http://youtube.com/watch?v="
base_api = "http://www.youtube.com/api2_rest?method=%s&dev_id=k1jPjdICyu0&%s"   # usage   base_api %( method, extra)   eg base_api %( youtube.videos.get_detail, video_id=yyPHkJMlD0Q)

the_re  =  re.compile('<title>([^<]*)</title>\n[^<]*<link>http://youtube.com/[?]v=([^<]*)</link>')
#the_re  =  re.compile('<author>rss@youtube.com \((.*)\)</author>\n[^<]*<title>([^<]*)</title>\n[^<]*<link>http://youtube.com/[?]v=([^<]*)</link>\n[^<]*<description>\n[^<]*<!\[CDATA\[\n[^<]*<img src="([^"]*)"')
the_t_reg = str('var fo = new SWFObject\("\/player2.swf[?]video_id=.*[&]l=(.*)[&]t=([^"]*)')

import xml.dom.minidom

def parseXMLFile(filename,win):
        doc = xml.dom.minidom.parse(filename)
        title = []
        win.videoList.reset()
        try:
            root = doc.documentElement
            # make sure this is a valid xml file
            if (not root or root.tagName != 'ut_response'): raise
            # make sure <video_list> block exists
            video_list = root.firstChild
            if (not video_list or video_list.tagName != 'video_list'): raise
            # parse and resolve each <video>
            data = video_list.getElementsByTagName('video')
            if (not data): raise
            for video in data:
                node = video.firstChild
                title = ""
                url = ""
                while (node):
                    # key node get value
                    if (node.tagName.lower() == 'title' and node.hasChildNodes()):
                        title = node.firstChild.nodeValue
                    elif (node.tagName.lower() == 'url' and node.hasChildNodes()):
                        url = node.firstChild.nodeValue
                        url = url[26:]
                    node = node.nextSibling
                win.videoList.addItem(title)
                win.title_list.append(title)
                win.video_id_list.append(url)
                #print "title: %s    url: %s" % (title,url)
            return 1
        except:
            return 0

def parseFriendsXMLFile(filename,win):
        doc = xml.dom.minidom.parse(filename)
        win.friend_list = []
        win.friendList.reset()
        try:
            root = doc.documentElement
            # make sure this is a valid xml file
            if (not root or root.tagName != 'ut_response'): raise
            # make sure <video_list> block exists
            video_list = root.firstChild
            if (not video_list or video_list.tagName != 'friend_list'): raise
            # parse and resolve each <video>
            data = video_list.getElementsByTagName('friend')
            if (not data): raise
            for video in data:
                node = video.firstChild
                #node = self.FirstChildElement(tmp, None)
                title = ""
                while (node):
                    # key node get value
                    if (node.tagName.lower() == 'user' and node.hasChildNodes()):
                        title = node.firstChild.nodeValue
                    node = node.nextSibling
                win.friendList.addItem(title)
                win.friend_list.append(title)
                #print "title: %s    url: %s" % (title,url)
            return 1
        except:
            return 0
def SetupButtons(win,x,y,w,h,a="Vert",f=yPath+"button-focus.png",nf=yPath+"button-nofocus.png",gap=0,txtOffSet=0,font=thefont10):
    win.numbut  = 0
    win.butx = x
    win.buty = y
    win.butwidth = w
    win.butheight = h
    win.butalign = a
    win.butfocus_img = f
    win.butnofocus_img = nf
    win.gap = gap
    win.txtOffSet = txtOffSet
    win.font=font

def AddButton(win,text):
    if win.butalign == "Hori":
        c = xbmcgui.ControlButton(win.butx + (win.numbut * win.butwidth + win.gap * win.numbut),win.buty,win.butwidth,win.butheight,text,win.butfocus_img,win.butnofocus_img,textColor=fc,font=thefont13)
    elif win.butalign == "Vert":
        c = xbmcgui.ControlButton(win.butx ,win.buty + (win.numbut * win.butheight + win.gap* win.numbut) ,win.butwidth,win.butheight,text,win.butfocus_img,win.butnofocus_img,textColor=fc,font=thefont13,alignment=0)
    else:
        c = xbmcgui.ControlButton(win.butx ,win.buty + (win.numbut * win.butheight + win.gap* win.numbut) ,win.butwidth,win.butheight,text,win.butfocus_img,win.butnofocus_img,textColor=fc,font=thefont13,alignment=0)
    win.numbut += 1
    win.addControl(c)
    return c

class YouTube(xbmcgui.Window):
    def __init__(self):
        if Emulating: xbmcgui.Window.__init__(self)
        global yPath
        """ Define your sript's Window size here: """
        self.setCoordinateResolution(6)
        """ Add your GUI images to your script here: """
        self.addControl(xbmcgui.ControlImage(0,0, 720,576, 'background-blue.png'))
        self.addControl(xbmcgui.ControlImage(18,0, 702,576, xbmc.getInfoLabel('Skin.String(Media)')))
        self.addControl(xbmcgui.ControlImage(70,0, 16,64, 'bkgd-whitewash-glass-top-left.png'))
        self.addControl(xbmcgui.ControlImage(86,0, 667,64, 'bkgd-whitewash-glass-top-middle.png'))
        self.addControl(xbmcgui.ControlImage(753,0, 16,64, 'bkgd-whitewash-glass-top-right.png'))
        self.addControl(xbmcgui.ControlImage(86,427, 667,64, 'bkgd-whitewash-glass-bottom-middle.png'))
        self.addControl(xbmcgui.ControlImage(70,427, 16,64, 'bkgd-whitewash-glass-bottom-left.png'))
        self.addControl(xbmcgui.ControlImage(753,427, 667,64, 'bkgd-whitewash-glass-bottom-right.png'))
        self.addControl(xbmcgui.ControlImage(60,0, 32,576, 'background-overlay-whitewash-left.png'))
        self.addControl(xbmcgui.ControlImage(92,0, 628,576, 'background-overlay-whitewash-centertile.png'))
        self.addControl(xbmcgui.ControlImage(-61,0, 128,576, 'blades-runner-left.png'))
        self.addControl(xbmcgui.ControlImage(18,0, 80,576, 'blades-size4-header.png'))
        self.addControl(xbmcgui.ControlLabel(102,35, 200,35, 'You Tube', font="font18"))
        self.addControl(xbmcgui.ControlImage(125,505, 21,21, 'button-Y-turnedoff.png'))
        self.addControl(xbmcgui.ControlImage(112,525, 21,21, 'button-X.png'))
        if xbmc.Player().isPlayingAudio():
            self.addControl(xbmcgui.ControlLabel(145,528, 300,35, 'Full Screen Visualization',font="font12"))
            self.x_img = xbmcgui.ControlImage(112,525, 21,21, 'button-X.png')
            self.addControl(self.x_img)
        elif xbmc.Player().isPlayingVideo():
            self.addControl(xbmcgui.ControlLabel(145,528, 300,35, 'Full Screen Video',font="font12"))
            self.x_img = xbmcgui.ControlImage(112,525, 21,21, 'button-X.png')
            self.addControl(self.x_img)
        else:
            self.x_img = xbmcgui.ControlImage(112,525, 21,21, 'button-X-turnedoff.png')
            self.addControl(self.x_img)
        self.addControl(xbmcgui.ControlImage(620,505, 21,21, 'button-B.png'))
        self.addControl(xbmcgui.ControlImage(633,525, 21,21, 'button-A.png'))

        self.addControl(xbmcgui.ControlLabel(623,528, 200,35, 'Select',alignment=1,font="font12"))
        self.addControl(xbmcgui.ControlLabel(610,510, 200,35, 'Back',alignment=1,font="font12"))
        self.addControl(xbmcgui.ControlLabel(79,155, 200,35, 'media',angle=270,textColor="0xFF000000",font="font14"))
        self.addControl(xbmcgui.ControlLabel(79,155, 200,35, 'media',angle=270,textColor="0xFF000000",font="font14"))

        #self.addControl(xbmcgui.ControlImage(50,45,200,60, yPathMain+"youtube.png")) #i like it where it is looks nice its in the middle
        self.lblCatergory = xbmcgui.ControlLabel(320,45,200,60,"",font=thefont14,textColor="0xFFFFFFFF")

        self.addControl(self.lblCatergory)
        """ Create your Menu buttons here: """
        SetupButtons(self, 90,95, 180, 28, "Vert", button_hl,button_normal, 2,5)
        self.btnRA = AddButton(self,'Recently Added')
        self.btnRF = AddButton(self,'Recently Featured')
        self.btnTF = AddButton(self,'Top Favorites')
        self.btnTR = AddButton(self,'Top Rated')
        self.btnMV = AddButton(self,'Most Viewed')
        self.btnMD = AddButton(self,'Most Discussed')
        self.btnTag = AddButton(self,'** Tag **')
        self.btnSearch = AddButton(self,'** Search **')

        self.lblCatOpen = xbmcgui.ControlLabel(90,335,205,60,"",font=thefont14,textColor=fc)
        self.addControl(self.lblCatOpen)
        SetupButtons(self, 90,365, 155, 28, "Vert", button_hl,button_normal, 2,5)
        self.btnMVT = AddButton(self,'- Today')
        self.btnMTW = AddButton(self,'- This Week')
        self.btnMTN = AddButton(self,'- This Month')
        self.btnMAT = AddButton(self,'- All Time')
        self.title_list = []
        self.video_id_list = []
        self.author_list = []
        self.thumb_picurl = []
        SetupButtons(self, int(90),int(365), int(155), int(28), "Vert", button_hl,button_normal, 2,5)
        self.btnMDVT = AddButton(self,'- Today')
        self.btnMDVTW = AddButton(self,'- This Week')
        self.btnMDVTM = AddButton(self,'- This Month')
        self.selT = 0
        self.mode = 0
        self.addControl(xbmcgui.ControlImage(60,90,210,355, "systemhomebutton-1-top.png"))
        self.contextUp = 0
        ct_x = 325
        if SD == "pdm":
            yPath = yPathMain+"gfx\\"
        self.cbgt = xbmcgui.ControlImage(ct_x, 150-30, 230,31, yPath+"dialog-context-top.png")
        self.cbgm = xbmcgui.ControlImage(ct_x, 150, 230,210, yPath+"dialog-context-middle.png")
        self.cbgb = xbmcgui.ControlImage(ct_x, 150+210, 230,37, yPath+"dialog-context-bottom.png")
        self.clbl= xbmcgui.ControlLabel(ct_x+20, 160, 150, 30, "Select Action",font=thefont14,textColor=fc)
        self.clbgl= xbmcgui.ControlFadeLabel(ct_x+20, 190, 180, 30, thefont10,textColor=fc)
        self.conButs = []
        self.checkMark_DownPlay = xbmcgui.ControlCheckMark(270, 450,200, 20,"Save",yPath+"check-box.png",yPath+"check-boxNF.png",font=thefont10,textColor=fc)
        self.addControl( self.checkMark_DownPlay)
        self.videoList = xbmcgui.ControlList(270,90,430, 340,"font12",fc,yPath+"iconlist-nofocus.png",yPath+"iconlist-focus.png",itemTextXOffset=-10,)
        self.addControl(self.videoList)
        self.setFocus(self.btnRA)
        self.setNav()
        self.vis(0)

    def vis(self,t):
        if t == 2:
            self.btnMVT.setVisible(0)
            self.btnMTW.setVisible(0)
            self.btnMTN.setVisible(0)
            self.btnMAT.setVisible(0)
            self.btnMDVT.setVisible(1)
            self.btnMDVTW.setVisible(1)
            self.btnMDVTM.setVisible(1)
            self.btnSearch.controlDown(self.btnMDVT)
        elif t == 1:
            self.btnMDVT.setVisible(0)
            self.btnMDVTW.setVisible(0)
            self.btnMDVTM.setVisible(0)
            self.btnMVT.setVisible(1)
            self.btnMTW.setVisible(1)
            self.btnMTN.setVisible(1)
            self.btnMAT.setVisible(1)
            self.btnSearch.controlDown(self.btnMVT)
        else:
            self.btnMVT.setVisible(0)
            self.btnMTW.setVisible(0)
            self.btnMTN.setVisible(0)
            self.btnMAT.setVisible(0)
            self.btnMDVT.setVisible(0)
            self.btnMDVTW.setVisible(0)
            self.btnMDVTM.setVisible(0)
            self.btnSearch.controlDown(self.checkMark_DownPlay)

    def setNav(self):
        self.videoList.controlLeft(self.btnRA)

        self.btnRA.controlRight(self.videoList)
        self.btnRF.controlRight(self.videoList)
        self.btnTF.controlRight(self.videoList)
        self.btnTR.controlRight(self.videoList)

        self.btnMVT.controlRight(self.videoList)
        self.btnMTW.controlRight(self.videoList)
        self.btnMTN.controlRight(self.videoList)
        self.btnMAT.controlRight(self.videoList)

        self.btnMDVT.controlRight(self.videoList)
        self.btnMDVTW.controlRight(self.videoList)
        self.btnMDVTM.controlRight(self.videoList)
        self.btnMD.controlRight(self.videoList)
        self.btnMV.controlRight(self.videoList)
        self.btnTag.controlRight(self.videoList)
        self.btnSearch.controlRight(self.videoList)
        self.btnMDVTM.controlRight(self.videoList)
        self.checkMark_DownPlay.controlRight(self.videoList)

        self.btnRA.controlDown(self.btnRF)
        self.btnRF.controlDown(self.btnTF)
        self.btnTF.controlDown(self.btnTR)
        self.btnTR.controlDown(self.btnMV)
        self.btnMV.controlDown(self.btnMD)
        self.btnMD.controlDown(self.btnTag)
        self.btnTag.controlDown(self.btnSearch)
        self.btnSearch.controlDown(self.checkMark_DownPlay)

        self.btnMVT.controlDown(self.btnMTW)
        self.btnMTW.controlDown(self.btnMTN)
        self.btnMTN.controlDown(self.btnMAT)
        self.btnMAT.controlDown(self.checkMark_DownPlay)

        self.btnMDVT.controlDown(self.btnMDVTW)
        self.btnMDVTW.controlDown(self.btnMDVTM)
        self.btnMDVTM.controlDown(self.checkMark_DownPlay)
        self.checkMark_DownPlay.controlDown(self.btnRA)

        self.btnRA.controlUp(self.checkMark_DownPlay)
        self.btnRF.controlUp(self.btnRA)
        self.btnTF.controlUp(self.btnRF)
        self.btnTR.controlUp(self.btnTF)
        self.btnMV.controlUp(self.btnTR)
        self.btnMD.controlUp(self.btnMV)
        self.btnTag.controlUp(self.btnMD)
        self.btnSearch.controlUp(self.btnTag)

        self.btnMVT.controlUp(self.btnSearch)
        self.btnMTW.controlUp(self.btnMVT)
        self.btnMTN.controlUp(self.btnMTW)
        self.btnMAT.controlUp(self.btnMTN)

        self.btnMDVT.controlUp(self.btnSearch)
        self.btnMDVTW.controlUp(self.btnMDVT)
        self.btnMDVTM.controlUp(self.btnMDVTW)
        self.checkMark_DownPlay.controlUp(self.btnSearch)

    def onAction(self, action):
        if action == 9:
            if self.contextUp == 1:
                self.delconOL()
            else:
                self.close()
        elif action == 79:
            if self.getFocus() == self.videoList:
                self.playVideo()
        elif action == 11:
            if self.contextUp == 1:
                self.delconOL()
            elif self.getFocus() == self.videoList:
                if self.videoList.getSelectedPosition() != -1:
                    if self.mode == 0:
                        self.createConText(self.title_list[self.videoList.getSelectedPosition()],325,"Add To Favorites")
                    else:
                        self.createConText(self.title_list[self.videoList.getSelectedPosition()],325,"Remove From Favorites")
        elif action == ACTION_WHITE:
            if self.contextUp == 1:
                self.delconOL()
            elif self.getFocus() == self.videoList:
                if self.videoList.getSelectedPosition() != -1:
                    if self.mode == 0:
                        self.createConText(self.title_list[self.videoList.getSelectedPosition()],325,"Add To Favorites")
                    else:
                        self.createConText(self.title_list[self.videoList.getSelectedPosition()],325,"Remove From Favorites")
        elif action == ACTION_Y:
            if self.mode == 0:
                self.lblCatergory.setLabel("Saved/ Booked Marked Videos")
                self.mode = 1
                self.getFavList()
        elif action == ACTION_PREVIOUS_MENU:
            if self.contextUp == 1:
                self.delconOL()
            else:
                self.close()
    def onControl(self, control):
        if self.btnRA == control:
            self.lblCatergory.setLabel("Recently Added")
            self.getViewList("recently_added.rss")
            self.videoList.controlLeft(self.btnRA)
        if self.btnRF == control:
            self.lblCatergory.setLabel("Recently Featured")
            self.getViewList("recently_featured.rss")
            self.videoList.controlLeft(self.btnRF)
        if self.btnTF == control:
            self.lblCatergory.setLabel("Top Favorites")
            self.getViewList("top_favorites.rss")
            self.videoList.controlLeft(self.btnTF)
        if self.btnTR == control:
            self.getViewList("top_rated.rss")
            self.lblCatergory.setLabel("Top Rated")
            self.videoList.controlLeft(self.btnTR)
        if self.btnMVT == control:
            self.lblCatergory.setLabel("Top Viewed Today")
            self.getViewList("top_viewed_today.rss")
            self.videoList.controlLeft(self.btnMV)
        if self.btnMTW == control:
            self.lblCatergory.setLabel("Top Viewed Week")
            self.getViewList("top_viewed_week.rss")
            self.videoList.controlLeft(self.btnMV)
        if self.btnMTN == control:
            self.lblCatergory.setLabel("Top Viewed Month")
            self.getViewList("top_viewed_month.rss")
            self.videoList.controlLeft(self.btnMV)
        if self.btnMAT == control:
            self.lblCatergory.setLabel("Top Viewed")
            self.getViewList("top_viewed.rss")
            self.videoList.controlLeft(self.btnMV)
        if self.btnMDVT == control:
            self.lblCatergory.setLabel("Most Discussed Today")
            self.getViewList("most_discussed_today.rss")
            self.videoList.controlLeft(self.btnMD)
        if self.btnMDVTW == control:
            self.lblCatergory.setLabel("Most Discussed Week")
            self.getViewList("most_discussed_week.rss")
            self.videoList.controlLeft(self.btnMD)
        if self.btnMDVTM == control:
            self.lblCatergory.setLabel("Most Discussed Month")
            self.getViewList("most_discussed_month.rss")
            self.videoList.controlLeft(self.btnMD)
        if self.btnSearch == control:
            searchstring = unikeyboard("","Search")
            if searchstring != "":
                self.lblCatergory.setLabel("Search: " + searchstring)
                searchstring = searchstring.replace(" ","+")
                self.getViewList(searchstring + ".rss",base_search)
        if self.btnTag == control:
            searchstring = unikeyboard("","Tag")
            self.lblCatergory.setLabel("Tag: " + searchstring)
            searchstring = searchstring.replace(" ","+")
            self.getViewList(searchstring + ".rss",base_tag)
        if self.btnMV == control:
            if self.selT == 1:
                self.lblCatOpen.setLabel("")
                self.vis(0)
                self.selT = 0
            else:
                self.lblCatOpen.setLabel("Most Viewed")
                self.vis(1)
                self.selT = 1
        if self.btnMD == control:
            if self.selT == 2:
                self.lblCatOpen.setLabel("")
                self.vis(0)
                self.selT = 0
            else:
                self.lblCatOpen.setLabel("Most Discussed")
                self.vis(2)
                self.selT = 2
        if self.videoList == control:
            self.playVideo()
        if self.contextUp == 1 and self.videoList.getSelectedPosition() != -1:
            if control == self.conButs[0]:
                self.delconOL()
                self.playVideo()
            elif control == self.conButs[1]:
                if self.mode == 0:
                    xebi('XBMC.Notification(YouTube.com,Added to Favorites)')
                    addFiletoList(self.title_list[self.videoList.getSelectedPosition()],self.video_id_list[self.videoList.getSelectedPosition()])
                else:
                    xebi('XBMC.Notification(YouTube.com,Favorites Removed)')
                    removeFromlist(self.title_list[self.videoList.getSelectedPosition()],self.video_id_list[self.videoList.getSelectedPosition()],self)
                self.delconOL()
            elif control == self.conButs[2]:
                self.delconOL()
                self.infoWin = YouTubeInfo(ext=self.title_list[self.videoList.getSelectedPosition()],id=self.video_id_list[self.videoList.getSelectedPosition()])
                self.infoWin.doModal()
                del self.infoWin

    def playVideo(self):
        if self.videoList.getSelectedPosition() != -1:
            if self.mode == 1:
                id = self.video_id_list[self.videoList.getSelectedPosition()]
                if os.path.exists(saves_folder + id + ".flv"):
                    askWatch = xbmcgui.Dialog().yesno(__title__,"Do you want it from HDD?")
                    if askWatch == 1:
                        xbmc.Player(1).play(saves_folder + id + ".flv")
                    else:
                        self.getVideo(id,self.title_list[self.videoList.getSelectedPosition()])
                else:
                    self.getVideo(id,self.title_list[self.videoList.getSelectedPosition()])
            else:
                self.getVideo(self.video_id_list[self.videoList.getSelectedPosition()],self.title_list[self.videoList.getSelectedPosition()])
    def createConText(s,text="",ct_x=450,but2="Add To Favorites"):
        s.contextUp = 1
        # 250 is fine but over (this way its on the right)
        s.addControl(s.cbgt)
        s.addControl(s.cbgm)
        s.addControl(s.cbgb)
        s.addControl(s.clbl)
        s.addControl(s.clbgl)
        s.clbgl.addLabel(text)
        SetupButtons(s,ct_x+20,220,195,32,2,gap=10)
        s.conButs = []
        s.conButs.append(AddButton(s,'Play Video'))
        s.conButs.append(AddButton(s,but2))
        s.conButs.append(AddButton(s,'Video Info'))
        s.createnav_context()
        s.setFocus(s.conButs[0])
    def createnav_context(self):
        self.conButs[0].controlDown(self.conButs[1])
        self.conButs[1].controlDown(self.conButs[2])
        self.conButs[2].controlDown(self.conButs[0])
        self.conButs[0].controlUp(self.conButs[2])
        self.conButs[1].controlUp(self.conButs[0])
        self.conButs[2].controlUp(self.conButs[1])

    def delconOL(s):
        s.setFocus(s.videoList)
        for i in range(0,len(s.conButs)):
            s.removeControl(s.conButs[i])
        s.removeControl(s.cbgt)
        s.removeControl(s.cbgm)
        s.removeControl(s.cbgb)
        s.removeControl(s.clbl)
        s.removeControl(s.clbgl)
        s.contextUp = 0
    def getVideo(self,id,title):
        dp = xbmcgui.DialogProgress()
        dp.create("YouTube.com","Playing Video")
        t = self.newTvalie(id)
        v_url = base_v_url + id + "&t=" + t
        print v_url
        request = urllib2.Request(v_url)
        opener = urllib2.build_opener(SRH)
        f = opener.open(request)
        vid_url = f.url
        print vid_url
        if self.checkMark_DownPlay.getSelected() == 0:
            dp.close()
            xbmc.Player(1).play(vid_url)
        else:
            if not os.path.exists(saves_folder):
                makeAllFolders(saves_folder)
            # Was going to save as Title but issue there is may be longer then fatx so instead use id
            retval = DownloaderClass(vid_url,saves_folder + id + ".flv",dp)
            if retval:
                addFiletoList(self.title_list[self.videoList.getSelectedPosition()],self.video_id_list[self.videoList.getSelectedPosition()]) # Add to Favoruties
                xbmc.Player(1).play(saves_folder + id + ".flv")
            else:
                delStuff = xbmcgui.Dialog().yesno(__title__,"Download Cancelled","Delete Part File?")
                if delStuff == 1:
                    xbmc.executehttpapi('FileDelete(' + saves_folder + id + ".flv" +')')

    def newTvalie(self,id):
        dp = xbmcgui.DialogProgress()
        dp.create("YouTube.com","Getting Session ID")
        url = base_t_url + id
        t = urllib.urlopen(url)
        dat = t.read()
        t.close()
        info = re.search(the_t_reg, dat,re.IGNORECASE)
        dp.close()
        return info.group(2)
    def getViewList(self,section,use_as_base=""):
        self.mode = 0
        dp = xbmcgui.DialogProgress()
        dp.create("YouTube.com","Getting List")
        if use_as_base == "":
            url = base_url + section
        else:
            url=  use_as_base + section
        try:
            urllib.urlretrieve(url,"Z:\\list",lambda nb, bs, fs, url=url: _pbhook(nb,bs,fs,url,dp,0.7))
        except:
            self.lblCatergory.setLabel("")
            dp.close()
            return 0
        self.videoList.reset()
        fs = open("Z:\\list", 'r')
        dat = fs.read()
        fs.close()
        dat = dat.replace("&amp;","&")
        dp.update(75)
        if dp.iscanceled():
            self.lblCatergory.setLabel("")
            dp.close()
            return 0
        dp.update(85)
        if dp.iscanceled():
            self.lblCatergory.setLabel("")
            dp.close()
            return 0
        info = the_re.findall(dat)
        self.title_list = []
        self.video_id_list = []
        self.author_list = []
        self.thumb_picurl = []
        if dp.iscanceled():
            self.lblCatergory.setLabel("")
            dp.close()
            return 0
        dp.update(90)
        for i in info:
            self.videoList.addItem(i[0])
            self.title_list.append(i[0])
            self.video_id_list.append(i[1])
        dp.close()
        return 1
    def getFavList(self):
        self.videoList.reset()
        lookstring = re.compile('<name>(.*)</name><id>(.*)</id>')
        f = open(saves_folder+"Fav.xml","r")
        d = f.read()
        f.close()
        gnfo = lookstring.findall(d)
        del d
        self.title_list = []
        self.video_id_list = []
        for i in gnfo:
            self.title_list.append(i[0])
            self.video_id_list.append(i[1])
            self.videoList.addItem(i[0])
class YouTubeProfile(xbmcgui.Window):
    def __init__(self):
        if Emulating: xbmcgui.Window.__init__(self)
        global yPath
        self.setCoordinateResolution(6)
        self.addControl(xbmcgui.ControlImage(0,0,720,576, yPath+"Background.png"))
        self.addControl(xbmcgui.ControlImage(0,0, 720,576, 'background-blue.png'))
        self.addControl(xbmcgui.ControlImage(18,0, 702,576, xbmc.getInfoLabel('Skin.String(Media)')))
        self.addControl(xbmcgui.ControlImage(70,0, 16,64, 'bkgd-whitewash-glass-top-left.png'))
        self.addControl(xbmcgui.ControlImage(86,0, 667,64, 'bkgd-whitewash-glass-top-middle.png'))
        self.addControl(xbmcgui.ControlImage(753,0, 16,64, 'bkgd-whitewash-glass-top-right.png'))
        self.addControl(xbmcgui.ControlImage(86,427, 667,64, 'bkgd-whitewash-glass-bottom-middle.png'))
        self.addControl(xbmcgui.ControlImage(70,427, 16,64, 'bkgd-whitewash-glass-bottom-left.png'))
        self.addControl(xbmcgui.ControlImage(753,427, 667,64, 'bkgd-whitewash-glass-bottom-right.png'))
        self.addControl(xbmcgui.ControlImage(60,0, 32,576, 'background-overlay-whitewash-left.png'))
        self.addControl(xbmcgui.ControlImage(92,0, 628,576, 'background-overlay-whitewash-centertile.png'))
        self.addControl(xbmcgui.ControlImage(-61,0, 128,576, 'blades-runner-left.png'))
        self.addControl(xbmcgui.ControlImage(18,0, 80,576, 'blades-size4-header.png'))
        self.addControl(xbmcgui.ControlLabel(102,35, 200,35, 'You Tube', font="font18"))
        self.addControl(xbmcgui.ControlImage(125,505, 21,21, 'button-Y-turnedoff.png'))
        self.addControl(xbmcgui.ControlImage(112,525, 21,21, 'button-X.png'))
        if xbmc.Player().isPlayingAudio():
            self.addControl(xbmcgui.ControlLabel(145,528, 300,35, 'Full Screen Visualization',font="font12"))
            self.x_img = xbmcgui.ControlImage(112,525, 21,21, 'button-X.png')
            self.addControl(self.x_img)
        elif xbmc.Player().isPlayingVideo():
            self.addControl(xbmcgui.ControlLabel(145,528, 300,35, 'Full Screen Video',font="font12"))
            self.x_img = xbmcgui.ControlImage(112,525, 21,21, 'button-X.png')
            self.addControl(self.x_img)
        else:
            self.x_img = xbmcgui.ControlImage(112,525, 21,21, 'button-X-turnedoff.png')
            self.addControl(self.x_img)
        self.addControl(xbmcgui.ControlImage(620,505, 21,21, 'button-B.png'))
        self.addControl(xbmcgui.ControlImage(633,525, 21,21, 'button-A.png'))

        self.addControl(xbmcgui.ControlLabel(623,528, 200,35, 'Select',alignment=1,font="font12"))
        self.addControl(xbmcgui.ControlLabel(610,510, 200,35, 'Back',alignment=1,font="font12"))
        self.addControl(xbmcgui.ControlLabel(79,155, 200,35, 'media',angle=270,textColor="0xFF000000",font="font14"))
        self.addControl(xbmcgui.ControlLabel(79,155, 200,35, 'media',angle=270,textColor="0xFF000000",font="font14"))
        self.lblCatergory = xbmcgui.ControlLabel(300,45,300,60,"",font=thefont14,textColor="0xFFFFFFFF")
        self.addControl(xbmcgui.ControlImage(60,90,210,355, "systemhomebutton-1-top.png"))
        self.addControl(self.lblCatergory)
        """ Create your Menu buttons here: """
        SetupButtons(self, 90,95, 180, 28, "Vert", button_hl,button_normal, 2,5)
        self.btnVP = AddButton(self,'View a Profile')
        self.btnUFA = AddButton(self,'User Favorites')
        self.btnUV = AddButton(self,'User Videos')
        self.btnUFR = AddButton(self,'User Friends')
        self.btnF = AddButton(self,'Feeds')

        self.lblCatOpen = xbmcgui.ControlLabel(40,350,205,60,"",font=thefont14,textColor=fc)
        self.addControl(self.lblCatOpen)
        self.title_list = []
        self.video_id_list = []
        self.friend_list = []
        self.author_list = []
        self.thumb_picurl = []
        self.selT = 0
        self.mode = 0
        self.ContextMode = 0

        self.contextUp = 0
        ct_x = 325
        if SD == "pdm":
            yPath = yPathMain+"gfx\\"
        self.cbgt = xbmcgui.ControlImage(ct_x, 150-30, 230,31, yPath+"dialog-context-top.png")
        self.cbgm = xbmcgui.ControlImage(ct_x, 150, 230,210, yPath+"dialog-context-middle.png")
        self.cbgb = xbmcgui.ControlImage(ct_x, 150+210, 230,37, yPath+"dialog-context-bottom.png")
        self.clbl= xbmcgui.ControlLabel(ct_x+20, 160, 150, 30, "Select Action",font=thefont14,textColor=fc)
        self.clbgl= xbmcgui.ControlFadeLabel(ct_x+20, 190, 180, 30, thefont10,textColor=fc)
        self.conButs = []
        self.checkMark_DownPlay = xbmcgui.ControlCheckMark(270, 450,200, 20,"Save",yPath+"check-box.png",yPath+"check-boxNF.png",font=thefont10,textColor=fc)
        self.curUser ="henryperu77"
        self.addControl(self.checkMark_DownPlay)

        self.videoList = xbmcgui.ControlList(270,90,430,340,"font12",fc,yPath+"iconlist-nofocus.png",yPath+"iconlist-focus.png",itemTextXOffset=-10)
        self.addControl(self.videoList)
        self.friendList = xbmcgui.ControlList(270,90,430,340,"font12",fc,yPath+"iconlist-nofocus.png",yPath+"iconlist-focus.png",itemTextXOffset=-10)
        self.addControl(self.friendList)

        self.infoBox = xbmcgui.ControlTextBox(270,90,430,340,"font12",fc)
        self.addControl(self.infoBox)

        self.setFocus(self.btnVP)
        self.btnVP.setNavigation(self.checkMark_DownPlay,self.btnUFA,self.btnVP,self.btnVP)
        self.btnUFA.setNavigation(self.btnVP,self.btnUV,self.btnUFA,self.btnUFA)
        self.btnUV.setNavigation(self.btnUFA,self.btnUFR,self.btnUV,self.btnUV)
        self.btnUFR.setNavigation(self.btnUV,self.btnF,self.btnUFR,self.btnUFR)
        self.btnF.setNavigation(self.btnUFR,self.checkMark_DownPlay,self.btnF,self.btnF)
        self.checkMark_DownPlay.setNavigation(self.btnF,self.btnVP,self.checkMark_DownPlay,self.checkMark_DownPlay)

    def onAction(self, action):
        if action == 9:
            if self.contextUp == 1:
                self.delconOL()
            else:
                self.close()
        elif action == 79:
            if self.getFocus() == self.videoList:
                self.playVideo()
        elif action == 11:
            if self.contextUp == 1:
                self.delconOL()
            elif self.getFocus() == self.videoList:
                if self.videoList.getSelectedPosition() != -1:
                    if self.mode == 0:
                        self.createConText(self.title_list[self.videoList.getSelectedPosition()],325,"Add To Favorites")
                    else:
                        self.createConText(self.title_list[self.videoList.getSelectedPosition()],325,"Remove From Favorites")
            elif self.getFocus() == self.friendList:
                if self.friendList.getSelectedPosition() != -1:
                    self.createConTextFriends(self.friend_list[self.friendList.getSelectedPosition()],325)
        elif action == ACTION_WHITE:
            if self.contextUp == 1:
                self.delconOL()
            elif self.getFocus() == self.videoList:
                if self.videoList.getSelectedPosition() != -1:
                    if self.mode == 0:
                        self.createConText(self.title_list[self.videoList.getSelectedPosition()],325,"Add To Favorites")
                    else:
                        self.createConText(self.title_list[self.videoList.getSelectedPosition()],325,"Remove From Favorites")
            elif self.getFocus() == self.friendList:
                if self.friendList.getSelectedPosition() != -1:
                    self.createConTextFriends(self.friend_list[self.friendList.getSelectedPosition()],325)
        elif action == ACTION_Y:
            if self.mode == 0:
                self.lblCatergory.setLabel("Saved/ Booked Marked Videos")
                self.mode = 1
                self.getFavList()
        elif action == ACTION_PREVIOUS_MENU:
            if self.contextUp == 1:
                self.delconOL()
            else:
                self.close()

    def ViewProfile(self,tname):
        url = base_api % ("youtube.users.get_profile","user=" + tname)
        dp = xbmcgui.DialogProgress()
        dp.create("YouTube.com","Gathering Profile Infomation")
        try:
            urllib.urlretrieve(url,"E:\\info",lambda nb, bs, fs, url=url: _pbhook(nb,bs,fs,url,dp))
        except:
            self.lblCatergory.setLabel("")
            dp.close()
            return 0
        fsock = open("E:\\info", 'r')
        dat = fsock.read()
        fsock.close()
        dat = dat.replace("&amp;","&")
        #dat= re.search("<user_profile>([^</]*)</user_profile>", dat,re.IGNORECASE)
        dat2= re.search("<user_profile>(.*)</user_profile>", dat,re.IGNORECASE)
        if dat2 is None:
            xbmcgui.Dialog().ok(__title__,"Error Occured","Most likey because user was not found")
            self.lblCatergory.setLabel("")
            dp.close()
            return []
        else:
            dat = dat2.group()
        lookstring = re.compile('<([^>]*)>([^</]*)</[^>]*>')
        nfo = {}
        gnfo = lookstring.findall(dat)
        nfostr = ""
        for x in gnfo:
            nfo[x[0]] = x[1]
            nfostr += "%s: %s\n" % (x[0],x[1])
        dp.close()
        self.infoBox.setText(nfostr)
        self.curUser = tname

        self.btnVP.setNavigation(self.checkMark_DownPlay,self.btnUFA,self.btnVP,self.infoBox)
        self.btnUFA.setNavigation(self.btnVP,self.btnUV,self.infoBox,self.infoBox)
        self.btnUV.setNavigation(self.btnUFA,self.btnUFR,self.infoBox,self.infoBox)
        self.btnUFR.setNavigation(self.btnUV,self.btnF,self.infoBox,self.infoBox)
        self.btnF.setNavigation(self.btnUFR,self.checkMark_DownPlay,self.infoBox,self.infoBox)
        self.setFocus(self.infoBox)
        self.infoBox.setNavigation(self.infoBox,self.infoBox,self.btnVP,self.btnVP)
        self.infoBox.setVisible(1)
        self.videoList.setVisible(0)
        self.friendList.setVisible(0)
        return nfo

    def ViewVideoList(self,tname,mode):
        url = base_api % ("youtube."+mode,"user=" + tname)
        dp = xbmcgui.DialogProgress()
        dp.create("YouTube.com","Grabbing User Video List")
        try:
            urllib.urlretrieve(url,"E:\\info",lambda nb, bs, fs, url=url: _pbhook(nb,bs,fs,url,dp))
        except:
            self.lblCatergory.setLabel("")
            dp.close()
            return 0
        if dp.iscanceled():
            self.lblCatergory.setLabel("")
            dp.close()
            return 0
        self.title_list = []
        self.video_id_list = []
        retV = parseXMLFile("E:\\info",self)
        if retV == 0:
            self.lblCatergory.setLabel("")
            dp.close()
            return 0
        self.btnVP.setNavigation(self.checkMark_DownPlay,self.videoList,self.btnVP,self.videoList)
        self.btnUFA.setNavigation(self.btnVP,self.btnUV,self.videoList,self.videoList)
        self.btnUV.setNavigation(self.btnUFA,self.btnUFR,self.videoList,self.videoList)
        self.btnUFR.setNavigation(self.btnUV,self.btnF,self.videoList,self.videoList)
        self.btnF.setNavigation(self.btnUFR,self.checkMark_DownPlay,self.infoBox,self.infoBox)
        self.videoList.setNavigation(self.videoList,self.videoList,self.btnUFA,self.btnUFA)
        self.infoBox.setVisible(0)
        self.setFocus(self.videoList)
        self.videoList.setVisible(1)
        self.friendList.setVisible(0)
        self.curUser = tname
        dp.close()
        return 1
    def ViewFriendList(self,tname):
        url = base_api % ("youtube.users.list_friends","user=" + tname)
        dp = xbmcgui.DialogProgress()
        dp.create("YouTube.com","Grabbing Friend List")
        try:
            urllib.urlretrieve(url,"E:\\info",lambda nb, bs, fs, url=url: _pbhook(nb,bs,fs,url,dp))
        except:
            self.lblCatergory.setLabel("")
            dp.close()
            return 0
        if dp.iscanceled():
            self.lblCatergory.setLabel("")
            dp.close()
            return 0
        self.friend_list = []
        retV = parseFriendsXMLFile("E:\\info",self)
        if retV == 0:
            self.lblCatergory.setLabel("")
            dp.close()
            return 0
        self.btnVP.setNavigation(self.checkMark_DownPlay,self.friendList,self.btnVP,self.friendList)
        self.btnUFA.setNavigation(self.btnVP,self.btnUV,self.friendList,self.friendList)
        self.btnUV.setNavigation(self.btnUFA,self.btnUFR,self.friendList,self.friendList)
        self.btnUFR.setNavigation(self.btnUV,self.btnF,self.friendList,self.friendList)
        self.btnF.setNavigation(self.btnUFR,self.checkMark_DownPlay,self.friendList,self.friendList)
        self.friendList.setNavigation(self.friendList,self.friendList,self.btnUFR,self.btnUFR)
        self.infoBox.setVisible(0)
        self.videoList.setVisible(0)
        self.friendList.setVisible(1)
        self.setFocus(self.friendList)
        self.curUser = tname
        dp.close()
        return 1

    def onControl(self, control):
        if self.btnVP == control:
            tname = unikeyboard(self.curUser,"Enter in a Username to view profile infomation")
            if tname != "":
                self.lblCatergory.setLabel("Viewing Profile of %s" % tname)
                self.ViewProfile(tname)
                self.mode = 0
        elif self.btnUFA == control:
            tname = unikeyboard(self.curUser,"Enter in a Username to view favorites")
            if tname != "":
                self.lblCatergory.setLabel("Viewing Favorites of %s" % tname)
                self.ViewVideoList(tname,"users.list_favorite_videos")
                self.mode = 0
        elif self.btnUV == control:
            tname = unikeyboard(self.curUser,"Enter in a Username to view there video")
            if tname != "":
                self.lblCatergory.setLabel("Viewing Videos of %s" % tname)
                self.ViewVideoList(tname,"videos.list_by_user")
                self.mode = 0
        elif self.btnUFR == control:
            tname = unikeyboard(self.curUser,"Enter in a Username to view friends")
            if tname != "":
                self.lblCatergory.setLabel("Viewing Friends of %s" % tname)
                self.ViewFriendList(tname)
                self.mode = 0
        elif self.btnF == control:
            self.feedwin = YouTube()
            self.feedwin.doModal()
            del self.feedwin
        elif self.videoList == control:
            self.playVideo()
        elif self.friendList == control:
            if self.friendList.getSelectedPosition() != -1:
                self.createConTextFriends(self.friend_list[self.friendList.getSelectedPosition()],325)
        elif self.ContextMode == 1 and self.videoList.getSelectedPosition() != -1:
            if control == self.conButs[0]:
                self.delconOL()
                self.playVideo()
            elif control == self.conButs[1]:
                if self.mode == 0:
                    xebi('XBMC.Notification(YouTube.com,Added to Favorites)')
                    addFiletoList(self.title_list[self.videoList.getSelectedPosition()],self.video_id_list[self.videoList.getSelectedPosition()])
                else:
                    xebi('XBMC.Notification(YouTube.com,Favorites Removed)')
                    removeFromlist(self.title_list[self.videoList.getSelectedPosition()],self.video_id_list[self.videoList.getSelectedPosition()],self)
                self.delconOL()
            elif control == self.conButs[2]:
                self.delconOL()
                self.infoWin = YouTubeInfo(ext=self.title_list[self.videoList.getSelectedPosition()],id=self.video_id_list[self.videoList.getSelectedPosition()])
                self.infoWin.doModal()
                del self.infoWin
        elif  self.ContextMode == 2 and self.friendList.getSelectedPosition() != -1:
            if control == self.conButs[0]:
                tname = self.friend_list[self.friendList.getSelectedPosition()]
                self.delconOL()
                self.lblCatergory.setLabel("Viewing Profile of %s" % tname)
                self.ViewProfile(tname)
            elif control == self.conButs[1]:
                tname = self.friend_list[self.friendList.getSelectedPosition()]
                self.delconOL()
                self.lblCatergory.setLabel("Viewing Favorites of %s" % tname)
                self.ViewVideoList(tname,"users.list_favorite_videos")
            elif control == self.conButs[2]:
                tname = self.friend_list[self.friendList.getSelectedPosition()]
                self.delconOL()
                self.ViewVideoList(tname,"videos.list_by_user")
                self.lblCatergory.setLabel("Viewing Videos of %s" % tname)
            elif control == self.conButs[3]:
                tname = self.friend_list[self.friendList.getSelectedPosition()]
                self.delconOL()
                self.ViewFriendList(tname)
                self.lblCatergory.setLabel("Viewing Friends of %s" % tname)
    def playVideo(self):
        if self.videoList.getSelectedPosition() != -1:
            if self.mode == 1:
                id = self.video_id_list[self.videoList.getSelectedPosition()]
                if os.path.exists(saves_folder + id + ".flv"):
                    askWatch = xbmcgui.Dialog().yesno(__title__,"Do you want it from HDD?")
                    if askWatch == 1:
                        xbmc.Player(1).play(saves_folder + id + ".flv")
                    else:
                        self.getVideo(id,self.title_list[self.videoList.getSelectedPosition()])
                else:
                    self.getVideo(id,self.title_list[self.videoList.getSelectedPosition()])
            else:
                self.getVideo(self.video_id_list[self.videoList.getSelectedPosition()],self.title_list[self.videoList.getSelectedPosition()])
    def createConText(s,text="",ct_x=450,but2="Add To Favorites"):
        s.contextUp = 1
        # 250 is fine but over (this way its on the right)
        s.addControl(s.cbgt)
        s.addControl(s.cbgm)
        s.addControl(s.cbgb)
        s.addControl(s.clbl)
        s.addControl(s.clbgl)
        s.clbgl.addLabel(text)
        SetupButtons(s,ct_x+20,220,195,32,2,gap=10)
        s.conButs = []
        s.conButs.append(AddButton(s,'Play Video'))
        s.conButs.append(AddButton(s,but2))
        s.conButs.append(AddButton(s,'Video Info'))
        s.createnav_context()
        s.setFocus(s.conButs[0])
        s.ContextMode = 1

    def createConTextFriends(s,text="",ct_x=450):
        s.contextUp = 1
        # 250 is fine but over (this way its on the right)
        s.addControl(s.cbgt)
        s.addControl(s.cbgm)
        s.addControl(s.cbgb)
        s.addControl(s.clbl)
        s.addControl(s.clbgl)
        s.clbgl.addLabel(text)
        SetupButtons(s,ct_x+20,220,195,30,2,gap=10)
        s.conButs = []
        s.conButs.append(AddButton(s,'Their Profile'))
        s.conButs.append(AddButton(s,'Their Favorites'))
        s.conButs.append(AddButton(s,'Their Videos'))
        s.conButs.append(AddButton(s,'Their Friends'))
        s.createnav_context()
        s.conButs[0].controlUp(s.conButs[3])
        s.conButs[2].controlDown(s.conButs[3])
        s.conButs[3].controlUp(s.conButs[2])
        s.conButs[3].controlDown(s.conButs[0])
        s.setFocus(s.conButs[0])
        s.ContextMode = 2
    def createnav_context(self):
        self.conButs[0].controlDown(self.conButs[1])
        self.conButs[1].controlDown(self.conButs[2])
        self.conButs[2].controlDown(self.conButs[0])
        self.conButs[0].controlUp(self.conButs[2])
        self.conButs[1].controlUp(self.conButs[0])
        self.conButs[2].controlUp(self.conButs[1])

    def delconOL(s):
        if s.ContextMode == 1:
            s.setFocus(s.videoList)
        else:
            s.setFocus(s.friendList)
        for i in range(0,len(s.conButs)):
            s.removeControl(s.conButs[i])
        s.removeControl(s.cbgt)
        s.removeControl(s.cbgm)
        s.removeControl(s.cbgb)
        s.removeControl(s.clbl)
        s.removeControl(s.clbgl)
        s.contextUp = 0
        s.ContextMode = 0
    def getVideo(self,id,title):
        dp = xbmcgui.DialogProgress()
        dp.create("YouTube.com","Playing Video",title)
        t = self.newTvalie(id)
        v_url = base_v_url + id + "&t=" + t
        request = urllib2.Request(v_url)
        opener = urllib2.build_opener(SRH)
        f = opener.open(request)
        vid_url = f.url
        if self.checkMark_DownPlay.getSelected() == 0:
            dp.close()
            xbmc.Player(1).play(vid_url)
        else:
            if not os.path.exists(saves_folder):
                makeAllFolders(saves_folder)
            # Was going to save as Title but issue there is may be longer then fatx so instead use id
            retval = DownloaderClass(vid_url,saves_folder + id + ".flv",dp)
            if retval:
                addFiletoList(self.title_list[self.videoList.getSelectedPosition()],self.video_id_list[self.videoList.getSelectedPosition()]) # Add to Favoruties
                xbmc.Player(1).play(saves_folder + id + ".flv")
            else:
                delStuff = xbmcgui.Dialog().yesno(__title__,"Download Cancelled","Delete Part File?")
                if delStuff == 1:
                    xbmc.executehttpapi('FileDelete(' + saves_folder + id + ".flv" +')')

    def newTvalie(self,id):
        dp = xbmcgui.DialogProgress()
        dp.create("YouTube.com","Getting Session ID")
        url = base_t_url + id
        t = urllib.urlopen(url)
        dat = t.read()
        t.close()
        info = re.search(the_t_reg, dat,re.IGNORECASE)
        dp.close()
        return info.group(2)

    def getViewList(self,section,use_as_base=""):
        self.mode = 0
        dp = xbmcgui.DialogProgress()
        dp.create("YouTube.com","Getting List")
        if use_as_base == "":
            url = base_url + section
        else:
            url=  use_as_base + section
        try:
            urllib.urlretrieve(url,"Z:\\list",lambda nb, bs, fs, url=url: _pbhook(nb,bs,fs,url,dp,0.7))
        except:
            self.lblCatergory.setLabel("")
            dp.close()
            return 0
        self.videoList.reset()
        fs = open("Z:\\list", 'r')
        dat = fs.read()
        fs.close()
        dat = dat.replace("&amp;","&")
        dp.update(75)
        if dp.iscanceled():
            self.lblCatergory.setLabel("")
            dp.close()
            return 0
        dp.update(85)
        if dp.iscanceled():
            self.lblCatergory.setLabel("")
            dp.close()
            return 0
        info = the_re.findall(dat)
        self.title_list = []
        self.video_id_list = []
        self.author_list = []
        self.thumb_picurl = []
        if dp.iscanceled():
            self.lblCatergory.setLabel("")
            dp.close()
            return 0
        dp.update(90)
        for i in info:
            self.videoList.addItem(i[0])
            self.title_list.append(i[0])
            self.video_id_list.append(i[1])
        dp.close()
        return 1
    def getFavList(self):
        self.videoList.reset()
        lookstring = re.compile('<name>(.*)</name><id>(.*)</id>')
        f = open(saves_folder+"Fav.xml","r")
        d = f.read()
        f.close()
        gnfo = lookstring.findall(d)
        del d
        self.title_list = []
        self.video_id_list = []
        for i in gnfo:
            self.title_list.append(i[0])
            self.video_id_list.append(i[1])
            self.videoList.addItem(i[0])

class YouTubeInfo(xbmcgui.WindowDialog):
    def __init__(self,ext="",id=""):
        if Emulating: xbmcgui.WindowDialog.__init__(self)
        self.setCoordinateResolution(6)
        posl = 190
        #self.addControl(xbmcgui.ControlImage(posl-40,190,425,300, yPathMain+"gfx\\mc360dialog-popup.png"))
        self.addControl(xbmcgui.ControlImage(posl-40, 190-30, 425,31, yPath+"dialog-context-top.png"))
        self.addControl(xbmcgui.ControlImage(posl-40, 190, 425,270, yPath+"dialog-context-middle.png"))
        self.addControl(xbmcgui.ControlImage(posl-40, 190+270, 425,37, yPath+"dialog-context-bottom.png"))
        self.addControl(xbmcgui.ControlLabel(posl,203,360,32, "%s Video Info %s" % (__title__,ext),textColor=fc))
        self.infobox = xbmcgui.ControlTextBox(posl,245,340,185,textColor=txtboxColor,font=thefont13)
        self.addControl(self.infobox)
        self.addControl(xbmcgui.ControlImage(posl,393,32,32,yPathMain+"gfx\\button-back.png"))
        self.addControl(xbmcgui.ControlLabel(posl+40,405,200,32, "[Back] Close Infomation",textColor=fc,font=thefont13))
        yt_nfo = ShowInfo(id)

        txtnfo = ""
        txtnfo += self.info(yt_nfo,"author","Author")
        txtnfo += self.info(yt_nfo,"title","Title")
        txtnfo += self.info(yt_nfo,"rating_count","Rating Count")
        txtnfo += self.info(yt_nfo,"view_count","View Count")
        txtnfo += self.info(yt_nfo,"tags","Tags")
        self.infobox.setText(txtnfo)
        self.setFocus(self.infobox)

    def info(self,nfo,tag,nice):
        if nfo.__contains__(tag):
            if nfo == "Tags":
                return "%s: %s" % (nice,nfo[tag])
            else:
                return "%s: %s\n" % (nice,nfo[tag])
        else:
            return ""
    def onAction(self,action):
        if action == ACTION_PREVIOUS_MENU:
            self.close()
    def onControl(self,control):
        pass
class SRH(urllib2.HTTPRedirectHandler):
    def http_error_302(self, req, fp, code, msg, headers):
        result = urllib2.HTTPRedirectHandler.http_error_302(
            self, req, fp, code, msg, headers)
        result.status = code
        return result
    def http_error_303(self, req, fp, code, msg, headers):
        result = urllib2.HTTPRedirectHandler.http_error_302(
            self, req, fp, code, msg, headers)
        result.status = code
        return result

class AppURLopener(urllib.FancyURLopener):
    version = "XBMC YouTube/1.6"

def DownloaderClass(url,dest,dp):
    try:
        urllib.urlretrieve(url,dest,lambda nb, bs, fs, url=url: _pbhook(nb,bs,fs,url,dp))
        dp.close()
        return 1
    except:
        dp.close()
        xebi('XBMC.Notification(YouTube.com,Download Cancelled)')
        return 0

def _pbhook(numblocks, blocksize, filesize, url=None,dp=None,ratio=1.0):
    try:
        percent = min((numblocks*blocksize*100)/filesize, 100)
        dp.update(int(percent*ratio))
    except:
        percent = 100
        dp.update(int(percent*ratio))
    if dp.iscanceled():
        raise IOError

def addFiletoList(title,path):
    d = "<name>%s</name><id>%s</id>\n" % (title,path)
    f = open(saves_folder+"Fav.xml","a")
    f.write(d)
    f.close()

def ShowInfo(id=""):
    dp = xbmcgui.DialogProgress()
    dp.create("YouTube.com","Showing Video Details")

    url = base_api % ("youtube.videos.get_details", "video_id="+id)
    try:
        urllib.urlretrieve(url,"E:\\info",lambda nb, bs, fs, url=url: _pbhook(nb,bs,fs,url,dp))
    except:
        #self.lblCatergory.setLabel("")
        return 0
    fsock = open("E:\\info", 'r')
    dat = fsock.read()
    fsock.close()
    dat = dat.replace("&amp;","&")
    #info = re.search(the_re_getdetail, dat,re.IGNORECASE)
    lookstring = re.compile('<([^>]*)>([^</]*)</[^>]*>')
    nfo = {}
    gnfo = lookstring.findall(dat)
    nfostr = ""
    for x in gnfo:
        nfo[x[0]] = x[1]
        nfostr += "%s: %s\n" % (x[0],x[1])
    dp.close()
    return nfo
    # TO CALL INFO use  nfo['author'] # do a check first to make sure we can

def removeFromlist(title,path,win):
    ts = "<name>%s</name><id>%s</id>" % (title,path)
    f = open(saves_folder+"Fav.xml","r")
    d = f.read()
    f.close()
    d = d.replace(ts,"")
    f = open(saves_folder+"Fav.xml","w")
    f.write(d)
    f.close()
    del d
    win.getFavList()

def makeAllFolders(folderpath):
    folders = folderpath.split("\\")
    curfolderpath = folders[0]
    for i in range(1,len(folders)-1):
        curfolderpath = curfolderpath + "\\" + folders[i]
        try:
            os.mkdir(curfolderpath)
        except:
            pass
def unikeyboard(default,t):    # Open the Virutal Keyboard.
    keyboard = xbmc.Keyboard(default,t)
    keyboard.doModal()
    if (keyboard.isConfirmed()):
        return keyboard.getText()
    else:
        return default
def dbugPrnt(text,lvl=1):
    if DEBUG >= lvl:
        print text
def xebi(td):
    xbmc.executebuiltin(td)

def main():
    if not os.path.exists(saves_folder):
        makeAllFolders(saves_folder)
    print "Starting " + __title__
    urllib._urlopener = AppURLopener() # Sets Up UserAgent
    mainwin = YouTubeProfile()
    mainwin.doModal()
    del mainwin
    print "Closing " + __title__

if __name__ == "__main__":
    main()

