# Authors: Andrea Galimberti (andrea.galimberti@polimi.it),
#          Davide Zoni (davide.zoni@polimi.it)
# Date: January 16,2024

# Description:
# This Python program takes as input a text file containing statistics dumped from a gem5 simulation
# and produces as output a CSV file containing select network statistics.
# The paths to the input and output files must be passed to this Python program through
# the --inputFilepath and --outputFilePath arguments, respectively.
# --benchmark and --thread arguments specify the processes run in the gem5 simulation
# and the number of threads associated to each of them. 

# Usage:
# python gem5-stats-to-csv-parser.py [-h]
#                                    --benchmark PROCESS#1-PROCESS#2-PROCESS#3-...-PROCESS#K
#                                    --thread THREADS#1-THREADS#2-THREADS#3-...-THREADS#K
#                                    --core CORES#1-CORES#2-CORES#3-...-CORES#K
#                                    --inputFilePath INPUTFILEPATH
#                                    --outputFilePath OUTPUTFILEPATH

# Example:
# python gem5-stats-to-csv-parser.py --benchmark blackscholes-bodytrack-bodytrack --thread 4-5-3 --core 1,2,3,4-6,8,10,12,14-5,7,9 --inputFilePath /home/user/example-stats.txt --outputFilePath /home/user/example-stats.csv

# Structure of the generated CSV file:
#   Lines 1-16: Control traffic distribution matrix
#       Line 1: From router 0 to ...
#           Column 1: ... router 0
#           Column 2: ... router 1
#           Column 3: ... router 2
#           ...
#           Column 16: ... router 15
#       Line 2: From router 1 to the 16 routers
#       Line 3: From router 2 to the 16 routers
#       ...
#       Line 16: From router 15 to the 16 routers   
#   Lines 17-32: Data traffic distribution matrix
#       Line 17: From router 0 to ...
#           Column 1: ... router 0
#           Column 2: ... router 1
#           Column 3: ... router 2
#           ...
#           Column 16: ... router 15
#       Line 18: From router 1 to the 16 routers
#       Line 19: From router 2 to the 16 routers
#       ...
#       Line 32: From router 15 to the 16 routers
#   Lines 33-48: Router stats matrix
#       Line 33: Router 0's ...
#           Column 1: ... buffer_reads
#           Column 2: ... buffer_writes
#           Column 3: ... crossbar_activity
#           Column 4: ... sw_input_arbiter_activity
#           Column 5: ... sw_output_arbiter_activity
#           Column 6: ... power_state.pwrStateResidencyTicks
#       Line 34: Router 1's six stats values
#       Line 35: Router 2's six stats values
#       ...
#       Line 48: Router 15's six stats values
#   Lines 49-61: Network stats matrix
#       Line 49: board.cache_hierarchy.ruby_system.network.average_flit_latency
#       Line 50: board.cache_hierarchy.ruby_system.network.average_flit_network_latency
#       Line 51: board.cache_hierarchy.ruby_system.network.average_flit_queueing_latency
#       Line 52: board.cache_hierarchy.ruby_system.network.average_flit_vnet_latency
#       Line 53: board.cache_hierarchy.ruby_system.network.average_flit_vqueue_latency
#       Line 54: board.cache_hierarchy.ruby_system.network.average_hops
#       Line 55: board.cache_hierarchy.ruby_system.network.average_packet_latency
#       Line 56: board.cache_hierarchy.ruby_system.network.average_packet_network_latency
#       Line 57: board.cache_hierarchy.ruby_system.network.average_packet_queueing_latency
#       Line 58: board.cache_hierarchy.ruby_system.network.average_packet_vnet_latency
#       Line 59: board.cache_hierarchy.ruby_system.network.average_packet_vqueue_latency
#       Line 60: board.cache_hierarchy.ruby_system.network.avg_link_utilization
#       Line 61: board.cache_hierarchy.ruby_system.network.avg_vc_load::total
#   Lines 62-63: Workload specification
#       Line 62: Running processes
#           Column 1: Name of process #1
#           Column 2: Name of process #2
#           ...
#       Line 63: Corresponding numbers of threads
#           Column 1: Number of threads of process #1 (see Line 62)
#           Column 2: Number of threads of process #2 (see Line 62)
#           ...
#       Line 64: Cores associated to process #1, process #2, ...

import argparse
import re
import math
import csv

# Parse paths of input and output files passed as arguments
parser = argparse.ArgumentParser(description="Extracts select network statistics from a text file dumped from a gem5 simulation and saves them in a CSV file.")
parser.add_argument("--benchmark", required=True, help="Benchmark programs to execute.")
parser.add_argument("--thread", required=True, help="Number of threads for each program.")
parser.add_argument("--core", required=True, help="Cores assigned to each program's threads.")
parser.add_argument("--inputFilePath", required=True, help="Path to the input text file")
parser.add_argument("--outputFilePath", required=True, help="Path to the output CSV file")
args = parser.parse_args()
benchList = (args.benchmark.rstrip()).split("-")
threadList = (args.thread.rstrip()).split("-")
coreList = (args.core.rstrip()).split("-")
textFile_path = args.inputFilePath
csvFile_path = args.outputFilePath

# Define number of cores in the CPU
num_cores = 16

# Create empty matrices for control traffic distribution,
# data traffic distribution, and router statistics
ctrlTraffic_matrix = [[None] * num_cores for _ in range(num_cores)]
dataTraffic_matrix = [[None] * num_cores for _ in range(num_cores)]
routerStats_matrix = [[None] * 6 for _ in range(num_cores)]
# Create empty dictionary for other network statistics
networkStats_dict = {}

# Regular expression pattern to match numbers and NaN
number_pattern = r"[-+]?\d*\.\d+|\d+|nan"
# Set of valid keys for the network stats dictionary
valid_keys = set([
    "board.cache_hierarchy.ruby_system.network.average_flit_latency",
    "board.cache_hierarchy.ruby_system.network.average_flit_network_latency",
    "board.cache_hierarchy.ruby_system.network.average_flit_queueing_latency",
    "board.cache_hierarchy.ruby_system.network.average_flit_vnet_latency",
    "board.cache_hierarchy.ruby_system.network.average_flit_vqueue_latency",
    "board.cache_hierarchy.ruby_system.network.average_hops",
    "board.cache_hierarchy.ruby_system.network.average_packet_latency",
    "board.cache_hierarchy.ruby_system.network.average_packet_network_latency",
    "board.cache_hierarchy.ruby_system.network.average_packet_queueing_latency",
    "board.cache_hierarchy.ruby_system.network.average_packet_vnet_latency",
    "board.cache_hierarchy.ruby_system.network.average_packet_vqueue_latency",
    "board.cache_hierarchy.ruby_system.network.avg_link_utilization",
    "board.cache_hierarchy.ruby_system.network.avg_vc_load",
    "board.cache_hierarchy.ruby_system.network.avg_vc_load::total"
])

# Read and parse the relevant data from the text file
period_ctr = 1
with open(textFile_path, 'r', encoding='utf-8') as file:
    for line in file:
        line = line.strip()
        if line.startswith('board.cache_hierarchy.ruby_system.network.ctrl_traffic_distribution'):
            parts = line.split()
            i = int(parts[0].split('.')[-2][1:])
            j = int(parts[0].split('.')[-1][1:])
            value = int(parts[1])
            ctrlTraffic_matrix[i][j] = value
        elif line.startswith('board.cache_hierarchy.ruby_system.network.data_traffic_distribution'):
            parts = line.split()
            i = int(parts[0].split('.')[-2][1:])
            j = int(parts[0].split('.')[-1][1:])
            value = int(parts[1])
            dataTraffic_matrix[i][j] = value
        elif line.startswith('board.cache_hierarchy.ruby_system.network.routers'):
            parts = line.split()
            if len(parts[0].split('.')[-2].strip("routers")) == 2:
                i = int(parts[0].split('.')[-2].strip("routers"))
#               Requires Python 3.10+ !!!
#               match parts[0].split('.')[-1]:
#                   case "buffer_reads":
#                       j = 0
#                   case "buffer_writes":
#                       j = 1
#                   case "crossbar_activity":
#                       j = 2
#                   case "sw_input_arbiter_activity":
#                       j = 3
#                   case "sw_output_arbiter_activity":
#                       j = 4
#               Works also on Python 3.9
#               Equivalent to commented-out code
                matchLabel = parts[0].split('.')[-1]
                if matchLabel == "buffer_reads":
                    j = 0
                elif matchLabel == "buffer_writes":
                    j = 1
                elif matchLabel == "crossbar_activity":
                    j = 2
                elif matchLabel == "sw_input_arbiter_activity":
                    j = 3
                elif matchLabel == "sw_output_arbiter_activity":
                    j = 4
                value = int(parts[1])
                routerStats_matrix[i][j] = value
            else:
                i = int(parts[0].split('.')[-3].strip("routers"))
                j = 5 # "power_state" case
                value = int(parts[1])
                routerStats_matrix[i][j] = value
        elif line.startswith('---------- End Simulation Statistics'):
            # Open a CSV file, at path indicated by the csvFile_path variable, for writing
            # 'w' indicates that we're opening the file in write mode
            # newline='' ensures consistent line endings across different platforms
            with open(csvFile_path + "_" + str(period_ctr) + ".csv", 'w', newline='') as csvfile:
                # Create a CSV writer object
                csvwriter = csv.writer(csvfile)
                # Use the writerows method to write all the rows from each matrix
                csvwriter.writerows(ctrlTraffic_matrix)
                csvwriter.writerows(dataTraffic_matrix)
                csvwriter.writerows(routerStats_matrix)
                csvwriter.writerows([values for values in networkStats_dict.values()])
                csvwriter.writerow(benchList)
                csvwriter.writerow(threadList)
                csvfile.write(",".join(coreList) + "\n")
            # Increment counter for the time period
            period_ctr += 1
        else:
            parts = line.split()
            if len(parts) > 1 and parts[0] in valid_keys and not any('%' in part for part in parts):
                key = parts[0]
                numbers = re.findall(number_pattern, line)
                if numbers:
                    networkStats_dict[key] = [float(num) if num != 'nan' else math.nan for num in numbers]

