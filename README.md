#Docker Executor
Script to launch docker containers with varying configurations and record stats for resource utilization.
Graph scripts help to visually represent the collected stats.

##Environment Variables
```
DOCKER_EXECUTOR_CLUSTERHOSTS_FILE_LOCATION --> location of the file which contains the hostnames of the cluster

DOCKER_EXECUTOR_CLUSTERAUTH_USERNAME --> username for superuser access on the cluster hosts
DOCKER_EXECUTOR_CLUSTERAUTH_PASSWORD --> password for superuser access on the cluster hosts
```

##Run the following command to launch docker containers, given the benchmark image tag, and record the stats.
```
        python3 executor.py <image tag> <number of runs>
```

The files containing the stats would be in the following directory,
```
        stats/<benchmark name>
```

The output files of the benchmark would be in the following directory,
```
        output/<benchmark name>
```

##Run the following command to generate graphs, given the stats files, for all the benchmarks that were run.
```
        python3 extractor_graph.py stats output <destination directory>
```
Note that if the output directory does not contain an output file for a benchmark run with a particular configuration, then the graphs for that benchmark and configuration will not be generated.

The graphs would be stored in the specified destination directory as <benchmark>.png.
