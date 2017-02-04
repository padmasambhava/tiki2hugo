
import os
import sys
import glob
import urllib
import urllib2
import urlparse

import sqlalchemy
from sqlalchemy.orm import sessionmaker

import bs4
import html2text
import codecs


Conf = None
Engine = None
Db = None

def write_file(file_path, content):
	with codecs.open(file_path, "w", "utf-8") as f:
		f.write(content)
		f.close()
			
def read_file(file_path):
	with open(file_path, "r") as f:
		return f.read()
		

class Tiki:
    
    def __init__(self):
        
        self.conf = None
        self.engine = None
        self.db = None
    
        self.hugo_dir = None
        self.tiki_server = None
        
    def init(self, conf):
        #global Engine, Db, Conf
        self.conf = conf
        self.hugo_dir = self.conf.get("hugo_dir")
        self.tiki_server = self.conf.get("tiki_server")
        
        db_conn_str = self.conf.get('tiki_db')
        #print "> DB.init()", db_conn_str
        if db_conn_str == None:
            return "Conf config"
        self.engine = sqlalchemy.create_engine(db_conn_str)
        #self.engine.connect()
        sess = sessionmaker(bind=self.engine)
        self.session = sess()
    
        
    def test_db(self):
        self.select.execute("select 1")
        return npper
        

    def menu_tree(self, mid):
        
        sql = "select optionId, menuid, type, name, url from tiki_menu_options where menuId=%s" % mid
        sql += " order by position asc"
        res = self.session.execute(sql)
        
        lst = []
        
        con_dir = "%s/content" % (self.hugo_dir)
        section_dir = ""
        
        for r in res:
            #dic = dict(optionid=r[0], menid=r[1], type=r[2], name=r[3], url=r[4])
            typ = r[2]
            name = r[3]
            url = r[4]
            
            print "----------------------"
            slug = name.lower().replace(" ", "_")
            
            
            
            if typ == "s":
                # This is a section so page title comes directory
                section_dir = con_dir + "/" + slug
                #print dirr
                if not os.path.exists(section_dir):
                    os.makedirs(section_dir)
                filelist = glob.glob(section_dir + "/*.md")
                for f in filelist:
                    os.remove(f) 
                filelist = glob.glob(section_dir + "/*.html")
                for f in filelist:
                    os.remove(f)     
                ## TODO gen index
            else:
                
                # determine is page is wiki page
                p = urlparse.urlparse(url)
                qdic = urlparse.parse_qs(p.query)
                page = qdic.get("page")
                if page:
                    #print "=",  qdic, page
                    u = self.tiki_server
                    u += "tiki-index_raw.php"
                    u += "?page=" + urllib.quote(page[0])
                    out_pth = "%s/%s.md" % (section_dir, slug)
                    ok = self.rip_page(u, out_pth)
                
                
                    
            
        return lst
    
    def get_img(self, imageid):
        sql = "select imageid, name from tiki_images where imageId=%s" % imageid
        res = self.session.execute(sql)
        for r in res:
            return r[1]
        return None
        
        
    

    def rip_page(self, url, out_path):
        
        # https://doc.tiki.org/Raw+page+display
        #
        # the tiki URL deom menu has spaces, eg `page=This Spaced Title` 
        # and causes problems
        # so parse url and query
        #p = urlparse.urlparse(url)
        #qdic = urlparse.parse_qs(p.query)
        #print p, qdic
        
        # assemble url again, quoting the query
       
        #for k, v in qdic.iteritems():
        #   u += "%s=%s" % (k, urllib.quote(v[0]))
        
        print "U=",  url
        print "out=", out_path
        #req = "%s%s%s" % (self.tiki_server, p['path'], q)
        #print "file_name=", req, "=", req
        resp = urllib2.urlopen(url)
        rr = resp.read()
        #print rr[0:40]
            
        raw = unicode(rr, "utf-8")
        write_file(out_path + ".html", raw)
        
        soup = bs4.BeautifulSoup(raw, "lxml")
        #for idx in soup.contents:
        #    print "=====", idx
        results = soup.find_all("img")
        #print results
        images = {}
        for res in results:
            img_src = res['src']
            fn = os.path.basename(img_src)
            print fn, self.tiki_server + img_src
            if fn.startswith("show_image.php"):
                uu = urlparse.urlparse(fn)
                idic = urlparse.parse_qs(uu.query)
                idss = idic.get("id")
                if idss:
                    imageid = idss[0]
                    print self.get_img(imageid)
            urllib.urlretrieve(self.tiki_server + img_src, fn)
        #for idx, resu in enumerate(results):
        #raw = unicode(resu) #.decode().encode('utf-8')
        #print "raw=", type(raw), raw[0:40]
        
    
        
        
        #md = html2text.html2text( raw , encoding="utf-8")
        h = html2text.HTML2Text()
        h.ignore_links = False
        h.escape_snob = True
        h.unicode_snob = True
        md = h.handle( raw )
        print md[0:30]
        
        
        

        #print u.query, page
        write_file(out_path, md)
		