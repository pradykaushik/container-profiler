#!usr/bin/python

import os
import subprocess
from queue import Queue
import utils

#name of the directory to store the stats files.
DIR_NAME = "stats"

#recording stats
def record_stats(cpu_quota, mem, cpu_shares, image_tag, q):

	#getting benchmark name
	benchmark_name = utils.get_benchmark_name(image_tag)
	#creating directory for the stats files
	stats_path = utils.create_dir(DIR_NAME, benchmark_name)
	#filename of the file into which the stats are going to be stored.
	filename = benchmark_name+"_"+str(cpu_quota)+"_"+mem+"_"+str(cpu_shares)

	#the command retrieves the stats for the most recently run docker image. The command also picks out only the necessary headers from the output of docker stats.
	command = "sudo docker stats $(docker ps | awk \'{if(NR>1) print $NF}\') | sed \'s/|/ /\' | awk \'{print $1, $2, $3, $4, $5, $6, $7, $8}\' >> "
	stats_proc = subprocess.Popen(command+stats_path+"/"+filename, shell=True)

	#returning the pid of the process that is recording the stats, which is 1 greater than the pid of the spawned shell.
	q.put([stats_proc.pid, filename, stats_path])

if __name__ == "__main__":
	#making sure the script is run with superuser privileges.
	if os.getenv("SUDO_USER") == None:
		print("Error: Please run with superuser privileges.")
	else:
		record_stats()
