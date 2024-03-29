import subprocess as sub
import os
import glob
import re

from shlex import split

pth = os.path
debug = False


def edit_plotscript(folder, nstart=1, nend=500, nstep=1):
    os.chdir("{}/src".format(folder))
    new_file_content = ""
    with open("vis_hdf5.m", 'r') as f:
        for i, line in enumerate(f.readlines()):
            splitline = line.split()
            if i == 29:
                expname = splitline[2]
                print(expname) if debug else None
                newname = "\'/scratch/tectonics/agtmaal/STM/low_res/%s/%s\';" % (folder, folder)
                line = line.replace(expname, newname)
            elif i == 34:
                current_nstart = splitline[2]
                line = line.replace(current_nstart, "%d;" % nstart)
            elif i == 35:
                current_nend = splitline[2] + ' ' + splitline[3]
                line = line.replace(current_nend, "nstart +%d;" % nend)
                print(line) if debug else None
            elif i == 36:
                current_nstep = splitline[2]
                line = line.replace(current_nstep, "%d;" % nstep)
            elif i == 40:
                sp_var1 = splitline[2]
                line = line.replace(sp_var1, "%d;" % 4)
            elif i == 41:
                sp_var2 = splitline[2]
                line = line.replace(sp_var2, "%d;" % 3)
            elif i == 42:
                sp_var3 = splitline[2]
                line = line.replace(sp_var3, "%d;" % 7)
            elif i == 52:
                zoom = splitline[2]
                line = line.replace(zoom, "%d;" % 1)
            new_file_content += line

    with open("pyvis_hdf5.m", 'w') as f:
        f.write(new_file_content)

    new_file_content = ""
    with open("../../plotjob.sbatch", 'r') as f:
        for line in f.readlines():
            if line.startswith('srun'):
                newline = line.replace("Coolmodel", "%s" % folder)
            else:
                newline = line
            new_file_content += newline

    with open("plotjob.sbatch", 'w') as f:
        print("writing new batch file at {}".format(os.getcwd()))
        f.write(new_file_content)


def main():
    # list of directory paths to restart
    folders = str('ER').split(', ')
    for folder in folders:
        print("trying to plot stuff for model {}".format(folder))
        curr = os.getcwd()
        try:
            edit_plotscript(folder)
            command = split("sbatch plotjob.sbatch")
            print(command)
            list_files = sub.run(command, stdout=sub.PIPE, stderr=sub.STDOUT)
            print("matlab command submitted with return code %d" % list_files.returncode)
            if debug:
                proceed = input("Continue?")
                if proceed != "y":
                    print("aborting")
                    exit()
        finally:
            os.chdir(curr)


# , ES, ET, EU, EV, EX, EY, EZ, FA, FB, FC, FD, FE, FF, FG, FH, FI, FJ, FK, FL, FM, FN, FO, FP, FQ, FR, FS, FT, FU


if __name__ == "__main__":
    main()
