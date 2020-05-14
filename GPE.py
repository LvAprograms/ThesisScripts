import h5py as h5
import numpy as np
from plot_grids import get_steps_from_init_file
from matplotlib import pyplot as plt



class GPE_calculator(object):
    def __init__(self, modelname, timestep, nx, nz, x_oro:int, x_hinter:int, z_iso=700):
        self.name = modelname       # model name for file naming
        self.dt = timestep          # timestep of output (3 digits, i.e. 001-800)
        self.rho = None             # transposed density matrix from hdf5 file
        self.z = []                 # vertical grid
        self.x = []                 # horizontal grid
        self.nx = nx                # number of x-nodes
        self.nz = nz                # number of z-nodes
        self.z_iso = z_iso
        self.P_total = np.zeros((nz-1, nx-1)) # total Pressure matrix
        self.P_mountain = []        # Pressure through mountain
        self.P_ref = []             # Pressure through hinterland
        self.dy = []                # Gridsteps in vertical direction
        self.fig, [self.ax1, self.ax2, self.ax3] = plt.subplots(1, 3) # axis on which to plot pressure profiles
        self.x_oro = x_oro          # node number of orogen core column
        self.x_hinter = x_hinter    # node number of hinterland

    def read_data(self):
        # Read the data using h5py package
        f = h5.File('E:/ThesisData/{}/{}{}.gzip.h5'.format(self.name, self.name, self.dt), 'r')
        dset = f['NodeGroup']
        # print(list(f['VisMarkerGroup'].keys()))
        print(list(dset.keys()))
        rho_tmp = dset['ro']
        tk_tmp = dset['tk']
        self.tk = np.reshape(tk_tmp, (self.nx, self.nz)).transpose() - 273
        self.rho = np.reshape(rho_tmp, (self.nx, self.nz)).transpose()

    def calculate_grid(self):
        x_nodes, y_nodes, dx, self.dy = get_steps_from_init_file("../../initfiles/{}_init_ls.t3c".format(modelname))

        # initial staggered grid cells:
        self.x.append(dx[0]/1000/2)
        self.z.append(self.dy[0]/1000/2)

        # Fill rest of staggered grid for accurate plotting
        for j in range(1, self.nx-1):
            if j < self.nz-1:
                self.z.append(self.z[j - 1] + self.dy[j] / 1000)
                self.x.append(self.x[j - 1] + dx[j] / 1000)
            else:
                self.x.append(self.x[j - 1] + dx[j] / 1000)


    def calc_P(self):
        limit = self.nz-1
        locs = [self.x_oro, self.x_hinter]
        for i, loc in enumerate(locs):
            P = [0]
            for j in range(1, limit):
                if self.z[j] <= self.z_iso+5:
                    P.append(P[j - 1] - self.rho[j, loc] * 9.80665 * self.dy[j])
                else:
                    P.append(0)

            self.P_total[:, loc] = P
            self.ax1.plot(P, self.z, label="x-node {}".format(loc))

        self.P_mountain = self.P_total[:, self.x_oro]
        self.P_ref = self.P_total[:, self.x_hinter]
        diff = []       # Pressure difference at each depth interval
        GPE = []        # Integral of pressure difference down to each depth interval
        for i in range(len(self.P_ref)):
            diff.append(self.P_mountain[i] - self.P_ref[i])
            GPE.append(diff[i] * self.z[i])
        # dGPE = self.z.index()
        print("The total difference in GPE per unit area down to {} km, between orogen and hinterland is {:.4f} TN/m".format(self.z_iso, max(diff)/1e12))
        self.ax3.plot(GPE, self.z)
        self.ax2.plot([val/1E6 for val in diff], self.z)

    def label_plot(self):
        self.ax1.set_ylim([self.z_iso, 0])
        self.ax1.set_xlim([0, min(self.P_mountain)])
        self.ax1.set_xlabel("Pressure [Pa]")
        self.ax1.set_ylabel("Depth [km]")
        self.ax1.grid(b=True)
        self.ax1.set_title('Lithostatic pressure at orogen vs hinterland')
        self.ax1.legend()

        self.ax2.set_title(r'Lithostatic pressure difference')
        self.ax2.set_ylim([self.z_iso, 0])
        self.ax2.set_xlabel(r'$P_{oro}(z) - P_{ref}(z)$ [MPa]')
        self.ax2.set_ylabel("Depth [km]")
        self.ax2.grid(b=True)
        self.ax2.set_ylabel('Depth [km]')

        self.ax3.set_ylim([self.z_iso, 0])
        self.ax3.set_xlabel(r'$\int_{z}^{0}(P_{oro} - P_{ref})(z))gdz$ [N/m]')
        self.ax3.grid(b=True)
        self.ax3.set_title('GPE difference with depth')

        plt.suptitle("GPE Model {}".format(self.name))

        plt.pause(0.001)

    def topography(self):
        [XX, ZZ] = np.meshgrid(self.x, [-v + 20 for v in self.z])
        f, ax = plt.subplots()
        levels = [9, 450, 1300]
        # cp = ax.contour(XX, ZZ, self.rho[0:self.nz-1, 0:self.nx-1], levels)
        cp = ax.contour(XX, ZZ, self.tk[0:self.nz-1, 0:self.nx-1], levels)

        ax.set_xlabel("Distance [km]")
        ax.set_ylabel("Altitude [km]")
        ax.clabel(cp, inline=False, fontsize=10)
        ax.set_ylim([-250, 15])
        ax.set_xlim([600, 1900])
        ax.grid(b=True)
        ax.plot([self.x[self.x_oro] for _ in self.z], [-v+10 for v in self.z], 'r--', label='"orogen"')
        ax.plot([self.x[self.x_hinter] for _ in self.z], [-v+10 for v in self.z], 'b--', label='"hinterland"')
        f.legend()
        # f.colorbar(cp)


modelname = "BJ_new"

testGPE = GPE_calculator(modelname, timestep=370, nx=2001, nz=436, x_oro=120, x_hinter=1800, z_iso=270)
testGPE.read_data()
testGPE.calculate_grid()
testGPE.calc_P()
testGPE.label_plot()
# plt.savefig("GPE_{}_t{}.png".format(modelname, testGPE.dt))

testGPE.topography()

plt.savefig("{}_{}_topo_GPElocs.png".format(modelname, testGPE.dt))

plt.show()
