from matplotlib import pyplot as plt
from numpy import zeros
from math import erf, sqrt
z = range(0, 801, 1)
x = range(0, 3001, 1)
nz = len(z)
nx = len(x)
T = zeros((nz, nx))

def linear(xleft, ytopleft, ybottomleft, xright, ytopright, ybottomright, Ttopleft, Tbotleft, Ttopright, Tbotright):
    dTdz_left = (Tbotleft - Ttopleft) / (ybottomleft - ytopleft - 1)
    dTdz_right = (Tbotright - Ttopright) / (ybottomright - ytopright - 1)
    for j in range(nx):
        if xleft <= x[j] <= xright:
            relative_pos = (x[j]-xleft) / (xright - xleft)
            T[z[ytopleft], j] = Ttopleft + relative_pos * (Ttopright - Ttopleft)
            dTdz = dTdz_left + relative_pos * (dTdz_right-dTdz_left)
            for i in range(1, nz):
                if ytopleft <= z[i] <= ybottomleft:
                    T[i,j] = T[i-1, j] + dTdz
            # print(T[:,j])

def halfspacetemp(xleft, ytopleft, ybottomleft, xright, T0, T1, diffusivity, ageyr, depth):
    ageseconds = ageyr * 365.25 * 24 * 3600
    for j in range(nx):
        if xleft <= x[j] <= xright:
            T[z[ytopleft], j] = T0
            for i in range(1, nz):
                if ytopleft <= z[i] <= ybottomleft:
                    T[i,j] = T1 + (T0 - T1) * (1 - erf((depth[i] - ytopleft) * 1e3 / (2*sqrt(diffusivity * ageseconds))))


fig, [ax1, ax2] = plt.subplots(1,2)
ax1.grid(b=True)
ax1.invert_yaxis()
ax2.grid(b=True)
ax2.invert_yaxis()

with open("temp_input.txt", 'r') as f:
    for i, l in enumerate(f.readlines()):
        posdata = []
        tdata = []
        line = l.split()
        for j, item in enumerate(line):
            if 0 < j < 9:
                if item.startswith('m'):
                    posdata.append(int(int(item.strip('m'))/1000))
                elif int(item) == 0:
                    posdata.append(int(item))
                elif int(item) == 1:
                    if j % 2 == 0:
                        # y max
                        line[j] = str(z[-1])
                    else:
                        line[j] = str(x[-1])
                    posdata.append(int(line[j]))

            elif j >= 9:
                tdata.append(float(item))
        if i < 4 or i > 6:
            linear(posdata[0], posdata[1], posdata[3], posdata[4], posdata[5], posdata[7], tdata[0], tdata[1], tdata[2], tdata[3])
            ax1.plot(T[:, 50], z, label='step {} left continent'.format(i))
        if i == 5:
            halfspacetemp(posdata[0], posdata[1], posdata[3], posdata[4], tdata[0], tdata[1], tdata[6], tdata[5], z)
            ax2.plot(T[:, 1500], z, label='step {} ocean'.format(i))

        # cm = ax.pcolormesh(x, z, T)
        # plt.pause(0.001)
# fig.colorbar(cm)
ax1.set_xlabel("Temperature [K]")
ax1.set_ylabel("Depth [km]")
fig.legend()
# ax.set_xlabel("Horizontal distance [m]")
# ax.set_ylabel("Depth [km]")
# ax.set_title("Initial temperature for ref model steps 1-3, 5 and 6-7")

plt.show()
