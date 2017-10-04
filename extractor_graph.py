import matplotlib.pyplot as plt; plt.rcdefaults()
import matplotlib.patches as mpatches
import numpy as np
import matplotlib.pyplot as plt
import sys
import os
import numpy as np
import warnings
docker_stats_dictionary = {}
docker_stats_dictionary_SD = {}
np.seterr(all='ignore')


destination_directory = ""
def plot_bar_graph(directory):
    configurations = [] # x-axis
    runtimes = [] # y-axis
    for i in docker_stats_dictionary:
        if float(docker_stats_dictionary[i]["Runtime"] != 0.0):
            configurations.append(i.split("_",1)[1])
            runtimes.append(float(docker_stats_dictionary[i]["Runtime"]))
    y_pos = np.arange(len(configurations))
    #for i in y_pos:
    #    y_pos[i] = y_pos[i] * 2
    plt.barh(y_pos,runtimes,align='center',alpha=0.4)
    #plt.barh(y_pos,runtimes,align='center',alpha=0.4,label="Configuration Format : cpu-quota[x/1000]%_memory(GB)_cpu-shares[x/1024]")
    plt.yticks(y_pos,configurations)
    plt.xlabel("Runtime (s)",fontsize=17)
    plt.ylabel("Configuration",fontsize=17)
    #red_patch = mpatches.Patch(color='red')
    #plt.legend(fontsize=17,loc='upper center', bbox_to_anchor=(0.47, -0.05),fancybox=False, shadow=False, ncol=5, frameon = False)
    plt.figtext(0.05, 0.01,"Configuration Format : cpu-quota[x/1000]%_memory(GB)_cpu-shares[x/1024]",color='black',fontsize=17)
    #print(docker_stats_dictionary.keys())
    #title = list(docker_stats_dictionary.keys())[0].split("_",1)[0]
    plt.title(directory,fontsize=17)
    mng = plt.get_current_fig_manager()
    mng.full_screen_toggle()
    figure = plt.gcf()
    figure.set_size_inches(25,11)
    print("\nGenerating graph for the following benchmark : ",directory)
    plt.savefig(destination_directory+"/"+directory+".png")
    plt.close()
    #plt.show()


def extract_raw_data(filepath,filename):
    read_stat = open(filepath,"r")
    read_stat_lines = read_stat.readlines()
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

    cpu_percentage_standard_deviation = 0.0
    memory_usage_standard_deviation = 0.0

    # FOR CALCULATING STANDARD DEVIATIONS
    if float(len(docker_stats_dictionary[benchmark_dict_key]["cpu%"])) != 0.0:
        cpu_percentage_diff = 0.0
        for i in docker_stats_dictionary[benchmark_dict_key]["cpu%"]:
            cpu_percentage_diff = cpu_percentage_diff + (i -docker_stats_dictionary[benchmark_dict_key]["avg-cpu%"])
        cpu_percentage_standard_deviation = cpu_percentage_diff / float(len(docker_stats_dictionary[benchmark_dict_key]["cpu%"]))

    if float(len(docker_stats_dictionary[benchmark_dict_key]["mem_usage"])) !=0.0:
        memory_usage_diff = 0.0
        for i in docker_stats_dictionary[benchmark_dict_key]["mem_usage"]:
            memory_usage_diff = memory_usage_diff + (i -docker_stats_dictionary[benchmark_dict_key]["avg-mem_usage"])
        memory_usage_standard_deviation = memory_usage_diff / float(len(docker_stats_dictionary[benchmark_dict_key]["mem_usage"]))

    docker_stats_dictionary_SD[benchmark_dict_key] = {"cpu%":cpu_percentage,"avg-cpu%":np.mean(cpu_percentage),"mem_usage":mem_usage,"avg-mem_usage":np.mean(mem_usage),"limit":limit,"mem%":mem_percentage,"Runtime":RUNTIME,"cpu%_sd":cpu_percentage_standard_deviation,"mem_sd":memory_usage_standard_deviation}
    #print(docker_stats_dictionary)
    #print(docker_stats_dictionary)
    #print(cpu_percentage)


if __name__ == "__main__":

    stats_dir_name = sys.argv[1]
    outputs_directory = sys.argv[2]
    destination_directory = sys.argv[3]

    if not os.path.isdir(destination_directory):
        os.mkdir(destination_directory)
    killed_jobs = []
    output_file_names = []

    for dirName,subdirs,files in os.walk(outputs_directory):
        for filename in files:
            #print(filename)
            filepath = os.path.join(dirName,filename)
            #extract_raw_data(filepath,filename)
            fp = open(filepath,"r")
            output_file_names.append(filename.rsplit("_",1)[0])
            data = fp.read()
            if "killed" in data.lower():
                killed_jobs.append(filename.rsplit("_",1)[0])
            fp.close()

    for dirName,subdirs,files in os.walk(stats_dir_name):
        for filename in files:
            #print(filename)
            filepath = os.path.join(dirName,filename)
            #print("----",filename)
            if filename not in killed_jobs and filename in output_file_names:
                extract_raw_data(filepath,filename)
        directory = dirName.rsplit("/",1)[-1]
        if len(list(docker_stats_dictionary.keys())) != 0:
            '''for i in docker_stats_dictionary:
                print(i," --> "," Runtime : ",docker_stats_dictionary[i]["Runtime"]," avg-cpu% : ",docker_stats_dictionary[i]["avg-cpu%"]," avg-mem_usage : ",docker_stats_dictionary[i]["avg-mem_usage"])'''
            plot_bar_graph(directory)
            docker_stats_dictionary = {}



    #plot_bar_graph()
