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
sys.path.append(Root_Dir)
import default
Root_Dir = "Q:\\Scripts\\XinBox\\"
SRC_Dir = Root_Dir + "Src\\"
DATA_DIR = SRC_Dir + "Data\\"
DELETEFOLDER = "Deleted\\"
IDFOLDER = "IDS\\"
IMAGE_DIR = SRC_Dir + "Images\\"
LANGFOLDER =  SRC_Dir+"Language\\"
LIBFOLDER = SRC_Dir + "Lib\\"
NEWFOLDER = "NEW\\"
CORFOLDER = "COR\\"
SETTINGS_FILE = "settings.xml"
MMSETTINGS_FILE = "mmsettings.xml"
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
            if (( not ( currentResolution == resolution )) and resolution > 1 ):
                if ( currentResolution == 0 or currentResolution % 2 ): iCur16x9 = 1
                else: iCur16x9 = 0
                if ( resolution % 2 ): i16x9 = 1
                else: i16x9 = 0
                offset = iCur16x9 - i16x9
            self.setCoordinateResolution( resolution + offset )
            reso = self.CoordinateResolution
        except: print 'ERROR: setting resolution'

    def onAction(self, action):
            global test
            if action == 10: #
                self.close()
                test = 0
                
            else:
                self.close()





class main:
        def __init__(self):
                global lang
                lang = Language()
                lang.load(LANGFOLDER)
                
        def dummy( self ):
                self.Timer = threading.Timer( 60*60*60, self.dummy,() )
                self.Timer.start()


        def startup(self):
                global test
                self.gettally()
                self.readconfig()
                self.readmmconfig()
                test = 1
                box = 0
                self.startmini()

        def startmini(self):
                global user, test, box
                while test == 1:
                        if self.mmxb1 == "yes":
                                box = 1
                                user = self.user1
                                self.server = self.server1
                                self.passw = self.pass1
                                self.ssl = self.ssl1
                                if user == "-" or self.server == "-":
                                        pass
                                else:
                                        self.checkmail()
                        if self.mmxb2 == "yes":
                                box = 2
                                user = self.user2
                                self.server = self.server2
                                self.passw = self.pass2
                                self.ssl = self.ssl2
                                if user == "-" or self.server == "-":
                                        pass
                                else:
                                        self.checkmail()

        def checkmail(self):
                global user, minimssg
                self.EMAILFOLDER = DATA_DIR + user + "@" + self.server + "\\"
                for root, dirs, files in os.walk(self.EMAILFOLDER + "\\NEW\\", topdown=False):
                    for name in files:
                        os.remove(os.path.join(root, name))
                self.nummails = 0
                if self.ssl == "-": 
                    mail = poplib.POP3(self.server)
                else:
                    mail = poplib.POP3_SSL(self.server, self.ssl)
                mail.user(user)
                mail.pass_(self.passw)
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
                    self.newmails = 0
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
                            self.newmails = self.newmails + 1
                            self.writetally()
                            self.writemmconfig()
                        except:
                            return  
                    minimssg =  "XinBox - " + user +"\n" +str(self.newmails)+" " + lang.string(4) + "\n"+lang.string(5) +" XinBox" #string id 4, 5
                    wi = minis()
                    wi.doModal()
                    del wi

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
                
                
        def thread( self ):
                self.Timeme = threading.Timer( 60*60*60, self.thread,() )
                self.Timeme.start()

        def readconfig(self):
                try:
                    fh = open(Root_Dir + SETTINGS_FILE)
                    for line in fh.readlines():
                        theLine = line.strip()              
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
                except:return



        def readmmconfig(self):
                try:
                    fh = open(Root_Dir + MMSETTINGS_FILE)
                    for line in fh.readlines():
                        theLine = line.strip()
                        if theLine.count("<enable1>") > 0:
                            self.mmxb1 = theLine[9:-10]
                        if theLine.count("<enable2>") > 0:
                            self.mmxb2 = theLine[9:-10]               
                        if theLine.count("<startupenable>") > 0:
                            self.mmsten = theLine[15:-16]  
                            fh.close()
                    return
                except:return

        def writemmconfig(self):
                global box
                f = open(Root_Dir + MMSETTINGS_FILE, "wb")
                f.write("<mmsettings>\n")
                f.write("\t<enable1>"+ self.mmxb1 +"</enable1>\n")
                f.write("\t<enable2>"+ self.mmxb2 +"</enable2>\n")
                f.write("\t<startupenable>"+ self.mmsten +"</startupenable>\n")
                f.write("\t<selectedbox>"+ str(box) +"</selectedbox>\n")
                f.write("</mmsettings>\n")
                f.close() 
                return
m = main()
m.startup()
