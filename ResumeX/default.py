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
Script = "xbmc.executescript('Q:\\\\scripts\\\\ResumeX\\\\engine.py')"
if os.access("P:\\scripts\\", os.F_OK)==0:
        os.mkdir("P:\\scripts\\")
SETTINGFILE = "P:\\scripts\\resxsettings.xml"
DATA = "P:\\scripts\\resxdata.xml"

class main:
    def gui(self):
        global enabled
        self.fail = 0
        enabled = 0
        self.passme = 0
        self.readsettings()
        dialog = xbmcgui.Dialog()
        if self.enable == "no":
            if dialog.yesno("ResumeX","Enable ResumeX?"):
                self.enable = "yes"
                enabled = 1
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
            if os.access("P:\\scripts\\", os.F_OK)==0:
                    os.mkdir("P:\\scripts\\")
            autoexecfile = "P:\\scripts\\autoexec.py"                      
            if os.path.exists(autoexecfile):
                    fh = open(autoexecfile)
                    lines = []
                    for line in fh.readlines():
                         theLine = line.strip()
                         if theLine.startswith(Script):  
                                 return
                         lines.append(str(line))
                    fh.close()
                    lines.append(Script+"\n")
                    f = open(autoexecfile, "w")
                    f.writelines(lines)
                    f.close()
                    return
            else:
                    f = open(autoexecfile, "w")
                    f.write("import xbmc\n")
                    f.write(Script)
                    f.close()
                    return


    def removeauto(self):
            if os.access("P:\\scripts\\", os.F_OK)==0:
                    return
            autoexecfile = "P:\\scripts\\autoexec.py"
            if os.path.exists(autoexecfile):
                    fh = open(autoexecfile)
                    lines = [ line for line in fh if not line.strip().startswith(Script) ]
                    fh.close()
                    f = open(autoexecfile, "w")
                    f.writelines(lines)
                    f.close()
                    return
            return
        
m = main()
m.gui()
if enabled == 1:
        print "1"
        xbmc.executescript('Q:\\scripts\\ResumeX\\engine.py')
else:
        print "2"
        pass
del m
