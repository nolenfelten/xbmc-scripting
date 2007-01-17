# -*- coding: cp1252 -*-
      ##########################
      #                        #                      
      #   XBOX InBOX (V.0.1)   #         
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

Root_Dir = os.getcwd().replace(";","")+"\\"
SRC_Dir = Root_Dir + "Src\\"
DATA_DIR = SRC_Dir + "Data\\"
DELETEFOLDER = "Deleted\\"

SETTINGS_FILE = "settings.xml"

TEMPFOLDER = SRC_Dir + "temp\\"
VERSION = "(V.0.1)"

scriptpath = sys.path[0]
sys.path.append( os.path.join( sys.path[0], 'Src\\lib' ) )




class xbmcmail(xbmcgui.Window):
    def __init__(self):
        self.fullscreen = False
        self.showingimage = False
        self.setting1 = 0
        screenheight = self.getHeight()
        self.settings = False
        if screenheight==576: #pal
            self.addControl(xbmcgui.ControlImage(0,0,720,576, 'background.png'))
            self.fsoverlay = xbmcgui.ControlImage(0,0,720,576, 'background.png')
            self.seoverlay = xbmcgui.ControlImage(0,0,720,576, 'background.png')
            self.bgpanel = xbmcgui.ControlImage(55,60,0,0, 'panel-email.png')
            self.panel = xbmcgui.ControlImage(50,135,180,200, 'panel.png')
            self.title = xbmcgui.ControlLabel(250, 80, 200, 100, "XBOX InBOX", "font18", "FFB2D4F5")
            self.cmButton = xbmcgui.ControlButton(64, 158, 135, 30, "Check Email")
            self.csButton = xbmcgui.ControlButton(64, 192, 135, 30, "Check Email 2")
            self.fsButton = xbmcgui.ControlButton(64, 226, 135, 30, "Fullscreen")
            self.vaButton = xbmcgui.ControlButton(64, 260, 135, 30, "Attachments")
            self.seButton = xbmcgui.ControlButton(64, 294, 135, 30, "Settings")
            self.listControl = xbmcgui.ControlList(238, 120, 434, 200, 'font14')
            self.attachlist = xbmcgui.ControlList(238, 340, 434, 200, 'font14')
            self.msgbody = xbmcgui.ControlTextBox(216, 340, 456, 200, 'font13')
            self.fsmsgbody = xbmcgui.ControlTextBox(60, 50, 600, 500, 'font13')
        elif screenheight==720: #720p
            self.addControl(xbmcgui.ControlImage(0,0,1280,720, 'background.png'))
            self.fsoverlay = xbmcgui.ControlImage(0,0,1280,720, 'background.png')
            self.bgpanel = xbmcgui.ControlImage(55,60,0,0, 'panel-email.png')
            self.panel = xbmcgui.ControlImage(50,135,180,200, 'panel.png')
            self.title = xbmcgui.ControlLabel(200, 80, 200, 100, "XBOX InBOX", "font14", "FFB2D4F5")
            self.cmButton = xbmcgui.ControlButton(64, 158, 290, 30, "Check Email")
            self.csButton = xbmcgui.ControlButton(64, 192, 290, 30, "Check Email 2")
            self.fsButton = xbmcgui.ControlButton(64, 226, 290, 30, "Fullscreen")
            self.vaButton = xbmcgui.ControlButton(64, 260, 290, 30, "Attachments")
            self.seButton = xbmcgui.ControlButton(64, 294, 290, 30, "Settings") 
            self.listControl = xbmcgui.ControlList(238, 120, 958, 260, 'font14')
            self.attachlist = xbmcgui.ControlList(238, 410, 958, 260, 'font14')
            self.msgbody = xbmcgui.ControlTextBox(216, 410, 978, 260, 'font13')
            self.fsmsgbody = xbmcgui.ControlTextBox(60, 50, 1160, 620, 'font13')
        elif screenheight==1080: #1080i
            self.addControl(xbmcgui.ControlImage(0,0,1920,1080, 'background.png'))
            self.fsoverlay = xbmcgui.ControlImage(0,0,1920,1080, 'background.png')
            self.bgpanel = xbmcgui.ControlImage(55,60,0,0, 'panel-email.png')
            self.panel = xbmcgui.ControlImage(50,135,180,200, 'panel.png')
            self.title = xbmcgui.ControlLabel(200, 80, 50, 20, "XBOX InBOX", "font14", "FFB2D4F5")
            self.cmButton = xbmcgui.ControlButton(64, 158, 135, 30, "Check Email")
            self.csButton = xbmcgui.ControlButton(64, 192, 135, 30, "Check Email 2")
            self.fsButton = xbmcgui.ControlButton(64, 226, 135, 30, "Fullscreen")
            self.vaButton = xbmcgui.ControlButton(64, 260, 135, 30, "Attachments")
            self.seButton = xbmcgui.ControlButton(64, 294, 135, 30, "Settings")
            self.listControl = xbmcgui.ControlList(238, 120, 434, 160, 'font14')
            self.attachlist = xbmcgui.ControlList(238, 300, 434, 160, 'font14')
            self.msgbody = xbmcgui.ControlTextBox(216, 300, 456, 160, 'font13')
            self.fsmsgbody = xbmcgui.ControlTextBox(60, 50, 600, 400, 'font13')
        else: #assume ntsc/480p
            self.addControl(xbmcgui.ControlImage(0,0,720,576, 'background.png'))
            self.fsoverlay = xbmcgui.ControlImage(0,0,720,576, 'background.png')
            self.bgpanel = xbmcgui.ControlImage(55,60,0,0, 'panel-email.png')
            self.panel = xbmcgui.ControlImage(50,135,180,200, 'panel.png')
            self.title = xbmcgui.ControlLabel(200, 80, 50, 20, "XBOX InBOX", "font14", "FFB2D4F5")
            self.cmButton = xbmcgui.ControlButton(64, 158, 135, 30, "Check Email")
            self.csButton = xbmcgui.ControlButton(64, 192, 135, 30, "Check Email 2")
            self.fsButton = xbmcgui.ControlButton(64, 226, 135, 30, "Fullscreen")
            self.vaButton = xbmcgui.ControlButton(64, 260, 135, 30, "Attachments")
            self.seButton = xbmcgui.ControlButton(64, 294, 135, 30, "Settings")
            self.listControl = xbmcgui.ControlList(238, 120, 434, 160, 'font14')
            self.attachlist = xbmcgui.ControlList(238, 300, 434, 160, 'font14')
            self.msgbody = xbmcgui.ControlTextBox(216, 300, 456, 160, 'font13')
            self.fsmsgbody = xbmcgui.ControlTextBox(60, 50, 600, 400, 'font13')

        self.addControl(self.bgpanel)
        self.addControl(self.panel)
        self.addControl(self.title)
    
       
        self.cmButton.setLabel("XBOX InBOX 1", "font14")
        self.csButton.setLabel("XBOX InBOX 2", "font14")
        self.fsButton.setLabel("Fullscreen", "font14", "60ffffff")
        self.vaButton.setLabel("Attachments", "font14", "60ffffff")
        self.seButton.setLabel("Settings", "font14")
         
        
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
    
    def masterpasscheck(self):
        self.readconfig()
        passw = ""
        keyboard = xbmc.Keyboard(passw, "Enter Password")
        try:
            keyboard.setHiddenInput(True)
        except:pass
        keyboard.doModal()
        if (keyboard.isConfirmed()):
            passw = keyboard.getText()
            if passw != self.masterpass:
                dialog = xbmcgui.DialogProgress()
                dialog.create("Wrong Password, Please try again")
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
        self.gettally()
        self.define()
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
        return      

    def masspasswsetup(self):
        self.readconfig()
        dialog = xbmcgui.Dialog()
        if dialog.yesno("Master Password Setup", "Enable a Master Password on startup?"):
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
        keyboard = xbmc.Keyboard(mastpassw, "Please Enter Password")
        try:
            keyboard.setHiddenInput(True)
        except:pass
        keyboard.doModal()
        if (keyboard.isConfirmed()):
            mastpassw = keyboard.getText()
        else:
            return
        if mastpassw == "":
           dialog.create("No password entered, please try again")
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
        keyboard = xbmc.Keyboard(mastpassw2, "Please Confirm Password")
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
                dialog.create("Thankyou, your password has been set")
                time.sleep(1)
                dialog.close()
                if self.setting1 == 1:
                    return
                else:
                    self.writeconfig()
                    self.mainmenu()
            else:
                dialog = xbmcgui.DialogProgress()
                dialog.create("The password didn't match")
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
        dialog.create("Warning!","Please enter settings")
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
        self.one = xbmcgui.ControlLabel(40,124,200,35,"Server1","font13","0xFFFFFFFF")
        self.three = xbmcgui.ControlLabel(40,153,200,35,"User1","font13","0xFFFFFFFF")
        self.theList = xbmcgui.ControlList(205, 120, 470, 600, 'font14')
        self.four = xbmcgui.ControlLabel(40,182,200,35,"Password1","font13","0xFFFFFFFF")
        self.fourteen = xbmcgui.ControlLabel(40,211,200,35,"SSL1","font13","0xFFFFFFFF")
        self.five = xbmcgui.ControlLabel(40,240,200,35,"Server2","font13","0xFFFFFFFF")
        self.seven = xbmcgui.ControlLabel(40,269,200,35,"User2","font13","0xFFFFFFFF")
        self.eight = xbmcgui.ControlLabel(40,298,200,35,"Password2","font13","0xFFFFFFFF")
        self.fifteen = xbmcgui.ControlLabel(40,327,200,35,"SSL2","font13","0xFFFFFFFF")
        self.nine = xbmcgui.ControlLabel(40,354,200,35,"MastPasswordEnable","font13","0xFFFFFFFF")
        self.ten = xbmcgui.ControlLabel(40,383,200,35,"MasterPassword","font13","0xFFFFFFFF")
        self.elleven = xbmcgui.ControlLabel(102,35, 200,35, "XBOX InBOX Settings", font="font20")
        self.twelve = xbmcgui.ControlLabel(450,70, 300,35, "XBOX InBOX " + VERSION, font="font18")
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
            self.theList.addItem(xbmcgui.ListItem("Enter Server1 eg. pop.ihug.co.nz"))
        else:
            self.theList.addItem(xbmcgui.ListItem(self.server1))
        if self.user1 == "-":
            self.theList.addItem(xbmcgui.ListItem("Enter User1 name eg. monkeyman2000"))
        else:
            self.theList.addItem(xbmcgui.ListItem(self.user1))
        if self.pass1 == "-":
            self.theList.addItem(xbmcgui.ListItem("Enter Password1 eg. shshsh123"))
        else:
            self.theList.addItem(xbmcgui.ListItem('*' * len(self.pass1)))
        if self.ssl1 == "-":
            self.theList.addItem(xbmcgui.ListItem("Enable SSL for Server1?"))
        else:
            self.theList.addItem(xbmcgui.ListItem(self.ssl1))
        if self.server2 == "-":
            self.theList.addItem(xbmcgui.ListItem("Enter Server2 eg. pop.uhug.co.nz"))
        else:
            self.theList.addItem(xbmcgui.ListItem(self.server2))
        if self.user2 == "-":
            self.theList.addItem(xbmcgui.ListItem("Enter User2 name eg. mrworm123"))
        else:
            self.theList.addItem(xbmcgui.ListItem(self.user2))
        if self.pass2 == "-":
            self.theList.addItem(xbmcgui.ListItem("Enter Password2 eg. hushhush123"))
        else:
            self.theList.addItem(xbmcgui.ListItem('*' * len(self.pass2)))
        if self.ssl2 == "-":
            self.theList.addItem(xbmcgui.ListItem("Enable SSL for Server2?"))
        else:
            self.theList.addItem(xbmcgui.ListItem(self.ssl2))          
        if self.MasterPassEnable == "-":
            self.theList.addItem(xbmcgui.ListItem("Enable Master Password on startup?"))
        else:
            self.theList.addItem(xbmcgui.ListItem(self.MasterPassEnable))
        if self.masterpass == "-":
            self.theList.addItem(xbmcgui.ListItem("Enter Master Password"))
        else:
            self.theList.addItem(xbmcgui.ListItem('*' * len(self.masterpass)))
        self.theList.addItem(xbmcgui.ListItem("Save Settings"))
        self.theList.addItem(xbmcgui.ListItem("Back"))
        self.setFocus(self.theList)

    def openmail(self):
        self.listControl.controlLeft(self.cmButton)
        self.vaButton.setLabel("Attachments", "font14", "60ffffff")
        self.fsButton.setLabel("Fullscreen", "font14", "60ffffff")
        self.msgbody.reset()
        self.attachlist.setVisible(False)
        self.cmButton.controlDown(self.csButton)
        self.cmButton.controlRight(self.listControl)
        self.csButton.controlUp(self.cmButton)
        self.csButton.controlDown(self.seButton)
        self.csButton.controlRight(self.listControl)
        self.seButton.controlUp(self.csButton)
        self.seButton.controlRight(self.listControl)
        self.listControl.reset()
        self.emails = []
        self.count = 0
        self.count2 = 0
        self.addme()
        return

    def addme(self):
        for self.count in range(self.tally):
            try:
                fh = open(self.EMAILFOLDER + str(self.count) +".sss")
                tempStr = fh.read()
                fh.close()
                self.emails.append(email.message_from_string(tempStr))
                try:
                    temp20 = self.emails[self.count2].get('subject')
                    if temp20 == "":
                        self.listControl.addItem("[No Subject] from " + self.emails[self.count2].get('from'))
                    else:
                        self.listControl.addItem(self.emails[self.count2].get('subject') + " from " + self.emails[self.count2].get('from'))
                except:
                    self.listControl.addItem("[No Subject] from " + self.emails[self.count2].get('from'))
                self.count = self.count+1
                self.count2 = self.count2+1
            except:
                self.count = self.count+1
                pass
        return


    def comparemail(self):
        self.EMAILFOLDER = DATA_DIR + self.user1 + "@" + self.server1 + "\\"
        try:
            os.mkdir(self.EMAILFOLDER)
            os.mkdir(self.EMAILFOLDER + DELETEFOLDER)
        except:
            pass
        self.openmail()
        self.listControl.controlLeft(self.cmButton)
        self.vaButton.setLabel("Attachments", "font14", "60ffffff")
        self.fsButton.setLabel("Fullscreen", "font14", "60ffffff")
        self.msgbody.reset()
        self.attachlist.setVisible(False)
        self.cmButton.controlDown(self.csButton)
        self.cmButton.controlRight(self.listControl)
        self.csButton.controlUp(self.cmButton)
        self.csButton.controlDown(self.seButton)
        self.csButton.controlRight(self.listControl)
        self.seButton.controlUp(self.csButton)
        self.seButton.controlRight(self.listControl)
        dialog = xbmcgui.DialogProgress()
        dialog.create("Inbox - " + self.user1, "Logging in...")
        self.cmButton.controlRight(self.listControl)
        self.csButton.controlRight(self.listControl)
        try:
            if self.ssl1 == "-": 
                mail = poplib.POP3(self.server1)
            else:
                mail = poplib.POP3_SSL(self.server1, self.ssl1)
            mail.user(self.user1)
            mail.pass_(self.pass1)
            self.numEmails = mail.stat()[0]
            
            print "You have", self.numEmails, "new emails"
            dialog.close()
            if self.numEmails==0:
                dialog.create("Inbox - " + self.user1,"You have no new emails")
                mail.quit()
                time.sleep(2)
                dialog.close()
                return
            else:
                dialog.create("Inbox - " + self.user1)
                self.nummails = 0
                self.newmail = []
                for i in range(1, self.numEmails+1):                     
                    dialog.update((i*100)/self.numEmails,"Checking for new emails....")
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
                    dialog.create("Inbox - " + self.user1,"You have no new emails")
                    time.sleep(3)
                    dialog.close()
                else:
                    count = 0
                    count2 = 1
                    for i in range(1, self.nummails+1):
                        try:
                            dialog.update((i*100)/self.nummails,"You have " + str(self.nummails) + " new emails","Downloading new email #" + str(count2))
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
                            f = open(self.EMAILFOLDER + str(self.tally) +".id", "wb")
                            f.write(str(self.idme))
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
            dialog.create("Inbox - " + self.user1, "Problem connecting to server")
            time.sleep(2)
            dialog.close()
            return

    def comparemail2(self):
        self.EMAILFOLDER = DATA_DIR + self.user2 + "@" + self.server2 + "\\"
        try:
            os.mkdir(self.EMAILFOLDER)
            os.mkdir(self.EMAILFOLDER + DELETEFOLDER)
        except:
            pass
        self.openmail()
        self.listControl.controlLeft(self.cmButton)
        self.vaButton.setLabel("Attachments", "font14", "60ffffff")
        self.fsButton.setLabel("Fullscreen", "font14", "60ffffff")
        self.msgbody.reset()
        self.attachlist.setVisible(False)
        self.cmButton.controlDown(self.csButton)
        self.cmButton.controlRight(self.listControl)
        self.csButton.controlUp(self.cmButton)
        self.csButton.controlDown(self.seButton)
        self.csButton.controlRight(self.listControl)
        self.seButton.controlUp(self.csButton)
        self.seButton.controlRight(self.listControl)
        dialog = xbmcgui.DialogProgress()
        dialog.create("Inbox - " + self.user2, "Logging in...")
        self.cmButton.controlRight(self.listControl)
        self.csButton.controlRight(self.listControl)
        try:
            if self.ssl2 == "-": 
                mail = poplib.POP3(self.server2)
            else:
                mail = poplib.POP3_SSL(self.server2, self.ssl2)
            mail.user(self.user2)
            mail.pass_(self.pass2)
            self.numEmails = mail.stat()[0]
            
            print "You have", self.numEmails, "new emails"
            dialog.close()
            if self.numEmails==0:
                dialog.create("Inbox - " + self.user2,"You have no new emails")
                mail.quit()
                time.sleep(2)
                dialog.close()
                return
            else:
                dialog.create("Inbox - " + self.user2)
                self.nummails = 0
                self.newmail = []
                for i in range(1, self.numEmails+1):                     
                    dialog.update((i*100)/self.numEmails,"Checking for new emails....")
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
                    dialog.create("Inbox - " + self.user2,"You have no new emails")
                    time.sleep(3)
                    dialog.close()
                else:
                    count = 0
                    count2 = 1
                    for i in range(1, self.nummails+1):
                        try:
                            dialog.update((i*100)/self.nummails,"You have " + str(self.nummails) + " new emails","Downloading new email #" + str(count2))
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
                            f = open(self.EMAILFOLDER + str(self.tally) +".id", "wb")
                            f.write(str(self.idme))
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
            dialog.create("Inbox - " + self.user2, "Problem connecting to server")
            time.sleep(2)
            dialog.close()
            return

    def readid(self):
        self.count = 0
        self.count2 = 0
        for self.count in range(self.tally):
            try:
                fh = open(self.EMAILFOLDER + str(self.count) +".id")
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
        temp1 = self.listControl.getSelectedPosition()
        self.test2 = self.listControl.getSelectedItem(temp1).getLabel()
        dialog = xbmcgui.Dialog()
        if dialog.yesno("WARNING!!", "Delete selected email from XBOX InBOX?"):
            self.getemailnum()
        else:
            return
        dialog = xbmcgui.DialogProgress()
        dialog.create("WARNING!!","Email deleted from XBOX InBOX!")
        time.sleep(2)
        dialog.close()
        self.openmail()
        return

    def getemailnum(self):
        self.emails5 = []
        self.count = 0
        self.count2 = 0
        self.tryme()

    def tryme(self):
        for self.count in range(self.tally):
            try:
                fh = open(self.EMAILFOLDER + str(self.count) +".sss")
                tempStr = fh.read()
                fh.close()
                self.emails5.append(email.message_from_string(tempStr)) 
                try:
                    temp20 = self.emails5[self.count2].get('subject')
                    if temp20 == "":
                        self.test1 = "[No Subject] from " + self.emails5[self.count2].get('from')
                    else:
                        self.test1 = self.emails5[self.count2].get('subject') + " from " + self.emails5[self.count2].get('from')
                except:
                    self.test1 = "[No Subject] from " + self.emails5[self.count2].get('from')
                if self.test1 == self.test2:
                    os.remove(self.EMAILFOLDER + str(self.count)+".sss")
                    shutil.move(self.EMAILFOLDER + str(self.count)+".id", self.EMAILFOLDER + DELETEFOLDER)
                    return
                else:
                    self.count = self.count+1
                    self.count2 = self.count2+1
            except:
                self.count = self.count+1
                pass
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
        if control == self.cmButton:
            if self.user1 == "-":
                self.warning()
            elif self.pass1 == "-":
                self.warning()
            elif self.server1 == "-":
                self.warning()
            else:
                self.comparemail()
        elif control == self.csButton:
            if self.user2 == "-":
                self.warning()
            elif self.pass2 == "-":
                self.warning()
            elif self.server2 == "-":
                self.warning()
            else:
                self.comparemail2()
        elif control == self.seButton:
            self.settingsmenu()
        elif control == self.listControl:
            self.fsButton.setLabel("Fullscreen", "font14", "ffffffff")
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
                    keyboard = xbmc.Keyboard("", "Enter Server1")
                else:
                    keyboard = xbmc.Keyboard(self.server1, "Enter Server1")
                keyboard.doModal()
                self.server1 = keyboard.getText()
                if self.server1 == "":
                    self.server1 = "-"
                    self.theList.getSelectedItem(lstPos).setLabel("Enter Server1 eg. pop.ihug.co.nz")
                else:
                    self.theList.getSelectedItem(lstPos).setLabel(self.server1)
                del keyboard
                return
            if lstPos == 1:
                if self.user1 == "-":
                    keyboard = xbmc.Keyboard("", "Enter Username1")
                else:
                    keyboard = xbmc.Keyboard(self.user1, "Enter Username1")
                keyboard.doModal()
                self.user1 = keyboard.getText()
                if self.user1 == "":
                    self.user1 = "-"
                    self.theList.getSelectedItem(lstPos).setLabel("Enter User1 name eg. monkeyman2000")
                else:
                    self.theList.getSelectedItem(lstPos).setLabel(self.user1)
                del keyboard
                return
            if lstPos == 2:
                if self.pass1 == "-":
                    keyboard = xbmc.Keyboard("", "Enter Password1")
                else:
                    keyboard = xbmc.Keyboard(self.pass1, "Enter Password1")
                try:
                    keyboard.setHiddenInput(True)
                except:pass
                keyboard.doModal()
                if (keyboard.isConfirmed()):
                    self.pass1 = keyboard.getText()
                try:
                    keyboard.setHiddenInput(False)
                except:pass
                if self.pass1 == "":
                    self.pass1 = "-"
                    self.theList.getSelectedItem(lstPos).setLabel("Enter Password1 eg. shshsh123")
                else:
                    self.theList.getSelectedItem(lstPos).setLabel('*' * len(self.pass1))
                del keyboard
                return
            if lstPos == 3:
                dialog = xbmcgui.Dialog()
                if self.ssl1 == "-":
                    keyboard = xbmc.Keyboard("", "Enter SSL1")
                else:
                    if dialog.yesno("SSL Setup", "Remove SSL?"):
                        self.ssl1 = "-"
                        self.theList.getSelectedItem(lstPos).setLabel("Enable SSL for Server1?")
                        return
                    else:
                        return
                keyboard.doModal()
                self.ssl1 = keyboard.getText()
                if self.ssl1 == "":
                    self.ssl1 = "-"
                    self.theList.getSelectedItem(lstPos).setLabel("Enable SSL for Server1?")
                else:
                    self.theList.getSelectedItem(lstPos).setLabel(self.ssl1)
                del keyboard
                return
            if lstPos == 4:
                if self.server2 == "-":
                    keyboard = xbmc.Keyboard("", "Enter Server2 Address")
                else:
                    keyboard = xbmc.Keyboard(self.server2, "Enter Server2 Address")
                keyboard.doModal()
                self.server2 = keyboard.getText()
                if self.server2 == "":
                    self.server2 = "-"
                    self.theList.getSelectedItem(lstPos).setLabel("Enter Server2 eg. pop.uhug.co.nz")
                else:
                    self.theList.getSelectedItem(lstPos).setLabel(self.server2)
                del keyboard
                return
            if lstPos == 5:
                if self.user2 == "-":
                    keyboard = xbmc.Keyboard("", "Enter User2 name")
                else:
                    keyboard = xbmc.Keyboard(self.user2, "Enter Username2")
                keyboard.doModal()
                self.user2 = keyboard.getText()
                if self.user2 == "":
                    self.user2 = "-"
                    self.theList.getSelectedItem(lstPos).setLabel("Enter User2 name eg. mrworm123")
                else:
                    self.theList.getSelectedItem(lstPos).setLabel(self.user2)
                del keyboard
                return
            if lstPos == 6:
                if self.pass2 == "-":
                    keyboard = xbmc.Keyboard("", "Enter Password2")
                else:
                    keyboard = xbmc.Keyboard(self.pass2, "Enter Password2")
                try:
                    keyboard.setHiddenInput(True)
                except:pass
                keyboard.doModal()
                if (keyboard.isConfirmed()):
                    self.pass2 = keyboard.getText()
                try:
                    keyboard.setHiddenInput(False)
                except:pass         
                if self.pass2 == "":
                    self.pass2 = "-"
                    self.theList.getSelectedItem(lstPos).setLabel("Enter Password2 eg. hushhush123")
                else:
                    self.theList.getSelectedItem(lstPos).setLabel('*' * len(self.pass2))
                del keyboard
                return
            if lstPos == 7:
                dialog = xbmcgui.Dialog()
                if self.ssl2 == "-":
                    keyboard = xbmc.Keyboard("", "Enter SSL2")
                else:
                    if dialog.yesno("SSL Setup", "Remove SSL2?"):
                        self.ssl2 = "-"
                        self.theList.getSelectedItem(lstPos).setLabel("Enable SSL for Server2?")
                        return
                    else:
                        return
                keyboard.doModal()
                self.ssl2 = keyboard.getText()
                if self.ssl2 == "":
                    self.ssl2 = "-"
                    self.theList.getSelectedItem(lstPos).setLabel("Enable SSL for Server2?")
                else:
                    self.theList.getSelectedItem(lstPos).setLabel(self.ssl2)
                del keyboard
                return 
            if lstPos == 8:
                dialog = xbmcgui.Dialog()
                if dialog.yesno("Master Password Setup", "Enable a Master Password on startup?"):
                    if self.masterpass == "-":
                        self.setting1 = 1
                        self.getpassinput()
                        self.setting1 = 0
                        if self.masterpass == "-":
                            self.theList.getSelectedItem(self.theList.selectItem(9)).setLabel("Enter Master Password")
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
                        self.theList.getSelectedItem(lstPos).setLabel("Enter Master Password")
                    else:
                        self.theList.getSelectedItem(lstPos).setLabel('*' * len(self.masterpass))
                    return
                else:
                    if dialog.yesno("Warning!", "Change master password?"):
                        self.setting1 = 1
                        self.getpassinput()
                        self.setting1 = 0
                        if self.masterpass == "-":
                            self.theList.getSelectedItem(lstPos).setLabel("Enter Master Password")
                        else:
                            self.theList.getSelectedItem(lstPos).setLabel('*' * len(self.masterpass))
                    else:
                        return
            if lstPos == 10:
                self.writeconfig()
                self.settingssaved = 1
                dialog = xbmcgui.DialogProgress()
                dialog.create("Settings Saved")
                time.sleep(1)
                dialog.close()
                return
            elif lstPos == 11:
                if self.settingssaved != 1:
                    self.writetempconfig()
                    fh = open(TEMPFOLDER + "TEMPFILE.xml")
                    self.comparesettings2 = fh.read()
                    fh.close()
                    dialog = xbmcgui.Dialog()
                    if self.comparesettings1 != self.comparesettings2: 
                        if dialog.yesno("Warning!", "Exit without saving settings?"):
                            self.settings = False
                            self.settingssaved = 0
                            self.reset()
                            return
                        else:
                            return
                    else:
                        self.settingssaved = 0
                        self.settings = False
                        self.reset()
                        return
                else:
                    self.settingssaved = 0
                    self.settings = False
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
