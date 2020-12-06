from ForceCalculator import *

class TrenchSuctionCalculator(ForceCalculator):
    def __init__(self,  modelname, timestep, nx, nz, x_start, L_up, LAB, batch=False):
        super().__init__(modelname, timestep, nx, nz)
        self.name = modelname  # model name for file naming
        self.dt = timestep  # timestep of output (3 digits, i.e. 001-800)
        self.rho = None  # transposed density matrix from hdf5 file
        self.z = []  # vertical grid
        self.x = []  # horizontal grid
        self.nx = nx  # number of x-nodes
        self.nz = nz  # number of z-nodes
        self.dy = []  # Gridsteps in vertical direction
        self.s_xy = np.zeros((nz, nx))
        self.vx = np.zeros((nz, nx))
        self.LAB = LAB # Lithosphere-Asthenosphere boundary depth
        self.x_start = x_start
        self.L_up = L_up # length of upper plate
        if not batch:
            self.fig, self.ax = plt.subplots()
        self.batch = batch
        self.timesum = 0
        self.calculate_grid()

    def read_data(self):
        # Read the data using h5py package
        f = h5.File('E:/ThesisData/{}/{}{:03d}.gzip.h5'.format(self.name, self.name, self.dt), 'r')
        dset = f['NodeGroup']
        # print(list(f['VisMarkerGroup'].keys()))
        # print(list(dset.keys()))
        sxy_tmp = dset['sxy']
        tk_tmp = dset['tk']
        vx_tmp = dset['vx']
        eta_tmp = dset['nu']
        self.eta_eff = np.reshape(eta_tmp, (self.nx, self.nz)).transpose()
        self.tk = np.reshape(tk_tmp, (self.nx, self.nz)).transpose() - 273
        self.s_xy = np.reshape(sxy_tmp, (self.nx, self.nz)).transpose()
        self.vx = np.reshape(vx_tmp, (self.nx, self.nz)).transpose()
        self.timesum = f['/ModelGroup/Model'][0]/1e6 # Myr
        self.get_x_start()

    def get_x_start(self):
        plt.figure()
        XX, ZZ = np.meshgrid(self.x, self.z)
        d_sxy = self.s_xy[:, 1:] - self.s_xy[:, 0:-1]
        

    def get_vertical_velx_grad(self):
        """
        Plan: get 10 nodes above and below z_LAB, do a horizontal
        :return:
        """
        dVxdz = self.vx.transpose()[1:,1:] / np.array(self.dy)  # component-wise product of horizontal velocity with z step ~ dv/dz
        return dVxdz.transpose()

    def get_x_node(self, xpos:int):
        for i, x in enumerate(self.x):
            rest = xpos - x/1e3
            if abs(rest) <= 5:
                return i
        print("No match found for xpos {}".format(xpos))
        exit(1)

    def integrate(self, radius):
        """
        Iterate over z, if z within radius km of LAB, then integrate the shear stress.
        units: integral of N/m2 dx = N/m
        """
        vgrads = self.get_vertical_velx_grad()
        tractions = {}
        n_start = self.get_x_node(self.x_start)
        n_end = self.get_x_node(self.x_start+self.L_up)
        plot_depths = []
        forces = []
        for i, z in enumerate(self.z):
            if self.LAB - radius <= z/1e3 <= self.LAB + radius:
                tractions["{}".format(str(i))] = self.eta_eff[i, n_start:n_end+1] * vgrads[i, n_start:n_end+1]
                plot_depths.append(z)
                # forces.append(tractions[str(i)] * self.dx[n_start:n_end+1])
                forces.append(tractions[str(i)] * self.dx[n_start:n_end+1])

        if self.batch:
            meanminmax = np.zeros((len(plot_depths), 5))
            for i in range(len(plot_depths)):
                meanminmax[i, :] = self.timesum, plot_depths[i], -sum(forces[i])/len(forces[i]), min(-forces[i]), max(-forces[i])
            return meanminmax
        else:
            for i, depth in enumerate(plot_depths):
                self.ax.semilogy(self.x[n_start:n_end+1], -forces[i], '-', label="z={} km".format(depth/1e3))

            plt.grid(b=True)
            plt.xlabel("X position [m]")
            plt.ylabel("Mantle flow traction [N/m]")
            plt.title("Mantle traction around LAB for model {} (step={})".format(self.name, self.dt))
            plt.legend()
            plt.show()

data = np.zeros((69*4, 5))
index = 0
for i in range(10, 691, 10):
    TS = TrenchSuctionCalculator("ER", timestep=i, nx=1785, nz=509, x_start=1800-1.8*i, L_up=1000, LAB=160, batch=True)
    TS.read_data()
    data[index:index+4, :] = TS.integrate(radius=2)
    index += 4
    print("Using x_start = {} km at t = {} Myr. Is that somewhat accurate?".format(TS.x_start, TS.timesum))

plt.figure()

LABELS = []
def plot_from_data(data, col, offset, colour):
    index = 0
    t = []

    plotdata = []
    if col == 2:
        lw = 3
        sb = '*-'
        lb = 'mean'
    elif col == 3:
        lw = 1
        sb = '^--'
        lb = 'min'
    elif col == 4:
        lw = 1
        sb = 'v:'
        lb = 'max'
    label = "z={}km, {}".format(data[offset, 1] / 1e3, lb)
    if label not in LABELS:
        LABELS.append(label)
    while index < 69:
        plotdata.append(data[offset + 4 * index , col])
        t.append(data[offset + 4 * index, 0])
        index += 1
    plt.semilogy(t, plotdata,sb, color=colour, linewidth=lw)
    plt.semilogy()

colours = ['r', 'b','g', 'm']
for j in range(2, 5):
    for i in range(4):
        plot_from_data(data, j, i, colours[i])

plt.xlabel("Time [Myr]")
plt.ylabel("Mantle drag force [N/m]")
plt.title("Mantle drag force of upper plate for model {}".format(TS.name))
plt.grid(b=True)
plt.legend(labels=LABELS, ncol=2, loc='upper right')
plt.show()
# TS = TrenchSuctionCalculator("BJnew", timestep=370, nx=2001, nz=436, x_start=1220, L_up=1000, LAB=140)
#     TS.read_data()
#     data[index, :] = TS.integrate(radius=2)
# [XX, ZZ] = np.meshgrid(TS.x, TS.z)
# c = TS.ax.pcolormesh(XX, ZZ, TS.rho[0:-1,0:-1], vmin=3300, vmax=3600)
# SP.ax.set_aspect('equal')
# plt.colorbar(c)
# SP.ax.set_ylim(800, 0)

