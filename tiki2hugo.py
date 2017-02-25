#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import sys
import argparse
import yaml

from t2h import tiki


## Main Parser
parser = argparse.ArgumentParser(description="Tiki to Markdown Hugo style")

## Subparsers container
sub_parsers = parser.add_subparsers(help="commands", dest="command")

## test command
sp_setup = sub_parsers.add_parser("test", help="Check setup")

##  menu
sp_menu = sub_parsers.add_parser("menu", help="Menu stuff")
sp_menu.add_argument("-w", dest="write", action="store_false")

## convert commands
sp_convert = sub_parsers.add_parser("pages", help="Convert Pages stuff")
sp_articles = sub_parsers.add_parser("articles", help="Convert Articles")

## Add some standard items 
for p in [sp_setup, sp_convert, sp_menu, sp_articles]:
    p.add_argument("--debug", dest="debug", action="store_false", help="debug")
    p.add_argument("-c", dest="config_file", type=str, help="Convertion config", default="./config.yaml")
    

if __name__ == "__main__":

    args = parser.parse_args()
    #print args
    
    conf = None
    with open(args.config_file, "r") as f:
        conf = yaml.load(f)
        #print "conf=", conf
    
    if conf == None:
        print " No valid conf"
        sys.exit(0)
        
    tk = tiki.Tiki()
    err = tk.init(conf)
    #mmid = tk.conf.get("tiki_main_menu_id")
    
    if err:
        panic
    
    if args.command == "test":
        print tk.menu(mmid)

    if args.command == "menu":
        items = tk.write_menu()
        print items
        
    if args.command == "pages":
        items = tk.get_menu()
        #print items
        for sec_menu in items:
            
            # s#t.rip_page(menu)
            #if len(sec_menu['pages']) > 0:
            tk.rip_menu_section(sec_menu)

                    
    if args.command == "articles":
        arts = tk.get_articles()
        for idx, a in enumerate(arts):
            tk.rip_article(a)
            if idx == 10:
                sys.exit(0)
        
        
