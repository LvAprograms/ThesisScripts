import h5py as h5
import numpy as np
from plot_grids import get_steps_from_init_file
from matplotlib import pyplot as plt

class ForceCalculator(object):
    def __init__(self, modelname, timestep, nx, nz):
        self.name = modelname  # model name for file naming
        self.dt = timestep  # timestep of output (3 digits, i.e. 001-800)
        self.rho = None  # transposed density matrix from hdf5 file
        self.z = []  # vertical grid
        self.x = []  # horizontal grid
        self.dx = []
        self.nx = nx  # number of x-nodes
        self.nz = nz  # number of z-nodes
        self.dy = []  # Gridsteps in vertical direction

    def read_data(self):
        # Read the data using h5py package
        f = h5.File('E:/ThesisData/{}/{}{}.gzip.h5'.format(self.name, self.name, self.dt), 'r')
        dset = f['NodeGroup']
        print(list(f['VisMarkerGroup'].keys()))
        print(list(dset.keys()))
        rho_tmp = dset['ro']
        tk_tmp = dset['tk']
        self.tk = np.reshape(tk_tmp, (self.nx, self.nz)).transpose() - 273
        self.rho = np.reshape(rho_tmp, (self.nx, self.nz)).transpose()


    def calculate_grid(self):
        x_nodes, y_nodes, self.dx, self.dy = get_steps_from_init_file("../../initfiles/{}_init_ls.t3c".format(self.name))
        scale = 1
        dx = np.array(self.dx)
        dy = np.array(self.dy)
        # initial staggered grid cells:
        # self.x.append(dx[0]/1000/2)
        # self.z.append(self.dy[0]/1000/2)
        x0 = dx[0] * scale * 0.5
        z0 = dy[0] * scale * 0.5
        # Fill rest of staggered grid for accurate plotting
        x = np.empty(dx.shape)
        z = np.empty(dy.shape)
        x[1:] = dx[1:].cumsum() * scale + x0
        x[0] = x0
        z[1:] = dy[1:].cumsum() * scale + z0
        z[0] = z0
        # for j in range(1, self.nx-1):
        #     if j < self.nz-1:
        #         self.z.append(self.z[j - 1] + self.dy[j] / 1000)
        #         self.x.append(self.x[j - 1] + dx[j] / 1000)
        #     else:
        #         self.x.append(self.x[j - 1] + dx[j] / 1000)
        self.x = x
        self.z = z

    def topography(self, x1, x2):
        [XX, ZZ] = np.meshgrid(self.x, [-v + 20 for v in self.z])
        f, ax = plt.subplots()
        levels = [9, 450, 1300]
        # cp = ax.contour(XX, ZZ, self.rho[0:self.nz-1, 0:self.nx-1], levels)
        cp = ax.contour(XX, ZZ, self.tk[0:self.nz - 1, 0:self.nx - 1], levels)

        ax.set_xlabel("Distance [km]")
        ax.set_ylabel("Altitude [km]")
        ax.clabel(cp, inline=False, fontsize=10)
        ax.set_ylim([-15, 15])
        ax.set_xlim([600, 1900])
        ax.grid(b=True)
        ax.plot([self.x[x1] for _ in self.z], [-v + 10 for v in self.z], 'r--', label='"orogen"')
        ax.plot([self.x[x2] for _ in self.z], [-v + 10 for v in self.z], 'b--', label='"hinterland"')
        f.legend()
        # f.colorbar(cp)