
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

"""
class PMeta:
    def __init__(self, url=None, page=None):
        self.url = url
        self.page = page
"""

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
        self.tiki_main_menu_id = self.conf.get("tiki_main_menu_id")
        
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
        


    def get_menu(self, menuId=None):
        """The menu options are by position, we walk same way
        
        So this parses a list into a tree 
        's' type = a section 
        'o' type = option
        
        from db we also get the query of name"""
        
        if menuId == None:
            # unless given specific menu, use the main menu from config
            menuId = self.tiki_main_menu_id

        con_dir = "%s/content" % (self.hugo_dir)
        sdic = None
        lst = []
        
        sql = "  select optionId, menuid, type, name, url "
        sql += " from tiki_menu_options  "
        sql += " where menuId=%s" % menuId
        sql += " order by position asc"
        res = self.session.execute(sql)
        
        for idx, r in enumerate(res):

            dic = {}
            dic['type'] = r[2]
            dic['name'] = r[3]
            dic['url'] = r[4]
            dic['slug'] = slugify(dic['name']) 
            
 
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

        return lst
    
    def write_menu(self):
        main_menu = self.get_menu()
        lst = []
        for midx, mrec in enumerate(main_menu):
            mm = dict(name = mrec['page_name'], 
                     identifier = mrec['slug'],
                     url="/%s/" % mrec['slug'], 
                     weight = midx+1)
            lst.append(mm)
            ## Now we add child submenus as hugo parent
            for cidx, crec in enumerate(mrec['pages']):
                cm = dict(name = crec['page_name'], 
                     parent = mrec['slug'],     
                     identifier = mrec['slug'] + "|" + crec['slug'],
                     url="/%s/%s/" % (mrec['slug'], crec['slug']), 
                     weight = cidx+1)
                lst.append(cm)
        
        mdic = {}
        mdic['menu'] = {"main": lst}
        
        
        ys = h.to_yaml(mdic)
        h.write_file(self.hugo_dir + "/_menu.yaml", ys)
    
    def get_img_db(self, imageid):
        """Get info about image from tiki db,
          only name so far, but might be dims later

        :return: the name as str
        """
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
            page = pagex[0].strip()
            u = self.tiki_server
            u += "tiki-index_raw.php"
            u += "?page=" + urllib.quote(page)
            #out_dir = "%s/%s.md" % (section_dir, slug)
            return u
        return url
        #ok = self.rip_page(u, page_dir, page_name)
                    
    def rip_menu_section(self, sec_menu):
        """Rips out a section meniw" annd all pages"""
        print "== SECTION = > %s" % sec_menu['name'], sec_menu['section_dir']
        h.make_clean_dir(sec_menu['section_dir'])
        
        ## Rip out the sections
        sec_idx = []
        for p in sec_menu['pages']:

            # =====================
            # IGNORES. .for now
            ## TODO detect and clean urls
            if "tiki-browse_gallery.php" in p['url']:
                print "  IGNORE", p['url']
                continue
            if "tiki-view_events.php" in p['url']:
                print "  IGNORE", p['url']
                continue
                #else:
                ## SKIPPP
                #continue



            ## rip page
            print "  >", p['type'], p['name'], p['url']
            err = self.rip_tiki_page(p, v=1)
            if not err :
                sec_idx.append(p)
        #if len(sec_idx) > 0:
        #
        #   print "YES", sec_idx

        ## make index
        sec_md = ["# Heading", ""]

        #idx_lst = []
        for ix in sec_idx:
            lnk = "- [%s](%s/)" % (ix['name'].strip(), ix['slug'])
            sec_md.append(lnk)
            #idx_lst = "<li>%</li>"
        print sec_md
        sec_out = "\n".join(sec_md)
        fname = sec_menu['section_dir'] + "/_index.md"
        h.write_file(fname, sec_out)

    def parse_md_img(self, md):
        #rint "===", md 
        # the amateur way
        # ![Organic Garden](../wiki_xtras/ftp_images/Organic-garden.jpg)
        s = md[2:-1]
        parts = s.split("](")
        #print s, parts
        return parts[1], parts[0] 

    def process_images(self, page_dir, raw_html):
        ## === Download IMAGES ===
        # Find images in page, and download
        # use img_lookup for url to alt
        img_lookup = {}

        # We use beautiful soup to get all the images in html
        soup = bs4.BeautifulSoup(raw_html, "lxml")
        image_nodes = soup.find_all("img")

        # print results
        # images = {}

        for res in image_nodes:
            img_src = res['src']
            img_alt = res.get('alt')
            img_file = os.path.basename(img_src)
            # print img_file, self.tiki_server + img_src

            ## its and image to process
            if img_file.startswith("show_image.php"):
                uu = urlparse.urlparse(img_file)
                idic = urlparse.parse_qs(uu.query)
                idss = idic.get("id")

                if idss:
                    ## get meta from database
                    imageid = idss[0]
                    db_fn = self.get_img_db(imageid)
                    if db_fn:
                        # write out file
                        # print section_dir, db_fn
                        ftitle, fslug, fname = h.parts_from_filename(db_fn)
                        # print ftitle, fslug, fname
                        target_out = page_dir + "/" + fname
                        if not os.path.exists(target_out):
                            urllib.urlretrieve(self.tiki_server + img_src, target_out)
                        img_lookup[img_src] = dict(file_name=fname, alt=img_alt)
            else:
                srcc = self.conf['tiki_server'] + img_src
                ftitle, fslug, fname = h.parts_from_filename(srcc)
                # print srcc
                # print ftitle, fslug, fname
                target_out = page_dir + "/" + fname
                if not os.path.exists(target_out):
                    urllib.urlretrieve(self.tiki_server + img_src, target_out)
                img_lookup[img_src] = dict(file_name=fname, alt=img_alt)

        ## images we found
        if False:
            for img_ki, img_vi in img_lookup.iteritems():
                print "  IMG==", img_ki, img_vi

        ## Convert html to markdown and save in _raw.md_raw
        md_text = h.html_to_markdown(raw_html)
        #f_path = "%s/_md.raw" % (page_dir)
        #h.write_file("%s/_md.raw" % (page_dir), md_text)
        # print f_path
        # .write_file(f_path, md_text)


        ## Rewrite the image tags in markdown

        regex_img = r"\!\[.*\]\(.*\)"  # looking for ![Foo Bar](../someiamage.php?id = 21) in txt

        matches = re.finditer(regex_img, md_text)

        after_image_rewrite = ""
        start = 0

        for matchNum, match in enumerate(matches):
            matchNum = matchNum + 1

            # print ("m:{matchNum} at {start}-{end}: {match}".format(matchNum = matchNum, start = match.start(), end = match.end(), match = match.group()))

            after_image_rewrite += md_text[start:match.start()]
            # out += md_text[match.start():match.end()]
            snip = md_text[match.start():match.end()]
            mimg_url, mimg_alt = self.parse_md_img(snip)
            #
            if mimg_url in img_lookup:
                im = img_lookup[mimg_url]
                # print "   rewite img", im
                after_image_rewrite += "![%s](%s)" % (im['file_name'], im['file_name']) + "\n\n"
            else:
                after_image_rewrite += snip
            start = match.end()

            for groupNum in range(0, len(match.groups())):
                groupNum = groupNum + 1
                stoppp
                print ("Group {groupNum} found at {start}-{end}: {group}".format(groupNum=groupNum,
                                                                                 start=match.start(groupNum),
                                                                                 end=match.end(groupNum),
                                                                                 group=match.group(groupNum)))

        after_image_rewrite += md_text[start:]
        return after_image_rewrite

    def rip_tiki_page(self, pdic, v=0):
        

        # check dir exists and nuke files within
        h.make_clean_dir(pdic['page_dir'])
        
        # make some local vars for convience
        url = pdic['url']
        page_dir = pdic['page_dir']
        title = pdic['name'].title()
        slug = pdic['slug']
        print "------------page = %s" % title
        if v > 1:
            print "  src=",  slug, page_dir, url
        #print "  raw=", url
        #print "  clean=", self.clean_url(url)
        

        
        ## Get remote ?page= with cleaned url
        resp = urllib2.urlopen(self.clean_url(url))
        
        ## the raw html is here and save to file and in utf8
        raw_stuff = resp.read()
        raw_html = unicode(raw_stuff, "utf-8")
        h.write_file("%s/_source.txt" % (page_dir), raw_html)
        
        
        after_image_rewrite = self.process_images(page_dir, raw_html)
        # Phew now images have been rewitten,
        # we start again with out raw_stuff for hugo
        
        # cleanup tiki backlink header = first line       
        # split up md and replace first tiki md lines..
        tlines = after_image_rewrite.split("\n")
        
        cleaned_header = []
        if tlines[0].startswith("# "):
            if tlines[1] != "": 
                #print "tlines=", tlines[0:3]
                
                #start_idx = 0
                # replace double header
                #cleaned_header.append("# %s" % title)
                cleaned_header.extend(tlines[2:])
                
            else:
                #cleaned_header.append("# %s" % title)
                cleaned_header.extend(tlines[1:])
        else:
            print tlines[0:10]
            paniccc

        # Now walk cleaned and replace --|--
        cleaned = []
        cleaned.append("---")
        cleaned.append("title: %s" % title.title())
        #cleaned.append("description: %s" % "DESCRIPTION.TODOs")
        #cleaned.append("tagsd: %s" % "DESCRIPTION.TODOs")
        cleaned.append("---")
        cleaned.append("")

        for l in cleaned_header:
            s = l
            if l == "---|---":
                s = ""

            if l.startswith("##"):
                #print l
                s = "## " + l[2:].title()

            if l.startswith("Created"):
                s = ""
            if l.startswith("by "):
                s = ""

            if l.startswith("**") and l.endswith("**"):
                print "l=", l
                s = "**" + l[2:-2].strip() + "**"

            cleaned.append(s)


        out_md = "\n".join(cleaned)
        f_path = "%s/index.md" % (page_dir)
        #print f_path
        h.write_file(f_path, out_md)
              
        return None
              
        
        

    def get_articles(self):
        sql = "select articleid, topline, title, subtitle, heading, "
        sql += "useimage, image_name, image_caption, image_x, image_y "
        sql += " from tiki_articles "
        sql += " order by articleid desc"
        sql += " limit 10"
        res = self.session.execute(sql)
        l = []
        for r in res:
            dd = dict(articleid=r[0], topline=r[1], title=r[2], subtitle=r[3],
                      heading=r[4], use_image=r[5], image_name=r[6], image_caption=r[7],
                      image_x=r[8], image_y=r[9]
                      )
            ##print dd
            l.append( dd )
        return l

    def rip_article(self, adic):

        # check dir exists and nuke files within
        #h.make_clean_dir(pdic['page_dir'])

        # make some local vars for convience
        url = self.conf['tiki_server'] + "/tiki-print_article.php?articleId=%s" % adic['articleid']
        print url

        page_dir = "articles"


        ## Get remote ?page= with cleaned url
        resp = urllib2.urlopen(self.clean_url(url))

        ## the raw html is here and save to file and in utf8
        t_dir = "%s/content/articles/%s/" % (self.hugo_dir, adic['articleid'])
        h.make_clean_dir(t_dir)
        raw_stuff = resp.read()
        raw_html = unicode(raw_stuff, "utf-8")
        h.write_file("%s/_source.txt" % (t_dir), raw_html)

        ## Convert html to markdown and save in _raw.md_raw
        md_text = h.html_to_markdown(raw_html)
        f_path = "%s/_md.raw" % (page_dir)
        h.write_file("%s/_md.raw" % (t_dir), md_text)

        h.write_file("%s/index.md" % (t_dir), md_text)