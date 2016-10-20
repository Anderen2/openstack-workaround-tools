#!/usr/bin/env python

__author__ = "Andreas Skoglund"
__copyright__ = "Copyright 2016, Basefarm"
__license__ = "MIT"

import argparse
from getpass import getpass
from keystoneauth1 import identity
from keystoneauth1 import session
from neutronclient.v2_0 import client

cli_description = """
Neutron port dump for Zookeeper import.

Used to generate Mido Zookeeper paths for network ports and bridge "mac_maps". 
Use the --bridge option to switch between the functionality. 
"""

argparser = argparse.ArgumentParser(description=cli_description, formatter_class=argparse.RawDescriptionHelpFormatter)
argparser.add_argument("--file", dest="file", help="Filepath to dump ZK paths (Will dump to stdout if not set)")
argparser.add_argument("--username", dest="username", default="", help="Openstack Username, will prompt if not set")
argparser.add_argument("--password", dest="password", default="", help="Openstack Password, will prompt if not set")
argparser.add_argument("--project_name", dest="project_name", default="admin", help="Openstack project name")
argparser.add_argument("--project_domain_id", dest="project_domain_id", default="default", help="Openstack project domain id")
argparser.add_argument("--user_domain_id", dest="user_domain_id", default="default", help="Openstack user_domain_id")
argparser.add_argument("--auth_url", dest="auth_url", default="http://localhost:5000/v3", help="Openstack auth_url")
argparser.add_argument("--endpoint_type", dest="endpoint_type", default="publicURL", help="Openstack endpoint_type")
argparser.add_argument("--bridge", dest="bridge", action="store_true", help="Dump bridge mac_maps (Also checks if floating IP is allocated)")
argparser.add_argument("--return_non_allocated", dest="return_non_allocated", action="store_true", help="Dump only non allocated floating IP bridge mac_maps")

cliargs = argparser.parse_args()

if not cliargs.username: cliargs.username = raw_input("Username: ")
if not cliargs.password: cliargs.password = getpass()

auth = identity.Password(auth_url=cliargs.auth_url,
                         username=cliargs.username,
                         password=cliargs.password,
                         project_name=cliargs.project_name,
                         project_domain_id=cliargs.project_domain_id,
                         user_domain_id=cliargs.user_domain_id)

session = session.Session(auth=auth)
neutron = client.Client(session=session, endpoint_type=cliargs.endpoint_type)

ports = neutron.list_ports()["ports"]
if cliargs.bridge: floating_ips = neutron.list_floatingips()["floatingips"]

floating_ips_by_ip = {}
for fip in floating_ips:
	floating_ips_by_ip[fip["floating_ip_address"]] = fip

port_paths = []
for port in ports:
	if not cliargs.bridge:
		port_str = "%s,%s,2147483647" % (port["mac_address"], port["id"])
		port_paths.append("/midonet/v2/zoom/0/tables/Network/%s/mac_table/0/%s" % (port["network_id"], port_str))
	else:
		for fixed_ip in port["fixed_ips"]:
			if port["device_owner"] == "network:floatingip":
				if fixed_ip["ip_address"] in floating_ips_by_ip: 
					if not floating_ips_by_ip[fixed_ip["ip_address"]]["fixed_ip_address"]:
						# print("IP: %s not allocated" % fixed_ip["ip_address"])
						if cliargs.return_non_allocated: 
							port_paths.append("/midonet/v2/bridges/%s/ip4_mac_map/%s,%s,2147483647" % (port["network_id"], fixed_ip["ip_address"], port["mac_address"]))
						continue
			if not cliargs.return_non_allocated:
				port_paths.append("/midonet/v2/bridges/%s/ip4_mac_map/%s,%s,2147483647" % (port["network_id"], fixed_ip["ip_address"], port["mac_address"]))

if cliargs.file:
	with open(cliargs.file, "a") as fd:
		for path in port_paths:
			fd.write(path+"\n")
else:
	for path in port_paths:
		print path