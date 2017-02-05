
import os
import sys
import glob
import codecs
import re

import urllib
import urllib2
import urlparse

import sqlalchemy
from sqlalchemy.orm import sessionmaker

import bs4
from slugify import slugify


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
        


    def get_menu_tree(self, mid):
        """The menu options are by position, we walk same way
        
        So this parses a list into a tree 
        's' type = a section 
        'o' type = option
        
        from db we also get the query of name"""
        
        sql = "select optionId, menuid, type, name, url from tiki_menu_options where menuId=%s" % mid
        sql += " order by position asc"
        res = self.session.execute(sql)
        
        
        con_dir = "%s/content" % (self.hugo_dir)
        sdic = None
        lst = []
        for idx, r in enumerate(res):

            dic = {}
            dic['type'] = r[2]
            dic['page_name'] = r[3]
            dic['url'] = r[4]
            dic['slug'] = slugify(dic['page_name']) 
 
            if  dic['type'] == "s":
                # its a new SECTION    
                sdic = dict(dic)
                sdic['pages'] = []
                # We in a section so page title comes directory
                sdic['section_dir'] = con_dir + "/" + sdic['slug']
                
                lst.append(sdic)
                
            else:
                
                dic['page_dir'] = sdic['section_dir'] + "/" + dic['slug']
                
                sdic['pages'].append(dic)
                
                #h.make_clean_dir(page_dir)
                """
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
                    ok = self.rip_page(u, page_dir, page_name)
                
                """
        
            
        return lst
    
    def write_menu(self, menu):
        
        lst = []
        for idx, rec in enumerate(menu):
            m = dict(name=rec['page_name'], url=rec['slug'], weight=idx)
            lst.append(m)
        
        mdic = {}
        mdic['menu'] = {"main": lst}
        
        
        ys = yaml.dumps(mdic)
        h.write_file(self.hugo_dir + "/_menu.yaml", ys)
    
    def get_img_db(self, imageid):
        sql = "select imageid, name from tiki_images where imageId=%s" % imageid
        res = self.session.execute(sql)
        for r in res:
            return r[1]
        return None
    
    def clean_url(self, url):
        p = urlparse.urlparse(url)
        qdic = urlparse.parse_qs(p.query)
        pagex = qdic.get("page")
        if pagex:
            #print "=",  qdic, page
            page = pagex[0]
            u = self.tiki_server
            u += "tiki-index_raw.php"
            u += "?page=" + urllib.quote(page)
            #out_dir = "%s/%s.md" % (section_dir, slug)
            return u
        return url
        #ok = self.rip_page(u, page_dir, page_name)
                    
    def rip_section(self, sec_menu):
        print "=========== RIP > %s" % sec_menu['page_name'], sec_menu['section_dir']
        h.make_clean_dir(sec_menu['section_dir'])
        for p in sec_menu['pages']:
            print "  >", p['type'], p['page_name'], p['url']
            self.rip_page(p)

    def parse_md_img(self, md):
        #rint "===", md 
        # the amateur way
        # ![Organic Garden](../wiki_xtras/ftp_images/Organic-garden.jpg)
        s = md[2:-1]
        parts = s.split("](")
        #print s, parts
        return parts[1], parts[0] 


    def rip_page(self, pdic): #url, page_dir, page_name):
        print "------------page---------------"
        h.make_clean_dir(pdic['page_dir'])
        url = pdic['url']
        page_dir = pdic['page_dir']
        slug = pdic['slug']

        print "U=",  slug, page_dir
        #print "out=", page_dir
        
        #slug = slugify(page_name)
        #req = "%s%s%s" % (self.tiki_server, p['path'], q)
        #print "file_name=", req, "=", req
        
        if "tiki-browse_gallery.php" in url:
            print "  IGNORE"
            return
        
        print "  raw=", url
        print "  clean=", self.clean_url(url)
        resp = urllib2.urlopen(self.clean_url(url))
        rr = resp.read()
        #print rr[0:40]
            
        raw_html = unicode(rr, "utf-8")
        h.write_file("%s/_source.txt" % (page_dir), raw_html)
        
        
        soup = bs4.BeautifulSoup(raw_html, "lxml")
        #for idx in soup.contents:
        #    print "=====", idx
        results = soup.find_all("img")
        #print results
        #images = {}
        img_lookup = {}
        for res in results:
            img_src = res['src']
            img_alt = res['alt']
            img_file = os.path.basename(img_src)
            #print img_file, self.tiki_server + img_src
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
                        target_out = page_dir + "/" + fname
                        if not os.path.exists(target_out):
                            urllib.urlretrieve(self.tiki_server + img_src, target_out)
                        img_lookup[img_src] = dict(file_name=fname, alt=img_alt)
                        
        

        ## get raw markdown and save
        md_text = h.html_to_markdown(raw_html)
        f_path = "%s/_raw.md" % (page_dir)
        #print f_path
        h.write_file(f_path, md_text)
        
        ## images we found
        for img_ki, img_vi in img_lookup.iteritems():
            print "  IMG==", img_ki, img_vi
        
        

        
        regex = r"\!\[.*\]\(.*\)"

        #test_str = "some text and ![Image label](show_image.php?fii=909) here"

        matches = re.finditer(regex, md_text)
        
        out = ""
        start = 0

        for matchNum, match in enumerate(matches):
            matchNum = matchNum + 1
            
            print ("m:{matchNum} at {start}-{end}: {match}".format(matchNum = matchNum, start = match.start(), end = match.end(), match = match.group()))
            
            out += md_text[start:match.start()]
            #out += md_text[match.start():match.end()]
            snip = md_text[match.start():match.end()]
            mimg_url, mimg_alt = self.parse_md_img(snip)
            #
            if mimg_url in img_lookup:
                im = img_lookup[mimg_url]
                print "YES", im
                out += "![%s](%s)" % (im['file_name'], im['file_name'])
            else:
                out += snip
            start = match.end()
            
            
            for groupNum in range(0, len(match.groups())):
                groupNum = groupNum + 1
                
                print ("Group {groupNum} found at {start}-{end}: {group}".format(groupNum = groupNum, start = match.start(groupNum), end = match.end(groupNum), group = match.group(groupNum)))
       
        out += md_text[start:]
       
        f_path = "%s/index.md" % (page_dir)
        #print f_path
        h.write_file(f_path, out)
              
        #for idx, resu in enumerate(results):
        #raw = unicode(resu) #.decode().encode('utf-8')
        #print "IMG Lookup =", img_lookup
        #s = md_raw_text.replace("
        # process wiki style
        """
        out_lines = []
        for idx, line in enumerate(md_raw_text.split("\n")):
            #img_tag = "![%s](%s)" % ()
            if line.startswith("!["): # image at line startswith
                print "img_rep", line
                #find_me = "![%s](%s)" % ) 
        """        
              
        
        
        
        
        