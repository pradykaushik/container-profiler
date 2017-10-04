'''
Executor.py
-----------
1. Takes the name of the benchmark (docker iamge name) to run, and also the number of runs - N.
2. Generates CPU and Memory constraints (N {CPU, MEM} pairs).
3. Executes N runs of the docker images providing the {CPU, MEM} constraints.
4. Trigger the stats.py module to start recording the stats, for the runs, into a .csv files.
5. Trigger the stats_extractor.py module to extract the stats from the file.
'''

#!usr/bin/python
import os
import sys
import signal
import _thread
from multiprocessing.pool import ThreadPool
import stats_extractor as extractor
from queue import Queue
import random
import time

import stats_recorder
import utils

# directory that contains the stdout redirected files for the docker runs.
OUTPUT_DIRNAME = "output"

#run the benchmark and also kill the process that is recording the stats for the benchmark, once it is done running.
def run_docker_container(cpu_quota, mem, cpu_shares, image_tag, filename):
	#creating output directory
	output_path = utils.create_dir(OUTPUT_DIRNAME, utils.get_benchmark_name(image_tag))

	#running the docker container and recording the runtime.
	start_time = time.time()
	os.system("sudo docker run -t -m "+mem+" --cpu-shares="+str(cpu_shares)+" --cpu-quota="+str(cpu_quota)+" "+image_tag+" > "+output_path+"/"+filename)
	#calculating the runtime of the benchmark
	run_time = time.time() - start_time
	os.system("sudo killall docker && killall sed && killall awk && killall sudo")
	return run_time

#execute multiple runs, with different configurations, of the benchmark and record the stats of each one of them.
def execute(image_tag, number_of_runs):
	#retrieving the {CPU_SHARE, MEM, CPU_QUOTA} pairs
	cpu_mem_combinations = utils.generate_cpu_mem_configurations(number_of_runs)

	#queue for communication between threads.
	q = Queue()

	for cpu_mem_pair in reversed(cpu_mem_combinations):

		cpu_shares = cpu_mem_pair[0]*1024
		mem = cpu_mem_pair[1]
		cpu_quota = cpu_mem_pair[2]*1000

		print("Running benchmark "+image_tag+" with CPU_SHARE = "+str(cpu_shares)+" CPU% = "+str(cpu_mem_pair[2])+", MEM = "+str(mem)+"Giga Bytes ===========================")

		#initiating recording of the stats and retrieving the pid of that process and the location (filename and directory name) of the file that contains the stats.
		_thread.start_new_thread(stats_recorder.record_stats, (cpu_quota, str(mem)+"g", cpu_shares, image_tag, q))
		stats_proc_pid_and_filename_and_dir_name = q.get(block=True)
		stats_proc_pid = stats_proc_pid_and_filename_and_dir_name[0]
		filename = stats_proc_pid_and_filename_and_dir_name[1]
		dir_name = stats_proc_pid_and_filename_and_dir_name[2]

		print("Path of the file into which the output is being written to = "+dir_name+"/"+filename+"_output =====================")
		print("Path of the file into which the stats are being written to = "+dir_name+"/"+filename+" ============================")

		#running the benchmark for the above mentioned configuration
		run_time = run_docker_container(cpu_quota, str(mem)+"g", cpu_shares, image_tag, filename+"_output")
		#appending the runtime of the benchmark to the file in which the stats, for this run, are stored.
		utils.write_runtime_to_file(filename, dir_name, run_time)
		

if __name__ == "__main__":

	#checking whether benchmark name has been given
	number_of_arguments = len(sys.argv)
	if number_of_arguments < 2 or number_of_arguments < 3:
		print("Invalid input.")
		print("Input format: executor.py <benchmark> <number of runs>")
	else:
		#getting the benchmark name
		image_tag = sys.argv[1]
		#getting the number of runs
		number_of_runs = int(sys.argv[2])

		#executing
		execute(image_tag, number_of_runs)

		print("Process completed!!")

