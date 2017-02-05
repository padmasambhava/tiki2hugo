
import os
import glob


import html2text
import codecs


## Helper funcs
from slugify import slugify

def parts_from_filename(file_path):
    """ returns "My Image", "my_image" from "My"""
    
    # get ext
    file_base = os.path.basename(file_path)
    filep, ext = os.path.splitext(file_base)
    #print "\t", file_path, filep, ext
    slug = slugify(filep)   
    norm_name = slug +  ext.lower()
    
    
    
    return filep, slug, norm_name


def html_to_markdown(raw_html):
    
    #md = html2text.html2text( raw , encoding="utf-8")
    h2t = html2text.HTML2Text()
    h2t.ignore_links = False
    h2t.escape_snob = True
    h2t.unicode_snob = True
    md = h2t.handle( raw_html )
    #print md[0:30]
    
    ## mash special to remove trailing spaces
    lines = md.split("\n")
    ret = []
    for line in lines:
        ret.append(line.rstrip())
    return "\n".join(ret)



def write_file(file_path, content):
	with codecs.open(file_path, "w", "utf-8") as f:
		f.write(content)
		f.close()
			
def read_file(file_path):
	with open(file_path, "r") as f:
		return f.read()
    
    
def make_clean_dir(path, images=False):
    """Created a directory at x, and deletes files within if exist"""
    if not os.path.exists(path):
        os.makedirs(path)
    exts = ["md", "html", "txt"]
    if images:
        exts.extend(["jpg", "jpeg", "png"])
    for ext in exts:
        delete_files_in_dir(path, ext)

def delete_files_in_dir(path, ext):
    
    filelist = glob.glob(path + "/*.%s" % ext)
    for f in filelist:
        os.remove(f) 

                    
                    
def norman(s):
    """What is normal ?"""
    
    pass

    