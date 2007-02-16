# -*- coding: cp1252 -*-
      ##########################
      #                        #                      
      #   ResumeX (V.0.4)      #         
      #     By Stanley87       #         
      #                        #
#######                        #######             
#                                    #
#                                    #
#   An Auto Resume script for XBMC   #
#                                    #
######################################

import xbmcgui, xbmc
import string, time, re, os
Root_Dir = os.getcwd().replace(";","")+"\\"
   
SETTINGFILE = Root_Dir + "lib\settings.xml"
global enable

class main:
    def gui(self):
        global enable
        self.fail = 0
        self.passme = 0
        self.readsettings()
        dialog = xbmcgui.Dialog()
        if self.enable == "no":
            if dialog.yesno("ResumeX","Enable ResumeX?"):
                self.enable = "yes"
                enable = "yes"
                self.addauto()
            else:
                self.enable = "no"
                self.removeauto()
                self.winresume = "-"
                self.passme = 1
        else:
            if dialog.yesno("ResumeX","Disable ResumeX?"):
                self.enable = "no"
                self.removeauto()
                self.winresume = "-"
                self.passme = 1
                dialog = xbmcgui.DialogProgress()
                dialog.create("ResumeX Disabled - OK!")
                time.sleep(2)
                dialog.close()
            else:
                self.enable = "yes"
                enable = "no"
                self.passme = 1
        if self.passme !=1:
            if dialog.yesno("ResumeX","Enable window resume?"):
                self.winresume = "yes"
            else:
                self.winresume = "no"
            dialog = xbmcgui.DialogProgress()
            dialog.create("ResumeX Enabled - OK!")
            time.sleep(2)
            dialog.close()
        self.writesettings()

            

    def writesettings(self):
        f = open(SETTINGFILE, "wb")
        f.write("<settings>\n")
        f.write("\t<ENABLED>"+self.enable+"</ENABLED>\n")
        f.write("\t<WINRESUME>"+self.winresume+"</WINRESUME>\n")
        f.write("</settings>\n")
        f.close()


    def readsettings(self):
            try:
                fh = open(SETTINGFILE)
            except:
                self.enable = "no"
                self.winresume = "no"
                return
            tag = ["<ENABLED>", "<WINRESUME>"]
            for line in fh.readlines():
                    theLine = line.strip()
                    if theLine.count(tag[0]) > 0:
                            self.enable = theLine[9:-10]
                    if theLine.count(tag[1]) > 0:
                            self.winresume = theLine[11:-12]
            fh.close()
            return

    def addauto(self):
            test = xbmc.getInfoLabel("system.profilename")
            test = str(test)
            if test != "Master user":
                    if os.access("P:\\scripts\\", os.F_OK)==0:
                            os.mkdir("P:\\scripts\\")
                    autoexecfile = "P:\\scripts\\autoexec.py"                      
            else:
                    if os.access("Q:\\UserData\\scripts\\", os.F_OK)==0:
                            os.mkdir("Q:\\UserData\\scripts\\")
                    autoexecfile = "Q:\\UserData\\scripts\\autoexec.py"
            if os.path.exists(autoexecfile):
                    fh = open(autoexecfile)
                    count = 0
                    lines = []
                    for line in fh.readlines():
                         theLine = line.strip()
                         if theLine.startswith("xbmc.executescript('Q:\scripts\ResumeX\lib\engine.py')"):  
                                 return
                         lines.append(str(line))
                         count = count + 1
                    fh.close()
                    lines.append("xbmc.executescript('Q:\scripts\ResumeX\lib\engine.py')\n")
                    count = count + 1
                    f = open(autoexecfile, "w")
                    for i in range (0 , count):
                            f.write(lines[i])
                    f.close()
                    return
            else:
                    f = open(autoexecfile, "w")
                    f.write("import xbmc\n")
                    f.write("xbmc.executescript('Q:\scripts\ResumeX\lib\engine.py')")
                    f.close()
                    return


    def removeauto(self):
            test = xbmc.getInfoLabel("system.profilename")
            test = str(test)
            if test != "Master user":
                    if os.access("P:\\scripts\\", os.F_OK)==0:
                            return
                    autoexecfile = "P:\\scripts\\autoexec.py"                      
            else:
                    if os.access("Q:\\UserData\\scripts\\", os.F_OK)==0:
                            return
                    autoexecfile = "Q:\\UserData\\scripts\\autoexec.py"
            if os.path.exists(autoexecfile):
                    fh = open(autoexecfile)
                    count = 0
                    lines = []
                    for line in fh.readlines():
                         theLine = line.strip()
                         if theLine.startswith("xbmc.executescript('Q:\scripts\ResumeX\lib\engine.py')"):  
                                 pass
                         else:
                             lines.append(str(line))
                         count = count + 1
                    fh.close()
                    f = open(autoexecfile, "w")
                    for i in range (0 , count-1):
                            f.write(lines[i])
                    f.close()
                    return
            return             
m = main()
m.gui()
if enable == "yes":
    xbmc.executescript('Q:\scripts\ResumeX\lib\engine.py')
del m
