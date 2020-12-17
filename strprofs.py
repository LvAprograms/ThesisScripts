from znode import *
from math import floor
import h5py as h5
import numpy as np
from plot_grids import get_steps_from_init_file

# TODO: Rewrite this strength profile part such that it doesn't need so many hardcoded variables.


class Material(object):
    """Holds material properties read from the database table with keyword word"""
    def __init__(self, line):
        d = line
        self.type        = d[0]             # material index              -
        self.eta_MIN     = d[1]             # Minimum viscosity        Pa.s
        self.eta_MAX     = d[2]             # Maximum viscosity        Pa.s
        self.sigma_MIN   = d[3]             #                          Pa
        self.sigma_MAX   = d[4]             #                          Pa
        self.inv_Ad      = d[5]             # 1/Ad                     Pa^n/s
        self.Ad          = 1/self.inv_Ad    # Pre-np.exponential factor   Pa^n-1/s
        self.Ea          = d[6]             # Activation energy E,     J/mol
        self.Va          = d[7]             # Activation volume
        self.sigma_trans = d[8]             # change disl to diffcreep Pa
        self.n           = d[9]             # Stress np.exponent,         -
        self.G           = d[10]            # elastic shear modulus,   Pa
        self.defLamb     = d[11]            # default lambda(1-Pf/Ps) when no fluids
        self.Cmin        = d[12]            # min. cohesion,           Pa
        self.Cmax        = d[13]            # max. cohesion            Pa
        self.mu_min      = d[14]            # min. friction coeff      -
        self.mu_max      = d[15]            # max. friction coeff      -
        self.eps_trans   = d[16]            # needed strain for weaken.-
        self.eps_max     = d[17]            # strain when max weakened.-
        self.rho_lim1    = d[18]            # something with dilatation-
        self.rho_lim2    = d[19]            # same                     -
        self.rho_0       = d[20]            # initial density          kg/m3
        self.alpha       = d[21]            # thermal np.expansivity      K-1
        self.beta        = d[22]            # compressibility          MPa-1
        self.Cp          = d[23]            # Volumetric heat capac.   J/kg/K
        self.k0          = d[24]            # thermal conductivity     W/m/K
        self.kz          = d[25]            # T dep. coeff for k       -
        self.kP          = d[26]            # P dep. coeff for k       -
        self.Hr          = d[27]            # internal heat production W/m3


class StrengthProfile(object):
    def __init__(self, xnode, xcoord, z, materials, strainratelists, log=False):
        self.materials = materials          # Layering used
        self.log = log
        self.z = z                          # depth vector in m
        self.x_prof = xcoord
        self.node_prof = xnode
        self.sigma_brit = []             # yield strength for mu_max
        self.sigma_visc = []                # Viscous strength (2 * eta_eff * strainrate)
        self.strength = []               # Yield strength in the case of sigma_britmin
        self.strainrates = strainratelists  # input the strainrates for which the viscous strength is calculated
        self.fig, self.ax = plt.subplots()  # Figure to hold the strength profile
        self.composition = []
        self.mrho = []
        self.mtk = []
        self.mpr = []
        self.lithoP = []
        self.sigma_brit = []
        self.read_marker_data(setup=False)
        self.transition_nodes = self.get_layering_from_density()
        self.calc_brittle()

        # self.make_marker_grid()
        # self.calc_rho()
        # self.calc_k()
        # self.ax.invert_yaxis()

    def read_marker_data(self, setup=True):
        if setup:
            f = h5.File('E:/ThesisData/{}/setup001.gzip.h5'.format(MODEL), 'r')
        else:
            f = h5.File('E:/ThesisData/{}/{}800.gzip.h5'.format(MODEL, MODEL), 'r')
        dset = f['NodeGroup']
        print(list(f['VisMarkerGroup'].keys()))
        print(list(dset.keys()))

        rho_tmp = dset['ro']
        tk_tmp = dset['tk']
        pr_tmp = dset['pr']
        # s_brit = dset['sbrit']
        self.mtk = np.reshape(tk_tmp, (nx, nz))[self.node_prof]
        self.mpr = np.reshape(pr_tmp, (nx, nz))[self.node_prof]
        self.mrho = np.reshape(rho_tmp, (nx, nz))[self.node_prof]
        self.eta_eff = np.reshape(dset['nu'], (nx, nz))[self.node_prof]
        # self.sigma_brit = np.reshape(s_brit, (nx, nz))[self.node_prof]


    def get_layering_from_density(self):
        # iterate over density to find large changes. Correlate to materials using these steps.
        prev = 0
        transition_nodes = []
        d_rhos = np.zeros((len(self.mrho), 1))
        ynode = 0
        while ynode < len(self.mrho[0:-2]):
            if self.z[ynode] < 250:
                drho = self.mrho[ynode] - prev
                d_rhos[ynode] = drho
                if drho > 50:
                    transition_nodes.append(ynode+2)
                    prev = self.mrho[ynode+1]
                    ynode += 2
                else:
                    prev = self.mrho[ynode]
                    ynode += 1
            else:
                break
        # plt.plot(d_rhos[0:-1], self.z)
        # plt.gca().invert_yaxis()
        # plt.show()
        return transition_nodes

    def calc_brittle(self):
        P = 0
        self.sigma_brit = np.zeros((nz))
        mean_rho = 0
        for node, depth in enumerate(z):
            if node > 0:
                dz = depth - z[node-1]
                P += self.mrho[node] * 9.81 * dz * 1000
            else:
                P = 0
            self.lithoP.append(P)
            if node <= self.transition_nodes[0]:
                # air
                index = 0
            elif self.transition_nodes[0] < node <= self.transition_nodes[1]:
                # upper crust
                index = 4
            elif self.transition_nodes[1] < node <= self.transition_nodes[2]: # FIXME: not working if lower crust is plagioclase
                # lower crust
                index = 5
            elif z[node] < 160e3:
                # lithospheric mantle
                index = 9
            else:
                # asthenosphere
                index = 10

            self.sigma_brit[node] = materials[index].Cmax + materials[index].mu_max * (1 - materials[index].defLamb) * P


    def my_eff_visc(self, strainrate:float):
        for node in range(len(self.z)):
            if node <= self.transition_nodes[0]:
                # air
                index = 0
            elif self.transition_nodes[0] < node <= self.transition_nodes[1]:
                # upper crust
                index = 4
            elif self.transition_nodes[1] < node <= self.transition_nodes[2]: # FIXME: not working if lower crust is plagioclase
                # lower crust
                index = 5
            elif z[node] < 160e3:
                # lithospheric mantle
                index = 9
            else:
                # asthenosphere
                index = 10
            M = materials[index]
            F2 = 1 / (2 ** ((2*M.n-1)/M.n))
            exponent = np.exp((M.Ea + M.Va * self.lithoP[node]) / (M.n * 8.314 * self.mtk[node]))
            preexponent = 1 / (M.Ad ** (1/M.n) * strainrate ** ((M.n -1)/M.n))
            self.eta_eff[node] = F2 * preexponent * exponent


    def calc_viscous(self, strainrate:float):
        self.my_eff_visc(strainrate)
        for i, node in enumerate(self.z):
            self.sigma_visc.append(2 * self.eta_eff[i] * strainrate)

    def draw_1D(self):
        vars = [self.mtk, self.sigma_brit, self.mrho, np.log10(self.eta_eff)]
        xlabels = ["Temperature [K]", 'Lithostatic Presure [Pa]', "Density [kg/m3]", r'log$_{10}(\eta_{eff})$']
        fig, axes = plt.subplots(2,2, figsize=(8,7))
        plt.suptitle("Visualisation parameters for model {} at x = {}km".format(MODEL, self.x_prof))
        for i, var in enumerate(vars):
            if type(var) != list:
                var = var.transpose()
            axes.flatten()[i].plot(var[1::],self.z)
            axes.flatten()[i].invert_yaxis()
            axes.flatten()[i].grid(b=True)
            axes.flatten()[i].set_xlabel(xlabels[i])
            axes.flatten()[i].set_ylabel("Depth [km]")
            axes.flatten()[i].set_ylim([250, 0])


    def draw(self, strainrate:float=1E-14, zmin=0, zmax=250):
        """Calculates strength and plots it against depth"""
        self.calc_viscous(strainrate)
        for i, sv in enumerate(self.sigma_visc):
            if sv <= self.sigma_brit[i]:
                self.strength.append(sv)
            else:
                self.strength.append(self.sigma_brit[i])
        mpa = [val/1E6 for val in self.strength]
        if self.log:
            self.ax.semilogx(mpa, self.z, linewidth=2, label=r'$\mu_{max}, \dot{\epsilon}$' + "= {}".format(strainrate))
        else:
            # self.ax.plot(mpa, [z - 20 for z in self.z], label=r'$\mu_{max}, \dot{\epsilon}$' + "= {}".format(strainrate))
            self.ax.plot(mpa, self.z, linewidth=2, label=r'$\mu_{max}, \dot{\epsilon}$' + "= {}".format(strainrate))
            plt.pause(0.001)

        # self.ax.plot(mpamin, [z/1000 for z in self.z], label=r'$\mu_{min}, \dot{\epsilon}$' + "= {}".format(strainrate))

        self.ax.set_ylim(zmax, zmin)
        if self.log:
            self.ax.set_xlim([1E0, 1E4])
        else:
            self.ax.set_xlim([0, max(mpa)+ 100])

    def add_profile(self, strainrate:float):
        """Add the profile for another strainrate """
        self.sigma_visc = []
        self.strength = []
        self.draw(strainrate)
        # self.ax.invert_yaxis()

    def draw_all(self):
        for e in self.strainrates:
            self.add_profile(e)
        # self.fig.legend(ncol=2, loc='upper right', fancybox=True)
        self.ax.set_xlabel("Differential stress [MPa]")
        self.ax.set_ylabel("Depth [km]")
        # self.ax.grid(b=True)

    def draw_boundaries(self, midcrust, moho, LAB, air=20):
        BLACK = (0.0, 0.0, 0.0)
        BROWN = (0.6, 0.4, 0.0)
        RED = (1.0, 0.0, 0.0)
        BLUE = (0.0, 0.0, 1.0)
        colours = [BLACK, BROWN, RED, BLUE]
        labels = ['surface', 'mid-crust', 'moho', 'LAB']
        layers = [air, midcrust, moho, LAB]
        plotrange = [0, 2000]
        for i in range(4):
            self.ax.plot(plotrange, [layers[i], layers[i]], linestyle='--', color=colours[i], label=labels[i])
        self.fig.legend(ncol=2, loc='lower right', fancybox=True)


# TODO: get grid
def calc_grid():
    x_nodes, y_nodes, dx, dy = get_steps_from_init_file("../../initfiles/{}_init_ls.t3c".format(MODEL))
    x = []
    z = []
    # initial staggered grid cells:
    x.append(dx[0] / 1000 / 2)
    z.append(dy[0] / 1000 / 2)

    # Fill rest of staggered grid for accurate plotting
    for j in range(1, nx - 1):
        if j < nz - 1:
            z.append(z[j - 1] + dy[j] / 1000)
            x.append(x[j - 1] + dx[j] / 1000)
        else:
            x.append(x[j - 1] + dx[j] / 1000)
    return x, z


MODEL = "ER"
COL = 50                # where on the x axis do we want a strength profile


# TODO: get possible rock units from initfile
materials = []
with open("../../initfiles/{}_init_ls.t3c".format(MODEL)) as f:
    lines = f.readlines()
    nx = int(lines[1].split('-')[0])
    nz = int(lines[2].split('-')[0])
    xsize = int(lines[5].split('-')[0]) / 1e3
    ysize = int(lines[6].split('-')[0]) / 1e3

rocklines = []
for i, line in enumerate(lines):
    if line.startswith("/ROCKS_DESCRIPTIONS"):
        rocklines.append(i)
    if line.startswith("/END_ROCKS_DESCRIPTIONS"):
        rocklines.append(i)
for i in range(rocklines[0] + 2, rocklines[1]-1, 2):
    line = [float(v) for v in lines[i].split()]
    materials.append(Material(line))
print(materials)

#TODO: get marker data so that the rock type at this location can be determined?


#
# # TODO: get position on the grid for strength profile:
x, z = calc_grid()
str_pos = x[COL-1]



strprof = StrengthProfile(COL, str_pos, z, materials, [1E-13, 1E-14, 1E-15], log=False)
strprof.draw_1D()
# strprof.draw_layering()
# strprof.draw_all()
# strprof.add_profile(strainrate=1E-16)
# strprof.add_profile(strainrate=1E-15)
# strprof.draw_boundaries(40, 55, 140)
# strprof.ax.set_title("Strength profile for model {} through x = {} km".format(MODEL, str_pos))
 # """
plt.show()



# Lz = 800e3              # Depth of model, m
# nz = 508               # amount of nodes
# L_sticky = 20e3         # Thickness of sticky air
# L_uc = L_sticky + 20e3  # upper crustal bottom depth
# L_lc = L_uc + 15e3      # lower crustal bottom depth
# L_lm = 100e3            # lithosphere thickness
# L_m = L_lc              # moho depth
# nx = 1648
# # Read the data
# modelname = "CW"
# f = h5.File('E:/ThesisData/{}/setup001.gzip.h5'.format(modelname), 'r')
# dset = f['NodeGroup']
# print(list(f['VisMarkerGroup'].keys()))
# print(list(dset.keys()))
# rho_tmp = dset['ro']
# tk_tmp = dset['tk']
# pr_tmp = dset['pr']
# tk_tmp = np.reshape(tk_tmp, (nx, nz))
# pr_tmp = np.reshape(pr_tmp, (nx, nz))
# rho_tmp = np.reshape(rho_tmp, (nx, nz))
# eta_tmp = np.reshape(dset['nu'], (nx, nz))
#
# # Construct material database for this profile
# database = {}
# with open("CJ_rocprops.txt", 'r') as rheology:
#     rock = "rockless"
#     for i, line in enumerate(rheology.readlines()):
#         if line.startswith("/"):
#             rock = line.strip('/').strip('\n')
#             if rock not in database.keys():
#                 database[rock] = []
#             else:
#                 rock += "{}".format(i)
#                 database[rock] = []
#
#         else:
#             if rock != "rockless":
#                 for v in line.strip('\n').split():
#                     database[rock].append(float(v))
#
#
# materials = {"SA": Material("sticky_air_approximation", database),
#              "UC": Material("upper_continental_crust_dalzilio2018_wet_quartzite", database),
#              "LC": Material("lower_continental_crust_dalzilio2018_mafic_granulite", database),
#              "UOC": Material("interface_basalt_wet_quartzite", database),
#              "LOC": Material("lower_oceanic_crust_gabbro_anorthite_75%", database),
#              "LM": Material("lithospheric_mantle_dry_olivin", database),
#              "AM": Material("astenospheric_mantle_dry_olivin",database)}
#
# # for k, v in database.items():
# #     if k.startswith("dalzilio2018"):
# #         print("{}: {}".format(k, v))
# #
# x_stag = []
# x = []
# x_size = f['ModelGroup']['Model'][1]
# z_size = f['ModelGroup']['Model'][2]
# x_nodes = int(f['ModelGroup']['Model'][3])
# for i in range(1, x_nodes+1):
#     x.append(find_x(i))
#     if i > 1:
#         x_stag.append((x[i - 2] + x[i-1])/2)
# print(x_stag[0], x_stag[-1])
#
#
# nodes = []
# nodes.append(Znode(0, 0))
# z = [0]
# nodes[0].material = materials["SA"]
# for i in range(1, nz):
#     if i < 250:
#         nodes.append(Znode(i, nodes[i - 1].z + 400))
#         z.append(z[i-1] + 400)
#         if nodes[i].z <= L_sticky:
#             nodes[i].material = materials["SA"]
#         elif L_sticky < nodes[i].z <= L_uc:
#             nodes[i].material = materials["UC"]
#         elif L_uc < nodes[i].z <= L_m:
#             nodes[i].material = materials["LC"]
#         elif L_m < nodes[i].z <= L_lm:
#             nodes[i].material = materials["LM"]
#     elif 250 <= i < 300:
#         nodes.append(Znode(i, nodes[i - 1].z + 1000))
#         z.append(z[i-1] + 1000)
#         if L_m < nodes[i].z <= L_lm:
#             nodes[i].material = materials["LM"]
#         else:
#             nodes[i].material = materials["AM"]
#     elif 300 <= i < 350:
#         nodes.append(Znode(i, nodes[i - 1].z + 2500))
#         z.append(z[i-1] + 2500)
#         nodes[i].material = materials["AM"]
#     elif 350 <= i < nz:
#         nodes.append(Znode(i, nodes[i - 1].z + 5000))
#         z.append(z[i-1] + 5000)
#         nodes[i].material = materials["AM"]
#
#
# # Visualise variables in 1D
# vars = [tk_tmp, pr_tmp, rho_tmp, np.log10(eta_tmp)]
# xlabels = ["Temperature [K]", "Pressure [Pa]", "Density [kg/m3]", r'log$_{10}(\eta_{eff})$']
# fig, axes = plt.subplots(2,2)
# plt.suptitle("Visualisation parameters for model {} at x = {}km".format(modelname, find_x(COL)))
# for i, var in enumerate(vars):
#     var = var.transpose()
#     axes.flatten()[i].plot(var[:, COL], [n.z/1000 for n in nodes])
#     #fig.colorbar(axes.flatten()[i].pcolormesh(var), cmap='hot', ax=axes.flatten()[i])
#     axes.flatten()[i].invert_yaxis()
#     axes.flatten()[i].grid(b=True)
#     axes.flatten()[i].set_xlabel(xlabels[i])
#     axes.flatten()[i].set_ylabel("Depth [km]")
#     axes.flatten()[i].set_ylim([250, 0])
#     # axes.flatten()[i].colorbar()
# # plt.show()
# axes.flatten()[2].set_xlim([2700, 3550])
# # dset = f['VisMarkerGroup']
# # print(dset['Mtype'])
#
# plt.figure()
# plt.plot([node.material.type for node in nodes], [node.z/1000 for node in nodes],'-')
# plt.ylim([0, 100])
# plt.gca().invert_yaxis()
#
#
# # for rock, data in database.items():
# #     print(rock, data)
# # print(len(database['sticky_air_approximation']))
#
#
# # """
# for node in nodes:
#     node.rho = rho_tmp.transpose()[node.index, COL]
#     node.eta_eff = eta_tmp.transpose()[node.index, COL]
#     node.P = pr_tmp.transpose()[node.index, COL]
#     node.T = tk_tmp.transpose()[node.index, COL]
# # axes[1,1].plot(pr_tmp.transpose()[:, COL], [n.z for n in nodes])
# strprof = StrengthProfile(nodes, materials, [1E-14, 1E-16], log=False)
# strprof.draw_layering()
# strprof.draw_all()
# # strprof.add_profile(strainrate=1E-16)
# # strprof.add_profile(strainrate=1E-15)
# plt.title("vertical strength profile through x = {} km".format(find_x(COL)))
#  # """
# plt.show()


# fig, [ax1, ax2] = plt.subplots(1,2)
# y = [n.z for n in nodes]
# x = [n.material.type for n in nodes]
# ax1.plot(x,y)
# plt.grid(b=True)
# ax1.invert_yaxis()
# # plt.show()
#
# # Initial geotherm
# T = np.zeros(nz)
# T0 = 293    # K
# Tm = 1617.6 # K
# T[0] = 293
# c0 = T[0]
# for node in nodes:
#     node.T = node.calc_T(Tm, L_lm)
# xT = [n.T for n in nodes]
# ax2.plot(xT, y)
# ax2.invert_yaxis()
# plt.show()
