import sys
# sys.path.append("BeautifulSoup-3.1.0.1/")
from BeautifulSoup import BeautifulSoup
import codecs
import urllib2
import re

streamWriter = codecs.lookup('utf-8')[-1]
sys.stdout = streamWriter(sys.stdout)


class SoupHelpers:

    def __init__(self,url):
        self.link = url

    def load(self):
        data = urllib2.urlopen(self.link).read()
        # the myspace html is malformed, quick hack to fix that problem
        ar = data.split("<table id=\"mainLayout\">")
        if len(ar) != 2:
            raise "Invalid or Malformed Myspace Application page"
        # we know it's the second one =)
        htmltext = ar[1]
        self.soup = BeautifulSoup( htmltext, convertEntities="html" )

    def extract_integer(self,str):
        p = re.compile('\d+')
        # extract the biggest possible int
        return int(p.search(str).group())

    def extract_app_name(self):
        el = self.soup.find('div', id="profile_appdetail")
        lista = el.h4.contents
        return lista[0].__unicode__()

    def remove_tags(self,tag):
        tags = self.soup.findAll(tag)
        [tagg.extract() for tagg in tags]

    def extract_nusers(self):
        el = self.soup.find('div', id="profile_appdetail_content")
        # remove all unnecessary tags
        for tag in ['strong','a','br']:
            self.remove_tags(tag)
    
        return self.extract_integer(str(el.contents))


#obj =  SoupHelpers("http://www.myspace.com/505895944")
#obj = SoupHelpers("http://www.myspace.com/478442441")
#obj.load()
#print obj.extract_app_name()
#print obj.extract_nusers()

    
