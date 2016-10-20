# openstack-workaround-tools

### Midonet / Zookeeper scripts for syncing missing network ports / bridge mac_maps missing after upgrade
#### zk_neutron_pathdump.py
```bash
usage: zk_neutron_pathdump.py [-h] [--file FILE] [--username USERNAME]
                              [--password PASSWORD]
                              [--project_name PROJECT_NAME]
                              [--project_domain_id PROJECT_DOMAIN_ID]
                              [--user_domain_id USER_DOMAIN_ID]
                              [--auth_url AUTH_URL]
                              [--endpoint_type ENDPOINT_TYPE] [--bridge]

Neutron port dump for Zookeeper import.

Used to generate Mido Zookeeper paths for network ports and bridge "mac_maps". 
Use the --bridge option to switch between the functionality. 

optional arguments:
  -h, --help            show this help message and exit
  --file FILE           Filepath to dump ZK paths (Will dump to stdout if not
                        set)
  --username USERNAME   Openstack Username, will prompt if not set
  --password PASSWORD   Openstack Password, will prompt if not set
  --project_name PROJECT_NAME
                        Openstack project name
  --project_domain_id PROJECT_DOMAIN_ID
                        Openstack project domain id
  --user_domain_id USER_DOMAIN_ID
                        Openstack user_domain_id
  --auth_url AUTH_URL   Openstack auth_url
  --endpoint_type ENDPOINT_TYPE
                        Openstack endpoint_type
  --bridge              Dump bridge mac_maps
```

#### zk_path_create.py
```bash
usage: zk_path_create.py [-h] [--host HOST] [--port PORT] [-v] [--dryrun]
                         [--bridge]
                         file

Zookeeper path creation tool. 
This is a simple tool that takes a file containing paths seperated by newlines and checks for their existance. 
If the paths do not exist, the tool will ask if it should create them. 

Could be used to add missing network ports and bridge mac_maps. 
Using --bridge will add a extra check on network existence before adding the paths. 

positional arguments:
  file         File containing paths to import

optional arguments:
  -h, --help   show this help message and exit
  --host HOST  Hostname or IP-address towards Zookeeper
  --port PORT  Port towards Zookeeper
  -v           Be more verbose
  --dryrun     Only print, do not actually create
  --bridge     Create missing bridge ports (Adds extra check on network
               existance)
```
