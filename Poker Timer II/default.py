#################################################################################
# 'Display' on the remote hides/shows Pad when level timer is running.          #
# 'Display' on the remote toggles pad size. (Before 1st level starts)           #
#  (Except when in config mode)                                                 #
#                                                                               #
# 'X' on the control pad hides/shows Pad when level timer is running.           #
# 'X' on the control pad toggles pad size. (Before 1st level starts)            #
#  (Except when in config mode)                                                 #
#                                                                               #
# '0' on the remote toggles autohide on/off.                                    #
# 'Y' on the control pad toggles autohide on/off.                               #
#      (Lock in the upper left corner means autohide is disabled)               #
#      (It's set for 30 seconds in PTPadFile.xml                                #
#                                                                               #
# 'Title' on the remote switches to config mode. (Before 1st level starts)      #
# 'White' on the control pad switches to config mode. (Before 1st level starts) #
#      While in config mode Left/Right selects field to edit.                   #
#      Up/Down changes value.                                                   #
#      You can manually edit PTCfgFile.py for more customization.               #
#                                                                               #
# To set the number of levels in your tournament, you would set the next        #
# level's ante to -1. (i.e. for 10 levels set level 11's ante to -1)            #
#   (There are 20 levels in the tournament if no Ante is set to -1)             #
#                                                                               #
# Up/Down/Left/Right repositions the pad except when in config mode. Position   #
# is saved on exit.                                                             #
#                                                                               #
# If the Pad is hidden pause is disabled, pressing any key will show Pad.       #
#                                                                               #
# If you want music or a video playing, start them before you launch the script.#
#                                                                               #
# TIP: If you have music or video(s) playing. Make sure they're longer than the #
#      tournament or you have repeat folders checked in system/settings.        #
#                                                                               #
# TIP: If you create your own event alarms, make sure they're longer than the   #
#      corresponding AlarmTime + your crossfade setting.                        #
#                                                                               #
# Cool Animated slide in/out by:   Thanks to the skinners for the panel2.png:   #
#       EnderW                          Chokemaniac  (lock.png)                 #
#                                                                               #
# Thanks to Phunck for the code used for reading the config files.              #
#                                                                               #
# Inspired by j_guzzler                                                         #
#                                                                               #
#                                                                               #
#   Nuka1195                                                                    #
#################################################################################

from os import path, getcwd
import xbmc, xbmcgui, sys
from time import sleep
import thread, threading

ExtrasPath      = getcwd()[:-1] + '\\Extras\\'

debug           = False     # True outputs debug info to debug screen

try:
    Emulating = xbmcgui.Emulating
except:
    Emulating = False

sys.path.append(ExtrasPath)
sys.path.append(ExtrasPath + '\\_xmlplus.zip')
try:
    reload(PTconfigmgr)
except:
    try:
        import PTconfigmgr
    except:
        pass

ACTION_MOVE_LEFT     = 1
ACTION_MOVE_RIGHT    = 2
ACTION_MOVE_UP       = 3
ACTION_MOVE_DOWN     = 4
ACTION_SELECT_ITEM   = 7
ACTION_PARENT_DIR    = 9
ACTION_PREVIOUS_MENU = 10
#ACTION_BLACK_BUTTON  = 0    # BE CAREFUL
ACTION_WHITE_BUTTON  = 117

#ACTION_A_BUTTON      = 7
#ACTION_B_BUTTON      = 9
ACTION_X_BUTTON      = 18
ACTION_Y_BUTTON      = 34
#ACTION_BACK_BUTTON   = 10
#ACTION_LEFT_TRIGGER  = 111  # Some zeros were there 1110
#ACTION_RIGHT_TRIGGER = 112  # Same 1120

ACTION_0             = 58

XBFONT_LEFT          = 0x00000000
XBFONT_RIGHT         = 0x00000001
XBFONT_CENTER_X      = 0x00000002
XBFONT_CENTER_Y      = 0x00000004
#XBFONT_TRUNCATED     = 0x00000008

#HDTV_1080i           = 0     # (1920x1080, 16:9, pixels are 1:1)
#HDTV_720p            = 1     # (1280x720, 16:9, pixels are 1:1)
#HDTV_480p_4x3        = 2     # (720x480, 4:3, pixels are 4320:4739)
#HDTV_480p_16x9       = 3     # (720x480, 16:9, pixels are 5760:4739)
NTSC_4x3             = 4     # (720x480, 4:3, pixels are 4320:4739)
#NTSC_16x9            = 5     # (720x480, 16:9, pixels are 5760:4739)
#PAL_4x3              = 6     # (720x576, 4:3, pixels are 128:117)
#PAL_16x9             = 7     # (720x576, 16:9, pixels are 512:351)
#PAL60_4x3            = 8     # (720x480, 4:3, pixels are 4320:4739)
#PAL60_16x9           = 9     # (720x480, 16:9, pixels are 5760:4739)

#WINDOW_FULLSCREEN_VIDEO = 2005
#WINDOW_VISUALISATION    = 2006

class windowOverlay(xbmcgui.WindowDialog):

    def __init__(self):

        self.getPadConfig()
        self.initVariables()
        self.getConfigValues()
        self.calcPositions()
        self.addControls()
        self.setAutoHideStatus()
        self.setStatus()
        self.startScript = startScript(self)
        self.startScript.start()
        self.autoHideTimer = autoHideTimer(self)

    def initVariables(self):
        self.resolution = self.getResolution()
        self.setCoordinateResolution(NTSC_4x3 + (self.resolution == 0 or self.resolution % 2))
        #print resolution
        if self.padSize == 0:
            self.padW = 300#self.setWidth(300, NTSC_4x3, self.resolution)
            self.padH = 300
            self.padFontTitle = "font10"
            #self.padFontList = "font10"
            self.padFontLabel = "font12"
            self.padFontMessage = "font10"
        else:
            self.padW = 450#self.setWidth(450, NTSC_4x3, self.resolution)
            self.padH = 450
            self.padFontTitle = "font14"
            #self.padFontList = "font14"
            self.padFontLabel = "font14"
            self.padFontMessage = "font14"

        self.slideSpeed = 0.015

        self.msg = []
        self.msg.append("")
        self.msg.append("(Title/White) - Config Mode")
        self.msg.append("(L/R) - Select  (U) - Inc  (D) - Dec")
        self.msg.append("Tournament has completed.")
        self.msg.append("(Display/X) - Toggle Pad Size")
        self.msg.append("(0/Y) - Toggle autohide on/off")
        self.msg.append("(L/R/U/D) - Move pad")

        self.CHANGING_AMOUNT = False
        self.BREAK_TIMER = False
        self.HIDING_PANEL = False
        self.LEVEL = 0
        self.EXIT_SCRIPT = False
        self.HIDE_PANEL = False
        self.VISIBLE_BUTTON = 1
        self.RAISE_EXCEPTION = False
        self.TIMER_RUNNING = False
        self.START_SCRIPT = True
        self.RESET_PANEL = False
        self.ACTIVE_CONTROL = 1

        self.timeX = [0] * 4
        self.levelX = [0] * 2
        self.anteX = [0] * 4
        self.smBlindX = [0] * 4
        self.bigBlindX = [0] * 4
        self.chipX = [0] * 6

        self.TimeImage = [''] * 40
        self.LevelStatus = [0] * 2
        self.AnteStatus = [0] * 4
        self.SmBlindStatus = [0] * 4
        self.BigBlindStatus = [0] * 4
        self.ChipImage = [''] * 6
        self.ChipHeading = [''] * 6

    def getPadConfig(self):
        try:
            self.padsettings                = PTconfigmgr.ReadSettings(ExtrasPath + 'PTPadFile.xml')

            self.ScriptTitle                = self.padsettings['ScriptTitle']
            self.PadImageName               = self.padsettings['PadImageName']
            self.padSize                    = self.padsettings['padSize']
            self.animate                    = self.padsettings['animate']
            self.autoHide                   = self.padsettings['autoHide']
            self.autoHideTime               = self.padsettings['autoHideTime']
            self.padOffsetX                 = self.padsettings['padOffsetX']
            self.padOffsetY                 = self.padsettings['padOffsetY']
        except:
            if debug:
                print "Pad Settings File Missing or corrupt."

    def getConfigValues(self):

        try:
            self.settings = PTconfigmgr.ReadSettings(ExtrasPath + 'PTCfgFile.xml')

            self.EndTournamentAlarm     = self.settings['EndTournamentAlarm']
            self.EndTournamentAlarmTime = self.settings['EndTournamentAlarmTime']
            self.EndLevelAlarm          = self.settings['EndLevelAlarm']
            self.EndLevelAlarmTime      = self.settings['EndLevelAlarmTime']
            self.StartLevelAlarm        = self.settings['StartLevelAlarm']
            self.StartLevelAlarmTime    = self.settings['StartLevelAlarmTime']
            self.WarningAlarm           = self.settings['WarningAlarm']
            self.WarningAlarmTime       = self.settings['WarningAlarmTime']
            self.LEVEL_TIME             = self.settings['LEVEL_TIME']
            self.WARNING_TIME           = self.settings['WARNING_TIME']
            self.ANTE                   = self.settings['ANTE']
            self.SM_BLIND               = self.settings['SM_BLIND']
            self.BIG_BLIND              = self.settings['BIG_BLIND']
            self.BREAK_TIME             = self.settings['BREAK_TIME']
            self.CHIP_AMT               = self.settings['CHIP_AMT']
            self.CHIP_IMAGE             = self.settings['CHIP_IMAGE']
            self.CHIP_TABLE             = self.settings['CHIP_TABLE']
            self.BLIND_TABLE            = self.settings['BLIND_TABLE']

            self.LEVEL_TIME.insert(0,0)
            self.ANTE.insert(0,0)
            self.SM_BLIND.insert(0,0)
            self.BIG_BLIND.insert(0,0)
            self.BREAK_TIME.insert(0,0)
            self.CHIP_AMT.insert(0,0)
            self.CHIP_IMAGE.insert(0,'chip0.png')
            self.CHIP_TABLE.insert(0,0)
            self.BLIND_TABLE.insert(0,0)

            self.LEVELS = 0
            for x in range(1,21):
                if self.ANTE[x] == -1:
                    break
                self.LEVELS += 1

        except:
            if debug:
                print "Settings File Missing or corrupt."

    def setWidth(self, width, designResolution, resolution):
        pixelWidthMultiplier = [1.0,1.0,0.91158472251529858619962017303229,1.215446296687064781599493564043,\
        0.91158472251529858619962017303229,1.215446296687064781599493564043,1.0940170940170940170940170940171,\
        1.4586894586894586894586894586895,0.91158472251529858619962017303229,1.215446296687064781599493564043]

        if not (resolution == designResolution):
          width = int((width * pixelWidthMultiplier[designResolution]) / pixelWidthMultiplier[resolution])

        return width
        
    def calcPositions(self):

        self.screenW = 720
        self.screenH = 480

        imageSizeW = 505
        imageSizeH = 450
        self.titleH = 25
        self.messageH = 29

        self.slideRange = int(((float(self.padW + self.padOffsetX) / .295) ** .5) + .5)

        self.imageSizeMultiplierW = float(float(self.padW) / imageSizeW)
        self.imageSizeMultiplierH = float(float(self.padH) / imageSizeH)

        self.imageBorderLeftW = int(20 * self.imageSizeMultiplierW)
        self.imageBorderRightW = int(75 * self.imageSizeMultiplierW)
        self.imageBorderTopH = int((61 + (not self.padSize)) * self.imageSizeMultiplierH)
        self.imageBorderBottomH = int(57 * self.imageSizeMultiplierH)

        self.padX = self.screenW - self.padOffsetX - self.padW
        self.padY = self.padOffsetY

        self.titleW = self.padW - self.imageBorderLeftW - self.imageBorderRightW
        self.titleH = int(self.titleH * self.imageSizeMultiplierH)
        self.titleX = self.padX + self.imageBorderLeftW
        self.titleY = self.padY + self.imageBorderTopH

        self.label2W = int(float(self.padW - self.imageBorderLeftW - self.imageBorderRightW) / 3)
        self.label1W  = self.label2W * 2

        self.labelH = int((float(self.padH) / 25))
        self.label1X = self.padX + self.imageBorderLeftW
        self.label2X = self.label1X + self.label2W
        self.label3X = self.label2X + self.label2W

        self.aHideH = int(12 * self.imageSizeMultiplierH)
        self.aHideW = self.aHideH
        self.aHideX = self.padX + self.imageBorderLeftW + int(float(self.aHideW) / 2)
        self.aHideY = self.padY + self.imageBorderTopH + self.aHideH

        self.timeH = int(float(self.padH) / 8)
        self.timeW = int(self.timeH * .6)

        self.timeX[0] = int((float(self.label1W  - float((4 * self.timeW) + (self.timeW *.5))) / 2) + self.padX + self.imageBorderLeftW)
        self.timeX[1] = self.timeX[0] + self.timeW
        self.colonX = self.timeX[1] + int(self.timeW *.75)
        self.timeX[2] = self.colonX + int(self.timeW *.75)
        self.timeX[3] = self.timeX[2] + self.timeW
        self.label1Y = self.titleY + self.titleH + self.labelH
        self.timeY = self.label1Y + self.labelH
        self.label2Y = self.timeY + self.timeH + self.labelH

        self.buttonH = int(self.messageH * self.imageSizeMultiplierH)
        self.buttonW = int(float(self.padW - self.imageBorderLeftW - self.imageBorderRightW) / 4)
        self.buttonX = self.padW -  self.imageBorderRightW - self.buttonW + self.padX
        self.buttonY = self.padY + self.padH - self.imageBorderBottomH - self.buttonH

        self.messageH = int(self.messageH * self.imageSizeMultiplierH)
        self.messageW = self.padW - self.imageBorderLeftW - self.imageBorderRightW - self.buttonW
        self.messageX = self.padX + self.imageBorderLeftW
        self.messageY = self.padY + self.padH - self.imageBorderBottomH - self.messageH + 1


        self.chipH = int(float(self.padW - self.imageBorderLeftW - self.imageBorderRightW) / 7)
        self.chipW = self.chipH #self.setWidth(self.chipH, NTSC_4x3, self.resolution)
        for c in range(1,6):
            self.chipX[c] = int(self.padX + self.imageBorderLeftW + (((c * 2) - 1) * (float(self.padW - self.imageBorderLeftW - self.imageBorderRightW)) / 10) - (float(self.chipW) / 2))
        self.chipY = int(self.messageY - (self.messageH * 1.25) - self.chipH)

        self.chipHeadingY = int(self.chipY + self.chipH + (self.labelH * .5))

        self.amountH = int(float(self.padH) / 10)
        self.amountY = self.label2Y + self.labelH

        self.highlightH = self.labelH
        self.highlightW = self.label1W
        self.highlightX = self.label1X + self.padX
        self.highlightY = self.label1Y

        self.offScreenX = self.screenW * self.animate
        self.progressBarCount = int(float(self.messageW) / (4 + (self.padSize == 2)))

    def addControls(self):
        self.pad = xbmcgui.ControlImage(self.offScreenX + self.padX, self.padY, self.padW, self.padH, ExtrasPath + self.PadImageName, "", 0)
        self.addControl(self.pad)

        self.padTitle = xbmcgui.ControlLabel(self.offScreenX + self.titleX, self.titleY, self.titleW, self.titleH, self.ScriptTitle, self.padFontTitle, "0xFFF1EA40", "", XBFONT_CENTER_Y|XBFONT_CENTER_X)
        self.addControl(self.padTitle)

        self.highlight = xbmcgui.ControlImage(self.offScreenX + self.highlightX, self.highlightY, self.highlightW, self.highlightH, ExtrasPath + 'highlight.png', "", 0)
        self.addControl(self.highlight)
        self.highlight.setVisible(False)

        self.aHide = xbmcgui.ControlImage(self.offScreenX + self.aHideX, self.aHideY, self.aHideW, self.aHideH, ExtrasPath + 'lock.png', "", 2)
        self.addControl(self.aHide)
        #self.aHide.setVisible(False)

        self.TimeHeading = xbmcgui.ControlLabel(self.offScreenX + self.timeX[0], self.label1Y, self.label1W , self.labelH, "Level Time", self.padFontLabel, "", "", XBFONT_CENTER_Y|XBFONT_CENTER_X)
        self.addControl(self.TimeHeading)

        self.TimeHeading1 = xbmcgui.ControlLabel(self.offScreenX + self.timeX[0], self.label1Y, (2 * self.timeW) , self.labelH, "Level", self.padFontLabel, "", "", XBFONT_CENTER_Y|XBFONT_CENTER_X)
        self.addControl(self.TimeHeading1)
        self.TimeHeading1.setVisible(False)

        self.TimeHeading2 = xbmcgui.ControlLabel(self.offScreenX + self.timeX[2], self.label1Y, (2 * self.timeW) , self.labelH, "Break", self.padFontLabel, "", "", XBFONT_CENTER_Y|XBFONT_CENTER_X)
        self.addControl(self.TimeHeading2)
        self.TimeHeading2.setVisible(False)

        self.colon = xbmcgui.ControlImage(self.offScreenX + self.colonX, self.timeY, self.timeW, self.timeH, ExtrasPath + 'red_colon.png', "", 0)
        self.addControl(self.colon)

        for x in range(4):
            for y in range(10):
                self.TimeImage[x * 10 + y] = xbmcgui.ControlImage(self.offScreenX + self.timeX[x], self.timeY, self.timeW, self.timeH, ExtrasPath + 'red_' + str(y) + '.png', "", 0)
                self.addControl(self.TimeImage[x * 10 + y])
        self.resetTimer(self.LEVEL_TIME[self.LEVEL])

        self.LevelHeading = xbmcgui.ControlLabel(self.label3X, self.label1Y, self.label2W, self.labelH, "Level", self.padFontLabel, "", "", XBFONT_CENTER_Y|XBFONT_CENTER_X)
        self.addControl(self.LevelHeading)

        for x in range(2):
            self.LevelStatus[x] = xbmcgui.ControlImage(self.offScreenX,0 ,1 ,1 ,ExtrasPath + 'chip0.png', "", 0)
            self.addControl(self.LevelStatus[x])

        self.statusMessageSuccess = xbmcgui.ControlFadeLabel(self.offScreenX + self.messageX, self.messageY, self.messageW, self.messageH, self.padFontMessage, "0xFF00CCFF", XBFONT_CENTER_Y|XBFONT_LEFT)
        self.addControl(self.statusMessageSuccess)
        self.statusMessageSuccess.addLabel(self.msg[1])
        self.statusMessageSuccess.addLabel(self.msg[4])
        self.statusMessageSuccess.addLabel(self.msg[5])
        self.statusMessageSuccess.addLabel(self.msg[6])

        self.AnteHeading = xbmcgui.ControlLabel(self.offScreenX + self.label1X, self.label2Y, self.label2W, self.labelH, "Ante", self.padFontLabel, "", "", XBFONT_CENTER_Y|XBFONT_CENTER_X)
        self.addControl(self.AnteHeading)

        for x in range(4):
            self.AnteStatus[x] = xbmcgui.ControlImage(self.offScreenX, 0, 1, 1, ExtrasPath + 'chip0.png', "", 0)
            self.addControl(self.AnteStatus[x])

        self.SmBlindHeading = xbmcgui.ControlLabel(self.offScreenX + self.label2X, self.label2Y, self.label2W, self.labelH, "Small Blind", self.padFontLabel, "", "", XBFONT_CENTER_Y|XBFONT_CENTER_X)
        self.addControl(self.SmBlindHeading)

        for x in range(4):
            self.SmBlindStatus[x] = xbmcgui.ControlImage(self.offScreenX, 0, 1, 1, ExtrasPath + 'chip0.png', "", 0)
            self.addControl(self.SmBlindStatus[x])

        self.BigBlindHeading = xbmcgui.ControlLabel(self.offScreenX + self.label3X, self.label2Y, self.label2W, self.labelH, "Big Blind", self.padFontLabel, "", "", XBFONT_CENTER_Y|XBFONT_CENTER_X)
        self.addControl(self.BigBlindHeading)

        for x in range(4):
            self.BigBlindStatus[x] = xbmcgui.ControlImage(self.offScreenX, 0, 1, 1, ExtrasPath + 'chip0.png', "", 0)
            self.addControl(self.BigBlindStatus[x])

        for x in range(1,6):
            self.ChipImage[x] = xbmcgui.ControlImage(self.offScreenX + self.chipX[x], self.chipY, self.chipW, self.chipH, ExtrasPath + self.CHIP_IMAGE[x], "", 2)
            self.addControl(self.ChipImage[x])
            if self.CHIP_AMT[x]:
                s = str('%.2f' % self.CHIP_AMT[x])
                if s[-3:] == ".00":
                    s = s[:-3]
            self.ChipHeading[x] = xbmcgui.ControlLabel(self.offScreenX + self.chipX[x], self.chipHeadingY, self.chipW, self.labelH, s, self.padFontLabel, "0xFFF1EA40", "", XBFONT_CENTER_Y|XBFONT_CENTER_X)
            self.addControl(self.ChipHeading[x])

        self.Button = xbmcgui.ControlButton(self.offScreenX + self.buttonX, self.buttonY, self.buttonW, self.buttonH, "Start", "button-focus.png", "button-nofocus.png", 0, 0, XBFONT_CENTER_Y|XBFONT_CENTER_X, self.padFontLabel)
        self.addControl(self.Button)
        self.setFocus(self.Button)

    def setStatus(self):
        self.LEVEL += 1
        if self.LEVEL <= self.LEVELS:
            self.VISIBLE_BUTTON = 1
            self.Button.setLabel('Start')
            self.resetTimer(self.LEVEL_TIME[self.LEVEL])
            self.setLevelStatus()
            self.setAnteStatus()
            self.setSmBlindStatus()
            self.setBigBlindStatus()
            self.msg[0] = 'This is the final Level.'
            if self.LEVEL < self.LEVELS:
                if self.ANTE[self.LEVEL + 1] != -1:
                    self.msg[0] = 'Next Level: (' + str(self.LEVEL + 1) + ') ANTE: ' + \
                        returnStringAmount(self.ANTE[self.LEVEL + 1]) + \
                        ' - BLINDS: ' +  returnStringAmount(self.SM_BLIND[self.LEVEL + 1]) + \
                        '/' + returnStringAmount(self.BIG_BLIND[self.LEVEL + 1])

        else:
            self.statusMessageSuccess.reset()
            self.statusMessageSuccess.addLabel(self.msg[3])
            self.Button.setLabel('Exit')
            self.VISIBLE_BUTTON = 4
        self.Button.setVisible(True)
        self.setFocus(self.Button)

    def setAutoHide(self):
        self.autoHide = not self.autoHide
        #self.RESET_PANEL = True
        self.setAutoHideStatus()

    def setAutoHideStatus(self):
        self.aHide.setVisible(not self.autoHide)

    def setAnteStatus(self):
        m = self.offScreenX * self.START_SCRIPT
        s = returnStringAmount(self.ANTE[self.LEVEL])
        l = len(s)
        self.anteW = int(self.amountH * .5)
        self.anteX[0] = l * self.anteW
        self.anteX[0] = int((float(self.label2W - self.anteX[0]) / 2) + self.padX + self.imageBorderLeftW)
        self.anteX[1] = self.anteX[0] + self.anteW
        self.anteX[2] = self.anteX[1] + self.anteW
        self.anteX[3] = self.anteX[2] + self.anteW
        s = s + "    "

        for x in range(4):
            self.removeControl(self.AnteStatus[x])
            self.AnteStatus[x] = xbmcgui.ControlImage(m + self.anteX[x], self.amountY, self.anteW, self.amountH, ExtrasPath + 'green_' + s[x] + '.png', "", 0)
            self.addControl(self.AnteStatus[x])

    def setSmBlindStatus(self):
        m = self.offScreenX * self.START_SCRIPT
        s = returnStringAmount(self.SM_BLIND[self.LEVEL])
        l = len(s)
        self.smBlindW = int(self.amountH * .5)
        self.smBlindX[0] = int((float(self.label2W - (l * self.smBlindW)) / 2) + self.padX + self.imageBorderLeftW + self.label2W)
        self.smBlindX[1] = self.smBlindX[0] + self.smBlindW
        self.smBlindX[2] = self.smBlindX[1] + self.smBlindW
        self.smBlindX[3] = self.smBlindX[2] + self.smBlindW
        s = s + "    "

        for x in range(4):
            self.removeControl(self.SmBlindStatus[x])
            self.SmBlindStatus[x] = xbmcgui.ControlImage(m + self.smBlindX[x], self.amountY, self.smBlindW, self.amountH, ExtrasPath + 'green_' + s[x] + '.png', "", 0)
            self.addControl(self.SmBlindStatus[x])

    def setBigBlindStatus(self):
        m = self.offScreenX * self.START_SCRIPT
        s = returnStringAmount(self.BIG_BLIND[self.LEVEL])
        l = len(s)
        self.bigBlindW = int(self.amountH * .5)
        self.bigBlindX[0] = int((float(self.label2W - (l * self.bigBlindW)) / 2) + self.padX + self.imageBorderLeftW + (2 * self.label2W))
        self.bigBlindX[1] = self.bigBlindX[0] + self.bigBlindW
        self.bigBlindX[2] = self.bigBlindX[1] + self.bigBlindW
        self.bigBlindX[3] = self.bigBlindX[2] + self.bigBlindW
        s = s + "    "

        for x in range(4):
            self.removeControl(self.BigBlindStatus[x])
            self.BigBlindStatus[x] = xbmcgui.ControlImage(m + self.bigBlindX[x], self.amountY, self.bigBlindW, self.amountH, ExtrasPath + 'green_' + s[x] + '.png', "", 0)
            self.addControl(self.BigBlindStatus[x])

    def setLevelStatus(self):
        m = self.offScreenX * self.START_SCRIPT
        s = str(int(self.LEVEL))
        l = len(s)
        self.LevelW = int(self.amountH * .5)
        self.levelX[0] = l * self.LevelW
        self.levelX[0] = int((float(self.label2W - self.levelX[0]) / 2) + self.padX + self.imageBorderLeftW + self.label1W )
        self.levelX[1] = self.levelX[0] + self.LevelW
        s = s + "    "

        for x in range(2):
            self.removeControl(self.LevelStatus[x])
            self.LevelStatus[x] = xbmcgui.ControlImage(m + self.levelX[x], self.timeY, self.LevelW, self.amountH, ExtrasPath + 'yellow_' + s[x] + '.png', "", 0)
            self.addControl(self.LevelStatus[x])

    def resetTimer(self, time):
        for x in range(4):
            for y in range(10):
                self.TimeImage[x * 10 + y].setVisible(False)

        t = str('%02d%02d' % (time, 0))
        self.TimeImage[int(t[0])].setVisible(True)
        self.TimeImage[10 + int(t[1])].setVisible(True)
        self.TimeImage[20 + int(t[2])].setVisible(True)
        self.TimeImage[30 + int(t[3])].setVisible(True)

    def setBegin(self):
        self.highlight.setVisible(False)
        self.statusMessageSuccess.reset()
        self.statusMessageSuccess.addLabel(self.msg[1])
        self.statusMessageSuccess.addLabel(self.msg[4])
        self.statusMessageSuccess.addLabel(self.msg[5])
        self.statusMessageSuccess.addLabel(self.msg[6])
        self.padTitle.setLabel(self.ScriptTitle)
        self.LEVEL = 0
        self.setStatus()
        self.START_SCRIPT = True
        self.colon.setVisible(True)
        self.resetTimer(self.LEVEL_TIME[self.LEVEL])
        self.TimeHeading1.setVisible(False)
        self.TimeHeading2.setVisible(False)
        self.TimeHeading.setVisible(True)

    def resetSettings(self):
        self.getConfigValues()
        self.calcPositions()
        self.setChips()
        self.setBegin()
        self.set_panel(0)

    def saveSettings(self):
        self.settings['EndTournamentAlarm']     = self.EndTournamentAlarm
        self.settings['EndTournamentAlarmTime'] = self.EndTournamentAlarmTime
        self.settings['EndLevelAlarm']          = self.EndLevelAlarm
        self.settings['EndLevelAlarmTime']      = self.EndLevelAlarmTime
        self.settings['StartLevelAlarm']        = self.StartLevelAlarm
        self.settings['StartLevelAlarmTime']    = self.StartLevelAlarmTime
        self.settings['WarningAlarm']           = self.WarningAlarm
        self.settings['WarningAlarmTime']       = self.WarningAlarmTime
        self.settings['LEVEL_TIME']             = self.LEVEL_TIME
        self.settings['WARNING_TIME']           = self.WARNING_TIME
        self.settings['ANTE']                   = self.ANTE
        self.settings['SM_BLIND']               = self.SM_BLIND
        self.settings['BIG_BLIND']              = self.BIG_BLIND
        self.settings['BREAK_TIME']             = self.BREAK_TIME
        self.settings['CHIP_AMT']               = self.CHIP_AMT
        self.settings['CHIP_IMAGE']             = self.CHIP_IMAGE
        self.settings['CHIP_TABLE']             = self.CHIP_TABLE
        self.settings['BLIND_TABLE']            = self.BLIND_TABLE

        try:
            PTconfigmgr.saveSettings(self.settings, ExtrasPath + 'PTCfgFile.xml')
        except:
            print "ERROR: saving settings."

        self.setBegin()

    def savePadSettings(self):
        self.padsettings['ScriptTitle']         = self.ScriptTitle
        self.padsettings['PadImageName']        = self.PadImageName
        self.padsettings['padSize']             = self.padSize
        self.padsettings['animate']             = self.animate
        self.padsettings['autoHide']            = self.autoHide
        self.padsettings['autoHideTime']        = self.autoHideTime
        self.padsettings['padOffsetX']          = self.padOffsetX
        self.padsettings['padOffsetY']          = self.padOffsetY

        try:
            PTconfigmgr.savePadSettings(self.padsettings, ExtrasPath + 'PTPadFile.xml')
        except:
            print "ERROR: saving pad position."

    def setConfig(self):
        self.VISIBLE_BUTTON = 5
        self.Button.setLabel('Save')
        self.padTitle.setLabel(self.ScriptTitle + ' (config)')
        self.statusMessageSuccess.reset()
        self.statusMessageSuccess.addLabel(self.msg[2])
        self.ACTIVE_CONTROL = 1
        self.setHighlightPos()
        self.colon.setVisible(False)
        self.START_SCRIPT = False
        self.TimeHeading.setVisible(False)
        self.TimeHeading1.setVisible(True)
        self.TimeHeading2.setVisible(True)

        self.RT1 = str('%02d%02d' % (self.LEVEL_TIME[self.LEVEL], 0))
        self.setTimers()

    def setTimers(self):
        self.RT2 = str('%02d%02d' % (self.LEVEL_TIME[self.LEVEL], self.BREAK_TIME[self.LEVEL]))

        self.TimeImage[0 + int(self.RT1[0])].setVisible(False)
        self.TimeImage[0 + int(self.RT2[0])].setVisible(True)
        self.TimeImage[10 + int(self.RT1[1])].setVisible(False)
        self.TimeImage[10 + int(self.RT2[1])].setVisible(True)

        self.TimeImage[20 + int(self.RT1[2])].setVisible(False)
        self.TimeImage[20 + int(self.RT2[2])].setVisible(True)
        self.TimeImage[30 + int(self.RT1[3])].setVisible(False)
        self.TimeImage[30 + int(self.RT2[3])].setVisible(True)

        self.RT1 = str('%02d%02d' % (self.LEVEL_TIME[self.LEVEL], self.BREAK_TIME[self.LEVEL]))

    def setAmountsPos(self, a):
        if a:
            self.padOffsetX += a
            for x in range(4):
                if x < 2:
                    self.levelX[x] -= a
                    self.LevelStatus[x].setPosition(self.levelX[x], self.timeY)
                self.anteX[x] -= a
                self.AnteStatus[x].setPosition(self.anteX[x], self.amountY)
                self.smBlindX[x] -= a
                self.SmBlindStatus[x].setPosition(self.smBlindX[x], self.amountY)
                self.bigBlindX[x] -= a
                self.BigBlindStatus[x].setPosition(self.bigBlindX[x], self.amountY)
        self.calcPositions()
        self.set_panel(0)

    def setChips(self):
        for x in range(1,6):
            self.removeControl(self.ChipImage[x])
            self.ChipImage[x] = xbmcgui.ControlImage(self.chipX[x], self.chipY, self.chipW, self.chipH, ExtrasPath + self.CHIP_IMAGE[x], "", 2)
            self.addControl(self.ChipImage[x])
            if self.CHIP_AMT[x]:
                s = str('%.2f' % self.CHIP_AMT[x])
                if s[-3:] == ".00":
                    s = s[:-3]
            else:
                s =''
            self.ChipHeading[x].setLabel(s)

    def setChip(self, a):
        if a:
            self.CHIP_IMAGE_NUMBER += a
            self.CHIP_IMAGE[self.CHIP] = 'Chip' + str(self.CHIP_IMAGE_NUMBER) + '.png'
            self.removeControl(self.ChipImage[self.CHIP])
            self.ChipImage[self.CHIP] = xbmcgui.ControlImage(self.chipX[self.CHIP], self.chipY, self.chipW, self.chipH, ExtrasPath + self.CHIP_IMAGE[self.CHIP], "", 2)
            self.addControl(self.ChipImage[self.CHIP])
            if not self.CHIP_IMAGE_NUMBER:
                self.CHIP_AMT[self.CHIP] = 0


        if self.CHIP_AMT[self.CHIP]:
            s = returnStringAmount(self.CHIP_AMT[self.CHIP])
        else:
            s = ''
        self.ChipHeading[self.CHIP].setLabel(s)

    def calcAnteAmount(self, b, a):
        if b == 0 and a == -1:
            b = -1
        elif b == -1:
            b = 0
        elif b == 0:
            b = self.CHIP_TABLE[1]
        else:
            for x in range(1,21):
                if b <= self.CHIP_TABLE[x]:
                    b = self.CHIP_TABLE[x + a]
                    break
        return b

    def calcSmBlindAmount(self, b, a):
        for x in range(1,31):
            if b <= self.BLIND_TABLE[x]:
                b = self.BLIND_TABLE[x + a]
                break
        return b

    def calcBigBlindAmount(self, b, a):
        for x in range(1,31):
            if b <= (self.BLIND_TABLE[x] * 2):
                b = self.BLIND_TABLE[x + a] * 2
                break
        return b

    def setLevelAmount(self, a):
        self.CHANGING_AMOUNT = True
        self.LEVEL += a
        self.setLevelStatus()
        self.setTimers()
        self.setAnteStatus()
        self.setSmBlindStatus()
        self.setBigBlindStatus()
        self.setHighlightPos()
        self.CHANGING_AMOUNT = False

    def setAnteAmount(self, a):
        self.CHANGING_AMOUNT = True
        self.ANTE[self.LEVEL] = self.calcAnteAmount(self.ANTE[self.LEVEL], a)
        self.setAnteStatus()
        self.setHighlightPos()
        if self.ANTE[self.LEVEL] == -1:
            self.LEVELS = self.LEVEL - 1
        self.CHANGING_AMOUNT = False

    def setSmAmount(self, a):
        self.CHANGING_AMOUNT = True
        self.SM_BLIND[self.LEVEL] = self.calcSmBlindAmount(self.SM_BLIND[self.LEVEL], a)
        self.BIG_BLIND[self.LEVEL] = self.SM_BLIND[self.LEVEL] * 2
        self.setSmBlindStatus()
        self.setBigBlindStatus()
        self.setHighlightPos()
        self.CHANGING_AMOUNT = False

    def setBigAmount(self, a):
        self.CHANGING_AMOUNT = True
        self.BIG_BLIND[self.LEVEL] = self.calcBigBlindAmount(self.BIG_BLIND[self.LEVEL], a)
        self.SM_BLIND[self.LEVEL] = float(self.BIG_BLIND[self.LEVEL]) / 2
        self.setBigBlindStatus()
        self.setSmBlindStatus()
        self.setHighlightPos()
        self.CHANGING_AMOUNT = False

    def setChipAmount(self, a):
        self.CHANGING_AMOUNT = True
        self.CHIP_AMT[self.CHIP] = self.calcAnteAmount(self.CHIP_AMT[self.CHIP], a)
        self.CHANGING_AMOUNT = False
        self.setChip(0)

    def setLevelTime(self, a):
        if self.LEVEL_TIME[self.LEVEL] <= 15:
            self.LEVEL_TIME[self.LEVEL] += a + ((a == 1 and self.LEVEL_TIME[self.LEVEL] == 15) * 4)
        else:
            self.LEVEL_TIME[self.LEVEL] += (a * 5)
        self.setTimers()

    def setBreakTime(self, a):
        if self.BREAK_TIME[self.LEVEL] <= 15:
            self.BREAK_TIME[self.LEVEL] += a + ((a == 1 and self.BREAK_TIME[self.LEVEL] == 15) * 4)
        else:
            self.BREAK_TIME[self.LEVEL] += (a * 5)
        self.setTimers()

    def movePadDown(self):
        if self.VISIBLE_BUTTON == 5:
            self.decreaseValue()
        else:
            self.padOffsetY += 5
            self.setAmountsPos(0)

    def movePadUp(self):
        if self.VISIBLE_BUTTON == 5:
            self.increaseValue()
        else:
            self.padOffsetY -= 5
            self.setAmountsPos(0)

    def movePadLeft(self):
        if self.VISIBLE_BUTTON == 5:
            self.ACTIVE_CONTROL -= 1
            if self.ACTIVE_CONTROL == 0:
                self.ACTIVE_CONTROL = 16
            self.setHighlightPos()
        else:
            self.setAmountsPos(5)

    def movePadRight(self):
        if self.VISIBLE_BUTTON == 5:
            self.ACTIVE_CONTROL += 1
            if self.ACTIVE_CONTROL == 17:
                self.ACTIVE_CONTROL = 1
            self.setHighlightPos()
        else:
            self.setAmountsPos(-5)

    def increaseValue(self):
        if self.ACTIVE_CONTROL >= 7 and self.ACTIVE_CONTROL <= 11:
            if self.CHIP_IMAGE_NUMBER < 12:
                self.setChip(1)
        elif self.ACTIVE_CONTROL >= 12:
            if self.CHIP_AMT[self.CHIP] < self.CHIP_TABLE[20]:
                self.setChipAmount(1)
        elif self.ACTIVE_CONTROL == 1:
            if self.LEVEL_TIME[self.LEVEL] < 90:
                self.setLevelTime(1)
        elif self.ACTIVE_CONTROL == 2:
            if self.BREAK_TIME[self.LEVEL] < 90:
                self.setBreakTime(1)
        elif self.ACTIVE_CONTROL == 3:
            if self.LEVEL < 20 and self.ANTE[self.LEVEL] != -1:
                self.setLevelAmount(1)
        elif self.ACTIVE_CONTROL == 4:
            if self.ANTE[self.LEVEL] < self.CHIP_TABLE[20]:
                self.setAnteAmount(1)
        elif self.ACTIVE_CONTROL == 5:
            if self.SM_BLIND[self.LEVEL] < self.BLIND_TABLE[30]:
                self.setSmAmount(1)
        elif self.ACTIVE_CONTROL == 6:
            if self.BIG_BLIND[self.LEVEL] < (self.BLIND_TABLE[30] * 2):
                self.setBigAmount(1)

    def decreaseValue(self):
        if self.ACTIVE_CONTROL >= 7 and self.ACTIVE_CONTROL <= 11:
            if self.CHIP_IMAGE_NUMBER > 0:
                self.setChip(-1)
        elif self.ACTIVE_CONTROL >= 12 and self.CHIP_AMT[self.CHIP]:
            if self.CHIP_AMT[self.CHIP] > 0:
                self.setChipAmount(-1)
        elif self.ACTIVE_CONTROL == 1:
            if self.LEVEL_TIME[self.LEVEL] > 5:
                self.setLevelTime(-1)
        elif self.ACTIVE_CONTROL == 2:
            if self.BREAK_TIME[self.LEVEL] > 0:
                self.setBreakTime(-1)
        elif self.ACTIVE_CONTROL == 3:
            if self.LEVEL > 1:
                self.setLevelAmount(-1)
        elif self.ACTIVE_CONTROL == 4:
            if (self.ANTE[self.LEVEL] == 0 and self.LEVEL > 1) or self.ANTE[self.LEVEL] > 0:
                self.setAnteAmount(-1)
        elif self.ACTIVE_CONTROL == 5:
            if self.SM_BLIND[self.LEVEL] > self.BLIND_TABLE[1]:
                self.setSmAmount(-1)
        elif self.ACTIVE_CONTROL == 6:
            if self.BIG_BLIND[self.LEVEL] > (self.BLIND_TABLE[1] * 2):
                self.setBigAmount(-1)

    def setHighlightPos(self):
        self.highlight.setVisible(False)

        if self.ACTIVE_CONTROL >= 7 and self.ACTIVE_CONTROL <= 11:
            self.CHIP = self.ACTIVE_CONTROL - 6
            self.CHIP_IMAGE_NUMBER = int(self.CHIP_IMAGE[self.CHIP][4:-4])
            self.highlightX = self.chipX[self.CHIP]
            self.highlightY = self.chipY
            self.highlightW = self.chipW
            self.highlightH = self.chipH
        elif self.ACTIVE_CONTROL >= 12:
            self.CHIP = self.ACTIVE_CONTROL - 11
            self.highlightX = self.chipX[self.CHIP]
            self.highlightY = self.chipHeadingY
            self.highlightW = self.chipW
            self.highlightH = self.labelH
        elif self.ACTIVE_CONTROL == 1:
            self.highlightX = self.timeX[0]
            self.highlightY = self.timeY
            self.highlightW = self.timeW * 2
            self.highlightH = self.timeH
        elif self.ACTIVE_CONTROL == 2:
            self.highlightX = self.timeX[2]
            self.highlightY = self.timeY
            self.highlightW = self.timeW * 2
            self.highlightH = self.timeH
        elif self.ACTIVE_CONTROL == 3:
            self.highlightX = self.label3X
            self.highlightY = self.timeY
            self.highlightW = self.label2W
            self.highlightH = self.amountH
        elif self.ACTIVE_CONTROL == 4:
            self.highlightX = self.label1X
            self.highlightY = self.amountY
            self.highlightW = self.label2W
            self.highlightH = self.amountH
        elif self.ACTIVE_CONTROL == 5:
            self.highlightX = self.label2X
            self.highlightY = self.amountY
            self.highlightW = self.label2W
            self.highlightH = self.amountH
        elif self.ACTIVE_CONTROL == 6:
            self.highlightX = self.label3X
            self.highlightY = self.amountY
            self.highlightW = self.label2W
            self.highlightH = self.amountH

        self.highlight.setHeight(self.highlightH)
        self.highlight.setWidth(self.highlightW)
        self.highlight.setPosition(self.highlightX, self.highlightY)
        self.highlight.setVisible(True)

    def pauseTimer(self):
        self.VISIBLE_BUTTON = 3
        self.Button.setLabel('Resume')

    def resumeTimer(self):
        self.VISIBLE_BUTTON = 2
        self.Button.setLabel('Pause')

    def startTimer(self):
        self.START_SCRIPT = False
        self.resumeTimer()
        self.LevelTimer()

    def breakTimer(self):
        self.BREAK_TIMER = True
        if self.LEVEL <= self.LEVELS:
            self.statusMessageSuccess.reset()
            self.statusMessageSuccess.addLabel('Level (' + str(self.LEVEL) + \
                ') starts in ' + str('%d:%02d' % (self.BREAK_TIME[self.LEVEL], 0)))
            seconds = 60 * self.BREAK_TIME[self.LEVEL]
            t2 = str('%02d%02d' % (self.LEVEL_TIME[self.LEVEL],0))
            if seconds:
                activateGUI()
                self.setFocus(self.Button)

            try:
                for cnt in range(1, seconds + 1):
                    for x in range(10):
                        sleep(.1)
                        if x == 4:
                            self.blinkTimer(False, t2)
                        elif x == 9:
                            self.blinkTimer(True, t2)

                        if self.RAISE_EXCEPTION or self.EXIT_SCRIPT:
                            self.blinkTimer(True, t2)
                            cnt = seconds
                            raise loopExit

                    #only needed if music ends
                    self.setFocus(self.Button)
                    m = int(float(seconds - cnt) / 60)
                    s = int(float(seconds - cnt) % 60)
                    self.statusMessageSuccess.reset()
                    self.statusMessageSuccess.addLabel('Level (' + str(self.LEVEL) + \
                        ') starts in ' + str('%d:%02d' % (m, s)))

            except loopExit:
                self.RAISE_EXCEPTION = False

            self.BREAK_TIMER = False
            if not self.EXIT_SCRIPT:
                self.statusMessageSuccess.reset()
                self.startTimer()

    def LevelTimer(self):
        self.TIMER_RUNNING = True
        self.statusMessageSuccess.reset()
        self.statusMessageSuccess.addLabel(self.msg[0])
        self.notifyStartLevel()
        seconds = 60 * self.LEVEL_TIME[self.LEVEL]
        t2 = str('%02d%02d' % (int(float(seconds) / 60), int(float(seconds) % 60)))
        t3 = str('%02d%02d' % (self.WARNING_TIME,0))

        #if self.autoHide:
        self.autoHideTimer.start()

        try:
            for cnt in range(1, seconds + 1):
                for x in range(10):
                    sleep(.1)
                    while self.VISIBLE_BUTTON == 3:
                        for y in range(10):
                            sleep(.1)
                            if self.EXIT_SCRIPT:
                                self.blinkTimer(True, t2)
                                cnt = seconds
                                raise loopExit
                            elif y == 4:
                                self.blinkTimer(False, t2)
                            elif y == 9:
                                self.blinkTimer(True, t2)

                t = str('%02d%02d' % (int(float(seconds - cnt) / 60), int(float(seconds - cnt) % 60)))
                self.TimeImage[int(t2[0])].setVisible(False)
                self.TimeImage[int(t[0])].setVisible(True)
                self.TimeImage[10 + int(t2[1])].setVisible(False)
                self.TimeImage[10 + int(t[1])].setVisible(True)
                self.TimeImage[20 + int(t2[2])].setVisible(False)
                self.TimeImage[20 + int(t[2])].setVisible(True)
                self.TimeImage[30 + int(t2[3])].setVisible(False)
                self.TimeImage[30 + int(t[3])].setVisible(True)
                t2 = t

                if t2 == t3:
                    thread.start_new_thread(playWarning, (self.WarningAlarm, self.WarningAlarmTime,))

                #only needed if music ends
                self.setFocus(self.Button)

            self.TIMER_RUNNING = False
            self.notifyTimesUp()

        except loopExit:
            self.TIMER_RUNNING = False

    def blinkTimer(self, a, t2):
        self.TimeImage[int(t2[0])].setVisible(a)
        self.TimeImage[10 + int(t2[1])].setVisible(a)
        self.TimeImage[20 + int(t2[2])].setVisible(a)
        self.TimeImage[30 + int(t2[3])].setVisible(a)

    def notifyStartLevel(self):
        playAlarm(self.StartLevelAlarm, self.StartLevelAlarmTime)
        self.setFocus(self.Button)

    def notifyTimesUp(self):
        self.Button.setVisible(False)
        if not self.HIDE_PANEL:
            self.slidePanel()
        if self.LEVEL == self.LEVELS:
            playAlarm(self.EndTournamentAlarm, self.EndTournamentAlarmTime)
        else:
            playAlarm(self.EndLevelAlarm, self.EndLevelAlarmTime)
        self.setStatus()
        self.breakTimer()

    def slidePanel(self):
        if not self.HIDING_PANEL:
            self.HIDE_PANEL = not self.HIDE_PANEL
            if self.HIDE_PANEL:
                self.animate_panel(-1)
            else:
                self.animate_panel(1)

    def animate_panel(self, slide):
        self.HIDING_PANEL = True
        if self.animate:
            if slide == -1:
                pct = self.slideRange
            else:
                pct = 1
            for x in range(self.slideRange):
                m = int(pct**2 * 0.295)
                self.set_panel(m)
                pct += slide
                sleep(self.slideSpeed)
        else:
            if slide == -1:
                self.set_panel(0)
            else:
                self.set_panel(self.screenW)

        self.HIDING_PANEL = False

    def set_panel(self, m):
        self.pad.setPosition(m + self.padX, self.padY)

        self.padTitle.setPosition(m + self.titleX, self.titleY)

        self.aHide.setPosition(m + self.aHideX, self.aHideY)

        self.TimeHeading.setPosition(m + self.label1X, self.label1Y)
        self.TimeHeading1.setPosition(m + self.timeX[0], self.label1Y)
        self.TimeHeading2.setPosition(m + self.timeX[2], self.label1Y)

        self.colon.setPosition(m + self.colonX, self.timeY)

        for x in range(4):
            for y in range(10):
                self.TimeImage[x * 10 + y].setPosition(m + self.timeX[x], self.timeY)

        for x in range(1,6):
            self.ChipImage[x].setPosition(m + self.chipX[x], self.chipY)
            self.ChipHeading[x].setPosition(m + self.chipX[x], self.chipHeadingY)

        self.AnteHeading.setPosition(m + self.label1X, self.label2Y)
        for x in range(4):
            self.AnteStatus[x].setPosition(m + self.anteX[x], self.amountY)

        self.SmBlindHeading.setPosition(m + self.label2X, self.label2Y)
        for x in range(4):
            self.SmBlindStatus[x].setPosition(m + self.smBlindX[x], self.amountY)

        self.BigBlindHeading.setPosition(m + self.label3X, self.label2Y)
        for x in range(4):
            self.BigBlindStatus[x].setPosition(m + self.bigBlindX[x], self.amountY)

        self.LevelHeading.setPosition(m + self.label3X, self.label1Y)
        for x in range(2):
            self.LevelStatus[x].setPosition(m + self.levelX[x], self.timeY)

        self.Button.setPosition(m + self.buttonX, self.buttonY)

        self.statusMessageSuccess.setPosition(m + self.messageX, self.messageY)

        self.highlight.setPosition(m + self.highlightX, self.highlightY)

    def sizePanel(self):
        self.padSize = ((self.padSize == 0) * 1)
        self.savePadSettings()
        self.slidePanel()
        self.close()

    def exitScript(self):
        self.EXIT_SCRIPT = True
        self.savePadSettings()
        self.slidePanel()
        try:
            self.startScript.join(1)
            self.autoHideTimer.join(1)
        finally:
            #sleep(1)
            self.close()

    def onAction(self, action):
        if self.HIDE_PANEL and not self.EXIT_SCRIPT:
            self.RESET_PANEL = True
            if action == ACTION_WHITE_BUTTON and self.START_SCRIPT:
                self.setConfig()
            elif action == ACTION_0 or action == ACTION_Y_BUTTON:
                self.setAutoHide()
            elif action == ACTION_X_BUTTON and self.START_SCRIPT and not self.CHANGING_AMOUNT:
                self.sizePanel()
            elif action == ACTION_MOVE_RIGHT and not self.CHANGING_AMOUNT:
                self.movePadRight()
            elif action == ACTION_MOVE_LEFT and not self.CHANGING_AMOUNT:
                self.movePadLeft()
            elif action == ACTION_MOVE_UP and not self.CHANGING_AMOUNT:
                self.movePadUp()
            elif action == ACTION_MOVE_DOWN and not self.CHANGING_AMOUNT:
                self.movePadDown()
            elif self.VISIBLE_BUTTON == 5 and action == ACTION_PARENT_DIR:
                self.resetSettings()
            elif self.VISIBLE_BUTTON == 2 and action == ACTION_X_BUTTON:
                self.slidePanel()
            elif not self.VISIBLE_BUTTON == 2 and not self.EXIT_SCRIPT:
                if action == ACTION_PREVIOUS_MENU:
                    self.exitScript()
        elif not self.EXIT_SCRIPT and action != ACTION_SELECT_ITEM:
            self.slidePanel()

    def onControl(self, control):
        if self.HIDE_PANEL and not self.EXIT_SCRIPT:
            if self.VISIBLE_BUTTON == 1:
                if self.BREAK_TIMER:
                    self.RAISE_EXCEPTION = True
                else:
                    self.breakTimer()
            elif self.VISIBLE_BUTTON == 2:
                self.pauseTimer()
            elif self.VISIBLE_BUTTON == 3:
                self.resumeTimer()
            elif self.VISIBLE_BUTTON == 4:
                self.exitScript()
            elif self.VISIBLE_BUTTON == 5:
                self.saveSettings()
        elif not self.EXIT_SCRIPT:
            self.slidePanel()

class loopExit(Exception):
    pass

class startScript(threading.Thread):

    def __init__(self, windowOverlay):
        self.windowOverlay = windowOverlay
        threading.Thread.__init__(self)

    def run(self):
        self.windowOverlay.slidePanel()

class autoHideTimer(threading.Thread):

    def __init__(self, windowOverlay):
        self.windowOverlay = windowOverlay
        threading.Thread.__init__(self)

    def run(self):
        while self.windowOverlay.TIMER_RUNNING and not self.windowOverlay.EXIT_SCRIPT:
            self.windowOverlay.RESET_PANEL = False
            try:
                while self.windowOverlay.HIDE_PANEL and self.windowOverlay.autoHide:
                    s = self.windowOverlay.autoHideTime * 10
                    for x in range(s):
                        sleep(.1)
                        if self.windowOverlay.VISIBLE_BUTTON == 3 or not self.windowOverlay.HIDE_PANEL \
                            or not self.windowOverlay.TIMER_RUNNING or self.windowOverlay.RESET_PANEL:
                            raise loopExit
                    if self.windowOverlay.HIDE_PANEL:
                        self.windowOverlay.slidePanel()
            except:
                pass

def playWarning(alarm, SleepTime):
    playAlarm(alarm, SleepTime)

def playAlarm(alarm, SleepTime):
    CURRENT_FILE = getPlayingFile()
    CURRENT_TIME = getPlayingTime()
    xbmc.Player().play(ExtrasPath + alarm)
    sleep(SleepTime)
    playFile(CURRENT_FILE, CURRENT_TIME)
    activateGUI()

def playFile(CURRENT_FILE, CURRENT_TIME):
    if CURRENT_FILE == "{none}":
        xbmc.Player().stop()
    else:
        xbmc.Player().play(CURRENT_FILE)
        xbmc.Player().seekTime(CURRENT_TIME)

def getPlayingFile():
    if xbmc.Player().isPlayingAudio() or xbmc.Player().isPlayingVideo():
        CURRENT_FILE = xbmc.Player().getPlayingFile()
    else:
        CURRENT_FILE = "{none}"
    return CURRENT_FILE

def getPlayingTime():
    if xbmc.Player().isPlayingAudio() or xbmc.Player().isPlayingVideo():
        CURRENT_TIME = xbmc.Player().getTime()
    else:
        CURRENT_TIME = "{none}"
    return CURRENT_TIME

def activateGUI():
    if xbmc.Player().isPlayingAudio():
        xbmc.executebuiltin('XBMC.ActivateWindow(2006)')
    elif xbmc.Player().isPlayingVideo():
        xbmc.executebuiltin('XBMC.ActivateWindow(2005)')
    sleep(.5)

def returnStringAmount(a):
    e = ''
    if a >= 10000:
        a = int(float(a) / 1000)
        e = 'k'
    s = str('%.2f' % a)
    if s[-3:] == ".00":
        s = s[:-3]
    s = s + e
    return s

while 1:
    MyDisplay = windowOverlay()
    MyDisplay.doModal()
    if MyDisplay.EXIT_SCRIPT: break
    #del MyDisplay
del MyDisplay
