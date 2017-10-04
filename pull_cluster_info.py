import re
import json
import sys
import os
import multiprocessing

def setup():
	os.system("sudo apt-get install build-essential libssl-dev libffi-dev python3-dev")
	os.system("sudo apt-get install python3-setuptools && sudo easy_install3 pip")
	os.system("sudo pip3 install cryptography")
	os.system("sudo pip3 install spur")


try:
	import spur
except ImportError:
	setup()

def get_info(HOSTNAME,USERNAME,PASSWORD,FIELD):
	shell = spur.SshShell(hostname=HOSTNAME,username = USERNAME ,password=PASSWORD,missing_host_key=spur.ssh.MissingHostKey.accept)
	with shell:
		result = shell.run(["cat","/proc/meminfo"])
	res = result.output.decode("utf-8")
	stripped_data = res.strip()
	parsed_data = re.split(r'[\n]+',stripped_data)
	info_dict = {}
	for i in parsed_data:
		splitted = re.split(r'\s{2,}',i)
		info_dict[splitted[0].strip(":")] = float(splitted[1].split(" ")[0])
	return info_dict[FIELD]

def get_total_free_memory_across_all_cluster(USERNAME, PASSWORD, FIELD):
	host_names = get_cluster_hostnames()
	host_memfree_dict = {} 
	for host in host_names:
		host_memfree_dict[host] = get_info(host, USERNAME, PASSWORD, FIELD)
	total_free_mem = round(sum(host_memfree_dict.values()))
	total_free_mem_gigs = total_free_mem // (1024 * 1024)
	return total_free_mem_gigs

def get_cpu_count():
	return multiprocessing.cpu_count()

def get_cluster_hostnames():
	hosts = list()
	with open(os.getenv('DOCKER_EXECUTOR_CLUSTERHOSTS_FILE_LOCATION')) as cluster_hostnames_file:
		hosts = cluster_hostnames_file.readlines()
	# removing the new line character at the end of each line
	hosts = [line.strip() for line in hosts]
	return hosts

if __name__ == "__main__":
	if(len(sys.argv)<2):
		print("USAGE: python3 pull_cluster_info.py <FIELD>")
	elif(len(sys.argv)>3):
		print("Too many Arguments !\n")
		print("USAGE: python3 pull_cluster_info.py <FIELD>")
	else:
		Host_names = []
		USERNAME = os.getenv('DOCKER_EXECUTOR_CLUSTERAUTH_USERNAME')
		PASSWORD = os.getenv('DOCKER_EXECUTOR_CLUSTERAUTH_PASSWORD')
		FIELD = sys.argv[1]

		for host in Host_names:
			print(get_info(host,USERNAME,PASSWORD,FIELD))

