from matplotlib import pyplot as plt
import numpy as np
from ForceCalculator import *


class SlabPullCalculator(ForceCalculator):
    def __init__(self, modelname, timestep, nx, nz, slab_dip, tipleft, tipright, origin):
        super().__init__(modelname, timestep, nx, nz)
        self.name = modelname  # model name for file naming
        self.dt = timestep  # timestep of output (3 digits, i.e. 001-800)
        self.rho = None  # transposed density matrix from hdf5 file
        self.z = []  # vertical grid
        self.x = []  # horizontal grid
        self.nx = nx  # number of x-nodes
        self.nz = nz  # number of z-nodes
        self.dy = []  # Gridsteps in vertical direction
        self.tipright = tipright
        self.tipleft = tipleft
        self.x_tip = tipright[0] # rightmost point of slab
        self.z_tip = tipleft[1]  # deepest point of slab
        self.dip = slab_dip      # slab dip in degrees
        self.origin = (origin[0], origin[1]) # origin of rotated coordinate frame.
        self.rho_mantle = np.zeros((nz, nx)) # matrix containing average mantle density at that depth.
        self.rho_slab = np.zeros((nz, nx))
        self.x_rot = None  # placeholder for rotated x vector
        self.z_rot = None  # placeholder for rotated z vector
        self.nz_x = []     # indices of x values that are rotated so we can find them
        self.nz_z = []     # indices of z values that are rotated so we can find them
        self.fig, self.ax = plt.subplots()
        self.calculate_grid()


    def rotate_axes(self, angle:float, X, Z):
        """
        SOSCASTOA: sin(angle) = Overstaand/Schuin, cos(angle) = Aanliggend/Schuin
        Schuin = Overstaand/sin(angle)
        Schuin = Aanliggend/cos(angle)
        :param angle: slab dip and angle by which the x- and z-axes have to be rotated.
        :return:rotated x and z mesh?
        """
        theta = np.deg2rad(angle)
        print("initiating rotation...\n")
        e = np.array((np.cos(theta), np.sin(theta)))    # unit vector representing the rotation
        x_rot = np.zeros(len(X))
        z_rot = np.zeros(len(Z))
        # check if positioned inside slab area
        nz_x = [] # nonzero x indices of rotated axis
        nz_z = [] # nonzero z indices
        for i, x in enumerate(X):
            if self.origin[0]*1e3 <= x <= self.x_tip*1e3:
                nz_x.append(i)
                for j, z in enumerate(Z):
                    if self.origin[1]*1e3 <= z <= self.z_tip*1e3:
                        if len(nz_x) == 1:
                            nz_z.append(j)
                        v = np.array((x-self.origin[0]*1e3, z-self.origin[1]*1e3)) # vector representation of x and z coordinates
                        # rotate x and z at that point
                        v_rot = np.cos(theta) * v + np.sin(theta) * np.cross(e, v)\
                                               + (1 - np.cos(theta)) * (np.dot(e, v)) * e
                        x_rot[i], z_rot[j] = v_rot[0], v_rot[1]
        print("rotation completed\n")
        self.nz_x = np.array(nz_x)
        self.nz_z = np.array(nz_z)
        return x_rot[nz_x[0]:nz_x[-1]], z_rot[nz_z[0]:nz_z[-1]]


    def plot_delta_rhos(self, ref=3350):
        drhos = self.rho
        for i in range(1,drhos.shape[0]):
            for j in range(1,drhos.shape[1]):
                drhos[i,j] = self.rho[i,j] - ref
        plt.figure()
        xx, zz = np.meshgrid(self.x, self.z)
        plt.pcolormesh(xx, zz, drhos[1:,1:], vmin=-100, vmax=200)
        plt.gca().invert_yaxis()
        plt.gca().set_aspect('equal')
        plt.colorbar()
        plt.show()

    def integrate_slab_area(self):
        """
        Calculates mean densities of the mantle below the lower plate, and of the slab by using the local coordinate
        system. then it integrates the density difference.
        units: [rho] * [g] = m/s2 * kg/m3 = kg*m/(s2*m2) = (kg*m/s2) * (1/m2) = N/m2. integrate over x and z
        gives N.
        :return: series of mean slab and mantle density as a function of (rotated?) depth
        """
        self.read_data() # to get the density matrix
        self.x_rot, self.z_rot = self.rotate_axes(self.dip, self.x, self.z)
        # self.check_x, self.check_z = self.rotate_axes(-self.dip, self.x_rot, self.z_rot)
        self.rho_slab = np.zeros((self.nz_z[-1]-self.nz_z[0], self.nz_x[-1] - self.nz_x[0]))
        self.rho_mantle = np.zeros((self.nz_x[-1]-self.nz_x[0], self.nz_x[-1] - self.nz_x[0]))
        # self.plot_delta_rhos()
        # TODO: iterate over nonzero rotated coordinates, get density with the nonzero index lists, sum them, average them
        F = []
        rho_changes = np.zeros((len(self.x_rot),1))
        for i, xc in enumerate(self.x_rot):
            d_rho = []
            if i > 0:
                dx = xc - self.x_rot[i-1] * 1e3
                for j, zc in enumerate(self.z_rot):
                    if j > 0:
                        dz = zc - self.z_rot[j-1] * 1e3
                        dA = dx * dz
                        self.rho_slab[j,i] = self.rho[self.nz_z[j], self.nz_x[i]] # slab density in the local coordinates
                        #FIXME: rho_mantle[i] is overwritten each time. If it depends on j, use j?
                        self.rho_mantle[j, i] = sum(self.rho[self.nz_z[j],0:self.nz_x[0]-10])/(self.nz_x[0]-10) # average density up to the slab position
                        d_rho.append(sum(self.rho_mantle[j,:])/len(self.nz_x) - sum(self.rho_slab[:,i])/len(self.nz_z))
                rho_changes[i-1]= sum(d_rho)
                F.append(9.81*sum(d_rho) * dA)
        plt.figure()
        plt.plot(self.x[self.nz_x[0]:self.nz_x[-1]], rho_changes)
        plt.show()
        print("the slab pull force is {}N/m. Is that reasonable?".format(sum(F)))





# SP = SlabPullCalculator("BJ_new", timestep=150, nx=2001, nz=436, slab_dip=-55, tipleft=(1300,500), tipright=(1420,420), origin=(1000,100))
SP = SlabPullCalculator("BJ_new", timestep=150, nx=2001, nz=436, slab_dip=-25, tipleft=(1700,390), tipright=(1800,320), origin=(1350,100))

SP.integrate_slab_area()
[XX, ZZ] = np.meshgrid(SP.x, SP.z)
c = SP.ax.pcolormesh(XX, ZZ, SP.rho[0:-1,0:-1], vmin=3300, vmax=3600)
for point in [SP.origin, SP.tipleft, SP.tipright]:
    SP.ax.plot(point[0], point[1], 'x')
SP.ax.set_aspect('equal')
plt.colorbar(c)
SP.ax.set_ylim(800, 0)
plt.show()