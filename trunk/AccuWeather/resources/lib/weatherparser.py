from sgmllib import SGMLParser
import re

class ImageParser(SGMLParser):
    def reset(self):
        self.images = []
        SGMLParser.reset(self)

    def unknown_starttag(self, tag, attrs):
        if (tag == 'img'):
            for key, value in attrs:
                if (key == 'src'):
                    self.images.append(value)
                    

class CityParser(SGMLParser):
    def reset(self):
        self.city = []
        SGMLParser.reset(self)

    def start_meta(self, attrs):
        for key, value in attrs:
            #if key == "content":
            #    print "----------------"
            #    print value
            #    print "----------------"
            if (key == 'content' and (value[:4] == 'locz' or value[:6] == 'canada' or value[:5] == 'world')):
                self.city.append(value)

#<a href="canada-radar-metro.asp?partner=accuweather&myadc=0&postalcode=&level=metro&type=re2&site=YAW" class="textsmall" >Halifax</a><br />
#<a href="radar-metro.asp?partner=accuweather&myadc=0&amp;zipcode=48161&amp;level=metro&amp;type=re2&amp;site=MBS" class="textsmall" >Central Michigan</a> | <a href="radar-metro.asp?partner=accuweather&myadc=0&amp;zipcode=48161&amp;level=metro&amp;type=re2&amp;site=DTW" class="textsmall" >Detroit</a><br />
#<a href="http://wwwa.accuweather.com/index-world-forecast.asp?partner=accuweather&myadc=0&amp;traveler=0&amp;zipcode=EUR|DE|GM007|FRANKFURT|">Frankfurt</a></td>

class OtherParser(SGMLParser):
    def reset(self):
        self.pattern = 'site=[A-Z]{3,4}'
        self.metro = []
        self.line = None
        self.strong = ''
        self.strongFound = False
        SGMLParser.reset(self)

    def start_a(self, attrs):
        for key, value in attrs:
            if key == 'href':
                self.line = re.findall(self.pattern, value)
                
    def handle_data(self, text):
        if (self.line):
            if (self.line[0][5:] != 'MLB' and self.line[0][5:] != 'KML'):
                if (self.strong): sep = ', '
                else: sep = ''
                self.fline = ('%s%s%s  -  (%s)' % (self.strong, sep, text, self.line[0][5:],))
                self.metro.append(self.fline)
                self.line = None
        elif (self.strongFound):
            self.strongFound = False
            self.strong = text
            
    def unknown_starttag(self, tag, attrs):
        if (tag == 'strong'):
            self.strongFound = True


####### Not needed for US ########
class AlertParser(SGMLParser):
    def reset(self):
        self.pattern = '\\((.*)\\)'
        self.rssFeeds = []
        SGMLParser.reset(self)

    def start_link(self, attrs):
        for key, value in attrs:
            if (key ==     'title'):
                line = re.findall(self.pattern, value)
                if (line):
                    self.rssFeeds.append(line[0])
