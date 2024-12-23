#!/bin/bash -l

#SBATCH --job-name=PortScan		# Name for your job
#SBATCH --comment="Simulate Port Scan"		# Comment for your job

#SBATCH --account=trustnoc		# Project account to run your job under
#SBATCH --partition=debug		# Partition to run your job on 

#SBATCH --output=%x_%j.out		# Output file
#SBATCH --error=%x_%j.err		# Error file

#SBATCH --mail-user=slack:@ajb3715	# Slack username to notify 
#SBATCH --mail-type=END			# Type of slack notifications to send

#SBATCH --time=0-24:00:00		# Time limit (tbd)
#SBATCH --ntasks=1		# 1 tasks (i.e. processes) (tbd)
#SBATCH --nodes=1			# How many nodes to run on (tbd)
#SBATCH --cpus-per-task=24		# Number of CPUs per task   (tbd)
#SBATCH --mem-per-cpu=4g		# Memory per CPU    (tbd)

spack load gem5@22.1.0.0 /gmehopf

pwd
which gem5.fast

