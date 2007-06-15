"""
    WindowSettings

    A WindowXML setup to handle the basis modifying the settings provided by the settings class

    Author: Sean Donnellan (Donno)  [darkdonno@gmail.com]
    Depends on: xbmcgui, xbmc, os
    Requires: A Setting and Language class passed to it

    How to Use:
        from windowsettings import WindowSettings
        class className(WindowSettings):
            def __init__(self,xmlName,thescriptPath,defaultName,forceFallback):
                WindowSettings.__init__(self, xmlName,thescriptPath,defaultName,forceFallback, scriptSettings, lang, __title__)
                
        # the point is u pass all the main info on as well as the settings and language classes and title
"""

### IMPORTS ###
import xbmcgui
import xbmc
import os

#from language import Language
#from settings import Settings

### VIEWS ###
VIEW_SETTINGS_ROOT = 1
VIEW_SETTINGLIST = 2
VIEW_LISTTOREMOVE = 3
VIEW_SUBSETTINGS = 4
VIEW_SETTINGSIMPLELIST = 5
VIEW_SIMPLELISTTOREMOVE = 6

### KEYS ###
KEY_BUTTON_BACK = 275
KEY_KEYBOARD_ESC = 61467

class WindowSettings(xbmcgui.WindowXML):
    def __init__(self, xmlName, thescriptPath,defaultName,forceFallback, scriptSettings, language, title):
        #print "WindowSettings.__init__() starting"
        self.title = title
        self.thescriptPath = thescriptPath
        self.depth = 0
        self.language = language
        
        self.settingName = ""
        self.theSettings = scriptSettings

        self.preSettings = []
        self.curSettings = scriptSettings
        self.view = VIEW_SETTINGS_ROOT
        self.addType = "text"
        #print "WindowSettings.__init__() finished"

    def onInit(self):
        self.populateList()

    def populateList(self):
        for set in self.curSettings.settings:
            if self.curSettings.getSettingType(set) == "list":
                self.addItem(self.SettingListItem(set,"-- List --"))
            elif self.curSettings.getSettingType(set) == "simplelist":
                self.addItem(self.SettingListItem(set,"-- List --"))
            elif self.curSettings.getSettingType(set) == "settings":
                self.addItem(self.SettingListItem(set,"-- Settings --"))
            else:
                self.addItem(self.SettingListItem(set, self.curSettings.getSetting(set)))

        if (self.depth == 0):
            self.addItem(self.MenuListItem(self.language.string(3,"Quit %s") % self.title,self.language.string(9,"Leave %s") % self.language.string(1,"Settings"), "exit.png", "exit.png"))
        else:
            self.addItem(self.MenuListItem(self.language.string(11,"Back to %s") % self.language.string(1,"Settings"),self.language.string(9,"Leave %s") % "list", "back.png", "back.png"))

    def popuplateListwithList(self,isSimple=0):
        if (isSimple == 0):
            for i in self.curSettings.getSetting(self.settingName)[1]:
                if (i[2] == "settings"):
                    self.addItem(self.SettingListItem(i[0],"-- Settings --"))
                elif (i[2] == "simplelist"):
                    self.addItem(self.SettingListItem(i[0],"-- List --"))
                else:
                    self.addItem(self.SettingListItem(i[0],i[1]))
        else:
            for i in self.curSettings.getSetting(self.settingName):
                self.addItem(i)
        self.addItem(self.MenuListItem(self.language.string(12,"Add %s") % self.language.string(14,"item"), self.language.string(16,"Add an item to the list"), "edit_add.png", "edit_add.png"))
        self.addItem(self.MenuListItem(self.language.string(18,"Remove %s") % self.language.string(14,"item"), self.language.string(17,"Remove an item from list"), "edit_remove.png", "edit_remove.png"))
        self.addItem(self.MenuListItem(self.language.string(11,"Back to %s") % self.language.string(1,"Settings"),self.language.string(9,"Leave %s") % "list", "back.png", "back.png"))

    def goBack(self):
        if (self.view == VIEW_SETTINGS_ROOT):
            self.theSettings.saveXMLfromArray()
            self.close()
        elif (self.view == VIEW_SIMPLELISTTOREMOVE):
            self.clearList()
            self.view = VIEW_SETTINGSIMPLELIST
            self.popuplateListwithList(1)
        elif (self.view == VIEW_LISTTOREMOVE):
            self.clearList()
            self.view = VIEW_SETTINGLIST
            self.popuplateListwithList()
        elif (self.view == VIEW_SETTINGLIST):
            self.clearList()
            preSet = self.preSettings[len(self.preSettings) - 1]
            self.settingName = preSet[0]
            self.view = preSet[2]
            self.preSettings.remove(preSet)
            self.populateList()
        elif (self.view == VIEW_SETTINGSIMPLELIST):
            self.clearList()
            preSet = self.preSettings[len(self.preSettings) - 1]
            self.settingName = preSet[0]
            self.view = preSet[2]
            self.preSettings.remove(preSet)
            self.populateList()
        elif (self.view == VIEW_SUBSETTINGS):
            self.depth -= 1
            self.view = VIEW_SUBSETTINGS
            preSet = self.preSettings[len(self.preSettings) - 1]
            self.settingName = preSet[0]
            self.curSettings = preSet[1]

            self.clearList()
            self.preSettings.remove(preSet)
            if (preSet[2] == VIEW_SETTINGLIST):
                self.view = VIEW_SETTINGLIST
                self.popuplateListwithList()
            else:
                if (self.depth == 0):
                    self.settingName = ""
                    self.view = VIEW_SETTINGS_ROOT
                    self.curSettings = self.theSettings
                self.populateList()
        else:
            xbmcgui.Dialog().ok(self.title , "No goBack implmeneted for this view") # no need to translate only for testing/just incase.

    def onAction(self, action):
        buttonCode =  action.getButtonCode()
        actionID   =  action.getId()
        if (buttonCode == KEY_BUTTON_BACK or buttonCode == KEY_KEYBOARD_ESC or buttonCode == 61467):
            self.goBack()

    def onClick(self, controlID):
        if (50 <= controlID <= 52):
            # Bottom item in the list should always be a 'go back/quit/cancel'
            if (self.getCurrentListPosition() == self.getListSize()  - 1):
                self.goBack()
                return

            # Important Values:
            curPos  = self.getCurrentListPosition()
            curItem = self.getListItem(curPos)
            curName = curItem.getLabel()

            if (self.view == VIEW_SETTINGS_ROOT or self.view == VIEW_SUBSETTINGS):
                type = self.curSettings.getSettingType(curName)
                if (type == "text"):
                    value = self.showKeyboard(self.language.string(10,"Change %s") % curName,curItem.getLabel2())
                    curItem.setLabel2(value)
                    self.curSettings.setSetting(curName,value)
                elif (type == "boolean"):
                    if self.curSettings.getSetting(curName,"true") == "false":
                        self.curSettings.setSetting(curName,"true")
                        curItem.setLabel2("true")
                    else:
                        self.curSettings.setSetting(curName,"false")
                        curItem.setLabel2("false")
                elif (type == "list"):
                    xbmcgui.lock()
                    self.preSettings.append([curName, self.curSettings, self.view])
                    self.view = VIEW_SETTINGLIST
                    self.settingName = curName
                    self.clearList()
                    self.popuplateListwithList()
                    xbmcgui.unlock()
                elif (type == "simplelist"):
                    self.preSettings.append([curName, self.curSettings, self.view])
                    self.view = VIEW_SETTINGSIMPLELIST
                    xbmcgui.lock()
                    self.clearList()
                    self.settingName = curName
                    self.popuplateListwithList(1)
                    xbmcgui.unlock()
                elif (type == "settings"):
                    xbmcgui.lock()
                    self.view = VIEW_SUBSETTINGS
                    self.preSettings.append([curName, self.curSettings, self.view])
                    self.settingName = curName
                    self.clearList()
                    self.depth += 1
                    self.curSettings = self.curSettings.getSetting(curName,None)
                    self.populateList()
                    xbmcgui.unlock()
            elif (self.view == VIEW_SETTINGLIST or self.view == VIEW_SETTINGSIMPLELIST ):
                # three actions can be done on when viewing a settings of type list or simplelist
                # Changing, Adding, and choosing to Delete
                if  (self.getCurrentListPosition() == self.getListSize()  - 3):

                    if (self.view == VIEW_SETTINGSIMPLELIST):
                        value1 = self.showKeyboard(self.language.string(12,"Add %s") % self.language.string(14,"item"),"")
                        self.curSettings.addSettingInSimpleList(self.settingName,value1)
                        self.addnewItem(value1)
                    else:
                        self.onListAdd(self.settingName)

                elif  (self.getCurrentListPosition() == self.getListSize()  - 2):
                    if (self.view == VIEW_SETTINGSIMPLELIST):
                        self.view = VIEW_SIMPLELISTTOREMOVE
                    else:
                        self.view = VIEW_LISTTOREMOVE
                    self.removeItem( self.getListSize() - 1 )
                    self.removeItem( self.getListSize() - 1 )
                    self.removeItem( self.getListSize() - 1 )
                    self.addItem(self.MenuListItem(self.language.string(19,"Cancel"), self.language.string(20,"Cancel the operation"), "cancel.png", "cancel.png"))
                    #self.addItem(MenuListItem(self.language.string(11,"Back to %s") % self.language.string(15,"list"),self.language.string(21,"Stop the operation"), "back.png", "back.png"))
                else:
                    # Change based on type
                    if (self.view == VIEW_SETTINGLIST):
                        type = self.curSettings.getSettingTypeInList(self.settingName,curPos)
                    else:
                        type = "text"
                    value1 = self.showKeyboard(self.language.string(10,"Change %s") % "",curItem.getLabel())
                    curItem.setLabel(value1)

                    if (self.view == VIEW_SETTINGSIMPLELIST):
                        self.curSettings.setSettingInSimpleList( self.settingName , curName , value1 )
                        return
                    if (type == "settings"):
                        xbmcgui.lock()
                        self.preSettings.append([self.settingName, self.curSettings, self.view])
                        self.view = VIEW_SUBSETTINGS
                        self.curSettings = self.curSettings.getSettingInList(self.settingName,curPos)
                        self.settingName = curName
                        self.clearList()
                        self.depth += 1
                        self.populateList()
                        xbmcgui.unlock()
                        return
                    value2 = ""
                    if (type == "text"):
                        value2 = self.showKeyboard(self.language.string(13,"Set %s") % value1,curItem.getLabel2())
                    elif (type == "boolean"):
                        if curItem.getLabel2() == "false":
                            value2 = "true"
                        else:
                            value2 = "false"
                    curItem.setLabel2(value2)
                    self.curSettings.setSettingInList( self.settingName , curName , value1 , value2 )

            elif (self.view == VIEW_LISTTOREMOVE or self.view == VIEW_SIMPLELISTTOREMOVE):
                self.curSettings.removeSettingInList ( self.settingName , curPos )
                self.removeItem( curPos )
    
    def addnewItem(self, value1,value2="",type="text"):
        xbmcgui.lock()
        self.removeItem( self.getListSize() - 1 )
        self.removeItem( self.getListSize() - 1 )
        self.removeItem( self.getListSize() - 1 )
        if (self.view == VIEW_SETTINGSIMPLELIST):
            self.curSettings.addSettingInSimpleList(self.settingName,value1)
            self.addItem(value1)
        elif (self.view == VIEW_SETTINGLIST):
            if (type == "text" or type == "boolean"):
                self.curSettings.addSettingInList(self.settingName,value1,value2,"text")
                self.addItem(self.SettingListItem(value1,value2))
            elif (type == "settings"):
                self.curSettings.addSettingInList(self.settingName,value1,value2,"settings")
                self.addItem(self.SettingListItem(value1,"-- Settings --"))
                ## ZOOM into item so user can edit it
                self.preSettings.append([self.settingName, self.curSettings, self.view])
                self.view = VIEW_SUBSETTINGS
                self.curSettings = value2
                self.settingName = value1
                self.clearList()
                self.depth += 1
                self.populateList()
                xbmcgui.unlock()
                return
        else:
            print "*** ERROR ***"
        self.addItem(self.MenuListItem(self.language.string(12,"Add %s") % self.language.string(14,"item"), self.language.string(16,"Add an item to the list"), "edit_add.png", "edit_add.png"))
        self.addItem(self.MenuListItem(self.language.string(18,"Remove %s") % self.language.string(14,"item"), self.language.string(17,"Remove an item from list"), "edit_remove.png", "edit_remove.png"))
        self.addItem(self.MenuListItem(self.language.string(11,"Back to %s") % self.language.string(1,"Settings"),self.language.string(9,"Leave %s") % "list", "back.png", "back.png"))
        xbmcgui.unlock()

        #END OF FUNCTION addnewItem()
    def onFocus(self, controlID):
        pass

    def onListAdd(self, settingName):
        """
            This function is for overwritting the add operation on a normal List
            Generally so the client coder, can hook a custom add 
                Call this function if u want it to od boolean or text 
                and do set self.addType = "text" or self.addType = "boolean"
        """
        value1 = self.showKeyboard(self.language.string(12,"Add %s") % self.language.string(14,"item"),"")
        if (self.addType == "text"):
            value2 = self.showKeyboard(self.language.string(10,"Change %s") % value1,"")
            self.addnewItem(value1,value2,"text")
        elif (self.addType == "boolean"):
            self.addnewItem(value1,value2,"boolean")
    def showKeyboard(self, heading,default=""):
        # Open the Virutal Keyboard.
        keyboard = xbmc.Keyboard(default,heading)
        keyboard.doModal()
        if (keyboard.isConfirmed()):
            return keyboard.getText()
        else:
            return default

    def SettingListItem(self, label1,label2):
        return xbmcgui.ListItem(label1,label2,"","")

    def MenuListItem(self, label1,label2,thumb,icon):
        basePath = os.path.join(self.thescriptPath,'media')
        return xbmcgui.ListItem(label1,label2,os.path.join(basePath,thumb) , os.path.join(basePath,icon))
