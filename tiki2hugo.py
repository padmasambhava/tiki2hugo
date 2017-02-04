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

## convert command
sp_convert = sub_parsers.add_parser("convert", help="Convert stuff")

## Add some standard items 
for p in [sp_setup, sp_convert]:
    p.add_argument("--debug", dest="debug", action="store_false", help="debug")
    p.add_argument("config_file", type=str, help="File to convert")
    

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
        
    t = tiki.Tiki()
    err = t.init(conf)
    mmid = t.conf.get("tiki_main_menu_id")
    
    if err:
        panic
    
    if args.command == "test":
        print t.menu(mmid)

    if args.command == "convert":
        menu = t.menu(mmid)
        for m in menu:
            t.rip_page(menu)
            
        
        
        
        
