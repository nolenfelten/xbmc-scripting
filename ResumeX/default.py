# -*- coding: cp1252 -*-
      ##########################
      #                        #                      
      #   ResumeX (V.0.1)      #         
      #     By Stanley87       #         
      #                        #
#######                        #######             
#                                    #
#                                    #
#   An Auto Resume script for XBMC   #
#                                    #
######################################

import sys, email, xbmcgui, xbmc
import string, time, mimetypes, re, os
import shutil
SLEEPTIME = 2 #seconds
WINDOWRESUME = 1 # 1 = yes, 0 = no

Root_Dir = os.getcwd().replace(";","")+"\\"
   
DATAFILE = Root_Dir + "data.xml"
class main:
        def loader(self):
                try:
                     shutil.move(Root_Dir + "autoexec.py", "Q:\\scripts\\")   
                except:pass
                try:
                        fh = open(DATAFILE)
                        fh.close()
                        self.opendata()
                except:
                        self.saver()
                if WINDOWRESUME == 1:
                        xbmc.executebuiltin("XBMC.ReplaceWindow("+self.window+")")
                xbmc.executebuiltin("XBMC.SetVolume("+self.volume+")")
                time.sleep(1)
                if self.plsize == False: #there is no playlist
                        if self.playing == False:  #no other song is playing
                                self.saver()
                        else:  #song is playing but no playlist
                              xbmc.Player().play(self.playing)
                              try:
                                      xbmc.Player().seekTime(self.time)
                              except:pass
                              self.saver()
                 #there must be a playlist present from now on
                self.testme()
                count = 0
                self.plist = xbmc.PlayList(0)
                self.plist.clear()
                if self.playing == False: #there is playlist but no media is playing
                        for count in range (0, self.plsize):
                             self.plist.add(self.playlist[count])
                             count = count + 1
                        self.saver()                        
                if self.bingo == 1:#there is a playlist and the current playing song is in this playlist
                        for count in range (0, self.plsize):
                             self.plist.add(self.playlist[count])
                             count = count + 1
                        xbmc.Player().play(self.plist)
                        xbmc.Player().playselected(self.place)
                        try:
                                xbmc.Player().seekTime(self.time)
                        except:pass
                        self.saver()
                else:#there is a playlist that is loaded but a different file is playing over the top (need to make this so the file doesnt need to be added)
                        for count in range (0, self.place+1):
                             self.plist.add(self.playlist[count])
                             count = count + 1
                        self.plist.add(self.playing)
                        count = self.place
                        for count in range (self.place, self.plsize):
                             self.plist.add(self.playlist[count])
                             count = count + 1                        
                        xbmc.Player().play(self.plist)
                        xbmc.Player().playselected(self.place+1)
                        try:
                                xbmc.Player().seekTime(self.time)
                        except:pass
                        self.plist.remove(self.playing)
                        self.saver()

        def testme(self):
                fh = open(DATAFILE)
                count = 0
                try:
                        temp1 = self.playing
                except:
                        temp1 = "-"
                for count in range (0, self.plsize):
                        for line in fh.readlines():
                                theLine = line.strip()
                                temp3 = "<plistfile"+str(count)+">"
                                if theLine.startswith(temp3):
                                        temp4 = theLine[len(temp3):-1*len(temp3)-1]
                                        if temp4 == temp1:
                                                self.bingo = 1
                                                fh.close()
                                                return
                                        else:
                                                count = count + 1
                fh.close()
                self.bingo = 0
                return


        def opendata(self):
                self.playlist = []
                tag = ["<window>", "<volume>", "<time>", "<plspos>", "<plsize>","<playing>"]
                fh = open(DATAFILE)
                count = 0
                for line in fh.readlines():
                        theLine = line.strip()
                        if theLine.count(tag[0]) > 0:
                              self.window = theLine[8:-9]
                        if theLine.count(tag[1]) > 0:
                              self.volume = theLine[8:-9]
                        if theLine.count(tag[2]) > 0:
                              self.time = theLine[6:-7]
                              if self.time == "-":
                                      self.time = False
                              else:
                                      self.time = float(self.time)
                        if theLine.count(tag[3]) > 0:
                              self.place = theLine[8:-9]
                              if self.place == "-":
                                      self.place = False
                              else:
                                      self.place = int(self.place)
                        if theLine.count(tag[4]) > 0:
                              self.plsize = theLine[8:-9]
                              if self.plsize == "-":
                                      self.plsize = False
                              else:  
                                      self.plsize = int(self.plsize)
                        if theLine.count(tag[5]) > 0:
                              self.playing = theLine[9:-10]
                              if self.playing == "-":
                                      self.playing = False
                fh.close()
                fh = open(DATAFILE)
                if self.plsize != 0:
                        for line in fh.readlines():
                                theLine = line.strip()
                                for count in range(0, self.plsize):
                                        temp = "<plistfile"+str(count)+">"
                                        if theLine.startswith(temp):
                                                temp = theLine[len(temp):-1*len(temp)-1]
                                                self.playlist.append(temp)
                                                count = count + 1
                else:pass
                fh.close()
                return
                        

                        


                
        def saver (self):
                while 1:
                        self.playlist = []
                        self.window = xbmcgui.getCurrentWindowId()
                        self.volume = xbmc.getInfoLabel("Player.Volume")
                        self.volume = re.sub("dB", '', self.volume)
                        self.volume = 100.00 + float(self.volume)/60.00*100.00
                        if xbmc.Player().isPlayingAudio():
                                self.time = xbmc.Player().getTime()
                                self.plist = xbmc.PlayList(0)
                                self.plsize = self.plist.size()
                                self.playing = xbmc.Player().getPlayingFile()
                                for i in range (0 , self.plsize):
                                        temp = self.plist[i]
                                        self.playlist.append(xbmc.PlayListItem.getfilename(temp))
                                self.place = self.plist.getposition()
                                self.writedata()
                        elif xbmc.Player().isPlayingVideo():
                                self.time = xbmc.Player().getTime()
                                self.plist = xbmc.PlayList(1)
                                self.plsize = self.plist.size()
                                self.playing = xbmc.Player().getPlayingFile()
                                for i in range (0 , self.plsize):
                                        temp = self.plist[i]
                                        self.playlist.append(xbmc.PlayListItem.getfilename(temp))
                                self.place = self.plist.getposition()
                                self.writedata()
                        else:
                               self.checkme()
                               self.time = "-"
                               self.playing = "-"
                               self.place = "-"
                               self.writedata()
                                        
        def checkme(self):
                self.plist = xbmc.PlayList(0)
                self.plsize = self.plist.size()
                if self.plsize !=0:
                        for i in range (0 , self.plsize):
                                temp = self.plist[i]
                                self.playlist.append(xbmc.PlayListItem.getfilename(temp))
                        return
                else:pass
                self.plist = xbmc.PlayList(1)
                self.plsize = self.plist.size()                
                if self.plsize !=0:
                        for i in range (0 , self.plsize):
                                temp = self.plist[i]
                                self.playlist.append(xbmc.PlayListItem.getfilename(temp))
                        return
                else:
                        self.plsize = "-"
                        self.playlist = "-"
                        return
        
        def writedata(self):
                f = open(DATAFILE, "wb")
                f.write("<data>\n")
                f.write("\t<window>"+str(self.window)+"</window>\n")
                f.write("\t<volume>"+str(self.volume)+"</volume>\n")
                f.write("\t<time>"+str(self.time)+"</time>\n")
                f.write("\t<plspos>"+str(self.place)+"</plspos>\n")
                f.write("\t<plsize>"+str(self.plsize)+"</plsize>\n")
                if self.plsize != "-":
                        for i in range (0 , self.plsize): 
                                f.write("\t<plistfile"+str(i)+">"+str(self.playlist[i])+"</plistfile"+str(i)+">\n")
                f.write("\t<playing>"+str(self.playing)+"</playing>\n")
                f.write("</data>\n")
                f.close()
                time.sleep(SLEEPTIME)
                return
                        
                     

m = main()
m.loader()
del m
