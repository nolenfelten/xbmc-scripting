      ##########################
      #                        #                      
      #   XinBox (V.0.9)       #         
      #     By Stanley87       #         
      #                        #
#######                        #######             
#                                    #
#                                    #
#   A pop3 email client for XBMC     #
#                                    #
######################################


import xib_util, traceback
import default, gui
import sys, email, xbmcgui, xbmc
import string, time, mimetypes, re, os
import poplib
import shutil
import threading
import language
_ = language.Language().string

SETTINGDIR = default.__scriptsettings__
SCRIPTSETDIR = SETTINGDIR + default.__scriptname__ + "\\"
SETTINGSFILE = SCRIPTSETDIR + "settings.xib"
MMSETTINGSFILE = SCRIPTSETDIR + "mmsettings.xib"
ROOTDIR = default.__scriptpath__
SRCDIR = ROOTDIR + "src\\"
EMAILDIR = SCRIPTSETDIR + "data\\"
DATADIR = SCRIPTSETDIR + "data\\"
TEMPDIR = SCRIPTSETDIR + "temp\\"
CORFOLDER = "cor\\"
MAILFOLDER = "mail\\"
MESSAGELIST = "message.list"

class Checkemail:
    def __init__( self, inbox, minimode):
        self.minimode = minimode
        self.inbox = inbox
        self.getSettings()

    def setupemail ( self ):
        if self.inbox == 1:
            self.user = self.settings.user1
            self.server = self.settings.server1
            self.passw = self.settings.pass1
            self.ssl = self.settings.ssl1
        elif self.inbox == 2:
            self.user = self.settings.user2
            self.server = self.settings.server2
            self.passw = self.settings.pass2
            self.ssl = self.settings.ssl2  
        self.checkme()
        self.returnvar = self.nummails
       

    def buildinbox ( self ):
        self.emfolder = DATADIR + self.user + "@" + self.server + "\\"
        if not os.path.exists(self.emfolder):
            os.mkdir(self.emfolder)
        if not os.path.exists(self.emfolder + CORFOLDER):
            os.mkdir(self.emfolder + CORFOLDER)
        if not os.path.exists(self.emfolder + MAILFOLDER):
            os.mkdir(self.emfolder + MAILFOLDER)
        self.gettally()
        return
            
    def checkme ( self ):
        if self.minimode == 0:
            dialog = xbmcgui.DialogProgress()
            dialog.create( _( 0 ) + " - " + self.user, _( 50 ))
        try:
            if self.ssl == "-":
                mail = poplib.POP3(self.server)
            else:
                mail = poplib.POP3_SSL(self.server, self.ssl)
            mail.user(self.user)
            mail.pass_(self.passw)
        except:
            traceback.print_exc()
            if self.minimode == 0:
                dialog.close()
                dialog = xbmcgui.Dialog()
                dialog.ok( _( 0 ) + " - " + self.user, _( 55 ) )
            mail.quit()
            return
        self.buildinbox()
        try:
            self.numEmails = mail.stat()[0]
            if self.numEmails==0:
                self.nummails = 0
                mail.quit()
                if self.minimode == 0:
                    dialog.close()
                    dialog = xbmcgui.Dialog()
                    dialog.ok( _( 0 ) + " - " + self.user,_( 52 ) )
                return        
            else:
                self.nummails = 0
                self.octetlist = [(x.split()[1]) for x in mail.uidl()[1]]
                if not os.path.exists(self.emfolder + MESSAGELIST):
                    f = open(self.emfolder + MESSAGELIST, "w")
                    for octet in self.octetlist:
                        f.write(octet + "|")
                    f.close()
                    self.writelist = self.octetlist
                    self.nummails = self.numEmails
                    self.createoc()
                else:
                    self.toclist = []
                    f = open(self.emfolder + MESSAGELIST, "r")
                    s = f.read().split('|')
                    f.close()
                    for t in s:
                        self.toclist.append(str(t))
                    self.toclist.pop()
                    self.writelist = self.toclist
                    self.compareoc()
                self.nummails = len(self.newemail)
                if self.nummails == 0:
                    if self.minimode == 0:
                        dialog.close()
                        dialog = xbmcgui.Dialog()
                        dialog.ok( _( 0 ) + " - " + self.user, _( 52 ) )
                    return
                else:
                    count = 0
                    count2 = 1
                    if self.minimode == 0:
                        dialog = xbmcgui.DialogProgress()
                        dialog.create( _( 0 ) + " - " + self.user,)
                    for i in range(1, self.nummails+1):
                        try:
                            if self.minimode == 0:
                                dialog.update((i*100)/self.nummails, _(51) % self.nummails,_(54) % count2)
                            dome = self.newemail[count]
                            mailMsg = mail.retr(dome)[1]
                            tempStr = ''
                            for line in mailMsg:
                                if line == '':
                                    line = ' '
                                tempStr = tempStr + line + '\n'
                            self.email = (email.message_from_string(tempStr))
                            f = open(self.emfolder + MAILFOLDER + str(self.tally) +".sss", "w")
                            f.write("UNREAD" + "|")
                            f.write(str(self.email))
                            self.tally = self.tally+1
                            count = count + 1
                            count2 = count2 + 1
                            self.writetally()
                        except:
                            traceback.print_exc()
                            if self.minimode == 0:
                                dialog.close()
                                dialog = xbmcgui.Dialog()
                                dialog.ok( _( 0 ) + " - " + self.user, _(56) )
                            mail.quit()
                            return
                    self.updateoc()
                    if self.minimode == 0:
                        dialog.close()
                        dialog = xbmcgui.Dialog()
                        dialog.ok( _( 0 ) + " - " + self.user, _(57) % self.nummails)
                    return
        except:
            traceback.print_exc()
            if self.minimode == 0:
                dialog.close()
                dialog = xbmcgui.Dialog()
                dialog.ok( _( 0 ) + " - " + self.user, _(56) )
            mail.quit()
            return

    def updateoc(self):
        f = open(self.emfolder + MESSAGELIST, "w")
        for octet in self.writelist:
            f.write(octet + "|")
        f.close()  
        return


    def createoc(self):
        self.newemail = []
        for i in range (0, len(self.octetlist)):
            self.newemail.append(i + 1)
        return

        
    def compareoc(self):
        self.newemail = []
        for i in range (0, len(self.octetlist)):
            testme = self.octetlist[i]
            if not testme in self.toclist:
                self.newemail.append(i + 1)
                self.writelist.append(testme)
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
            fh = open(self.emfolder + "tally.sss")
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
            f = open(self.emfolder + "tally.sss", "wb")
            f.write("\t<tally>"+ str(self.tally) +"</tally>\n")
            f.close()
            return

    def createtally(self):
            f = open(self.emfolder + "tally.sss", "wb")
            f.write("\t<tally>-</tally>\n")
            f.close()
            return

    def getSettings( self ):
        self.settings = xib_util.Settings()

