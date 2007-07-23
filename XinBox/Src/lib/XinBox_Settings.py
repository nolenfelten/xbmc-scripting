from xml.dom import minidom

from os.path import join, exists
from os import mkdir
import re
import XinBox_Util

DATADIR = XinBox_Util.__datadir__
SETTINGSDIR = XinBox_Util.__settingdir__
ACCOUNTDIR = XinBox_Util.__accountsdir__
TEMPDIR = XinBox_Util.__tempdir__

class Settings:
    """
        Settings Class
            For reading and writting XML Files to hold the settings for scripts
        Coded by Donno

        getSetting, saveXMLfromArray and other get methods are designed for outside access
        get methods are

    """
    settingVer = 1.0

    def __init__(self,filename,scriptTitle,defaultSettings,fromFile=1):
        self.scriptTitle = scriptTitle
        
        self.filename = filename
        self.defaultSettings = defaultSettings
        self.settings = {}
        if (fromFile == 1):
            # Load from File
            self.load()
        elif (fromFile == 2):
            # Load from Default Settings
            self.settings = defaultSettings

        
    def getSettingType(self,settingName):
        """
            Returns the value of the setting
            If the setting doesn't exist it will return no such setting
        """
        if self.settings.has_key(settingName):
            return self.settings[settingName][1].strip()
        else:
            return "no such setting"

    def getSetting(self, settingName, defaultValue=""):
        """
            Returns the value of the setting
            If the setting doesn't exist it will use default Value just incase internal one has none
        """
        if self.settings.has_key(settingName):
            return self.settings[settingName][0]
        elif self.defaultSettings.has_key(settingName):
            return self.defaultSettings[settingName][0]
        else:
            return defaultValue


    def getSettingTypeInList(self,settingName,pos):
        """

        """
        if self.settings.has_key(settingName):
            return self.settings[settingName][0][1][pos][2].strip()
        else:
            return "none"

    def getSettingInList(self,settingName,pos):
        """

        """
        if self.settings.has_key(settingName):
            return self.settings[settingName][0][1][pos][1]
        else:
            return "none"

    def getSettingInListbyname(self,settingName,name):
        if self.settings.has_key(settingName):
            for item in self.settings[settingName][0][1]:
                if item[0] == name:
                    return item[1]
            return "none"
        else:
            return "none"

    def setSettingInList(self, settingName, Name, newValue):
        """
            changes a setting in a list, in the settings array.
        """
        for item in self.settings[settingName][0][1]:
            if (item[0] == Name):
                item[1] = newValue     

    def setSettingnameInList(self, settingName, oldName, newName):
        for item in self.settings[settingName][0][1]:
            if (item[0] == oldName):
                item[0] = newName
                
    def setSettingInSimpleList(self, settingName, oldName, newName):
        """
            changes a setting in a Simple List, in the settings array.
        """
        for i in xrange(0,len(self.settings[settingName][0])):
            if (self.settings[settingName][0][i] == oldName):
                self.settings[settingName][0][i] = newName

    def addSettingInSimpleList(self, settingName, newName):
        """
            add a new item in a list, in the settings array.
        """
        self.settings[settingName][0].append(newName)
        
    def addSettingInList(self, settingName, newName, newValue, type):
        """
            add a new item in a list, in the settings array.
        """
        self.settings[settingName][0][1].append([ newName , newValue, type])
        
    def removeSettingInList(self, settingName, itemPosition):
        """
            remove a item in a list or simple list, in the settings array.
        """
        type = self.getSettingType(settingName)

        if self.settings.has_key(settingName):
            if (type == "simplelist"):
                if (0 <= itemPosition < len(self.settings[settingName][0])):
                    del self.settings[settingName][0][itemPosition]
            elif (type == "list"):
                if (itemPosition < len(self.settings[settingName][0][1])):
                    del self.settings[settingName][0][1][itemPosition]
            else:
                print "---- Not A SimpleList or List wierd ----"
        # END OF FUNCTION

    def removeinbox(self, settingName,inbox):
        for i,item in enumerate(self.settings[settingName][0][1]):
            if item[0] == inbox:
                del self.settings[settingName][0][1][i]
                break
                
    def setSetting(self,settingName, value):
        """
            Sets the Setting
        """
        self.settings[settingName][0] = value

    def loadFromDOM(self, xmldoc, sub=0):
        try:
            if (xmldoc.toxml() == "" and sub == 0):
                self.create()
            xmlsettings = xmldoc.getElementsByTagName("settings")[0]
        except:
            self.create()
            return
        elements = xmldoc.getElementsByTagName("setting")
        for elem in elements:
            if (elem.parentNode == xmlsettings):
                if (elem.getAttribute('type') == "list"):
                    theList = []
                    #<"elem.getAttribute('identifier')" name="testing">
                    for e in elem.getElementsByTagName(elem.getAttribute('identifier')):
                        if (e.getAttribute('type')  == "settings"):
                            subSettings = self.createSubSettingsDOM(e.getAttribute('name'),e.childNodes)
                            theList.append([e.getAttribute('name'),subSettings,e.getAttribute('type')])
                        elif (e.getAttribute('type')  == "text" or e.getAttribute('type') == "boolean"):
                            theList.append([e.getAttribute('name'),e.firstChild.data.strip(),e.getAttribute('type')])


                    self.settings[elem.getAttribute('name')] = [ [elem.getAttribute('identifier'), theList] , elem.getAttribute('type')]
                elif (elem.getAttribute('type') == "simplelist"):
                    theList = []
                    #<item>Text</item>
                    for e in elem.getElementsByTagName("item"):
                        theList.append(e.firstChild.data.strip())

                    self.settings[elem.getAttribute('name')] = [theList , elem.getAttribute('type')]
                    #self.settings[elem.getAttribute('name')] = [ [elem.getAttribute('identifier'), theList] , elem.getAttribute('type')]
                elif (elem.getAttribute('type') == "settings"):
                    subSettings = self.createSubSettingsDOM(elem.getAttribute('name'),elem.childNodes)
                    #Step 4) Put the Setting class, this settings array
                    self.settings[elem.getAttribute('name')] = [subSettings, elem.getAttribute('type')]
                else:
                    self.settings[elem.getAttribute('name')] = [elem.firstChild.data.strip(), elem.getAttribute('type')]

    def createSubSettingsDOM(self, subName, childNodes):
        # Step 1) Fake the <settings> xml (as <setting name="bah" type="settings"> is going to be our <settings> for a subsettings
        subxmldoc = minidom.Document()

        # Create the <settings> base element
        settingElem = subxmldoc.createElement("settings")
        settingElem.setAttribute("setting-version", str(self.settingVer))
        settingElem.setAttribute("name", subName)
        subxmldoc.appendChild(settingElem)

        # Step 2) Fill the <settings> blah </settings> with  the contents of the current elments children
        settingElem.childNodes = childNodes
        #  fix the reference to parent
        for e in settingElem.childNodes:
            e.parentNode = settingElem

        #Step 3) Create new 'Settings' class for it. and load the 'SUB' DOM/settings in it
        subSettings = Settings("",subName,{},0)
        subSettings.loadFromDOM(subxmldoc,1)

        return subSettings

    def load(self):
        """
            Reads in given filename from the Profile scriptsetting directory
        """
        filepath = join(SETTINGSDIR, self.filename)
        if exists(filepath):
                try:
                    xmldoc = minidom.parse(filepath)
                    self.loadFromDOM(xmldoc)
                except:
                    self.create()
                return
        else:
            self.create()

    def create(self,forceOverwrite=0):
        filepath = join("P:\\","script_settings", self.filename)
        if not exists(filepath) or forceOverwrite:
            self.setDefaultSettings()
            self.saveXMLfromArray()

    def setDefaultSettings(self):
        self.settings = self.defaultSettings

    def createfromtheDict(self,xmldoc, settingElem):

        # Interate over each setting
        for key in self.settings:
            type = self.settings[key][1]
            value = self.settings[key][0]
            newElem = xmldoc.createElement("setting")
            newElem.setAttribute("name", key)
            newElem.setAttribute("type" , type)
            if type == "list":
                newElem.setAttribute("identifier" , self.settings[key][0][0])
                self.createElementFromArray(xmldoc,newElem,self.settings[key][0])
            elif type == "simplelist":
                self.createSimpleListFromArray(xmldoc, newElem , self.settings[key][0])
            elif type == "settings":
                self.settings[key][0].createfromtheDict(xmldoc,newElem)
            else:
                newElem.appendChild(minidom.Document().createTextNode(value))
            settingElem.appendChild(newElem)
        # Done
        return xmldoc

    def saveXMLfromArray(self):
        """
            saveXMLfromArray
                Creates a dom Document of the settings array and saves it to the xml
        """
        # Create the DOM
        xmldoc = minidom.Document()

        # Create the <settings> base element and add it to the DOM
        settingElem = xmldoc.createElement("settings")
        settingElem.setAttribute("setting-version", str(self.settingVer))
        settingElem.setAttribute("name", self.scriptTitle)
        xmldoc.appendChild(settingElem)

        self.createfromtheDict(xmldoc,settingElem)
        # Create a element for each setting with the textnode as the value
        self.save(xmldoc)

    def createElementFromArray(self, xmldoc, nodeToAddTo, array):
        for i in array[1]:
            newElem = xmldoc.createElement(array[0])
            newElem.setAttribute("name", i[0])
            newElem.setAttribute("type", i[2])
            # help
            if (i[2] == "settings"):
                # Create Child then append to newElem
                i[1].createfromtheDict( xmldoc, newElem)
            else:
                newElem.appendChild(xmldoc.createTextNode(i[1]))
            nodeToAddTo.appendChild(newElem)

    def createSimpleListFromArray(self, xmldoc, nodeToAddTo,  array):
        for i in array:
            newElem = xmldoc.createElement("item")
            newElem.appendChild(xmldoc.createTextNode(i))
            nodeToAddTo.appendChild(newElem)

    def save(self,xmldoc):
        """
            This function takes a xml Document object and saves it to XML
        """
        filepath = join(SETTINGSDIR, self.filename)
        if not exists(DATADIR):
            mkdir(DATADIR)
        if not exists(SETTINGSDIR):
            mkdir(SETTINGSDIR)
        if not exists(ACCOUNTDIR):
            mkdir(ACCOUNTDIR)
        if not exists(TEMPDIR):
            mkdir(TEMPDIR)            
            

        fsock = open(filepath,"w")
        fsock.write(xmldoc.toprettyxml(indent="    "))
        fsock.close()
