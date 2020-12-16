# Use this file if eejit crashes once more and many models are stopped. This saves loads of time. 
import subprocess as sub
import os
import glob
import re

from shlex import split

pth = os.path

def latest_prn(folder: str) -> str:
    return sorted(
        # glob for prn files
        glob.iglob(pth.join(folder, "*.prn")),
        # sort by modification time
        key=pth.getmtime
    )[-1]

number_regexp = re.compile("[0-9]+")

def extract_index(path: str) -> int:
    matches = number_regexp.search(path)
    
    if matches is None:
        raise RuntimeError(
            "failed to find number to extract index in path '%s'", path
        )
    return int(matches[0])

def main():
    # list of directory paths to restart
    folders = ("EV", "EW",\
	       "EX","EZ","FC","FL","FO","FQ","FR","FS","FT","FU")
    
    for folder in folders:
        print("attempting folder %s" % folder)
        prn = latest_prn(folder)
        
        with open(pth.join(folder, "file.t3c"), "w") as f:
            f.write("%d\n"% extract_index(prn))
        
        with open(pth.join(folder, "run_eejit.sbatch"), "w") as f:
            # you can set job name to be something useful
            f.write(template.format(**default_options, job_name=folder))
        
        curr = os.getcwd()
        
        try:
            # pretty much the same as 'ch "$folder"'
            os.chdir(folder)
            
            # you can call commands as if you were calling them from the
            # terminal or from a bash script
            sub.call(split("sbatch run_eejit.sbatch"))
        finally:
            # change back to original directory whatever happens
            # (error or success)
            os.chdir(curr)


default_options = {
    "ntasks": 1,
    "ntasks_per_node": 6,
    "threads_per_core": 1,
    "nodes": 1,
    "partition": "defq",
}


template = \
"""\
#!/bin/sh
#SBATCH --ntasks={ntasks:d}
#SBATCH --ntasks-per-node={ntasks_per_node:d}
#SBATCH --threads-per-core={threads_per_core:d}
#SBATCH --partition={partition:s}
#SBATCH --nodes={nodes:d}
#SBATCH -o job.%N.%j.out  # STDOUT
#SBATCH -e job.%N.%j.err  # STDERR
#SBATCH --job-name {job_name:s}

# Eejit:
# There is 4GB of memory per core. Only if this is not submittingcient
# ntasks-per-node should be reduced.

# -- How to run other things --
# - execute script, once *c and *t3c are ok -
# source modload_eejit.sh
# make 
# sbatch run_lab_eejit.sbatch
#
#
# - or get an interactive job: OLD ETH -
# salloc -p fichtner_compute -t 10:00:00 -N 1 --mem=30GB
# than to run on allocated compute node (i.s.o. login node) use:
# srun -n 1 gdb ./i2stm       (-T 2)
# Note if you get comments about time limit than you are not in the
# sallocated terminal

# - matlab -:
# interactive job above
# module load matlab
# srun matlab - on command line
# matlab & - GUI
#

# -- execute runs --
#module load gcc    
#module load intel/14.0.1
#module load openmpi/icc-14.0.1
#module load hdf5/1.8.11-intel
#module load mkl/11.1.1.106-intel14.0.1
#module load lapack

module purge
module load opt/all
module load userspace/custom
module load intel-compiler/64/2018.3.222
module load intel-mkl/64/2018.3.222
module load intel-mpi/64/2018.3.222
module load hdf5/1.10.4
#module load Ruby/2.6.2

export OMP_NUM_THREADS=6

echo "Running on hosts: $SLURM_NODELIST"
echo "Running on $SLURM_NNODES nodes."
echo "Running on $SLURM_NPROCS processors."
echo "Current working directory is `pwd`"

#srun ./in2stm
echo "  submitting the first job: `date` "
srun ./i2stm
echo "  first job finished: `date` "
"""


if __name__ == "__main__":
    main()
