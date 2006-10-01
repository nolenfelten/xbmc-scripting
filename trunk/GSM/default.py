# Game Save Manger
# Coded by Donno
# BG by Sollie
# This version is an independatley skin of my Game Save Manger
# Game Saver Manger 1.5


## FREE USAGE do what you like

"""
If it crashes when loading
Please Set ur loglevel of xbmc to 1 and send me the the log
My email is darkdonno@gmail.com

"""

import xbmc, xbmcgui
import urllib
import os, codecs, string
import re, shutil
from limpp import Get_image
from os.path import join, getsize

ACTION_MOVE_LEFT       =  1
ACTION_MOVE_RIGHT      =  2
ACTION_MOVE_UP         =  3
ACTION_MOVE_DOWN       =  4
ACTION_PAGE_UP         =  5
ACTION_PAGE_DOWN       =  6
ACTION_SELECT_ITEM     =  7
ACTION_HIGHLIGHT_ITEM  =  8
ACTION_PARENT_DIR      =  9
ACTION_PREVIOUS_MENU   = 10
ACTION_SHOW_INFO       = 11
ACTION_PAUSE           = 12
ACTION_STOP            = 13
ACTION_NEXT_ITEM       = 14
ACTION_PREV_ITEM       = 15
ACTION_Y = 34
ACTION_LEFT_TRIGGER = 111
ACTION_RIGHT_TRIGGER = 112
ACTION_WHITE = 117
ACTION_B = 9

DISABLE_THUMBS = 0

global MGS_DIR
MGS_DIR = "E:\\UDATA\\"
curGS_DIR = "E:\\UDATA\\"


Root = os.getcwd().replace(";","")+"\\"

bnf=Root+"button-nofocus.png"
bf=Root+"button-focus.png"
lcf=Root+"list-nofocus.png"
lcnf=Root+"list-focus.png"
fc = "0xFFFFFFFF"
posLoc = ["E:\\UDATA\\","E:\\backup\\UDATA\\", "F:\\backup\\UDATA\\",Root+"UDATA\\"]
THUMB_FOLDER = "Q:\\UserData\\Thumbnails\\GameSaves\\"
THUMB_X = 521
THUMB_Y = 130

def ping(host):
    import socket,time
    s = socket.socket( socket.AF_INET, socket.SOCK_STREAM )
    t1=float(0)
    t2=float(0)
    t1 = float(time.time()*1000)
    try:
        s.connect(( host, 80 ))
        t2 = float(time.time()*1000)
        s.close()
        del s
        return int((t2 - t1))
    except socket.error, (errcode, errmsg):
        t2 = time.time()
        if errcode == 111:# connection refused; means that the machine is up
            return int((t2 - t1))
        else:# something else; means that the machine is not up
            return None

def onlineChecker():
    pingdns=ping("www.megaxkey.com")
    pingip=ping("70.85.73.34")
    if not(pingdns and pingip):
        xbmcgui.Dialog().ok('Game Saves',"Detected that DNS is most likey","not working correctly","Please set and try again")
        return 0
    else:
        return 1
def SetupButtons(win,x,y,w,h,gap=0,):
    win.numbut  = 0
    win.butx = x
    win.buty = y
    win.butwidth = w
    win.butheight = h
    win.gap = gap

def AddButton(win,text,ext_gap=0,text_fc=Root+"button-focus.png",textn_fc=Root+"button-nofocus.png"):
    #text_fc="button-focus.png",textn_fc="button-nofocus.png"
    win.buty = win.buty + ext_gap
    c = xbmcgui.ControlButton(win.butx ,win.buty + (win.numbut * win.butheight + win.gap*win.numbut),win.butwidth,win.butheight,text,text_fc,textn_fc,textColor=fc,font="font13",alignment=6)
    win.addControl(c)
    win.numbut += 1
    return c

class GSTitle:
    def __init__(self, name, folder, loc):
        self.name = name.encode('utf-8')
        self.folder = folder
        self.loc = loc
        self.icon = "default-gamesave.png" # heres were can set it to use a 'default' one
        self.fsize = fsizeconv(fsizeGetter(loc+folder))
class GSSave:
    def __init__(self, name, folder,icon,id):
        self.name = name.encode('utf-8')
        self.gsid = id
        self.folder = folder
        self.fsize = fsizeconv(fsizeGetter(folder))
        if os.path.exists(icon):
            self.icon = icon
        else:
            self.icon = "default-gamesave.png" # heres were can set it to use a 'default' one

class GSM(xbmcgui.Window):
    def __init__(self):
        #xbmcgui.Window.__init__(self)
        self.state = 1
        scrW = 720
        self.setCoordinateResolution(7)
        YPos_NFO = 280
        #XPos_NFO = 110
        #XPos_LST = 350

        #XPos_NFO = 460
        XPos_NFO = 515
        XPos_LST = 60
        xbmcgui.lock()
        self.view = 1
        self.dllinfo ={}
        self.GSTitles = []
        self.download_url = []
        self.mode_context = False
        self.do_action = ""

        self.addControl(xbmcgui.ControlImage(0,0, 720,576, Root+'background-gsm.png'))

        self.addControl(xbmcgui.ControlLabel(XPos_LST,80, 200,35, 'Game Save Manager', font="font13"))
        self.top_panel = xbmcgui.ControlImage(XPos_NFO-15,280, 190,216, 'middle-panel.png')
        self.bot_panel = xbmcgui.ControlImage(XPos_NFO-15,90, 190,220, 'middle-panel.png')
        self.addControl(self.top_panel)
        self.addControl(self.bot_panel)

        self.list = xbmcgui.ControlList(250, 70, 430, 340,"font13",fc,lcf,lcnf,itemTextXOffset=-5)

        self.dis_pic = xbmcgui.ControlImage(THUMB_X,THUMB_Y, 128,128,'DefaultProgramBig.png')
        self.addControl(self.dis_pic)

        self.lblGame = xbmcgui.ControlLabel(XPos_NFO, YPos_NFO,225, 25, "GameSave Name", "font16",fc)
        self.lblGSID = xbmcgui.ControlLabel(XPos_NFO,YPos_NFO+40, scrW / 2 - 60, 25, "GS ID:", "font13",fc)
        self.lblFolder = xbmcgui.ControlLabel(XPos_NFO, YPos_NFO+60, 140, 25, "Folder:", "font13",fc)
        self.lblSvs = xbmcgui.ControlLabel(XPos_NFO, YPos_NFO+80,230, 25, "Saves: ", "font13",fc)
        #self.lblLoc = xbmcgui.ControlLabel(XPos_NFO, YPos_NFO+100, scrW / 2 - 60, 25, "Source: ", "font13",fc)
        self.lblLoc = xbmcgui.ControlLabel(XPos_LST, 125, 400, 25, "Source: ", "font13",fc)
        self.lblSize = xbmcgui.ControlLabel(XPos_NFO, YPos_NFO+120, scrW / 2 - 60, 25, "Folder\File Size", "font13",fc)

        self.addControl(self.lblGame)
        self.addControl(self.lblGSID)
        self.addControl(self.lblSvs)
        self.addControl(self.lblFolder)
        self.addControl(self.lblLoc)
        self.addControl(self.lblSize)

        #self.lstGS = xbmcgui.ControlList(XPos_LST, 150, 430, 360, "font13",fc,lcf,lcnf,itemTextXOffset=4,imageWidth=32, imageHeight=32,itemHeight=32)
        self.lstGS = xbmcgui.ControlList(XPos_LST, 150, 430, 380, "font13",fc,lcf,lcnf,itemTextXOffset=4,imageWidth=32, imageHeight=32,itemHeight=32)
        self.lstGSchd = xbmcgui.ControlList(XPos_LST, 150, 430, 380, "font13",fc,lcf,lcnf,itemTextXOffset=4,imageWidth=48, imageHeight=48,itemHeight=48)

        self.addControl(self.lstGS)
        self.addControl(self.lstGSchd)
        self.lstGSchd.setVisible(0)
        self.lblGame.setVisible(0)
        self.lblGSN = xbmcgui.ControlLabel(250, 80, 300, 400,"", font="font13")
        self.lstGSN = xbmcgui.ControlList(XPos_LST, 150, 425, 380, "font13",fc,lcf,lcnf,itemTextXOffset=-5)


        self.addControl(self.lblGSN)
        self.addControl(self.lstGSN)

        self.lblGSN.setVisible(0)
        self.lstGSN.setVisible(0)
        DiaConTxt_X = 260  # 400 orignally
        self.cbg1 = xbmcgui.ControlImage(DiaConTxt_X, 215, 235,25, Root+"dialog-context-top.png")
        self.cbg2 = xbmcgui.ControlImage(DiaConTxt_X, 215+25, 235,130, Root+"dialog-context-middle.png")
        self.cbg3 = xbmcgui.ControlImage(DiaConTxt_X, 215+130+25, 235,25, Root+"dialog-context-bottom.png")
        self.addControl(self.cbg1)
        self.addControl(self.cbg2)
        self.addControl(self.cbg3)
        self.cbg1.setVisible(0)
        self.cbg2.setVisible(0)
        self.cbg3.setVisible(0)

        SetupButtons(self,DiaConTxt_X+20,215+25,200,38,5)
        self.btnCpy = AddButton(self,'Copy To')
        self.btnDel = AddButton(self,'Delete')
        self.btnDown = AddButton(self,'Download')
        self.btnCpy.setVisible(0)
        self.lblFolder.setVisible(0)
        self.btnDel.setVisible(0)
        self.btnDown.setVisible(0)

        self.state1_nav()
        xbmcgui.unlock()
        self.loadGS("E:\\UDATA\\")
    def MakeContextMenu(self):
        xbmcgui.lock()
        self.mode_context = True
        self.cbg1.setVisible(1)
        self.cbg2.setVisible(1)
        self.cbg3.setVisible(1)
        self.btnCpy.setVisible(1)
        self.btnDel.setVisible(1)
        if self.state == 1:
            self.btnDown.setVisible(1)
        else:
            self.btnDown.setVisible(1) # make this a 0 if you don't want Download button appearing while inside the game
        self.setFocus(self.btnCpy)
        xbmcgui.unlock()

    def RemoveContextMenu(self):
        xbmcgui.lock()
        self.mode_context = False
        self.cbg1.setVisible(0)
        self.cbg2.setVisible(0)
        self.cbg3.setVisible(0)
        self.btnCpy.setVisible(0)
        self.btnDel.setVisible(0)
        self.btnDown.setVisible(0)
        if self.state == 1:
            self.setFocus(self.lstGS)
            self.lblFolder.setVisible(0)
        elif self.state == 2:
            self.lblFolder.setVisible(1)
            self.setFocus(self.lstGSchd)
        elif self.state == 3:
            self.setFocus(self.lstGSN)
        else:
            self.setFocus(self.lstGS)
        xbmcgui.unlock()

    def state1_nav(self):
        self.btnCpy.controlDown(self.btnDel)
        self.btnDel.controlDown(self.btnDown)
        self.btnDown.controlDown(self.btnCpy)

        self.btnCpy.controlUp(self.btnDown)
        self.btnDel.controlUp(self.btnCpy)
        self.btnDown.controlUp(self.btnDel)

    def createDL(self):
        xbmcgui.lock()
        self.state = 3
        self.RemoveContextMenu()
        self.lstGS.setVisible(0)
        self.lstGSchd.setVisible(0)
        self.lblGSN.setVisible(1)
        self.lstGSN.setVisible(1)
        self.lblFolder.setVisible(1)
        self.lblLoc.setVisible(0)
        self.lblSvs.setVisible(0)
        self.lblGSN.setVisible(1)
        self.setFocus(self.lstGSN)
        xbmcgui.unlock()

    def RestoreDL(self):
        xbmcgui.lock()
        self.lstGS.setVisible(1)
        self.lstGSchd.setVisible(1)
        self.lblFolder.setVisible(0)
        self.lblLoc.setVisible(1)
        self.lblSvs.setVisible(1)
        self.lstGSN.setVisible(0)
        xbmcgui.unlock()

    def loadGS(self,gs_dir):
        dp = xbmcgui.DialogProgress()
        dp.create("Game Save Manger","Reading Save Games","Please Wait","Do not press Cancel")
        dp.update(0,"Reading Save Games","Please Wait","Do not press Cancel")
        try:
            lstGSdir = os.listdir(gs_dir)
        except:
            lstGSdir == []
        if lstGSdir == []:
            dp.close()
            xebi('XBMC.Notification(GSM,No Game Save Found)')
            return
        global MGS_DIR
        MGS_DIR = gs_dir
        GS_DIR = MGS_DIR
        self.lstGS.reset()
        self.GSTitles = []
        #Finding the Gamesave Title
        p = 0
        for folder in lstGSdir:
            p += 1
            if p == 1:
                dp.update(int(p/ float(len(lstGSdir))*100),"Reading Save Games",folder,"Do not press Cancel")
            #if dp.iscanceled():
            #    return
            if os.path.isdir(GS_DIR + folder):
                strFilePath = GS_DIR + folder + "\\TitleMeta.xbx"
                #Check to see the .xbx exists file.
                if os.path.exists(strFilePath):
                    strFile = open(strFilePath , "r")
                    gscheck = strFile.read()
                    strFile.close
                    #Check for plaintext .xbx file.
                    if gscheck[0:5] == "Title":
                        aName = gscheck[10:]
                        tmp = GSTitle(aName, folder, GS_DIR)
                        self.GSTitles.append(tmp)
                    else:
                        uFile = codecs.open(strFilePath , "r", "utf-16")
                        try:
                            ugscheck = uFile.read()  #One tester got error > utf16' codec can't decode bytes in position 3226-3227: illegal encoding
                        except:
                            if DISABLE_THUMBS == 0:
                                ugscheck="TitleName=Can not read title  "
                            else:
                                ugscheck="TitleName=%s  " % folder
                        uFile.close
                        fndTitle = string.find(ugscheck, "Title")
                        #Unicode UTF-16, Xbx with Title Only
                        if ugscheck[0:5] == "Title":
                            aName = ugscheck[10:-2]
                            aName = aName.strip()
                            tmp = GSTitle(aName, folder, GS_DIR)
                            self.GSTitles.append(tmp)
                        #Uuencode UTF-16, Xbx with Extra Parameters
                        elif fndTitle > 1:
                            fndReturn = string.find(ugscheck[fndTitle:], '\r')
                            foo = fndTitle+fndReturn
                            aName = ugscheck[fndTitle+10:foo]
                            aName = aName.strip()
                            tmp = GSTitle(aName, folder, GS_DIR)
                            self.GSTitles.append(tmp)

                        if DISABLE_THUMBS == 0:
                            self.getImg(GS_DIR + folder + "\\TitleImage.xbx",folder)
                            self.getImg(GS_DIR + folder + "\\SaveImage.xbx","sg"+folder) #a adding the sg makes it so its the sg image :D
                else:
                    aName = "Reading Save Games"
                dp.update(int(p/ float(len(lstGSdir))*100),"Reading Save Games",aName,"Do not press Cancel")
        self.GSTitles.sort(lambda x, y: cmp(x.name, y.name))
        for item in self.GSTitles:
            if DISABLE_THUMBS == 0:
                icon =  THUMB_FOLDER+item.folder+".png"
                if os.path.exists(icon):
                    item.icon = icon
                if len(item.name) > 30:
                    self.lstGS.addItem(xbmcgui.ListItem(item.name[0:28]+"...",item.folder,item.icon,item.icon))
                else:
                    self.lstGS.addItem(xbmcgui.ListItem(item.name,item.folder,item.icon,item.icon))
            else:
                self.lstGS.addItem((item.name))
        self.setFocus(self.lstGS)
        dp.close()
        self.GSUpdt()

    def getImg(self,filename,id,name=""):
        if os.path.exists(filename):
            dest = THUMB_FOLDER+id+".png"
            if getsize(filename) != 0:
                if not os.path.exists(dest):
                    img = Get_image(file=filename)
                    if img:
                        file = os.path.join(dest)
                        if img.type == "BMP":
                            shutil.copy(filename, file)
                        else:
                            img.Write_PNG(file)

    def onAction(self, action):
        #print str(action)
        if action == ACTION_Y:
            if self.state != 3:
                ndex = xbmcgui.Dialog().select("Select Source for Saves", posLoc)
                if ndex != -1:
                    if os.path.exists(posLoc[ndex]):
                        self.loadGS(posLoc[ndex])
                    else:
                        xebi('XBMC.Notification(GSM,No Game Save Found)')
                    if self.state == 2:
                        self.actBack()
        elif action == ACTION_WHITE:
            if self.state == 1:
                if self.lstGS.getSelectedPosition() != -1:
                    self.MakeContextMenu()
                if self.lstGSchd.getSelectedPosition() != -1:
                    self.MakeContextMenu()
        if self.mode_context:
            if action == ACTION_PREVIOUS_MENU or action == ACTION_B:
                self.RemoveContextMenu()
        elif self.state == 1:
            if action == ACTION_PREVIOUS_MENU:
                self.close()
        elif self.state >= 2 and action == ACTION_PREVIOUS_MENU:
            self.close()
        elif self.state >= 2 and action == ACTION_B:
            self.actBack()
        if (self.lstGS.getSelectedPosition()  != -1 and self.getFocus() == self.lstGS) or (self.lstGSchd.getSelectedPosition()  != -1 and self.getFocus() == self.lstGSchd) or (self.lstGSN.getSelectedPosition()  != -1 and self.getFocus() == self.lstGSN):
            if action == ACTION_MOVE_DOWN or action == ACTION_MOVE_UP or action == ACTION_LEFT_TRIGGER or action == ACTION_RIGHT_TRIGGER:
                self.doAction()
    def doAction(self):
        if self.state != 3:
            self.GSUpdt()
        else:
            self.GSDLLUpdt()
    def actBack(self):
        
        if self.state == 3:
            self.RestoreDL()
        xbmcgui.lock()
        self.state = 1
        self.lstGS.setVisible(1)
        self.lstGSchd.setVisible(0)
        self.lblGSN.setVisible(0)
        self.lblLoc.setVisible(1)
        self.lblFolder.setVisible(0)
        self.lstGSchd.reset()
        xbmcgui.unlock()
        self.state1_nav()
        self.setFocus(self.lstGS)
        global MGS_DIR
        if self.do_action == "DEL":
            self.loadGS(MGS_DIR)
            self.do_action = ""
        self.GSUpdt()
        

    def onControl(self, control):
        global MGS_DIR
        if control == self.btnDel:
            if self.state == 1:
                if self.lstGS.getSelectedPosition() != -1:
                    self.GSDel()
            elif self.state == 2:
                if self.lstGSchd.getSelectedPosition() != -1:
                    self.GSDel()
            self.RemoveContextMenu()
        elif control == self.btnCpy:
            if self.state == 1 and self.lstGS.getSelectedPosition() == -1:
                return
            elif self.state == 2 and self.lstGSchd.getSelectedPosition() == -1:
                return
            posLocations = []
            for i in posLoc:
                if MGS_DIR != i:
                    posLocations.append(i)
            dlgCpy = xbmcgui.Dialog()
            if self.state == 1:
                ndex = dlgCpy.select("Select copy destination?", posLocations)
                chcCpy = posLocations[ndex]
                srcCpy = self.GSTitles[self.lstGS.getSelectedPosition()].loc + self.GSTitles[self.lstGS.getSelectedPosition()].folder + "\\"
                dstCpy = str(chcCpy) + self.GSTitles[self.lstGS.getSelectedPosition()].folder + "\\"
                makeAllFolders(dstCpy)
            if self.state == 2:
                ndex = dlgCpy.select("Select copy destination?", posLocations)
                chcCpy = posLocations[ndex]
                srcCpy = self.GSSaves[self.lstGSchd.getSelectedPosition()].folder + "\\"
                dstCpy = str(chcCpy) + self.GSSaves[self.lstGSchd.getSelectedPosition()].folder.replace(MGS_DIR,"")
                makeAllFolders(dstCpy)
                self.copySGI(recompileFP(srcCpy,1),str(chcCpy)+recompileFP(srcCpy,1)[9:]) # So we have the info for new save
            if ndex != -1:
                self.cpyloc(srcCpy, dstCpy,self.state)
            self.RemoveContextMenu()
        if control == self.lstGSN:
            if self.lstGSN.getSelectedPosition() != -1:
                dest="Z:\\savegame.zip"
                retVal = downloader(self.dllinfo['url'][self.lstGSN.getSelectedPosition()],dest)
                if retVal == 1:
                    installer()
        elif control == self.lstGS:
            
            self.RemoveContextMenu()
            
            if self.lstGS.getSelectedPosition() != -1:
                xbmcgui.lock()
                self.state = 2
                self.lblFolder.setVisible(1)
                self.lstGS.setVisible(0)
                self.lstGSchd.setVisible(1)
                self.lblGSN.setVisible(1)
                self.setFocus(self.lstGSchd)
                self.lblGSN.setLabel(self.GSTitles[self.lstGS.getSelectedPosition()].name)
                xbmcgui.unlock()
                self.loadSaves(self.GSTitles[self.lstGS.getSelectedPosition()].loc + self.GSTitles[self.lstGS.getSelectedPosition()].folder,self.GSTitles[self.lstGS.getSelectedPosition()].folder)
                
            """
            # Till XBMC fixes this problem this will be disabled
            # Note u must unindent this once
            elif control == self.btnView:
                if self.view == 1:
                    self.view = 2
                    self.btnView.setLabel("View: Big Icons")
                    self.lstGS.setImageDimensions(64,64)
                    self.lstGSchd.setImageDimensions(64,64)
                    self.lstGS.setItemHeight(64)
                    self.lstGSchd.setItemHeight(64)
                else:
                    self.view = 1
                    self.btnView.setLabel("View: Icons")
                    self.lstGS.setImageDimensions(32,32)
                    self.lstGSchd.setImageDimensions(48,48)
                    self.lstGS.setItemHeight(32)
                    self.lstGSchd.setItemHeight(48)
        """
        elif control == self.lstGSchd:
            if self.lstGSchd.getSelectedPosition() != -1:
                self.MakeContextMenu()
        elif control == self.btnDown:
            #xbmcgui.Dialog().ok("Game Saves","Game Save Website Is Down")
            #"""
            xbmcgui.lock()
            self.RemoveContextMenu()
            if self.lstGS.getSelectedPosition() != -1:
                self.lstGSN.reset()
                self.lblGSN.setVisible(1)
                self.lblGSN.setLabel(self.GSTitles[self.lstGS.getSelectedPosition()].name)
                self.dllinfo ={}
                self.dllinfo['url'] = []
                self.dllinfo['size'] = []
                self.dllinfo['creator'] = []
                self.createDL()
                self.getDLDlst(self.GSTitles[self.lstGS.getSelectedPosition()].folder)
                self.GSDLLUpdt()
            xbmcgui.unlock()
            #"""
    def copySGI(self,s,d):
        if not os.path.exists(d+"SaveImage.xbx"):
            shutil.copy(s+"SaveImage.xbx", d+"SaveImage.xbx")
        if not os.path.exists(d+"TitleImage.xbx"):
            shutil.copy(s+"TitleImage.xbx", d+"TitleImage.xbx")
        if not os.path.exists(d+"TitleMeta.xbx"):
            shutil.copy(s+"TitleMeta.xbx", d+"TitleMeta.xbx")
    def getDLDlst(self,gid):
        self.download_url = []
        wsock = urllib.urlopen("http://www.megaxkey.com/unleashx.php?gameid=" + str(gid))
        thexml = wsock.read()
        wsock.close()
        if "<TITLE>400 Bad Request</TITLE>" in thexml.lower():
            xbmcgui.Dialog().ok("A error has occured")
        regex = '<save desc="(.*)" creator="(.*)" url="(.*)" size="(.*)"/>'
        save_info = re.compile(regex,re.IGNORECASE).findall(thexml)
        for s in save_info:
            self.lstGSN.addItem(str(s[0]))
            self.dllinfo['creator'].append(str(s[1]))
            self.dllinfo['url'].append(str(s[2]))
            self.dllinfo['size'].append(str(s[3]))
        if '<?xml version="1.0" encoding="utf-8"?>\n<xboxsaves/>' == thexml:
            xbmc.log("no info Found")
            xbmcgui.Dialog().ok("Game Saves","No Saves Games found", "For "+ self.GSTitles[self.lstGS.getSelectedPosition()].name)
            self.actBack()

    def GSDel(self):
        if self.state == 1:
            if xbmcgui.Dialog().yesno("Delete Confirmation", "Are you sure you want to delete ",self.GSTitles[self.lstGS.getSelectedPosition()].name + "?"):
                try:
                    shutil.rmtree(self.GSTitles[self.lstGS.getSelectedPosition()].loc + self.GSTitles[self.lstGS.getSelectedPosition()].folder)
                except:
                    pass
                try:
                    shutil.rmtree(self.GSTitles[self.lstGS.getSelectedPosition()].loc.replace("UDATA","TDATA")+self.GSTitles[self.lstGS.getSelectedPosition()].folder)
                except:
                    pass
                global MGS_DIR
                lstGSdir = os.listdir(MGS_DIR)
                if lstGSdir == []:
                    self.loadGS("E:\\UDATA\\")
                else:
                    self.loadGS(MGS_DIR)
        elif self.state == 2:
            if xbmcgui.Dialog().yesno("Delete Confirmation", "Are you sure you want to delete " + self.GSSaves[self.lstGSchd.getSelectedPosition()].name + "?"):
                try:
                    shutil.rmtree(self.GSSaves[self.lstGSchd.getSelectedPosition()].folder)
                except:
                    pass
                self.lstGSchd.reset()
                self.loadSaves(self.GSTitles[self.lstGS.getSelectedPosition()].loc + self.GSTitles[self.lstGS.getSelectedPosition()].folder,self.GSTitles[self.lstGS.getSelectedPosition()].folder)
                self.do_action = "DEL"

    def cpyloc(self, source, destination,type):
        dialog = xbmcgui.Dialog()
        ecc = 0
        if not os.path.exists(destination):
            try:    shutil.copytree(source, destination)
            except:
                print "Shouldn't get error here"
                ecc += 1
            xebi('XBMC.Notification(GSM,Save Game Copied)')
        else:
            if type == 2:
                if dialog.yesno("Warning","Detected, destination already exists",str(destination),"Would you like to delete then copy?"):
                    shutil.rmtree(destination)
                    self.cpyloc(source,destination,type)
                    return
                else:
                    xebi('XBMC.Notification(GSM,Copy Aborted)')
            else:
                posChocies = ["Leave","Delete and Copy", "Copy and Overwrite"]
                ndex = xbmcgui.Dialog().select("Action to Take", posChocies)
                if ndex < 1:
                    xebi('XBMC.Notification(GSM,Copy Aborted)')
                elif ndex == 1:
                    shutil.rmtree(destination)
                    self.cpyloc(source,destination,type)
                    xebi('XBMC.Notification(GSM,Save Game Copied)')
                    return
                elif ndex == 2:
                    recusive_copier(source,destination)
                    xebi('XBMC.Notification(GSM,Save Game Copied)')
                else:
                    xebi('XBMC.Notification(GSM,Failed to Selection)')
        if ecc != 0:
            xbmcgui.Dialog().ok("Error Copying", source, ' to ',destination)

    def loadSaves(self, dir,id):
        lstSGdir = os.listdir(dir)
        self.GSSaves = []
        for save in lstSGdir:
            try:
                if save[-4] != ".":
                    alte = os.path.exists(dir + "\\" + save + "\\SaveImage.xbx")
                    strSGFile = codecs.open(dir + "\\" + save + "\\SaveMeta.xbx", 'r', 'UTF-16')
                    strSavName = strSGFile.read()
                    fndReturn = string.find(strSavName, '\r')
                    aName = strSavName[5:fndReturn]
                    aName = aName.strip()
                    icon = THUMB_FOLDER+"sg"+id+".png"
                    if DISABLE_THUMBS == 0:
                        if alte:
                            self.getImg(dir + "\\" + save + "\\SaveImage.xbx","sgs"+save) # The other SaveImage is the default for whole game, this one checks
                            icon = THUMB_FOLDER+"sgs"+save+".png"
                    tmp = GSSave(aName, dir + "\\" + save,icon,id)
                    self.GSSaves.append(tmp)
            except: pass
        for aSave in self.GSSaves:
            if DISABLE_THUMBS == 0: self.lstGSchd.addItem(xbmcgui.ListItem(aSave.name,"",aSave.icon,aSave.icon))
            else:   self.lstGSchd.addItem(aSave.name)
        self.GSUpdt()

    def GSUpdt(self):
        global MGS_DIR
        self.lblLoc.setLabel('Source Location: %s' % MGS_DIR)
        self.lblLoc.setVisible(1)
        if self.state == 1:
            if self.lstGS.getSelectedPosition() != -1:
                self.lblGSID.setLabel('GS ID: ' + self.GSTitles[self.lstGS.getSelectedPosition()].folder)
                self.lblGame.setLabel(self.GSTitles[self.lstGS.getSelectedPosition()].name)
                self.lblFolder.setLabel('Folder: ' + self.GSTitles[self.lstGS.getSelectedPosition()].folder)
                try:
                    x = 0
                    lstSGdir = os.listdir(self.GSTitles[self.lstGS.getSelectedPosition()].loc + self.GSTitles[self.lstGS.getSelectedPosition()].folder)
                    for save in lstSGdir:
                        if save[-4] != ".":
                            x = x + 1
                except: x = 0
                self.lblSvs.setLabel('Saves: ' + str(x))
                self.lblSize.setLabel(self.GSTitles[self.lstGS.getSelectedPosition()].fsize)
                self.removeControl(self.dis_pic)
                self.dis_pic = xbmcgui.ControlImage(THUMB_X,THUMB_Y, 128,128, self.GSTitles[self.lstGS.getSelectedPosition()].icon)
                self.addControl(self.dis_pic)
        elif self.state == 2:
            if self.lstGSchd.getSelectedPosition() != -1:
                tgssave = self.GSSaves[self.lstGSchd.getSelectedPosition()]
                thefolder =  tgssave.folder
                thefolder = thefolder.replace(MGS_DIR,"")
                self.lblGSID.setLabel('GS ID: ' + tgssave.gsid)
                thefolder = thefolder.replace(tgssave.gsid,"")
                self.lblLoc.setLabel('Item Location: %s%s\\' % (MGS_DIR,tgssave.gsid))
                self.lblFolder.setLabel('Folder: ')
                self.lblSvs.setLabel(' ' + thefolder)
                self.lblSize.setLabel(tgssave.fsize)
                self.removeControl(self.dis_pic)
                self.dis_pic = xbmcgui.ControlImage(THUMB_X,THUMB_Y, 128,128, tgssave.icon)
                self.addControl(self.dis_pic)


    def GSDLLUpdt(self):
        if self.lstGSN.getSelectedPosition() != -1:
            fsize = int(self.dllinfo['size'][self.lstGSN.getSelectedPosition()])
            self.lblSize.setLabel(fsizeconv(fsize))
            self.lblFolder.setLabel("Creator: "+ str(self.dllinfo['creator'][self.lstGSN.getSelectedPosition()]))
"""
## FTP CODE START ##
## For this to work would need to add few extra varibles also needs probley some more improving.
def copyToFTP(ip,un,pwd,sgf,bf):
    import ftplib
    ftp = ftplib.FTP(ip)
    try:    ftp.login(un,pwd)
    except Exception, e:
        if str(e) == "421 Too many users are connected, please try again later.": print "TOO MANY USERS" # Show Notificaiton
        else: print ">%s<" % e
        return
    init_dir = "/E/backup/UDATA/"+sgf+"/"
    fmkd(ftp,init_dir)
    ftp.cwd(init_dir)
    os.path.walk(bf, callback, [ftp,bf,init_dir])
    ftp.quit()
    ftp.close()

def fmkd(ftp,folderpath):
    folders = folderpath.split("/")
    curfolderpath = "/" + folders[1] + "/"
    for i in range(2,len(folders)-1):
        ftp.cwd(curfolderpath)
        curfolderpath = curfolderpath + folders[i]+ "/"
        try:    ftp.mkd(folders[i]) # Make Fist Folder
        except: pass

def upFile(ftp,filename,path):
    fnp = os.path.join(path, filename)
    open(fnp,"rb")
    ftp.storbinary("STOR "+filename,open(fnp,"rb"))
def callback(a, d, f):
    for file in f:
        if os.path.exists(os.path.join(d, file)):
            if os.path.isdir(os.path.join(d, file)):
                try:    a[0].mkd(a[2] + file)
                except: pass
            else:
                a[0].cwd(a[2]+ d.replace(a[1],""))
                upFile(a[0],file,d)
Usage: copyToFTP('10.10.1.51','xbox','xbox',"4c410013","e:\\udata\\4c410013\\")
"""
def fsizeGetter(path):
    fSize = 0
    for root, dirs, files in os.walk(path):
        for name in files:
            fSize = fSize + getsize(join(root, name))
    return fSize

def recusive_copier(src,dest):
    for i in os.listdir(src):
        ts = os.path.join(src,i)
        ds = os.path.join(dest,i)
        if os.path.isdir(ds):
            if os.path.exists(ts):  # Check if desination exists if so then run teh 'recusive_copier
                recusive_copier(ts,ds)
            else:
                try:    shutil.copytree(ts, ds)# Coz it doesn't exist we can copy tree
                except: pass
        else:
            if os.path.exists(ds):
                xbmc.executehttpapi('FileDelete(' + ds +')')
            try: shutil.copy(ts, os.path.join(dest,i))
            except: pass
            #print ("<src>%s</src><dest>%s</dest>") % (ts,ds),

def downloader(url,dest="Z:\\savegame.zip"):
    xbmc.executehttpapi('FileDelete(' + dest +')')
    dp = xbmcgui.DialogProgress()
    dp.create("GSM","Downloading File",url)
    try:
        urllib.urlretrieve(url,dest,lambda nb, bs, fs, url=url: _pbhook(nb,bs,fs,url,dp))
        dp.close()
        return 1
    except:
        dp.close()
        xebi('XBMC.Notification(MC360,Download Cancelled)')
        return 0

def recompileFP(path,numoff=0):
    src_array = path.split("\\")
    GameSaveSrc = ""
    for x in range(0,len(src_array)-1-numoff): # we take 1 be default as filepath is usally   something\\   (therefore after \\ == dischaded by the -1
        GameSaveSrc += src_array[x] + "\\"
    return GameSaveSrc

def xebi(td):
    xbmc.executebuiltin(td)

def _pbhook(numblocks, blocksize, filesize, url=None,dp=None):
    try:
        percent = min((numblocks*blocksize*100)/filesize, 100)
        dp.update(percent)
    except:
        percent = 100
        dp.update(percent)
    if dp.iscanceled():
        raise IOError
def installer(file="Z:\\savegame.zip"):
    if xbmcgui.Dialog().yesno("Install","Install Save Game?"):
        xbmc.executebuiltin('XBMC.Extract('+file+',' +"e:\\" + ')')
        xbmc.executehttpapi('FileDelete(e:\\gameid.ini)') # get rid of this file
        xbmcgui.Dialog().ok("Game Saves","Game Save Installed")
    else:
        xbmcgui.Dialog().ok("Game Saves","Game Save Not Installed")

def fsizeconv(num):
    if num < 1024:
        return str("Size: " + str(num) + " bytes")
    elif num < 1048576:
        return str("Size: " + str(num / 1024) + " KB")
    elif num < 1073741824:
        return str("Size: " + str(num / 1048576) + " MB")
    else:
        return str("Size: " + str(num / 1073741824) + " GB")

def ctrl(text,x,y,cbnf=bnf):
    # Set alignment to 4 for   x: left   y: center
    return xbmcgui.ControlButton(x , y, 200, 50, text,bf,cbnf,alignment=6,textColor=fc,textXOffset=5)

def makeAllFolders(folderpath):
    folders = folderpath.split("\\")
    curfolderpath = folders[0]
    for i in range(1,len(folders)-1):
        curfolderpath = curfolderpath + "\\" + folders[i]
        try:    os.mkdir(curfolderpath) # Make Fist Folder
        except: pass

def main():
    if not os.path.exists(Root+"UDATA"):    os.mkdir(Root+"UDATA")
    if not os.path.exists(THUMB_FOLDER):    os.mkdir(THUMB_FOLDER)
    mydisplay = GSM()
    mydisplay.doModal()
    del mydisplay
if __name__ == "__main__":
    main()
