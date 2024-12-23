#!/bin/bash -l

#SBATCH --job-name=PortScan		# Name for your job
#SBATCH --comment="Simulate Port Scan"		# Comment for your job

#SBATCH --account=trustnoc		# Project account to run your job under
#SBATCH --partition=debug		# Partition to run your job on (tbd)

#SBATCH --output=%x_%j.out		# Output file
#SBATCH --error=%x_%j.err		# Error file

#SBATCH --mail-user=slack:@ajb3715	# Slack username to notify (I can't determine what this is tbd)
#SBATCH --mail-type=END			# Type of slack notifications to send

#SBATCH --time=0-24:00:00		# Time limit (tbd)
#SBATCH --ntasks=1		# 1 tasks (i.e. processes) (tbd)
#SBATCH --nodes=1			# How many nodes to run on (tbd)
#SBATCH --cpus-per-task=1		# Number of CPUs per task   (tbd)
#SBATCH --mem-per-cpu=10g		# Memory per CPU    (tbd)
#SBATCH --gres=gpu:a100:1	# 1 a100 GPU    (tbd)

spack load gem5@22.1.0.0 /gmehopf

#Need to decide if this is going to be the correct path
./build/X86/gem5.fast -d stats_blackscholes_portscan_16 ./PoliMi_RIT/run_simulation_v1.py --benchmark blackscholes --period 1000 --thread 16 --size simsmall --image ./PoliMi_RIT/diskImage_Ubuntu18.04+PARSEC+taskset/disk-image/parsec/parsec-image/parsec