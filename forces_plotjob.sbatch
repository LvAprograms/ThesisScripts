#!/bin/bash
#SBATCH --ntasks=1
#SBATCH --ntasks-per-node=1
#SBATCH --threads-per-core=1
#SBATCH --partition=defq
#SBATCH --nodes=1
#SBATCH -o job.%N.%j.out # STDOUT
#SBATCH -e job.%N.%j.err # STDERR
#SBATCH --job-name matlab 
module load opt/all
module load matlab
srun matlab -logfile Coolmodel.log -nodisplay < pyForceAnalysis.m > vis.out
