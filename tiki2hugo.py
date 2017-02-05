#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import sys
import argparse
import yaml

import tiki


## Main Parser
parser = argparse.ArgumentParser(description="Tiki to Markdown Hugo style")

## Subparsers container
sub_parsers = parser.add_subparsers(help="commands", dest="command")

## test command
sp_setup = sub_parsers.add_parser("test", help="Check setup")

##  menu
sp_menu = sub_parsers.add_parser("menu", help="Menu stuff")
sp_menu.add_argument("-w", dest="write", action="store_false")

## convert command
sp_convert = sub_parsers.add_parser("convert", help="Convert stuff")

## Add some standard items 
for p in [sp_setup, sp_convert, sp_menu]:
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
        
    if args.command == "convert":
        items = tk.get_menu(mmid)
        #print items
        for sec_menu in items:
            
            # s#t.rip_page(menu)
            #if len(sec_menu['pages']) > 0:
            tk.rip_section(sec_menu)
                
            #print ">", sec_menu['type'], sec_menu['page_name'], sec_menu['url']
            #for p in sec_menu['pages']:
            #    print "  >", p['type'], p['page_name'], p['url']
                    
                    
        
        
        
