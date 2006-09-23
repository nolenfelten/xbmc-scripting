"""
    YouTube.Com Script for XBMC
    Using RSS Feed for the Data
    Coding By Donno [darkdonno@gmail.com]
    BackButton by BlackBolt
    Version: 1.7

    Changes Since 1.7
        - Cosmetic (PM1,PM2 and PM3 Native Support and PDM)
        - Special MC360 Version
        - Any other skin will look like PM3
        
    Changes Since 1.6
        - Hooked up INFO button to same behaviour as Y
        - Hooked up pressing PLAY on the List will play the video
        - Finally Hooked up teh Video Info
        - Added Context Menu (White/Title)
    Changes Since 1.5
        - Fixed REGEXP Due to Site changes
    Changelog Since 1.3
        - Fixed Due to Site Changes
        - Main Regexp string 'improved'

    Incomplete: Used
        - i[3] == Thumbnail URL << might need to create a 'thread' for doing url stuff in background so not to slow down browsing

    For Future Version: [if i ever get time to do it]
        - Help Pictures
        - Infomation <author>,  some of the <description> , credit,  catergory,pubdate
        - Maybe thumbnail

    Notes:
        Make Sure the save_folder has a trailling \\
        Have Fun

    HELP:
    Pressing White/Title will open Context Menu
    Press Y/Info to go into "Favorites'


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
yPath = os.getcwd().replace(";","")+"\\gfx\\"
yPathMain = os.getcwd().replace(";","")+"\\"

SD = xbmc.getSkinDir().lower() 

fc = "0xFFFFFFFF"
txtboxColor = fc
if SD == "pdm":
    yPath = ""
if  SD == "project mayhem ii" or  SD == "project mayhem 1":
    yPath = ""
    txtboxColor = "0xFF000000"

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

""" Create your script's Main Window """
class YouTube(xbmcgui.Window):
    def __init__(self):
        if Emulating: xbmcgui.Window.__init__(self)
        global yPath
        """ Define your sript's Window size here: """
        self.scaleX = ( float(720)  / float(720) )
        self.scaleY = ( float(576)  / float(576) )
        self.setCoordinateResolution(6)


        """ Add your GUI images to your script here: """
        self.addControl(xbmcgui.ControlImage(0,0,720,576, yPath+"Background.png"))
        
        self.addControl(xbmcgui.ControlImage(50,45,200,60, yPathMain+"youtube.png"))
        self.lblCatergory = xbmcgui.ControlLabel(320,75,200,60,"",font=thefont14,textColor=fc)
            
        self.addControl(self.lblCatergory)
        """ Create your Menu buttons here: """
        SetupButtons(self, int(45 * self.scaleX),int(110 * self.scaleY), int(155 * self.scaleX), int(28 * self.scaleY), "Vert", button_hl,button_normal, 2,5)
        self.btnRA = AddButton(self,'Recently Added')
        self.btnRF = AddButton(self,'Recently Featured')
        self.btnTF = AddButton(self,'Top Favorites')
        self.btnTR = AddButton(self,'Top Rated')
        self.btnMV = AddButton(self,'Most Viewed')
        self.btnMD = AddButton(self,'Most Discussed')
        self.btnTag = AddButton(self,'** Tag **')
        self.btnSearch = AddButton(self,'** Search **')

        self.lblCatOpen = xbmcgui.ControlLabel(40,350,205,60,"",font=thefont14,textColor=fc)
        self.addControl(self.lblCatOpen)
        SetupButtons(self, int(45 * self.scaleX),int(380 * self.scaleY), int(155 * self.scaleX), int(28 * self.scaleY), "Vert", button_hl,button_normal, 2,5)
        self.btnMVT = AddButton(self,'- Today')
        self.btnMTW = AddButton(self,'- This Week')
        self.btnMTN = AddButton(self,'- This Month')
        self.btnMAT = AddButton(self,'- All Time')
        self.title_list = []
        self.video_id_list = []
        self.author_list = []
        self.thumb_picurl = []
        SetupButtons(self, int(45 * self.scaleX),int(380 * self.scaleY), int(155 * self.scaleX), int(28 * self.scaleY), "Vert", button_hl,button_normal, 2,5)
        self.btnMDVT = AddButton(self,'- Today')
        self.btnMDVTW = AddButton(self,'- This Week')
        self.btnMDVTM = AddButton(self,'- This Month')
        self.selT = 0
        self.mode = 0

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
        if SD == "pdm":
            yPath = ""
            self.checkMark_DownPlay = xbmcgui.ControlCheckMark(55, 525,200, 20,"Save",yPath+"check-box.png",yPath+"check-boxNF.png",font=thefont10,textColor=fc)
        else:
            self.checkMark_DownPlay = xbmcgui.ControlCheckMark(55, 500,200, 20,"Save",yPath+"check-box.png",yPath+"check-boxNF.png",font=thefont10,textColor=fc)
        #self.checkMark_ThumbDown = xbmcgui.ControlCheckMark(55, 530,200, 20,"Thumbs")
        self.addControl( self.checkMark_DownPlay)
        #self.addControl( self.checkMark_ThumbDown)

        self.videoList = xbmcgui.ControlList(int(215 * self.scaleX),int(120 * self.scaleY), int(450 * self.scaleX), int(365 * self.scaleY),"font12",fc,yPath+"list-nofocus.png",yPath+"list-focus.png",itemTextXOffset=-10,)
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
        print info.group(1)
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
            """"
            self.videoList.addItem(i[1])
            self.author_list.append(i[0])
            self.title_list.append(i[1])
            self.video_id_list.append(i[2])
            self.thumb_picurl.append(i[3])
            """
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
        if SD == "pdm":
            self.addControl(xbmcgui.ControlImage(posl-40,190,425,300, yPath+"dialog-popup.png"))
            self.addControl(xbmcgui.ControlLabel(posl+5,215,350,32, "%s Video Info %s" % (__title__,ext),textColor=fc))
            self.infobox = xbmcgui.ControlTextBox(posl,255,340,175,textColor=txtboxColor,font=thefont13)
        else:
            self.addControl(xbmcgui.ControlImage(posl-40,190,425,300, yPath+"dialog-popup.png"))
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
    mainwin = YouTube()
    mainwin.doModal()
    del mainwin
    print "Closing " + __title__

if __name__ == "__main__":
    if SD == "mc360":
        xbmc.executebuiltin("XBMC.RunScript(%syt-mc360.py)" % yPathMain)
    else:
        main()

