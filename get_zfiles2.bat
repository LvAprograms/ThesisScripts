rem usage: in your Windows command line, type: psftp -i .ssh/id_rsa.ppk yourname@eejit.geo.uu.nl -bc -be -b get_zfiles.bat (-be = continue on errors, -bc = display batch commands as they are run, -b = supply a batch script
cd to/your/cluster/Figures/EY
lcd to\your\local\Figures\EY
mget EY_z_comp[3-8]*
cd ../EW
lcd ../EW
mget EW_z_comp[3-8]*
cd ../FB
lcd ../FB
mget FB_z_comp[3-8]*
cd ../FD
lcd ../FD
mget FD_z_comp[3-8]*
cd ../FE
lcd ../FE
mget FE_z_comp[3-8]*
cd ../FF
lcd ../FF
mget FF_z_comp[3-8]*
cd ../FG
lcd ../FG
mget FG_z_comp[3-8]*
cd ../FH
lcd ../FH
mget FH_z_comp[3-8]*
cd ../FI
lcd ../FI
mget FI_z_comp[3-8]*
cd ../FJ
lcd ../FJ
mget FJ_z_comp[3-8]*
cd ../FK
lcd ../FK
mget FK_z_comp[3-8]*