import xbmc, xbmcgui, os, re

class Language:
    """
        Language Class
            For reading in xml for automatiacall of the selected lanauge XBMC is running in
            And for returning the string in the given Language for a specified id
            By RockStar and Donno
    """
    title = ""

    def __init__(self,title):
        self.title = title
    
    def load(self,thepath):
        self.strings = {}
        tempstrings = []
        self.language = xbmc.getLanguage().lower()
        
        if os.path.exists(os.path.join(thepath,self.language,"strings.xml")):
            self.foundlang = self.language
        else:
            self.foundlang = "english"
        self.langdoc = os.path.join(thepath,self.foundlang,"strings.xml")
        print "- Loading Language: " + self.foundlang
        try:
            f=open(self.langdoc,'r')
            tempstrings=f.read()
            f.close()
        except:
            print "Error: Languagefile "+self.langdoc+" can not be opened"
            xbmcgui.Dialog().ok(self.title,"Error: Language file",self.langdoc+" can not be opened")
        self.exp='<string id="(.*?)">(.*?)</string>'
        self.res=re.findall(self.exp,tempstrings)
        for stringdat in self.res:
            self.strings[int(stringdat[0])] = str(stringdat[1])

    def string(self,number):
        if int(number) in self.strings:
            if self.language == "finnish":
                return self.strings[int(number)].decode("utf-8")
            else:return self.strings[int(number)]
        else:
            return "unknown string id"
