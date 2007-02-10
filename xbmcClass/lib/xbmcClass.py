import xbmc, os, sys
from xml.dom import minidom

class Setting:
  def __init__(self, setting, what):
    xmlFile = []
    self.rValue = ""
    if what == 0:
      if os.path.isfile("p:\\guisettings.xml"): xmlFile.insert(len(xmlFile), "p:\\guisettings.xml")
    elif what == 1:
      if os.path.isfile("p:\\advancedsettings.xml"): xmlFile.insert(len(xmlFile), "p:\\advancedsettings.xml")
      else:
        if os.path.isfile("q:\\advancedsettings.xml"): xmlFile.insert(len(xmlFile), "q:\\advancedsettings.xml")
    else:
      if os.path.isfile("p:\\advancedsettings.xml"): xmlFile.insert(len(xmlFile), "p:\\advancedsettings.xml")
      else:
        if os.path.isfile("q:\\advancedsettings.xml"): xmlFile.insert(len(xmlFile), "q:\\advancedsettings.xml")
      if os.path.isfile("p:\\guisettings.xml"): xmlFile.insert(len(xmlFile), "p:\\guisettings.xml")
    for file in xmlFile:
      TagValue = self.rValue
      try:
        xml = minidom.parse(x)
        Tag = xmldoc.getElementsByTagName(setting)
        TagName     =   Tag[0].nodeName
        TagValue    =   Tag[0].childNodes[0].data
        self.rValue = TagValue
      except:
        if len(self.rValue) == 0: self.rValue = 'INVALID KEY!'
        if self.rValue != 'INVALID KEY!' and len(self.rValue) == 0: self.rValue = 'ERROR READING FILE!'

  def read(self):
    return self.rValue

class Language:
  def __init__(self):
    def parseFile(theLang):
      self.rValue = True
      xmlTags = {}
      xml = minidom.parse(theLang)
      Elements = 'strings'
      Tags = xml.getElementsByTagName(Elements)
      for Elements in Tags:
        RootTag = "" ; TagName = '' ; TagValue = ''
        for Tag in Elements.childNodes:
          if Tag.nodeType == Tag.ELEMENT_NODE :
            if len(Tag.attributes) > 0  : TagName = int(Tag.attributes["id"].value)
            else                        : TagName = Tag.nodeName
            if len(Tag.childNodes) != 0 : TagValue = Tag.childNodes[0].data
            else                        : TagValue = ''
            if TagName != 'title'       :
              if self.strings.has_key(TagName):
                if len(TagValue) > 0: self.strings[TagName] = TagValue
              else:
                self.strings[TagName] = TagValue
            else                        : RootTag = TagValue
          TagName = '' ; TagValue = ''
          xmlTags[RootTag] = self.strings
          RootTag = ''
    module_dir = os.path.dirname( sys.modules['xbmcClass'].__file__ )
    cwd = os.path.join(os.path.dirname(module_dir), 'language')
    self.strings = {}
    language = xbmc.getLanguage().lower()
    langFile = os.path.join(cwd, 'english', 'strings.xml')
    if os.path.isfile(langFile):
      parseFile(langFile)
      langFile = os.path.join(cwd, language, 'strings.xml')
      if os.path.isfile(langFile):
        parseFile(langFile)
    else:
      if len(self.strings) <= 0:
        print "ERROR: Languagefile %s cant be opened" % (langFile, )
        self.rValue = False

  def read(self, strID):
    return self.strings.get(int(strID), str(strID))

  def exists(self):
    return self.rValue
  