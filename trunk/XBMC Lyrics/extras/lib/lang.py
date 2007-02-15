class Language:
    def load(self,path,default="english"):
        import re, os, xbmc
        path = path
        self.strings = {}
        self.tempstrings = []
        self.temp_string_id = ""
        self.temp_string_value = ""
        self.language = xbmc.getLanguage().lower()
        if os.path.exists(path+self.language+".xml"):
            self.foundlang = self.language
        else:
            self.foundlang = default



        self.langdoc = path+self.foundlang+".xml"
        print "loading language: " + self.foundlang
        try:
            f=open(self.langdoc,'r')
            self.tempstrings=f.readlines()
            f.close()
        except:
            print "Error: Languagefile "+self.langdoc+" cant be oponed"
                
        self.exp="""<string><id>(.*?)</id><value>(.*?)</value></string>"""
                            
        for self.line in self.tempstrings:
            try:
                self.res=re.findall(self.exp,self.line)
                self.results = self.res[0]
            except:
                self.results=0

            if self.results != 0:
                self.strings[int(self.results[0])] = str(self.results[1])
        print "langage loaded"

    def string(self,number):
        try:
            return self.strings[number]
        except:
            return "error"


