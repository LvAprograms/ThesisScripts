import h5py as h5
import numpy as np
from plot_grids import get_steps_from_init_file
from matplotlib import pyplot as plt
from ForceCalculator import *


class GPE_calculator(ForceCalculator):
    def __init__(self, modelname, timestep, nx, nz, x_oro:int, x_hinter:int, z_iso=700):
        super().__init__(modelname, timestep, nx, nz)
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


    def calc_P(self):
        limit = self.nz-1
        locs = [self.x_oro, self.x_hinter]
        for i, loc in enumerate(locs):
            P = [0]
            for j in range(1, limit):
                if self.z[j]/1e3 <= self.z_iso+5:
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

    def topography(self, x1, x2):
        x_km = [v/1000 for v in self.x]
        z_km = [v/1000 for v in self.z]
        [XX, ZZ] = np.meshgrid(x_km, [-v + 20 for v in z_km])
        f, ax = plt.subplots(figsize=(12,4))
        levels = [9]
        # cp = ax.contour(XX, ZZ, self.rho[0:self.nz-1, 0:self.nx-1], levels)
        cp = ax.contour(XX, ZZ, self.tk[0:self.nz-1, 0:self.nx-1], levels)
        cp2 = ax.contour(XX, ZZ, self.rho[0:self.nz-1, 0:self.nx-1], [3100])

        ax.set_xlabel("Distance [km]")
        ax.set_ylabel("Altitude [km]")
        #ax.clabel(cp, inline=False, fontsize=10)
        #ax.clabel(cp2, inline=False, fontsize=10)

        ax.set_ylim([-5, 10])
        ax.set_xlim([250, 2000])
        ax.grid(b=True)
        # ax.plot([x_km[x1] for _ in self.z], [-v+10 for v in z_km], 'r--', label='"orogen"')
        # ax.plot([x_km[x2] for _ in self.z], [-v+10 for v in z_km], 'b--', label='"hinterland"')
        # f.legend()
        # f.colorbar(cp)


modelname = "FT"

testGPE = GPE_calculator(modelname, timestep=800, nx=1785, nz=509, x_oro=250, x_hinter=1400, z_iso=270)
testGPE.read_data()
testGPE.calculate_grid()
# testGPE.calc_P()
# testGPE.label_plot()
# plt.savefig("GPE_{}_t{}.png".format(modelname, testGPE.dt))

testGPE.topography(testGPE.x_oro, testGPE.x_hinter)

# plt.savefig("{}_{}_topo_GPElocs.png".format(modelname, testGPE.dt))

plt.show()
