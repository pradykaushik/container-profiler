'''
Contains all the utility methods that are required across multiple scripts.
These methods don't depend on the state of any process.
'''

#!/usr/bin/python

import os
import sys
import pull_cluster_info as cluster_info
import random
import math
import utils


#extract the benchmark name from the image_tag
def get_benchmark_name(image_tag):
	arg_components = image_tag.split("/")
	return arg_components[len(arg_components)-1]


#credentials for logging into cluster to run the ssh scripts that retrieve the memory and cpu information.
USERNAME = os.getenv('CONTAINER_PROFILER_CLUSTERAUTH_USERNAME')
PASSWORD = os.getenv('CONTAINER_PROFILER_CLUSTERAUTH_PASSWORD')

#mem in range [2g, free_mem] and cpu_share in range [1, total number of cpus]
def generate_cpu_mem_configurations(number_of_runs):
	cpu_mem_combinations = []
	count = 0
	total_mem = cluster_info.get_total_free_memory_across_all_cluster(USERNAME, PASSWORD, "MemFree")	
	total_cpu = cluster_info.get_cpu_count()
	#generate powers of 2 for memory
	memory_config_list = []
	for i in range(2, total_mem):
		if i != 0 and ((i & (i - 1)) == 0):
			memory_config_list.append(i)

	#generating the cpu, memory and cpu-share configurations for the given ranges
	for cpu_share in range(total_cpu, 1, -6):
		for cpu_quota in range(100, 25, -25):
			for mem in memory_config_list:
				if count == number_of_runs:
					break
				cpu_mem_combinations.append([cpu_share, mem, cpu_quota])
				count += 1
	return cpu_mem_combinations

#creating directory to store the stats, if not present
def create_dir(dirname, benchmark_name):
	if not os.path.exists(dirname):
		os.makedirs(dirname)
		os.makedirs(dirname+"/"+benchmark_name)
	else:
		if not os.path.exists(dirname+"/"+benchmark_name):
			os.makedirs(dirname+"/"+benchmark_name)
	#returning path to store the stats
	return dirname+"/"+benchmark_name

#appending runtime of the benchmark to the given file.
def write_runtime_to_file(filename, dirname, run_time):
	file_obj = open(dirname+"/"+filename, 'a')
	file_obj.write("RunTime: "+str(run_time))

