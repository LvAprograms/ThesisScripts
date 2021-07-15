rem usage: in your Windows command line, type: psftp -i .ssh/id_rsa.ppk yourname@eejit.geo.uu.nl -bc -be -b get_zfiles.bat (-be = continue on errors, -bc = display batch commands as they are run, -b = supply a batch script
rem this particular file is for the output of ForceAnalysis.m
cd /scratch/tectonics/agtmaal/STM/low_res/PAPER/ER_rerun
lcd "C:\\Users\\Luuk van Agtmaal\\Documents\\Studie\\Masters\\Jaar2\\MSc_thesis\\initfiles
put ER_init_ls init_ls.t3c
cd ../FI_rerun/

put FI_init_ls init_ls.t3c
cd ../FJ_rerun/

put FJ_init_ls init_ls.t3c
cd ../FK_rerun/

put FK_init_ls init_ls.t3c
cd ../FP_rerun/

put FP_init_ls init_ls.t3c
cd ../FQ_rerun/

put FQ_init_ls init_ls.t3c
cd ../FR_rerun/

put FR_init_ls init_ls.t3c
cd ../FS_rerun/

put FS_init_ls init_ls.t3c
cd ../FT_rerun/

put FT_init_ls init_ls.t3c
cd ../FX_rerun/

put FX_init_ls init_ls.t3c


