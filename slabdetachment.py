from matplotlib import pyplot as plt

durations = []
depths = []
corrected_depths = []
d_baumann = []
t_baumann = []
d_duretz = []
t_duretz=  []
d_duretz_nP = []
t_duretz_nP=  []
d_duretz_nS = []
t_duretz_nS=  []

with open("../../detachment_data.txt") as f:
    for i, line in enumerate(f.readlines()):
        if i > 0:
           line = line.split()
           if line[0].startswith("cyd"):
               d_baumann.append(float(line[1]) -10)
               t_baumann.append(float(line[2]))
           elif line[0].startswith("dur"):
               if line[0].endswith("nP"):
                   d_duretz_nP.append(float(line[1]))
                   t_duretz_nP.append(float(line[2]))
               elif line[0].endswith("nS"):
                   d_duretz_nS.append(float(line[1]))
                   t_duretz_nS.append(float(line[2]))
               else:
                d_duretz.append(float(line[1]))
                t_duretz.append(float(line[2]))
           else:
               depths.append(float(line[1]) - 20)
               durations.append(float(line[2]))
           # corrected_depths.append(depths[i-1] - 20)

plt.figure()
#
plt.semilogx(durations, depths, 'bd', label='This research')
plt.semilogx(t_baumann, d_baumann, 'g^', label='Baumann et al (2010)')
plt.semilogx(t_duretz, d_duretz, 'ro', label='Duretz et al (2012)')
plt.semilogx(t_duretz_nP, d_duretz_nP, 'ro', fillstyle='none', label='Duretz, no Peierls')
plt.semilogx(t_duretz_nS, d_duretz_nS, 'ko', label='Duretz, no shear heat')


# plt.plot(durations, depths, 'bd', label='This research')
# plt.plot(t_baumann, d_baumann, 'g^', label='Baumann et al (2010)')
# plt.plot(t_duretz, d_duretz, 'ro', label='Duretz et al (2012)')
# plt.plot(t_duretz_nP, d_duretz_nP, 'ro', fillstyle='none', label='Duretz, no Peierls')
# plt.plot(t_duretz_nS, d_duretz_nS, 'ko', label='Duretz, no shear heat')

plt.xlabel("Breakoff duration [Myr]")
plt.ylabel("Breakoff depth (lowest point of slab) [km]")
plt.grid(b=True)
plt.legend(loc='upper left')
plt.savefig("detdepth.png")

plt.show()