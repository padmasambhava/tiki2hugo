
import os
import sys
import glob
import urllib
import urllib2
import urlparse

import sqlalchemy
from sqlalchemy.orm import sessionmaker

import bs4
import codecs


import helpers as h

Conf = None
Engine = None
Db = None

		

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
        
        for idx, r in enumerate(res):
            #dic = dict(optionid=r[0], menid=r[1], type=r[2], name=r[3], url=r[4])
            typ = r[2]
            page_name = r[3]
            url = r[4]
            
            print "----------------------"
            slug = h.slugify(page_name) 
            
            
            
            if typ == "s":
                # This is a section so page title comes directory
                section_dir = con_dir + "/" + slug
                #print dirr#
                #h.make_clean_dir(section_dir)
         
            else:
                
                # determine is page is wiki page
                p = urlparse.urlparse(url)
                qdic = urlparse.parse_qs(p.query)
                pagex = qdic.get("page")
                if pagex:
                    #print "=",  qdic, page
                    page = pagex[0]
                    u = self.tiki_server
                    u += "tiki-index_raw.php"
                    u += "?page=" + urllib.quote(page_name)
                    #out_dir = "%s/%s.md" % (section_dir, slug)
                    ok = self.rip_page(u, section_dir, page_name)
                
                
        
            
        return lst
    
    def get_img_db(self, imageid):
        sql = "select imageid, name from tiki_images where imageId=%s" % imageid
        res = self.session.execute(sql)
        for r in res:
            return r[1]
        return None
        
        

    def rip_page(self, url, section_dir, page_name):
        
        print "U=",  url
        print "out=", section_dir
        
        slug = h.slugify(page_name)
        #req = "%s%s%s" % (self.tiki_server, p['path'], q)
        #print "file_name=", req, "=", req
        resp = urllib2.urlopen(url)
        rr = resp.read()
        #print rr[0:40]
            
        raw_html = unicode(rr, "utf-8")
        h.write_file("%s/%s.html" % (section_dir, slug), raw_html)
        
        soup = bs4.BeautifulSoup(raw_html, "lxml")
        #for idx in soup.contents:
        #    print "=====", idx
        results = soup.find_all("img")
        #print results
        #images = {}
        img_lookup = {}
        for res in results:
            img_src = res['src']
            img_file = os.path.basename(img_src)
            print img_file, self.tiki_server + img_src
            if img_file.startswith("show_image.php"):
                uu = urlparse.urlparse(img_file)
                idic = urlparse.parse_qs(uu.query)
                idss = idic.get("id")
                if idss:
                    imageid = idss[0]
                    db_fn =  self.get_img_db(imageid)
                    if db_fn:
                        #print section_dir, db_fn
                        ftitle, fslug, fname = h.parts_from_filename(db_fn)
                        #print ftitle, fslug, fname
                        target_out = section_dir + "/" + fname
                        if not os.path.exists(target_out):
                            urllib.urlretrieve(self.tiki_server + img_src, target_out)
                        img_lookup[img_src] = fname
                        
                        
        #for idx, resu in enumerate(results):
        #raw = unicode(resu) #.decode().encode('utf-8')
        #print "raw=", type(raw), raw[0:40]
        
        ## get raw markdown and save
        md_raw_text = h.html_to_markdown(raw_html)
        f_path = "%s/%s.raw.md" % (section_dir, slug)
        print f_path
        h.write_file(f_path, md_raw_text)
        
        # process wiki style
        out_lines = []
        for idx, line in enumerate(md_raw_text):
            
            if line.startswith("!["): # image at line startswith
                
        
        
        
        
        