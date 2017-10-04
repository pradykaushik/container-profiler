'''

key = benchmark-container_cpu-quota_mem, value = [ {cpu%: "", mem_usage="", limit="", mem%=""}, ... ]

COMMAND to generate stat files: sudo docker stats | sed 's/|/ /' | awk '{print $1, $2, $3, $4, $5, $6, $7, $8}' >> <benchmark_tag>_cpuquota_mem

filename : benchmarkname_cpuquota_mem_cpushare

'''

import sys
import os
import numpy as np
import warnings
docker_stats_dictionary = {}

np.seterr(all='ignore')


def extract_raw_data(filepath,filename):
    read_stat = open(filepath,"r")
    read_stat_lines = read_stat.readlines()
    #print(read_stat_lines[1])
    extracted_data = []
    RUNTIME = 0.0
    for i in read_stat_lines:
        if "RunTime" in i:
            RUNTIME = i.split(":")[1]
            RUNTIME = RUNTIME.lstrip()
            RUNTIME = RUNTIME.strip()
        elif "CONTAINER" not in i and "[" not in i:
            extracted_data.append(i.strip())
        else:
            pass

    #print(RUNTIME)
    cpu_percentage = []
    mem_usage = []
    limit = []
    mem_percentage = []
    #print(extracted_data)
    for i in extracted_data:
        docker_stat = i.split(' ')
        if(len(docker_stat)<8):
            pass
        else:
            #print(docker_stat)
            # docker_stat --> ['3c29741b9666', '75.00%', '3.161', 'GiB', '/', '4', 'GiB', '79.02%']
            cpu_percentage.append(float(docker_stat[1].strip("%")))
            mem_usage.append(float(docker_stat[2]))
            limit.append(float(docker_stat[5]))
            mem_percentage.append(float(docker_stat[7].strip("%")))

    #container_id = extracted_data[0].split(' ')[0]
    benchmark_dict_key = filename


    docker_stats_dictionary[benchmark_dict_key] = {"cpu%":cpu_percentage,"avg-cpu%":np.mean(cpu_percentage),"mem_usage":mem_usage,"avg-mem_usage":np.mean(mem_usage),"limit":limit,"mem%":mem_percentage,"Runtime":RUNTIME}
    #print(docker_stats_dictionary)
    #print(cpu_percentage)


if __name__ == "__main__":
    stats_dir_name = sys.argv[1]
    for root,subdirs,files in os.walk(stats_dir_name):
        for filename in files:
            #print(filename)
            filepath = os.path.join(root,filename)
            extract_raw_data(filepath,filename)
    for i in docker_stats_dictionary:
        print(i," --> "," Runtime : ",docker_stats_dictionary[i]["Runtime"]," avg-cpu% : ",docker_stats_dictionary[i]["avg-cpu%"]," avg-mem_usage : ",docker_stats_dictionary[i]["avg-mem_usage"])
