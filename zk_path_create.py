#!/usr/bin/env python

__author__ = "Andreas Skoglund"
__copyright__ = "Copyright 2016, Basefarm"
__license__ = "MIT"

import argparse
from kazoo.client import KazooClient
from kazoo.client import KazooState

cli_description = """
Zookeeper path creation tool. 
This is a simple tool that takes a file containing paths seperated by newlines and checks for their existance. 
If the paths do not exist, the tool will ask if it should create them. 

Could be used to add missing network ports and bridge mac_maps. 
Using --bridge will add a extra check on network existence before adding the paths. 
"""

argparser = argparse.ArgumentParser(description=cli_description, formatter_class=argparse.RawDescriptionHelpFormatter)
argparser.add_argument("file", help="File containing paths to import")
argparser.add_argument("--host", dest="host", default="127.0.0.1", help="Hostname or IP-address towards Zookeeper")
argparser.add_argument("--port", dest="port", default="2181", help="Port towards Zookeeper")
argparser.add_argument("-v", dest="verbose", action="store_true", help="Be more verbose")
argparser.add_argument("--dryrun", dest="dryrun", action="store_true", help="Only print, do not actually create")
argparser.add_argument("--bridge", dest="bridge", action="store_true", help="Create missing bridge ports (Adds extra check on network existance)")
argparser.add_argument("--delete", dest="delete", action="store_true", help="Deletes nodes (non-recursive) instead of creating")
cliargs = argparser.parse_args()

zk = KazooClient(hosts='%s:%s' % (cliargs.host, cliargs.port))
zk.start()

def yesno(question):
    try:
        choice = raw_input(question).lower()
        if choice in ['yes','y']: return True
        elif choice in ['no','n']: return False
        else: print("Please respond with 'yes' or 'no'")
    except KeyboardInterrupt:
        pass
        
    exit(-1)

def zk_listener(state):
    if state == KazooState.LOST:
        print("ZK LOST. ")
    elif state == KazooState.SUSPENDED:
        print("ZK SUSPENDED. ")
    else:
        print("ZK OTHER (%r)" % state)

zk.add_listener(zk_listener)

with open(cliargs.file, "r") as fd:
    file_content = fd.read()

missing_paths = []
for path in file_content.split("\n"):
    if path=="": continue
    if not zk.exists(path):
        print("Path not found: %s" % path)
        if not cliargs.delete: missing_paths.append(path)
    else:
        if cliargs.verbose: print("Path found: %s" % path)
        if cliargs.delete: missing_paths.append(path)

if cliargs.bridge:
    valid_paths = []
    for path in missing_paths:
        path_struct = path.split("/")
        network_path = "/".join(path_struct[0:5])
        # print network_path
        if zk.exists(network_path):
            if cliargs.verbose: print("Network exists, continuing -> %s" % network_path)
            valid_paths.append(path)
        else:
            print("Network missing -> %s (Skipping)" % network_path)
else:
    valid_paths = missing_paths
    
if not cliargs.delete:
    if yesno("%s paths missing, do you want to continue with adding? (yes/no) %s" % (len(missing_paths), "[DRYRUN]" if cliargs.dryrun else "")):
        for path in valid_paths:
            print("Creating: %s" % path)
            if not cliargs.dryrun: zk.ensure_path(path) 
else:
    if yesno("%s paths will be deleted, do you want to continue? (yes/no) %s" % (len(missing_paths), "[DRYRUN]" if cliargs.dryrun else "")):
        for path in valid_paths:
            print("Deleting: %s" % path)
            if not cliargs.dryrun: zk.delete(path)