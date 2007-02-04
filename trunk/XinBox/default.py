# -*- coding: cp1252 -*-
      ##########################
      #                        #                      
      #   XinBox (V.0.3)       #         
      #     By Stanley87       #         
      #                        #
#######                        #######             
#                                    #
#                                    #
#   A pop3 email client for XBMC     #
#                                    #
######################################

import sys, email, xbmcgui, xbmc
import string, time, mimetypes, re, os
import poplib
import shutil
import threading

Root_Dir = os.getcwd().replace(";","")+"\\"
SRC_Dir = Root_Dir + "Src\\"
DATA_DIR = SRC_Dir + "Data\\"
DELETEFOLDER = "Deleted\\"
IDFOLDER = "IDS\\"
IMAGE_DIR = SRC_Dir + "Images\\"
LANGFOLDER = SRC_Dir+"Language\\"
NEWFOLDER = "NEW\\"
CORFOLDER = "COR\\"
   
SETTINGS_FILE = "settings.xml"

TEMPFOLDER = SRC_Dir + "temp\\"
VERSION = "(V.0.3)"

class Language:
	"""
		Language Class
			For reading in xml for automatiacall of the selected lanauge XBMC is running in
			And for returning the string in the given Language for a specified id
		Oringally Coded by Rockstar, Recoded by Donno :D
	"""
	def load(self,thepath):
		self.strings = {}
		tempstrings = []
		self.language = xbmc.getLanguage().lower()
		if os.path.exists(thepath+self.language+"\\strings.xml"):
			self.foundlang = self.language
		else:
			self.foundlang = "english"
		self.langdoc = thepath+self.foundlang+"\\strings.xml"
		print "-Loading Language: " + self.foundlang
		try:
			f=open(self.langdoc,'r')
			tempstrings=f.read()
			f.close()
		except:
			print "Error: Languagefile "+self.langdoc+" cant be opened"
			xbmcgui.Dialog().ok(__title__,"Error","Languagefile "+self.langdoc+" cant be opened")
		self.exp='<string id="(.*?)">(.*?)</string>'
		self.res=re.findall(self.exp,tempstrings)
		for stringdat in self.res:
			self.strings[int(stringdat[0])] = str(stringdat[1])

	def string(self,number):
		if int(number) in self.strings:
                        if self.foundlang == "french":
                                return self.strings[int(number)]
                        elif self.foundlang == "english":
                                return self.strings[int(number)]
                        else:
                                return unicode (self.strings[int(number)], 'utf-8')
		else:
			return "unknown string id"





class minis(xbmcgui.WindowDialog):
    def __init__(self):                               
            global minimssg
            self.setResolution()
            minibackground = xbmcgui.ControlImage(370,470,325,100, IMAGE_DIR + "pop.png")
            infoicon = xbmcgui.ControlImage(400,490,40,40, IMAGE_DIR + "infoicon.png")
            info = xbmcgui.ControlLabel(370,485,300,300, minimssg, "font18", alignment=2)
            self.addControl(minibackground)
            self.addControl(infoicon)
            self.addControl(info)
            try:
                DELAY =5
                self.a = -1
                self.shown = 1
            except:
                print "var"
           
            subThread = threading.Thread(target=self.SubthreadProc, args=())
            subThread.start()
          
    def SubthreadProc(self):
            time.sleep(8)
            if self.shown:
                    self.close()

    def setResolution( self ):
        #Thanks to Nuka for this function :-D
        global reso
        try:
            offset = 0
            resolutions = {'1080i' : 0, '720p' : 1, '480p' : 2, '480p16x9' : 3, 'ntsc' : 4, 'ntsc16x9' : 5, 'pal' : 6, 'pal16x9' : 7, 'pal60' : 8, 'pal6016x9' : 9}
            currentResolution = self.getResolution()
            resolution = resolutions[ 'pal' ]
            # if current and skinned resolutions differ and skinned resolution is not
            # 1080i or 720p (they have no 4:3), calculate widescreen offset
            if (( not ( currentResolution == resolution )) and resolution > 1 ):
                # check if current resolution is 16x9
                if ( currentResolution == 0 or currentResolution % 2 ): iCur16x9 = 1
                else: iCur16x9 = 0
                # check if skinned resolution is 16x9
                if ( resolution % 2 ): i16x9 = 1
                else: i16x9 = 0
                # calculate widescreen offset
                offset = iCur16x9 - i16x9
            self.setCoordinateResolution( resolution + offset )
            reso = self.CoordinateResolution
        except: print 'ERROR: setting resolution'

    def onAction(self, action):
            global minimssg, openmail, test
            if action == 10: #
                self.close()
                test = 0
                m = xbmcmail()
                m.imback()
                m.doModal()
                del m
            else:
                self.close()


class xbmcmail(xbmcgui.Window):
    def __init__(self):
        global lang
        lang = Language()
        lang.load(LANGFOLDER)
        self.fullscreen = False
        self.showingimage = False
        self.setting1 = 0
        screenheight = self.getHeight()
        self.settings = False
        self.setResolution()
        self.addControl(xbmcgui.ControlImage(0,0,720,576, IMAGE_DIR+'background.png'))
        self.fsoverlay = xbmcgui.ControlImage(0,0,720,576,IMAGE_DIR+ 'background.png')
        self.seoverlay = xbmcgui.ControlImage(0,0,720,576,IMAGE_DIR+ 'background.png')
        self.title = xbmcgui.ControlLabel(250, 80, 200, 100, "XinBox", "font18", "FFB2D4F5")
        self.cmButton = xbmcgui.ControlButton(64, 158, 135, 30, "XinBox 1",focusTexture=IMAGE_DIR+ 'button-focus.png',noFocusTexture=IMAGE_DIR+ 'button-nofocus.png')
        self.csButton = xbmcgui.ControlButton(64, 192, 135, 30, "XinBox 2",focusTexture=IMAGE_DIR+ 'button-focus.png',noFocusTexture=IMAGE_DIR+ 'button-nofocus.png')
        self.fsButton = xbmcgui.ControlButton(64, 226, 135, 30, "Fullscreen",focusTexture=IMAGE_DIR+ 'button-focus.png',noFocusTexture=IMAGE_DIR+ 'button-nofocus.png')
        self.vaButton = xbmcgui.ControlButton(64, 260, 135, 30, "Attachments",focusTexture=IMAGE_DIR+ 'button-focus.png',noFocusTexture=IMAGE_DIR+ 'button-nofocus.png')
        self.seButton = xbmcgui.ControlButton(64, 294, 135, 30, "Settings",focusTexture=IMAGE_DIR+ 'button-focus.png',noFocusTexture=IMAGE_DIR+ 'button-nofocus.png')
        self.mmButton = xbmcgui.ControlButton(64, 328, 135, 30, "Mini Mode",focusTexture=IMAGE_DIR+ 'button-focus.png',noFocusTexture=IMAGE_DIR+ 'button-nofocus.png')
        self.listControl = xbmcgui.ControlList(238, 120, 434, 200, 'font14',buttonFocusTexture=IMAGE_DIR+"focus.png")
        self.attachlist = xbmcgui.ControlList(238, 340, 434, 200, 'font14',buttonFocusTexture=IMAGE_DIR+"focus.png")
        self.msgbody = xbmcgui.ControlTextBox(216, 340, 456, 200, 'font13')
        self.fsmsgbody = xbmcgui.ControlTextBox(60, 50, 600, 500, 'font13')

        self.addControl(self.title)
        self.mmButton.setLabel(lang.string(0), "font14") #string id 0
        self.cmButton.setLabel("XinBox 1", "font14")
        self.csButton.setLabel("XinBox 2", "font14")
        self.fsButton.setLabel(lang.string(1), "font14", "60ffffff") # string id 1
        self.vaButton.setLabel(lang.string(2), "font14", "60ffffff")# string id 2
        self.seButton.setLabel(lang.string(3), "font14")# string id 3
         
        
        self.addControl(self.cmButton)
        self.addControl(self.csButton)
        self.addControl(self.fsButton)
        self.addControl(self.vaButton)
        self.addControl(self.seButton)
        self.addControl(self.listControl)
        self.addControl(self.attachlist)
        self.attachlist.setVisible(False)
        self.addControl(self.msgbody)

        #define control navigation          
        self.cmButton.controlDown(self.csButton)
        self.csButton.controlUp(self.cmButton)
        self.csButton.controlDown(self.seButton)
        self.seButton.controlUp(self.csButton)
        self.setFocus(self.cmButton)
        self.show()
        return


    def setResolution( self ):
        #Thanks to Nuka for this function :-D
        global reso
        try:
            offset = 0
            resolutions = {'1080i' : 0, '720p' : 1, '480p' : 2, '480p16x9' : 3, 'ntsc' : 4, 'ntsc16x9' : 5, 'pal' : 6, 'pal16x9' : 7, 'pal60' : 8, 'pal6016x9' : 9}
            currentResolution = self.getResolution()
            resolution = resolutions[ 'pal' ]
            # if current and skinned resolutions differ and skinned resolution is not
            # 1080i or 720p (they have no 4:3), calculate widescreen offset
            if (( not ( currentResolution == resolution )) and resolution > 1 ):
                # check if current resolution is 16x9
                if ( currentResolution == 0 or currentResolution % 2 ): iCur16x9 = 1
                else: iCur16x9 = 0
                # check if skinned resolution is 16x9
                if ( resolution % 2 ): i16x9 = 1
                else: i16x9 = 0
                # calculate widescreen offset
                offset = iCur16x9 - i16x9
            self.setCoordinateResolution( resolution + offset )
            reso = self.CoordinateResolution
        except: print 'ERROR: setting resolution'


    def imback(self):
        global user, Inbox1, Inbox2
        self.__init__()
        self.gettally()
        self.define()
        self.readconfig()
        self.writeconfig()
        if user == self.user1:
            Inbox1 = "stage1"
            Inbox2 = "stage0"
        elif user == self.user2:
            Inbox1 = "stage0"
            Inbox2 = "stage1"
        self.openinbox()
            
        
        
    def gogogo(self):
        global test
        test = 1
        self.close()
        self.run()

    def run(self):
        global user, server, passw, ssl, test
        while test == 1:
            try:
                user = self.user1
                server = self.server1
                passw = self.pass1
                ssl = self.ssl1
                self.checkmail()
            except:pass
            try:
                user = self.user2
                server = self.server2
                passw = self.pass2
                ssl = self.ssl2
                self.checkmail()
            except:pass
        self.close()


    def checkmail(self):
        global minimssg, user, server, passw, ssl, test
        self.EMAILFOLDER = DATA_DIR + user + "@" + server + "\\"
        for root, dirs, files in os.walk(self.EMAILFOLDER + "\\NEW\\", topdown=False):
            for name in files:
                os.remove(os.path.join(root, name))
        self.nummails = 0
        if ssl == "-": 
            mail = poplib.POP3(server)
        else:
            mail = poplib.POP3_SSL(server, ssl)
        mail.user(user)
        mail.pass_(passw)
        self.numEmails = mail.stat()[0]
        self.newmail = []
        for i in range(1, self.numEmails+1):                     
            self.bingo = 0
            self.track = 0
            self.idme = mail.uidl(i)  
            self.idme = re.sub(str(i), '', self.idme)
            self.readid()
            self.readid2()
            if self.bingo == 0:                
                self.newmail.append(i)
                self.nummails = self.nummails + 1                          
        if self.nummails == 0:
            return
        else:
            count = 0
            count2 = 1
            for i in range(1, self.nummails+1):
                try: 
                    dome = self.newmail[count]
                    mailMsg = mail.retr(dome)[1]
                    self.idme = mail.uidl(dome)  
                    self.idme = re.sub(str(dome), '', self.idme)
                    tempStr = ''
                    for line in mailMsg:
                        if line == '':
                            line = ' '
                        tempStr = tempStr + line + '\n'
                    self.email = (email.message_from_string(tempStr))
                    f = open(self.EMAILFOLDER + str(self.tally) +".sss", "wb")
                    f.write(str(self.email))
                    f.close()
                    f = open(self.EMAILFOLDER + IDFOLDER + str(self.tally) +".id", "wb")
                    f.write(str(self.idme))
                    f.close()
                    f = open(self.EMAILFOLDER +NEWFOLDER+ str(self.tally) +".new", "wb")
                    f.write(str(self.tally))
                    f.close()
                    self.tally = self.tally+1
                    count = count + 1
                    count2 = count2 + 1
                    self.writetally()
                    minimssg =  "XinBox - " + user +"\n" + lang.string(4) + "\n"+lang.string(5) +" XinBox" #string id 4, 5
                    wi = minis()
                    wi.doModal()
                    del wi
                except:
                    return
        
    
    def masterpasscheck(self):
        self.readconfig()
        passw = ""
        keyboard = xbmc.Keyboard(passw, lang.string(6)) #id 6
        try:
            keyboard.setHiddenInput(True)
        except:pass
        keyboard.doModal()
        if (keyboard.isConfirmed()):
            passw = keyboard.getText()
            if passw != self.masterpass:
                dialog = xbmcgui.DialogProgress()
                dialog.create(lang.string(7)) #id 7
                time.sleep(1)
                dialog.close()
                self.masterpasscheck()
            elif passw == self.masterpass:
                self.mainmenu()
        else:
            try:
                keyboard.setHiddenInput(False)
            except:pass
            del m

    def startup(self):
        self.define()
        self.gettally()
        self.readconfig()
        self.writeconfig()
        if self.MasterPassEnable == "yes": 
            if self.masterpass != "-":
                self.masterpasscheck()
            else:
                self.mainmenu()
        elif self.MasterPassEnable == "no": 
            self.mainmenu()
        elif self.MasterPassEnable == "-":
            self.masspasswsetup()

    def define(self):
        global Inbox1, Inbox2
        self.MasterPassEnable = "-"
        self.masterpass = "-"
        self.server1 = "-" 
        self.user1 = "-" 
        self.pass1 = "-" 
        self.ssl1 = "-" 
        self.server2 = "-" 
        self.user2 = "-" 
        self.pass2 = "-" 
        self.ssl2 = "-"
        self.settingssaved = 0
        self.firsttime = 0
        Inbox1 = "stage0"
        Inbox2 = "stage0"
        try:
                os.mkdir(DATA_DIR)
                os.mkdir(TEMPFOLDER)
        except:pass
        return      

    def masspasswsetup(self):
        self.readconfig()
        dialog = xbmcgui.Dialog()
        if dialog.yesno(lang.string(8), lang.string(9)): #id 8, 9
            self.MasterPassEnable = "yes"
            self.writeconfig()
            self.getpassinput()
        else:
            self.MasterPassEnable = "no"
            self.writeconfig()
            self.mainmenu()

    def readconfig(self):
        try:
            fh = open(Root_Dir + SETTINGS_FILE)
            for line in fh.readlines():
                theLine = line.strip()
                if theLine.count("<masterpassenable>") > 0:
                    self.MasterPassEnable = theLine[18:-19]
                if theLine.count("<masterpass>") > 0:
                    self.masterpass = theLine[12:-13]               
                if theLine.count("<server1>") > 0:
                    self.server1 = theLine[9:-10]
                if theLine.count("<user1>") > 0:
                    self.user1 = theLine[7:-8]
                if theLine.count("<pass1>") > 0:
                    self.pass1 = theLine[7:-8]
                if theLine.count("<ssl1>") > 0:
                    self.ssl1 = theLine[6:-7]                    
                if theLine.count("<server2>") > 0:
                    self.server2 = theLine[9:-10]
                if theLine.count("<user2>") > 0:
                    self.user2 = theLine[7:-8]
                if theLine.count("<pass2>") > 0:
                    self.pass2 = theLine[7:-8]            
                if theLine.count("<ssl2>") > 0:
                    self.ssl2 = theLine[6:-7]  
                    fh.close()
            return
        except IOError:
            self.createconfig()
            self.readconfig()
            return

    def gettally(self):
        self.readtally()
        if self.tally == "-":
            self.tally = 1
        self.tally = int(self.tally)
        self.writetally()
        return

    def readtally(self):
        try:
            fh = open(DATA_DIR + "tally.sss")
            for line in fh.readlines():
                theLine = line.strip()
                if theLine.count("<tally>") > 0:
                    self.tally = theLine[7:-8]    
                    fh.close()
            return
        except IOError:
            self.createtally()
            self.readtally()
            return
           

    def writetally(self):
            f = open(DATA_DIR + "tally.sss", "wb")
            f.write("\t<tally>"+ str(self.tally) +"</tally>\n")
            f.close()
            return

    def createtally(self):
            f = open(DATA_DIR + "tally.sss", "wb")
            f.write("\t<tally>-</tally>\n")
            f.close()
            return


    def createconfig(self):
            f = open(Root_Dir + SETTINGS_FILE, "wb")
            f.write("<settings>\n")
            f.write("\t<masterpassenable>-</masterpassenable>\n")
            f.write("\t<masterpass>-</masterpass>\n")
            f.write("\t<server1>-</server1>\n")
            f.write("\t<user1>-</user1>\n")
            f.write("\t<pass1>-</pass1>\n")
            f.write("\t<ssl1>-</ssl1>\n")
            f.write("\t<server2>-</server2>\n")
            f.write("\t<user2>-</user2>\n")
            f.write("\t<pass2>-</pass2>\n")
            f.write("\t<ssl2>-</ssl2>\n")
            f.write("</settings>\n")
            f.close()
            return

    def writeconfig(self):
            f = open(Root_Dir + SETTINGS_FILE, "wb")
            f.write("<settings>\n")
            f.write("\t<masterpassenable>"+ self.MasterPassEnable +"</masterpassenable>\n")
            f.write("\t<masterpass>"+ self.masterpass +"</masterpass>\n")
            f.write("\t<server1>"+ self.server1 +"</server1>\n")
            f.write("\t<user1>"+ self.user1 +"</user1>\n")
            f.write("\t<pass1>"+ self.pass1 +"</pass1>\n")
            f.write("\t<ssl1>"+ self.ssl1 +"</ssl1>\n")
            f.write("\t<server2>"+ self.server2 +"</server2>\n")
            f.write("\t<user2>"+ self.user2 +"</user2>\n")
            f.write("\t<pass2>"+ self.pass2 +"</pass2>\n")
            f.write("\t<ssl2>"+ self.ssl2 +"</ssl2>\n")
            f.write("</settings>\n")
            f.close() 
            return

    def writetempconfig(self):
            f = open(TEMPFOLDER + "TEMPFILE.xml", "wb")
            f.write("<settings>\n")
            f.write("\t<masterpassenable>"+ self.MasterPassEnable +"</masterpassenable>\n")
            f.write("\t<masterpass>"+ self.masterpass +"</masterpass>\n")
            f.write("\t<server1>"+ self.server1 +"</server1>\n")
            f.write("\t<user1>"+ self.user1 +"</user1>\n")
            f.write("\t<pass1>"+ self.pass1 +"</pass1>\n")
            f.write("\t<ssl1>"+ self.ssl1 +"</ssl1>\n")
            f.write("\t<server2>"+ self.server2 +"</server2>\n")
            f.write("\t<user2>"+ self.user2 +"</user2>\n")
            f.write("\t<pass2>"+ self.pass2 +"</pass2>\n")
            f.write("\t<ssl2>"+ self.ssl2 +"</ssl2>\n")
            f.write("</settings>\n")
            f.close() 
            return


    def getpassinput(self):
        dialog = xbmcgui.DialogProgress()
        mastpassw = ""
        keyboard = xbmc.Keyboard(mastpassw, lang.string(10)) #id 10
        try:
            keyboard.setHiddenInput(True)
        except:pass
        keyboard.doModal()
        if (keyboard.isConfirmed()):
            mastpassw = keyboard.getText()
        else:
            return
        if mastpassw == "":
           dialog.create(lang.string(11)) #id 11
           time.sleep(1)
           dialog.close()
           self.getpassinput()
        else:
            self.mastpass = mastpassw
            try:
                keyboard.setHiddenInput(False)
            except:pass
            self.confirmpassinput()

    def confirmpassinput(self):
        mastpassw2 = ""
        keyboard = xbmc.Keyboard(mastpassw2, lang.string(12)) #id 12
        try:
            keyboard.setHiddenInput(True)
        except:pass
        keyboard.doModal()
        mastpassw2 = keyboard.getText()
        if (keyboard.isConfirmed()):
            if self.mastpass == mastpassw2:
                self.masterpass = mastpassw2
                try:
                    keyboard.setHiddenInput(False)
                except:pass
                dialog = xbmcgui.DialogProgress()
                dialog.create(lang.string(13)) #id 13
                time.sleep(1)
                dialog.close()
                if self.setting1 == 1:
                    return
                else:
                    self.writeconfig()
                    self.mainmenu()
            else:
                dialog = xbmcgui.DialogProgress()
                dialog.create(lang.string(14)) #id 14
                time.sleep(1)
                dialog.close()
                try:
                    keyboard.setHiddenInput(False)
                except:pass
                self.getpassinput()
        else:
            try:
                keyboard.setHiddenInput(False)
            except:pass
            return
    def warning (self):
        dialog = xbmcgui.DialogProgress()
        dialog.create(lang.string(15),lang.string(16)) #id 15, 16
        time.sleep(1)
        dialog.close()
        self.settingsmenu()
        
    def mainmenu(self):	
        self.readconfig()
        self.setFocus(self.cmButton)
      
    def reset(self):
        self.removeControl(self.seoverlay)
        self.removeControl(self.one)
        self.removeControl(self.three)
        self.removeControl(self.four)
        self.removeControl(self.five)
        self.removeControl(self.seven)
        self.removeControl(self.eight)
        self.removeControl(self.nine)
        self.removeControl(self.ten)
        self.removeControl(self.elleven)
        self.removeControl(self.twelve)
        self.removeControl(self.thirteen)
        self.removeControl(self.fourteen)
        self.removeControl(self.fifteen)
        self.removeControl(self.theList)
        self.setFocus(self.cmButton)
        return
        
    def settingsmenu(self):
        fh = open(Root_Dir + SETTINGS_FILE)
        self.comparesettings1 = fh.read()
        fh.close()
        self.settings = True
        self.readconfig()
        self.addControl(self.seoverlay)
        self.one = xbmcgui.ControlLabel(40,124,200,35,lang.string(17)+"1","font13","0xFFFFFFFF") #id 17
        self.three = xbmcgui.ControlLabel(40,153,200,35,lang.string(18)+"1","font13","0xFFFFFFFF")#id 18
        self.theList = xbmcgui.ControlList(205, 120, 470, 600, 'font14',space=0, buttonFocusTexture=IMAGE_DIR+"focus.png")
        self.four = xbmcgui.ControlLabel(40,182,200,35,lang.string(19)+"1","font13","0xFFFFFFFF")#id 19
        self.fourteen = xbmcgui.ControlLabel(40,211,200,35,"SSL1","font13","0xFFFFFFFF")
        self.five = xbmcgui.ControlLabel(40,240,200,35,lang.string(17)+"2","font13","0xFFFFFFFF")#id 17
        self.seven = xbmcgui.ControlLabel(40,269,200,35,lang.string(18)+"2","font13","0xFFFFFFFF")#id 18
        self.eight = xbmcgui.ControlLabel(40,298,200,35,lang.string(19)+"2","font13","0xFFFFFFFF")#id 19
        self.fifteen = xbmcgui.ControlLabel(40,327,200,35,"SSL2","font13","0xFFFFFFFF")
        self.nine = xbmcgui.ControlLabel(40,354,200,35,lang.string(25),"font13","0xFFFFFFFF")#id 25
        self.ten = xbmcgui.ControlLabel(40,383,200,35,lang.string(26),"font13","0xFFFFFFFF")#id 26
        self.elleven = xbmcgui.ControlLabel(102,35, 200,35, "XinBox " + lang.string(27), font="font20") #id 27
        self.twelve = xbmcgui.ControlLabel(450,70, 300,35, "XinBox " + VERSION, font="font18")
        self.thirteen = xbmcgui.ControlLabel(500,86, 300,35, "By Stanley87", font="font18")
        self.addControl(self.one)
        self.addControl(self.three)
        self.addControl(self.four)
        self.addControl(self.five)
        self.addControl(self.seven)
        self.addControl(self.eight)
        self.addControl(self.nine)
        self.addControl(self.ten)
        self.addControl(self.elleven)
        self.addControl(self.twelve)
        self.addControl(self.thirteen)
        self.addControl(self.fourteen)
        self.addControl(self.fifteen)
        self.addControl(self.theList)
        if self.server1 == "-":
            self.theList.addItem(xbmcgui.ListItem(lang.string(28)))#id 28
        else:
            self.theList.addItem(xbmcgui.ListItem(self.server1))
        if self.user1 == "-":
            self.theList.addItem(xbmcgui.ListItem(lang.string(29)))#id 29
        else:
            self.theList.addItem(xbmcgui.ListItem(self.user1))
        if self.pass1 == "-":
            self.theList.addItem(xbmcgui.ListItem(lang.string(30)))#id 30
        else:
            self.theList.addItem(xbmcgui.ListItem('*' * len(self.pass1)))
        if self.ssl1 == "-":
            self.theList.addItem(xbmcgui.ListItem(lang.string(31)))#id 31
        else:
            self.theList.addItem(xbmcgui.ListItem(self.ssl1))
        if self.server2 == "-":
            self.theList.addItem(xbmcgui.ListItem(lang.string(32)))#id 32
        else:
            self.theList.addItem(xbmcgui.ListItem(self.server2))
        if self.user2 == "-":
            self.theList.addItem(xbmcgui.ListItem(lang.string(33)))#id 33
        else:
            self.theList.addItem(xbmcgui.ListItem(self.user2))
        if self.pass2 == "-":
            self.theList.addItem(xbmcgui.ListItem(lang.string(34)))#id 34
        else:
            self.theList.addItem(xbmcgui.ListItem('*' * len(self.pass2)))
        if self.ssl2 == "-":
            self.theList.addItem(xbmcgui.ListItem(lang.string(35)))#id 35
        else:
            self.theList.addItem(xbmcgui.ListItem(self.ssl2))          
        if self.MasterPassEnable == "-":
            self.theList.addItem(xbmcgui.ListItem(lang.string(36)))#id 36
        else:
            self.theList.addItem(xbmcgui.ListItem(self.MasterPassEnable))
        if self.masterpass == "-":
            self.theList.addItem(xbmcgui.ListItem(lang.string(37)))#id 37
        else:
            self.theList.addItem(xbmcgui.ListItem('*' * len(self.masterpass)))
        self.theList.addItem(xbmcgui.ListItem(lang.string(38)))#id 38
        self.theList.addItem(xbmcgui.ListItem(lang.string(39)))#id 39
        self.setFocus(self.theList)

    def openmail(self):
        self.listControl.controlLeft(self.cmButton)
        self.vaButton.setLabel(lang.string(2), "font14", "60ffffff")#id 2
        self.fsButton.setLabel(lang.string(1), "font14", "60ffffff")#id 1
        self.msgbody.reset()
        self.attachlist.setVisible(False)
        self.cmButton.controlDown(self.csButton)
        self.cmButton.controlRight(self.listControl)
        self.csButton.controlUp(self.cmButton)
        self.csButton.controlDown(self.seButton)
        self.csButton.controlRight(self.listControl)
        self.seButton.controlUp(self.csButton)
        self.seButton.controlRight(self.listControl)
        self.mmButton.controlRight(self.listControl)
        self.listControl.reset()
        self.emails = []
        self.count = 0
        self.count2 = 0
        self.count3 = self.tally
        self.addme()
        if self.listControl.size() == 0:
            self.listControl.addItem("XinBox "+ lang.string(40)) #id 40
            self.cmButton.controlRight(self.cmButton)
            self.csButton.controlRight(self.csButton)
            self.seButton.controlRight(self.seButton)
            self.mmButton.controlRight(self.mmButton)
        else:
            self.setFocus(self.listControl)
        return

    def addme(self):
        for self.count in range(self.tally):
            try:
                fh = open(self.EMAILFOLDER + str(self.count3) +".sss")
                tempStr = fh.read()
                fh.close()
                self.emails.append(email.message_from_string(tempStr))
                try:
                    fh = open(self.EMAILFOLDER + NEWFOLDER +str(self.count3) +".new")
                    fh.close()
                    try:
                        temp20 = self.emails[self.count2].get('subject')
                        if temp20 == "":
                            self.listControl.addItem(lang.string(21) +" "+ lang.string(22) +" "+ lang.string(23) + " "+ self.emails[self.count2].get('from'))
                            f = open(self.EMAILFOLDER + CORFOLDER+ str(self.listControl.size() - 1) +".cor", "wb")
                            f.write(str(self.count3))
                            f.close()
                        else:
                            self.listControl.addItem(lang.string(21) +" " + self.emails[self.count2].get('subject') +" "+ lang.string(23) + " "+ self.emails[self.count2].get('from'))
                            f = open(self.EMAILFOLDER + CORFOLDER + str(self.listControl.size() - 1) +".cor", "wb")
                            f.write(str(self.count3))
                            f.close()
                    except:
                        self.listControl.addItem(lang.string(21) +" "+ lang.string(22) +" "+ lang.string(23) + " "+ self.emails[self.count2].get('from'))
                        f = open(self.EMAILFOLDER + CORFOLDER + str(self.listControl.size() -1) +".cor", "wb")
                        f.write(str(self.count3))
                        f.close()
                except:
                    try:
                        temp20 = self.emails[self.count2].get('subject')
                        if temp20 == "":
                            self.listControl.addItem(lang.string(22) +" "+ lang.string(23) + " "+ self.emails[self.count2].get('from'))
                            f = open(self.EMAILFOLDER + CORFOLDER + str(self.listControl.size()-1) +".cor", "wb")
                            f.write(str(self.count3))
                            f.close()
                        else:
                            self.listControl.addItem(self.emails[self.count2].get('subject') +" "+ lang.string(23) + " "+ self.emails[self.count2].get('from'))
                            f = open(self.EMAILFOLDER + CORFOLDER + str(self.listControl.size()-1) +".cor", "wb")
                            f.write(str(self.count3))
                            f.close()
                    except:
                        self.listControl.addItem(lang.string(22)+" "+ lang.string(23)+ " " + self.emails[self.count2].get('from'))
                        f = open(self.EMAILFOLDER + CORFOLDER + str(self.listControl.size()-1) +".cor", "wb")
                        f.write(str(self.count3))
                        f.close()
                self.count = self.count+1
                self.count2 = self.count2+1
                self.count3 = self.count3-1
            except:
                self.count = self.count+1
                self.count3 = self.count3-1
                pass
        return




    

    def openinbox(self):
        global user, server, passw, ssl, Inbox1, Inbox2
        try:
            self.addControl(self.mmButton)
            self.seButton.controlDown(self.mmButton)
            self.mmButton.controlUp(self.seButton)
            self.mmButton.controlRight(self.listControl)
        except: pass
        self.listControl.reset()
        self.removeControl(self.title)
        self.title = xbmcgui.ControlLabel(250, 80, 300, 300, "XinBox - "+ user, "font18", "FFB2D4F5")
        self.addControl(self.title)
        if Inbox1 == "stage1":
            self.cmButton.setLabel(lang.string(41), "font14")#id 41
            self.csButton.setLabel("XinBox 2", "font14")
        elif Inbox2 == "stage1":
            self.csButton.setLabel(lang.string(41), "font14")#id 41
            self.cmButton.setLabel("XinBox 1", "font14")
        self.EMAILFOLDER = DATA_DIR + user + "@" + server + "\\"
        try:
            os.mkdir(self.EMAILFOLDER)
            os.mkdir(self.EMAILFOLDER + IDFOLDER)
            os.mkdir(self.EMAILFOLDER + DELETEFOLDER)
            os.mkdir(self.EMAILFOLDER + NEWFOLDER)
            os.mkdir(self.EMAILFOLDER + CORFOLDER)
        except:
            pass
        self.openmail()

        
    def comparemail(self):
        global user, server, passw, ssl
        self.EMAILFOLDER = DATA_DIR + user + "@" + server + "\\"
        for root, dirs, files in os.walk(self.EMAILFOLDER + "\\NEW\\", topdown=False):
            for name in files:
                os.remove(os.path.join(root, name))
        dialog = xbmcgui.DialogProgress()
        dialog.create("XinBox - " + user, lang.string(42)+"...")#id 42
        self.cmButton.controlRight(self.listControl)
        self.csButton.controlRight(self.listControl)
        try:
            if ssl == "-": 
                mail = poplib.POP3(server)
            else:
                mail = poplib.POP3_SSL(server, ssl)
            mail.user(user)
            mail.pass_(passw)
            self.numEmails = mail.stat()[0]
            
            print "You have", self.numEmails, "new emails"
            dialog.close()
            if self.numEmails==0:
                dialog.create("XinBox - " + user,lang.string(43))#id 43
                mail.quit()
                time.sleep(2)
                dialog.close()
                return
            else:
                dialog.create("XinBox - " + user)
                self.nummails = 0
                self.newmail = []
                for i in range(1, self.numEmails+1):                     
                    dialog.update((i*100)/self.numEmails,lang.string(44)+"....")#id 44
                    self.bingo = 0
                    self.track = 0
                    self.idme = mail.uidl(i)  
                    self.idme = re.sub(str(i), '', self.idme)
                    self.readid()
                    self.readid2()
                    if self.bingo == 0:                
                        self.newmail.append(i)
                        self.nummails = self.nummails + 1                          
                if self.nummails == 0:
                    dialog.create("XinBox - " + user,lang.string(43))#id 43
                    time.sleep(3)
                    dialog.close()
                else:
                    count = 0
                    count2 = 1
                    for i in range(1, self.nummails+1):
                        try:
                            dialog.update((i*100)/self.nummails,lang.string(45)+" " + str(self.nummails) + " "+lang.string(46),lang.string(47)+" #" + str(count2))#id 45, 46,47
                            dome = self.newmail[count]
                            mailMsg = mail.retr(dome)[1]
                            self.idme = mail.uidl(dome)  
                            self.idme = re.sub(str(dome), '', self.idme)
                            tempStr = ''
                            for line in mailMsg:
                                if line == '':
                                    line = ' '
                                tempStr = tempStr + line + '\n'
                            self.email = (email.message_from_string(tempStr))
                            f = open(self.EMAILFOLDER + str(self.tally) +".sss", "wb")
                            f.write(str(self.email))
                            f.close()
                            f = open(self.EMAILFOLDER + IDFOLDER + str(self.tally) +".id", "wb")
                            f.write(str(self.idme))
                            f.close()
                            f = open(self.EMAILFOLDER + NEWFOLDER +str(self.tally)+".new", "wb")
                            f.write(str(self.tally))
                            f.close()
                            self.tally = self.tally+1
                            count = count + 1
                            count2 = count2 + 1
                        except:pass
                    dialog.close()
                if self.nummails != 0:
                    self.play_sound("default")
                self.openmail()
                self.writetally()
                
        except:
            dialog.close()
            dialog.create("XinBox - " + user, lang.string(48))#id 48
            time.sleep(2)
            dialog.close()
            return


    def readid(self):
        self.count = 0
        self.count2 = 0
        for self.count in range(self.tally):
            try:
                fh = open(self.EMAILFOLDER + IDFOLDER + str(self.count) +".id")
                self.testmeid = fh.read()
                fh.close()
                if self.testmeid == self.idme:
                    self.bingo = 1
                    return
                else:
                    self.bingo = 0
                    self.count = self.count+1
                    self.count2 = self.count2+1
            except:
                self.bingo = 0
                self.count = self.count+1
        return

    def readid2(self):
        self.count = 0
        self.count2 = 0
        for self.count in range(self.tally):
            try:
                fh = open(self.EMAILFOLDER + DELETEFOLDER + str(self.count) +".id")
                self.testmeid = fh.read()
                fh.close()
                if self.testmeid == self.idme:
                    self.bingo = 1
                    return
                else:
                    self.count = self.count+1
                    self.count2 = self.count2+1
            except:
                self.count = self.count+1
        return


    def deletemail(self):
        dialog = xbmcgui.Dialog()
        if dialog.yesno(lang.string(15), lang.string(49)+" XinBox?"):#id 15, 49
            fh = open(self.EMAILFOLDER + CORFOLDER + str(self.listControl.getSelectedPosition())+ ".cor")
            deleteme = fh.read()
            fh.close()
            os.remove(self.EMAILFOLDER + str(deleteme)+".sss")
            try:
                os.remove(self.EMAILFOLDER + NEWFOLDER + str(deleteme)+".new")
            except:pass
            shutil.move(self.EMAILFOLDER + IDFOLDER + str(deleteme)+".id", self.EMAILFOLDER + DELETEFOLDER)
            dialog = xbmcgui.DialogProgress()
            dialog.create(lang.string(15),lang.string(50)+" XinBox!")#id 50
            time.sleep(2)
            dialog.close()
            if self.listControl.size() == 1:
                self.setFocus(self.cmButton)
                self.mmButton.controlRight(self.mmButton)
            self.openmail()
            return
        else:
            return

    def processEmail(self, selected):
        self.msgbody.setVisible(True)
        self.attachlist.setVisible(False)
        self.attachments = []
        if self.emails[selected].is_multipart():
            for part in self.emails[selected].walk():
                if part.get_content_type() != "text/plain" and part.get_content_type() != "text/html" and part.get_content_type() != "multipart/mixed" and part.get_content_type() != "multipart/alternative":
                    filename = part.get_filename()
                    if not filename:
                        ext = mimetypes.guess_extension(part.get_type())
                        if not ext:
                            # Use a generic extension
                            ext = '.bin'
                        filename = 'temp' + ext
                    try:
                        f=open(TEMPFOLDER + filename, "wb")
                        f.write(part.get_payload(decode=1))
                        f.close()
                    except:
                        print "problem saving attachment " + filename
                    self.attachments.append(filename)
        
        if len(self.attachments)==0:
            # disable the attachments button
            self.vaButton.setLabel("Attachments", "font14", "60ffffff")
            self.fsButton.controlDown(self.seButton)
        else:
            # enable the attachments button
            self.vaButton.setLabel("Attachments", "font14", "ffffffff")
            self.fsButton.controlDown(self.vaButton)
            self.vaButton.controlDown(self.seButton)
            self.seButton.controlUp(self.vaButton)
            self.vaButton.controlUp(self.fsButton)
            self.vaButton.controlRight(self.listControl)
        self.printEmail(selected)

    def parse_email(self, email):
        self.parsemail = re.sub('<STYLE.*?>', '<!--', email)
        self.parsemail = re.sub('&copy', '©', self.parsemail)
        self.parsemail = re.sub('&#174;', '®', self.parsemail)
        self.parsemail = re.sub('<SCRIPT.*?>', '<!--', self.parsemail)
        self.parsemail = re.sub('<style.*?>', '<!--', self.parsemail)
        self.parsemail = re.sub('<script.*?>', '<!--', self.parsemail)
        self.parsemail = re.sub('</STYLE>', '-->', self.parsemail)
        self.parsemail = re.sub('</SCRIPT>', '-->', self.parsemail)
        self.parsemail = re.sub('</style>', '-->', self.parsemail)
        self.parsemail = re.sub('</script>', '-->', self.parsemail)
        self.parsemail = re.sub('(?s)<!--.*?-->', '', self.parsemail)
        self.parsemail = re.sub('(?s)<.*?>', ' ', self.parsemail)
        self.parsemail = re.sub('&nbsp;', ' ', self.parsemail)
        return str(self.parsemail)

    def printEmail(self, selected):
        self.msgText = ""
        if self.emails[selected].is_multipart():
            for part in self.emails[selected].walk():
                if part.get_content_type() == "text/plain":
                    print part.get_payload()
                    email = self.parse_email(part.get_payload())
                    self.msgText = email
                    break
        else:
            if self.emails[selected].get_content_type() == "text/html":
                # email in html only, so strip html tags
                email2 = self.parse_email(self.emails[selected].get_payload())
                self.msgText = email2
            else:
                email3 = self.parse_email(self.emails[selected].get_payload())
                self.msgText = email3
                print self.msgText
        self.msgbody.setText(self.msgText)
        self.setFocus(self.msgbody)
        
    def showAttachments(self):
        self.fsButton.controlRight(self.listControl)
        self.vaButton.controlRight(self.attachlist)
        self.attachlist.controlLeft(self.vaButton)
        self.seButton.controlRight(self.listControl)
        self.msgbody.setVisible(False)
        self.attachlist.setVisible(True)
        self.attachlist.reset()
        for attachment in self.attachments:
            self.attachlist.addItem(attachment)

    def ShowImage(self, filename):
        self.img = xbmcgui.ControlImage(20,20,0,0, TEMPFOLDER + filename)
        self.addControl(self.img)
        self.showingimage = True

    def PlayMedia(self, filename):
        print "playing " + filename
        xbmc.Player().play(TEMPFOLDER + filename)

    def play_sound(self, toplay):
        if toplay != "":
            playpath = SRC_Dir + "Sounds\\" + toplay + ".wav"
        if os.path.exists(playpath):
            xbmc.playSFX(playpath)

    def goFullscreen(self):       
        self.addControl(self.fsoverlay)
        self.addControl(self.fsmsgbody)
        self.fsmsgbody.setText(self.msgText)
        self.setFocus(self.fsmsgbody)
        self.fullscreen = True

    def undoFullscreen(self):
        self.fullscreen = False
        self.removeControl(self.fsmsgbody)
        self.removeControl(self.fsoverlay)
        self.setFocus(self.listControl)

    def onAction(self, action):
        try:
            if action == 10: #Back Button
                if self.fullscreen:
                    self.undoFullscreen()
                elif self.showingimage:
                    self.removeControl(self.img)
                    self.showingimage = False
                elif self.settings:
                    self.settings = False
                    self.reset()
                    return
                else:
                    self.close()
            elif action == 9: # CHANGE BACK TO "9" - B Button  #18 is used for PC TAB button
                try:
                    if self.getFocus() == self.listControl:
                        self.deletemail()
                except: pass
        except: return
        return
            
    def onControl(self, control):
        global user, server, passw, ssl, Inbox1, Inbox2
        if control == self.cmButton:
            if self.user1 == "-":
                self.warning()
                Inbox1 = "stage0"
            elif self.pass1 == "-":
                self.warning()
                Inbox1 = "stage0"
            elif self.server1 == "-":
                self.warning()
                Inbox1 = "stage0"
            elif Inbox1 == "stage1":
                self.comparemail()
            else:
                user = self.user1
                server = self.server1
                passw = self.pass1
                ssl = self.ssl1
                Inbox1 = "stage1"
                Inbox2 = "stage0"
                self.openinbox()
        elif control == self.csButton:
            if self.user2 == "-":
                self.warning()
                Inbox2 = "stage0"
            elif self.pass2 == "-":
                self.warning()
                Inbox2 = "stage0"
            elif self.server2 == "-":
                self.warning()
                Inbox2 = "stage0"
            elif Inbox2 == "stage1":
                self.comparemail()
            else:
                user = self.user2
                server = self.server2
                passw = self.pass2
                ssl = self.ssl2
                Inbox1 = "stage0"
                Inbox2 = "stage1"
                self.openinbox()
        elif control == self.seButton:
            self.settingsmenu()
        elif control == self.mmButton:
            self.gogogo()
        elif control == self.listControl:
            self.fsButton.setLabel(lang.string(1), "font14", "ffffffff")#id 1
            self.listControl.controlLeft(self.cmButton)
            self.listControl.controlRight(self.msgbody)
            self.msgbody.controlUp(self.listControl)
            self.msgbody.controlLeft(self.fsButton)
            self.cmButton.controlDown(self.csButton)
            self.cmButton.controlRight(self.listControl)
            self.csButton.controlUp(self.cmButton)
            self.csButton.controlDown(self.fsButton)
            self.csButton.controlRight(self.listControl)
            self.fsButton.controlUp(self.csButton)
            self.fsButton.controlDown(self.seButton)
            self.fsButton.controlRight(self.listControl)
            self.seButton.controlUp(self.fsButton)
            self.seButton.controlRight(self.msgbody)
            self.processEmail(self.listControl.getSelectedPosition())
        elif control == self.fsButton:
            self.goFullscreen()
        elif control == self.vaButton:
            self.showAttachments()
        elif control == self.attachlist:
            selected = self.attachlist.getSelectedPosition()
            filetype = string.split(self.attachments[selected], '.').pop()
            print filetype
            lcfiletype = string.lower(filetype)
            if lcfiletype=="jpg" or lcfiletype=="jpeg" or lcfiletype=="gif" or lcfiletype=="png" or lcfiletype=="bmp":
                self.ShowImage(self.attachments[selected])
            else:
                self.PlayMedia(self.attachments[selected])

        elif control == self.theList:
            lstPos = self.theList.getSelectedPosition()
            if lstPos == 0:
                if self.server1 == "-":
                    keyboard = xbmc.Keyboard("", lang.string(51))#id 51
                else:
                    keyboard = xbmc.Keyboard(self.server1, lang.string(51))#id 51
                keyboard.doModal()
                if (keyboard.isConfirmed()):
                    self.server1 = keyboard.getText()
                else:return
                if self.server1 == "":
                    self.server1 = "-"
                    self.theList.getSelectedItem(lstPos).setLabel(lang.string(28))#id 28
                else:
                    self.theList.getSelectedItem(lstPos).setLabel(self.server1)
                del keyboard
                return
            if lstPos == 1:
                if self.user1 == "-":
                    keyboard = xbmc.Keyboard("", lang.string(52))#id 52
                else:
                    keyboard = xbmc.Keyboard(self.user1, lang.string(52))#id 52
                keyboard.doModal()
                if (keyboard.isConfirmed()):
                    self.user1 = keyboard.getText()
                else:return
                if self.user1 == "":
                    self.user1 = "-"
                    self.theList.getSelectedItem(lstPos).setLabel(lang.string(29))#id 29
                else:
                    self.theList.getSelectedItem(lstPos).setLabel(self.user1)
                del keyboard
                return
            if lstPos == 2:
                if self.pass1 == "-":
                    keyboard = xbmc.Keyboard("", lang.string(6)+"1")#id 6
                else:
                    keyboard = xbmc.Keyboard(self.pass1, lang.string(6)+"1")#id 6
                try:
                    keyboard.setHiddenInput(True)
                except:pass
                keyboard.doModal()
                if (keyboard.isConfirmed()):
                    self.pass1 = keyboard.getText()
                else:return
                try:
                    keyboard.setHiddenInput(False)
                except:pass
                if self.pass1 == "":
                    self.pass1 = "-"
                    self.theList.getSelectedItem(lstPos).setLabel(lang.string(30))#id 30
                else:
                    self.theList.getSelectedItem(lstPos).setLabel('*' * len(self.pass1))
                del keyboard
                return
            if lstPos == 3:
                dialog = xbmcgui.Dialog()
                if self.ssl1 == "-":
                    keyboard = xbmc.Keyboard("", lang.string(53))#id 53
                else:
                    if dialog.yesno(lang.string(54), lang.string(20)+" SSL1?"):#id 54,20
                        self.ssl1 = "-"
                        self.theList.getSelectedItem(lstPos).setLabel(lang.string(31))#id 31
                        return
                    else:
                        return
                keyboard.doModal()
                if (keyboard.isConfirmed()):
                    self.ssl1 = keyboard.getText()
                else:return
                if self.ssl1 == "":
                    self.ssl1 = "-"
                    self.theList.getSelectedItem(lstPos).setLabel(lang.string(31))#id 31
                else:
                    self.theList.getSelectedItem(lstPos).setLabel(self.ssl1)
                del keyboard
                return
            if lstPos == 4:
                if self.server2 == "-":
                    keyboard = xbmc.Keyboard("", lang.string(55))#id 55
                else:
                    keyboard = xbmc.Keyboard(self.server2, lang.string(55))#id 55
                keyboard.doModal()
                if (keyboard.isConfirmed()):
                    self.server2 = keyboard.getText()
                else:return
                if self.server2 == "":
                    self.server2 = "-"
                    self.theList.getSelectedItem(lstPos).setLabel(lang.string(32))#id 32
                else:
                    self.theList.getSelectedItem(lstPos).setLabel(self.server2)
                del keyboard
                return
            if lstPos == 5:
                if self.user2 == "-":
                    keyboard = xbmc.Keyboard("", lang.string(56))#id 56
                else:
                    keyboard = xbmc.Keyboard(self.user2, lang.string(56))#id 56
                keyboard.doModal()
                if (keyboard.isConfirmed()):
                    self.user2 = keyboard.getText()
                else:return
                if self.user2 == "":
                    self.user2 = "-"
                    self.theList.getSelectedItem(lstPos).setLabel(lang.string(33))#id 33
                else:
                    self.theList.getSelectedItem(lstPos).setLabel(self.user2)
                del keyboard
                return
            if lstPos == 6:
                if self.pass2 == "-":
                    keyboard = xbmc.Keyboard("", lang.string(57))#id 57
                else:
                    keyboard = xbmc.Keyboard(self.pass2, lang.string(57))#id 57
                try:
                    keyboard.setHiddenInput(True)
                except:pass
                keyboard.doModal()
                if (keyboard.isConfirmed()):
                    self.pass2 = keyboard.getText()
                else:return
                try:
                    keyboard.setHiddenInput(False)
                except:pass         
                if self.pass2 == "":
                    self.pass2 = "-"
                    self.theList.getSelectedItem(lstPos).setLabel(lang.string(34))#id 34
                else:
                    self.theList.getSelectedItem(lstPos).setLabel('*' * len(self.pass2))
                del keyboard
                return
            if lstPos == 7:
                dialog = xbmcgui.Dialog()
                if self.ssl2 == "-":
                    keyboard = xbmc.Keyboard("", lang.string(58))#id 58
                else:
                    if dialog.yesno(lang.string(54), lang.string(20)+" SSL2?"):#id 54,20
                        self.ssl2 = "-"
                        self.theList.getSelectedItem(lstPos).setLabel(lang.string(35))#id 35
                        return
                    else:
                        return
                keyboard.doModal()
                if (keyboard.isConfirmed()):
                    self.ssl2 = keyboard.getText()
                else:return
                if self.ssl2 == "":
                    self.ssl2 = "-"
                    self.theList.getSelectedItem(lstPos).setLabel(lang.string(35))#id 35
                else:
                    self.theList.getSelectedItem(lstPos).setLabel(self.ssl2)
                del keyboard
                return 
            if lstPos == 8:
                dialog = xbmcgui.Dialog()
                if dialog.yesno(lang.string(8), lang.string(9)): #id 8,9
                    if self.masterpass == "-":
                        self.setting1 = 1
                        self.getpassinput()
                        self.setting1 = 0
                        if self.masterpass == "-":
                            self.theList.getSelectedItem(self.theList.selectItem(9)).setLabel(lang.string(37))#id 37
                        else:
                            self.theList.getSelectedItem(self.theList.selectItem(9)).setLabel('*' * len(self.masterpass))
                    self.MasterPassEnable = "yes"
                    self.theList.getSelectedItem(self.theList.selectItem(8)).setLabel(self.MasterPassEnable)
                    return
                else:
                    self.MasterPassEnable = "no"
                    self.theList.getSelectedItem(lstPos).setLabel(self.MasterPassEnable)
                    return
            if lstPos == 9:
                dialog = xbmcgui.Dialog()
                if self.masterpass == "-":
                    self.setting1 = 1
                    self.getpassinput()
                    self.setting1 = 0
                    if self.masterpass == "-":
                        self.theList.getSelectedItem(lstPos).setLabel(lang.string(37))#id 37
                    else:
                        self.theList.getSelectedItem(lstPos).setLabel('*' * len(self.masterpass))
                    return
                else:
                    if dialog.yesno(lang.string(15), lang.string(59)):#id 15, 59
                        self.setting1 = 1
                        self.getpassinput()
                        self.setting1 = 0
                        if self.masterpass == "-":
                            self.theList.getSelectedItem(lstPos).setLabel(lang.string(37))#id 37
                        else:
                            self.theList.getSelectedItem(lstPos).setLabel('*' * len(self.masterpass))
                    else:
                        return
            if lstPos == 10:
                self.writeconfig()
                self.settingssaved = 1
                dialog = xbmcgui.DialogProgress()
                dialog.create(lang.string(60)) #id 60
                time.sleep(1)
                dialog.close()
                self.readconfig()
                return
            elif lstPos == 11:
                if self.settingssaved != 1:
                    self.writetempconfig()
                    fh = open(TEMPFOLDER + "TEMPFILE.xml")
                    self.comparesettings2 = fh.read()
                    fh.close()
                    dialog = xbmcgui.Dialog()
                    if self.comparesettings1 != self.comparesettings2: 
                        if dialog.yesno(lang.string(15), lang.string(61)): #id 15, 61
                            self.settings = False
                            self.settingssaved = 0
                            self.readconfig()
                            self.reset()
                            return
                        else:
                            return
                    else:
                        self.settingssaved = 0
                        self.settings = False
                        self.readconfig()
                        self.reset()
                        return
                else:
                    self.settingssaved = 0
                    self.settings = False
                    self.readconfig()
                    self.reset()
                    return

                
if os.access(TEMPFOLDER, os.F_OK)==0: #if folder doesn't exist
    print "creating temp folder"
    try:
        os.mkdir(TEMPFOLDER)
    except:
        print "failed creating folder, using xbmc root folder instead"
        TEMPFOLDER = "Z:\\"

m = xbmcmail()
m.startup()
m.doModal()
for root, dirs, files in os.walk(TEMPFOLDER, topdown=False):
    for name in files:
        os.remove(os.path.join(root, name))
del m
